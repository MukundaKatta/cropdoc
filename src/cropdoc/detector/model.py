"""CNN model for crop disease classification from leaf images."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from cropdoc.detector.diseases import DiseaseDatabase


class CropDiseaseClassifier(nn.Module):
    """Convolutional Neural Network for classifying crop diseases from leaf images.

    Architecture: lightweight CNN with 5 convolutional blocks followed by a
    classifier head. Designed for 224x224 RGB input images and outputs
    probabilities over all disease classes in the DiseaseDatabase.
    """

    def __init__(self, num_classes: int | None = None) -> None:
        super().__init__()
        self._db = DiseaseDatabase()
        self.num_classes = num_classes or len(self._db.all_diseases)
        self.class_names = self._db.disease_names[: self.num_classes]

        # Feature extraction blocks
        self.features = nn.Sequential(
            # Block 1: 224x224 -> 112x112
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 2: 112x112 -> 56x56
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 3: 56x56 -> 28x28
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 4: 28x28 -> 14x14
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 5: 14x14 -> 7x7
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

        # Global average pooling + classifier
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, self.num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network.

        Args:
            x: Input tensor of shape (N, 3, 224, 224).

        Returns:
            Logits tensor of shape (N, num_classes).
        """
        x = self.features(x)
        x = self.classifier(x)
        return x

    def predict(self, image: torch.Tensor) -> dict:
        """Run inference on a preprocessed image tensor.

        Args:
            image: Preprocessed tensor of shape (1, 3, 224, 224) or (3, 224, 224).

        Returns:
            Dictionary with keys:
                - disease_name: predicted disease name
                - disease_index: integer class index
                - confidence: float confidence score
                - probabilities: dict mapping disease names to probabilities
                - disease: Disease model instance
        """
        self.eval()
        if image.dim() == 3:
            image = image.unsqueeze(0)

        with torch.no_grad():
            logits = self.forward(image)
            probs = F.softmax(logits, dim=1)

        confidence, predicted_idx = probs.max(dim=1)
        idx = predicted_idx.item()
        conf = confidence.item()

        disease_name = self.class_names[idx]
        disease = self._db.get(disease_name)

        prob_dict = {
            name: probs[0, i].item()
            for i, name in enumerate(self.class_names)
        }

        return {
            "disease_name": disease_name,
            "disease_index": idx,
            "confidence": conf,
            "probabilities": prob_dict,
            "disease": disease,
        }

    def predict_top_k(self, image: torch.Tensor, k: int = 5) -> list[dict]:
        """Return top-k predictions sorted by confidence.

        Args:
            image: Preprocessed tensor.
            k: Number of top predictions to return.

        Returns:
            List of dicts with disease_name, confidence, and disease.
        """
        self.eval()
        if image.dim() == 3:
            image = image.unsqueeze(0)

        with torch.no_grad():
            logits = self.forward(image)
            probs = F.softmax(logits, dim=1)

        topk = torch.topk(probs, k=min(k, self.num_classes), dim=1)
        results = []
        for i in range(topk.indices.shape[1]):
            idx = topk.indices[0, i].item()
            conf = topk.values[0, i].item()
            name = self.class_names[idx]
            results.append({
                "disease_name": name,
                "confidence": conf,
                "disease": self._db.get(name),
            })
        return results

    @property
    def disease_database(self) -> DiseaseDatabase:
        """Access the underlying disease database."""
        return self._db

    def save(self, path: str) -> None:
        """Save model weights to disk."""
        torch.save(self.state_dict(), path)

    def load(self, path: str, device: str = "cpu") -> None:
        """Load model weights from disk."""
        state = torch.load(path, map_location=device, weights_only=True)
        self.load_state_dict(state)
