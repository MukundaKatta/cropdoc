"""Tests for pydantic data models."""

import pytest
from datetime import datetime

from cropdoc.models import (
    Disease,
    Diagnosis,
    LeafImage,
    SeverityLevel,
    TreatmentPlan,
    TreatmentStep,
    TreatmentType,
)


class TestLeafImage:
    def test_create_minimal(self):
        img = LeafImage(width=224, height=224)
        assert img.width == 224
        assert img.height == 224
        assert img.channels == 3
        assert img.crop_hint is None

    def test_create_with_crop_hint(self):
        img = LeafImage(width=640, height=480, crop_hint="tomato")
        assert img.crop_hint == "tomato"

    def test_invalid_width(self):
        with pytest.raises(Exception):
            LeafImage(width=0, height=224)

    def test_invalid_channels(self):
        with pytest.raises(Exception):
            LeafImage(width=224, height=224, channels=5)


class TestDisease:
    def test_create_disease(self):
        d = Disease(
            name="Test Blight",
            crop="tomato",
            pathogen_type="fungal",
            symptoms=["yellow spots"],
            treatment_organic=["neem oil"],
            treatment_chemical=["fungicide X"],
            prevention=["crop rotation"],
        )
        assert d.name == "Test Blight"
        assert d.crop == "tomato"
        assert d.spread_rate == 0.5

    def test_spread_rate_bounds(self):
        with pytest.raises(Exception):
            Disease(
                name="Bad",
                crop="x",
                pathogen_type="fungal",
                spread_rate=1.5,
            )


class TestDiagnosis:
    def test_create_diagnosis(self):
        leaf = LeafImage(width=224, height=224)
        disease = Disease(name="Test", crop="corn", pathogen_type="fungal")
        diag = Diagnosis(
            image=leaf,
            disease=disease,
            confidence=0.95,
            severity_score=0.6,
            severity_level=SeverityLevel.MODERATE,
            affected_area_pct=35.0,
        )
        assert diag.confidence == 0.95
        assert diag.severity_level == SeverityLevel.MODERATE
        assert isinstance(diag.timestamp, datetime)

    def test_confidence_bounds(self):
        leaf = LeafImage(width=224, height=224)
        disease = Disease(name="Test", crop="corn", pathogen_type="fungal")
        with pytest.raises(Exception):
            Diagnosis(
                image=leaf, disease=disease, confidence=1.5
            )


class TestTreatmentPlan:
    def test_create_plan(self):
        leaf = LeafImage(width=224, height=224)
        disease = Disease(name="Test", crop="corn", pathogen_type="fungal")
        diag = Diagnosis(image=leaf, disease=disease, confidence=0.9)
        step = TreatmentStep(
            action="Apply neem oil",
            treatment_type=TreatmentType.ORGANIC,
            frequency="Weekly",
        )
        plan = TreatmentPlan(
            diagnosis=diag,
            steps=[step],
            estimated_recovery_days=14,
        )
        assert len(plan.steps) == 1
        assert plan.steps[0].treatment_type == TreatmentType.ORGANIC
        assert plan.follow_up_days == 14


class TestSeverityLevel:
    def test_enum_values(self):
        assert SeverityLevel.HEALTHY.value == "healthy"
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_all_levels(self):
        levels = list(SeverityLevel)
        assert len(levels) == 5
