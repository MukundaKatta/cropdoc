"""Synthetic data generation for testing and development."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import torch

from cropdoc.detector.diseases import DiseaseDatabase
from cropdoc.detector.preprocessor import LeafImagePreprocessor
from cropdoc.models import (
    Diagnosis,
    Disease,
    LeafImage,
    SeverityLevel,
    TreatmentPlan,
)
from cropdoc.analyzer.severity import SeverityEstimator
from cropdoc.analyzer.treatment import TreatmentRecommender
from cropdoc.analyzer.spread import SpreadPredictor, EnvironmentalConditions


class CropSimulator:
    """Generates synthetic crop disease data for testing and demonstration.

    Creates realistic-looking leaf image tensors with simulated disease
    symptoms, along with full diagnostic pipelines including severity
    estimation, treatment plans, and spread predictions.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._db = DiseaseDatabase()
        self._preprocessor = LeafImagePreprocessor()
        self._severity_estimator = SeverityEstimator()
        self._treatment_recommender = TreatmentRecommender()
        self._spread_predictor = SpreadPredictor()
        self._rng = random.Random(seed)
        self._torch_seed = seed

    def generate_leaf_image(
        self,
        disease: Optional[Disease] = None,
        severity: float = 0.5,
    ) -> tuple[torch.Tensor, LeafImage]:
        """Generate a synthetic leaf image tensor and metadata.

        Args:
            disease: Disease to simulate (random if None).
            severity: Severity of symptoms, 0.0 to 1.0.

        Returns:
            Tuple of (raw tensor [3, H, W], LeafImage metadata).
        """
        seed = self._rng.randint(0, 100000) if self._torch_seed is None else self._torch_seed
        tensor = LeafImagePreprocessor.create_synthetic_leaf(
            height=224,
            width=224,
            disease_severity=severity,
            seed=seed,
        )

        if disease is None:
            disease = self._rng.choice(self._db.all_diseases)

        leaf = LeafImage(
            width=224,
            height=224,
            channels=3,
            crop_hint=disease.crop,
            capture_date=datetime.now() - timedelta(
                days=self._rng.randint(0, 30)
            ),
        )
        return tensor, leaf

    def generate_diagnosis(
        self,
        disease: Optional[Disease] = None,
        severity: Optional[float] = None,
    ) -> Diagnosis:
        """Generate a complete synthetic diagnosis.

        Args:
            disease: Specific disease (random if None).
            severity: Severity score (random if None).

        Returns:
            A fully populated Diagnosis object.
        """
        if disease is None:
            disease = self._rng.choice(self._db.all_diseases)
        if severity is None:
            severity = self._rng.uniform(0.05, 0.95)

        tensor, leaf = self.generate_leaf_image(disease, severity)

        confidence = self._rng.uniform(0.65, 0.99)
        level = self._severity_to_level(severity)
        affected_pct = severity * self._rng.uniform(60, 90)

        return Diagnosis(
            image=leaf,
            disease=disease,
            confidence=round(confidence, 4),
            severity_score=round(severity, 4),
            severity_level=level,
            affected_area_pct=round(min(100.0, affected_pct), 2),
        )

    def generate_treatment_plan(
        self,
        diagnosis: Optional[Diagnosis] = None,
        prefer_organic: bool = False,
    ) -> TreatmentPlan:
        """Generate a treatment plan for a synthetic or provided diagnosis.

        Args:
            diagnosis: Existing diagnosis (generates one if None).
            prefer_organic: Prefer organic treatments.

        Returns:
            A TreatmentPlan with recommended steps.
        """
        if diagnosis is None:
            diagnosis = self.generate_diagnosis()

        return self._treatment_recommender.recommend(
            diagnosis, prefer_organic=prefer_organic
        )

    def generate_batch(
        self,
        count: int = 10,
        include_treatment: bool = True,
    ) -> list[dict]:
        """Generate a batch of synthetic diagnostic cases.

        Args:
            count: Number of cases to generate.
            include_treatment: Whether to generate treatment plans.

        Returns:
            List of dicts, each with 'diagnosis', optionally 'treatment_plan'
            and 'spread_forecast'.
        """
        results = []
        for _ in range(count):
            disease = self._rng.choice(self._db.all_diseases)
            severity = self._rng.uniform(0.05, 0.95)
            diagnosis = self.generate_diagnosis(disease, severity)

            case: dict = {"diagnosis": diagnosis}

            if include_treatment:
                plan = self.generate_treatment_plan(diagnosis)
                case["treatment_plan"] = plan

                conditions = EnvironmentalConditions(
                    temperature_c=self._rng.uniform(15, 35),
                    humidity_pct=self._rng.uniform(40, 95),
                    rainfall_mm_per_week=self._rng.uniform(0, 80),
                    wind_speed_kmh=self._rng.uniform(0, 40),
                )
                forecast = self._spread_predictor.predict(
                    diagnosis, conditions
                )
                case["spread_forecast"] = forecast

            results.append(case)

        return results

    def save_synthetic_images(
        self,
        output_dir: str | Path,
        count: int = 10,
    ) -> list[Path]:
        """Generate and save synthetic leaf images as tensors.

        Args:
            output_dir: Directory to save .pt tensor files.
            count: Number of images to generate.

        Returns:
            List of paths to saved tensor files.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved = []
        for i in range(count):
            disease = self._rng.choice(self._db.all_diseases)
            severity = self._rng.uniform(0.0, 1.0)
            tensor, _ = self.generate_leaf_image(disease, severity)

            filename = output_path / f"leaf_{i:04d}_{disease.crop}_{severity:.2f}.pt"
            torch.save(tensor, filename)
            saved.append(filename)

        return saved

    @staticmethod
    def _severity_to_level(score: float) -> SeverityLevel:
        """Map continuous severity to categorical level."""
        if score < 0.1:
            return SeverityLevel.HEALTHY
        elif score < 0.3:
            return SeverityLevel.MILD
        elif score < 0.55:
            return SeverityLevel.MODERATE
        elif score < 0.8:
            return SeverityLevel.SEVERE
        else:
            return SeverityLevel.CRITICAL
