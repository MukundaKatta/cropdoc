"""Tests for the analyzer module: severity, treatment, spread."""

import pytest
import torch

from cropdoc.models import (
    Diagnosis,
    Disease,
    LeafImage,
    SeverityLevel,
    TreatmentPlan,
    TreatmentType,
)
from cropdoc.analyzer.severity import SeverityEstimator
from cropdoc.analyzer.treatment import TreatmentRecommender
from cropdoc.analyzer.spread import (
    EnvironmentalConditions,
    SpreadPredictor,
    SpreadForecast,
)
from cropdoc.detector.diseases import DiseaseDatabase


def _make_disease() -> Disease:
    db = DiseaseDatabase()
    return db.get("Tomato Early Blight")


def _make_diagnosis(
    severity: float = 0.5,
    level: SeverityLevel = SeverityLevel.MODERATE,
) -> Diagnosis:
    return Diagnosis(
        image=LeafImage(width=224, height=224),
        disease=_make_disease(),
        confidence=0.9,
        severity_score=severity,
        severity_level=level,
        affected_area_pct=severity * 60,
    )


class TestSeverityEstimator:
    def setup_method(self):
        self.estimator = SeverityEstimator()

    def test_estimate_returns_expected_keys(self):
        image = torch.rand(1, 3, 224, 224)
        prediction = {"confidence": 0.9, "disease_name": "Test"}
        result = self.estimator.estimate(image, prediction)
        assert "severity_score" in result
        assert "severity_level" in result
        assert "affected_area_pct" in result
        assert "confidence_factor" in result

    def test_severity_score_in_range(self):
        image = torch.rand(1, 3, 224, 224)
        prediction = {"confidence": 0.8}
        result = self.estimator.estimate(image, prediction)
        assert 0.0 <= result["severity_score"] <= 1.0

    def test_severity_level_is_enum(self):
        image = torch.rand(3, 224, 224)
        prediction = {"confidence": 0.7}
        result = self.estimator.estimate(image, prediction)
        assert isinstance(result["severity_level"], SeverityLevel)

    def test_affected_area_non_negative(self):
        image = torch.rand(1, 3, 224, 224)
        prediction = {"confidence": 0.5}
        result = self.estimator.estimate(image, prediction)
        assert result["affected_area_pct"] >= 0

    def test_green_image_lower_severity(self):
        # Very green image should have lower severity
        green = torch.zeros(3, 224, 224)
        green[1] = 0.8  # strong green channel
        pred = {"confidence": 0.5}
        result_green = self.estimator.estimate(green, pred)

        # Dark/brown image should have higher severity
        brown = torch.zeros(3, 224, 224)
        brown[0] = 0.4  # reddish
        brown[1] = 0.15  # low green
        brown[2] = 0.05
        result_brown = self.estimator.estimate(brown, pred)

        assert result_green["severity_score"] < result_brown["severity_score"]

    def test_score_to_level_mapping(self):
        assert SeverityEstimator._score_to_level(0.05) == SeverityLevel.HEALTHY
        assert SeverityEstimator._score_to_level(0.2) == SeverityLevel.MILD
        assert SeverityEstimator._score_to_level(0.4) == SeverityLevel.MODERATE
        assert SeverityEstimator._score_to_level(0.7) == SeverityLevel.SEVERE
        assert SeverityEstimator._score_to_level(0.9) == SeverityLevel.CRITICAL


class TestTreatmentRecommender:
    def setup_method(self):
        self.recommender = TreatmentRecommender()

    def test_recommend_returns_plan(self):
        diag = _make_diagnosis()
        plan = self.recommender.recommend(diag)
        assert isinstance(plan, TreatmentPlan)
        assert len(plan.steps) > 0

    def test_includes_organic_and_chemical(self):
        diag = _make_diagnosis()
        plan = self.recommender.recommend(diag, include_both=True)
        types = {s.treatment_type for s in plan.steps}
        assert TreatmentType.ORGANIC in types
        assert TreatmentType.CHEMICAL in types

    def test_prefer_organic(self):
        diag = _make_diagnosis()
        plan = self.recommender.recommend(
            diag, prefer_organic=True, include_both=False
        )
        for step in plan.steps:
            assert step.treatment_type == TreatmentType.ORGANIC

    def test_severe_includes_isolation_step(self):
        diag = _make_diagnosis(severity=0.7, level=SeverityLevel.SEVERE)
        plan = self.recommender.recommend(diag)
        actions = [s.action.lower() for s in plan.steps]
        assert any("isolate" in a for a in actions)

    def test_critical_includes_removal(self):
        diag = _make_diagnosis(severity=0.9, level=SeverityLevel.CRITICAL)
        plan = self.recommender.recommend(diag)
        actions = [s.action.lower() for s in plan.steps]
        assert any("remov" in a for a in actions)

    def test_has_preventive_measures(self):
        diag = _make_diagnosis()
        plan = self.recommender.recommend(diag)
        assert len(plan.preventive_measures) > 0

    def test_recovery_days_scale_with_severity(self):
        mild = _make_diagnosis(severity=0.2, level=SeverityLevel.MILD)
        severe = _make_diagnosis(severity=0.7, level=SeverityLevel.SEVERE)
        plan_mild = self.recommender.recommend(mild)
        plan_severe = self.recommender.recommend(severe)
        assert plan_mild.estimated_recovery_days < plan_severe.estimated_recovery_days

    def test_followup_days_decrease_with_severity(self):
        mild = _make_diagnosis(severity=0.2, level=SeverityLevel.MILD)
        critical = _make_diagnosis(severity=0.9, level=SeverityLevel.CRITICAL)
        plan_mild = self.recommender.recommend(mild)
        plan_critical = self.recommender.recommend(critical)
        assert plan_mild.follow_up_days > plan_critical.follow_up_days

    def test_chemical_steps_have_safety_notes(self):
        diag = _make_diagnosis()
        plan = self.recommender.recommend(diag)
        chemical = [
            s for s in plan.steps if s.treatment_type == TreatmentType.CHEMICAL
        ]
        for step in chemical:
            assert len(step.safety_notes) > 0


class TestSpreadPredictor:
    def setup_method(self):
        self.predictor = SpreadPredictor()

    def test_predict_returns_forecast(self):
        diag = _make_diagnosis()
        forecast = self.predictor.predict(diag)
        assert isinstance(forecast, SpreadForecast)

    def test_forecast_progression(self):
        diag = _make_diagnosis(severity=0.3, level=SeverityLevel.MODERATE)
        diag.affected_area_pct = 10.0
        forecast = self.predictor.predict(diag)
        # Infection should not decrease over time
        assert forecast.day_7_pct >= forecast.current_infection_pct
        assert forecast.day_14_pct >= forecast.day_7_pct
        assert forecast.day_30_pct >= forecast.day_14_pct

    def test_high_humidity_increases_spread(self):
        diag = _make_diagnosis()
        diag.affected_area_pct = 5.0

        dry = EnvironmentalConditions(humidity_pct=30)
        wet = EnvironmentalConditions(humidity_pct=95)

        f_dry = self.predictor.predict(diag, dry)
        f_wet = self.predictor.predict(diag, wet)

        assert f_wet.day_14_pct >= f_dry.day_14_pct

    def test_risk_level_is_valid(self):
        diag = _make_diagnosis()
        forecast = self.predictor.predict(diag)
        assert forecast.risk_level in ("low", "moderate", "high", "critical")

    def test_recommendations_not_empty(self):
        diag = _make_diagnosis()
        forecast = self.predictor.predict(diag)
        assert len(forecast.recommendations) > 0

    def test_default_conditions(self):
        diag = _make_diagnosis()
        # Should not raise with default conditions
        forecast = self.predictor.predict(diag)
        assert forecast.peak_infection_pct > 0

    def test_days_to_peak_positive(self):
        diag = _make_diagnosis()
        diag.affected_area_pct = 5.0
        forecast = self.predictor.predict(diag)
        assert forecast.days_to_peak >= 0
