"""Tests for the synthetic data simulator."""

import pytest
import torch

from cropdoc.simulator import CropSimulator
from cropdoc.models import Diagnosis, TreatmentPlan


class TestCropSimulator:
    def setup_method(self):
        self.sim = CropSimulator(seed=42)

    def test_generate_leaf_image(self):
        tensor, leaf = self.sim.generate_leaf_image()
        assert tensor.shape == (3, 224, 224)
        assert tensor.min() >= 0.0
        assert tensor.max() <= 1.0
        assert leaf.width == 224
        assert leaf.height == 224

    def test_generate_leaf_image_with_disease(self):
        from cropdoc.detector.diseases import DiseaseDatabase
        db = DiseaseDatabase()
        disease = db.get("Rice Blast")
        tensor, leaf = self.sim.generate_leaf_image(disease=disease, severity=0.7)
        assert leaf.crop_hint == "rice"

    def test_generate_diagnosis(self):
        diag = self.sim.generate_diagnosis()
        assert isinstance(diag, Diagnosis)
        assert diag.disease is not None
        assert 0.0 <= diag.confidence <= 1.0
        assert 0.0 <= diag.severity_score <= 1.0

    def test_generate_diagnosis_specific_disease(self):
        from cropdoc.detector.diseases import DiseaseDatabase
        db = DiseaseDatabase()
        disease = db.get("Wheat Rust")
        diag = self.sim.generate_diagnosis(disease=disease, severity=0.8)
        assert diag.disease.name == "Wheat Rust"
        assert diag.severity_score == 0.8

    def test_generate_treatment_plan(self):
        plan = self.sim.generate_treatment_plan()
        assert isinstance(plan, TreatmentPlan)
        assert len(plan.steps) > 0

    def test_generate_batch(self):
        batch = self.sim.generate_batch(count=5)
        assert len(batch) == 5
        for case in batch:
            assert "diagnosis" in case
            assert "treatment_plan" in case
            assert "spread_forecast" in case

    def test_generate_batch_without_treatment(self):
        batch = self.sim.generate_batch(count=3, include_treatment=False)
        assert len(batch) == 3
        for case in batch:
            assert "diagnosis" in case
            assert "treatment_plan" not in case

    def test_reproducibility(self):
        sim1 = CropSimulator(seed=99)
        sim2 = CropSimulator(seed=99)
        diag1 = sim1.generate_diagnosis()
        diag2 = sim2.generate_diagnosis()
        assert diag1.disease.name == diag2.disease.name
        assert diag1.severity_score == diag2.severity_score

    def test_save_synthetic_images(self, tmp_path):
        paths = self.sim.save_synthetic_images(tmp_path / "synth", count=3)
        assert len(paths) == 3
        for p in paths:
            assert p.exists()
            t = torch.load(p, weights_only=True)
            assert t.shape == (3, 224, 224)
