"""Tests for the detector module: model, preprocessor, diseases."""

import pytest
import torch

from cropdoc.detector.model import CropDiseaseClassifier
from cropdoc.detector.preprocessor import LeafImagePreprocessor
from cropdoc.detector.diseases import DiseaseDatabase


class TestDiseaseDatabase:
    def setup_method(self):
        self.db = DiseaseDatabase()

    def test_has_at_least_15_diseases(self):
        assert len(self.db.all_diseases) >= 15

    def test_disease_names_match_count(self):
        assert len(self.db.disease_names) == len(self.db.all_diseases)

    def test_supported_crops(self):
        crops = self.db.supported_crops
        assert "tomato" in crops
        assert "potato" in crops
        assert "corn" in crops
        assert "rice" in crops
        assert "wheat" in crops

    def test_get_existing_disease(self):
        d = self.db.get("Tomato Early Blight")
        assert d is not None
        assert d.crop == "tomato"
        assert d.pathogen_type == "fungal"
        assert len(d.symptoms) > 0
        assert len(d.treatment_organic) > 0
        assert len(d.treatment_chemical) > 0
        assert len(d.prevention) > 0

    def test_get_nonexistent_disease(self):
        assert self.db.get("Nonexistent Disease") is None

    def test_search(self):
        results = self.db.search("blight")
        assert len(results) >= 4  # tomato early/late, potato early/late

    def test_by_crop(self):
        tomato = self.db.by_crop("tomato")
        assert len(tomato) >= 3
        for d in tomato:
            assert d.crop == "tomato"

    def test_by_pathogen_type(self):
        fungal = self.db.by_pathogen_type("fungal")
        assert len(fungal) >= 12
        bacterial = self.db.by_pathogen_type("bacterial")
        assert len(bacterial) >= 2

    def test_get_by_index(self):
        d = self.db.get_by_index(0)
        assert d is not None
        # Wraps around
        d2 = self.db.get_by_index(len(self.db.all_diseases))
        assert d2.name == d.name

    def test_all_diseases_have_required_fields(self):
        for disease in self.db.all_diseases:
            assert disease.name
            assert disease.crop
            assert disease.pathogen_type
            assert len(disease.symptoms) >= 2
            assert len(disease.treatment_organic) >= 2
            assert len(disease.treatment_chemical) >= 2
            assert len(disease.prevention) >= 3
            assert 0.0 <= disease.spread_rate <= 1.0


class TestLeafImagePreprocessor:
    def setup_method(self):
        self.preprocessor = LeafImagePreprocessor()

    def test_preprocess_tensor(self):
        raw = torch.rand(3, 100, 150)
        result = self.preprocessor.preprocess(raw)
        assert result.shape == (1, 3, 224, 224)

    def test_preprocess_batched_tensor(self):
        raw = torch.rand(1, 3, 300, 300)
        result = self.preprocessor.preprocess(raw)
        assert result.shape == (1, 3, 224, 224)

    def test_preprocess_batch(self):
        images = [torch.rand(3, 100, 100) for _ in range(4)]
        batch = self.preprocessor.preprocess_batch(images)
        assert batch.shape == (4, 3, 224, 224)

    def test_normalization(self):
        raw = torch.ones(3, 224, 224) * 0.5
        result = self.preprocessor.preprocess(raw)
        # After normalization, values should differ from 0.5
        assert not torch.allclose(result, torch.tensor(0.5))

    def test_no_normalization(self):
        preprocessor = LeafImagePreprocessor(normalize=False)
        raw = torch.ones(3, 224, 224) * 0.5
        result = preprocessor.preprocess(raw)
        assert torch.allclose(result, torch.tensor(0.5), atol=0.01)

    def test_denormalize_roundtrip(self):
        raw = torch.rand(1, 3, 224, 224)
        normalized = self.preprocessor._normalize(raw)
        recovered = self.preprocessor.denormalize(normalized)
        assert torch.allclose(raw, recovered, atol=1e-5)

    def test_create_synthetic_leaf_healthy(self):
        leaf = LeafImagePreprocessor.create_synthetic_leaf(
            disease_severity=0.0, seed=42
        )
        assert leaf.shape == (3, 224, 224)
        assert leaf.min() >= 0.0
        assert leaf.max() <= 1.0
        # Healthy leaf should be mostly green
        assert leaf[1].mean() > leaf[0].mean()  # green > red

    def test_create_synthetic_leaf_diseased(self):
        leaf = LeafImagePreprocessor.create_synthetic_leaf(
            disease_severity=0.9, seed=42
        )
        assert leaf.shape == (3, 224, 224)

    def test_synthetic_leaf_reproducible(self):
        a = LeafImagePreprocessor.create_synthetic_leaf(seed=123)
        b = LeafImagePreprocessor.create_synthetic_leaf(seed=123)
        assert torch.equal(a, b)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            self.preprocessor.load_and_preprocess("/nonexistent/leaf.jpg")

    def test_custom_target_size(self):
        preprocessor = LeafImagePreprocessor(target_size=(128, 128))
        raw = torch.rand(3, 200, 200)
        result = preprocessor.preprocess(raw)
        assert result.shape == (1, 3, 128, 128)


class TestCropDiseaseClassifier:
    def setup_method(self):
        self.model = CropDiseaseClassifier()

    def test_model_output_shape(self):
        x = torch.rand(1, 3, 224, 224)
        output = self.model(x)
        assert output.shape == (1, self.model.num_classes)

    def test_batch_inference(self):
        x = torch.rand(4, 3, 224, 224)
        output = self.model(x)
        assert output.shape == (4, self.model.num_classes)

    def test_predict_returns_dict(self):
        x = torch.rand(1, 3, 224, 224)
        result = self.model.predict(x)
        assert "disease_name" in result
        assert "confidence" in result
        assert "disease_index" in result
        assert "probabilities" in result
        assert "disease" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_3d_input(self):
        x = torch.rand(3, 224, 224)
        result = self.model.predict(x)
        assert result["disease_name"] in self.model.class_names

    def test_predict_top_k(self):
        x = torch.rand(1, 3, 224, 224)
        results = self.model.predict_top_k(x, k=5)
        assert len(results) == 5
        # Should be sorted by confidence (descending)
        confs = [r["confidence"] for r in results]
        assert confs == sorted(confs, reverse=True)

    def test_num_classes_matches_database(self):
        db = DiseaseDatabase()
        assert self.model.num_classes == len(db.all_diseases)

    def test_class_names(self):
        assert len(self.model.class_names) == self.model.num_classes
        assert "Tomato Early Blight" in self.model.class_names

    def test_probabilities_sum_to_one(self):
        x = torch.rand(1, 3, 224, 224)
        result = self.model.predict(x)
        total = sum(result["probabilities"].values())
        assert abs(total - 1.0) < 1e-4

    def test_disease_database_property(self):
        db = self.model.disease_database
        assert isinstance(db, DiseaseDatabase)
