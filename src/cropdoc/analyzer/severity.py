"""Severity estimation for detected crop diseases."""

from __future__ import annotations

import torch
import torch.nn as nn

from cropdoc.models import Disease, SeverityLevel


class SeverityEstimator:
    """Estimates disease severity from leaf image features.

    Produces a continuous score in [0, 1] and maps it to a categorical
    SeverityLevel. Uses color-channel statistics and texture features
    to approximate the extent of visible disease damage.
    """

    THRESHOLDS = {
        SeverityLevel.HEALTHY: (0.0, 0.1),
        SeverityLevel.MILD: (0.1, 0.3),
        SeverityLevel.MODERATE: (0.3, 0.55),
        SeverityLevel.SEVERE: (0.55, 0.8),
        SeverityLevel.CRITICAL: (0.8, 1.0),
    }

    def __init__(self) -> None:
        # Small MLP for refining raw heuristic score
        self._refiner = nn.Sequential(
            nn.Linear(8, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def estimate(
        self,
        image: torch.Tensor,
        prediction: dict,
    ) -> dict:
        """Estimate disease severity from image and prediction.

        Args:
            image: Preprocessed image tensor (1, 3, H, W) or (3, H, W).
            prediction: Output dict from CropDiseaseClassifier.predict().

        Returns:
            Dictionary with:
                - severity_score: float in [0, 1]
                - severity_level: SeverityLevel enum
                - affected_area_pct: estimated percentage of leaf affected
                - confidence_factor: how much prediction confidence
                  influenced the score
        """
        if image.dim() == 3:
            image = image.unsqueeze(0)

        features = self._extract_features(image)
        raw_score = self._compute_raw_score(features, prediction)

        with torch.no_grad():
            refined = self._refiner(features).item()

        # Blend raw heuristic with learned refinement
        score = 0.6 * raw_score + 0.4 * refined
        score = max(0.0, min(1.0, score))

        level = self._score_to_level(score)
        affected_pct = self._estimate_affected_area(image, score)

        return {
            "severity_score": round(score, 4),
            "severity_level": level,
            "affected_area_pct": round(affected_pct, 2),
            "confidence_factor": round(prediction.get("confidence", 0.0), 4),
        }

    def _extract_features(self, image: torch.Tensor) -> torch.Tensor:
        """Extract 8-dimensional feature vector from the image."""
        # Channel statistics
        r, g, b = image[:, 0], image[:, 1], image[:, 2]

        brown_ratio = (r.mean() / (g.mean() + 1e-8)).item()
        green_intensity = g.mean().item()
        red_intensity = r.mean().item()
        color_variance = image.var().item()

        # Texture approximation via gradient magnitude
        dx = (image[:, :, :, 1:] - image[:, :, :, :-1]).abs().mean().item()
        dy = (image[:, :, 1:, :] - image[:, :, :-1, :]).abs().mean().item()
        texture = (dx + dy) / 2

        # Dark pixel ratio (potential necrosis)
        dark_ratio = (image.mean(dim=1) < 0.2).float().mean().item()

        # Brightness uniformity
        brightness = image.mean(dim=1)
        uniformity = 1.0 - brightness.std().item()

        features = torch.tensor([
            brown_ratio,
            green_intensity,
            red_intensity,
            color_variance,
            texture,
            dark_ratio,
            uniformity,
            0.0,  # placeholder for future features
        ]).unsqueeze(0)

        return features

    def _compute_raw_score(
        self, features: torch.Tensor, prediction: dict
    ) -> float:
        """Compute raw severity score from features and prediction."""
        f = features[0]
        brown_ratio = f[0].item()
        green_intensity = f[1].item()
        dark_ratio = f[5].item()

        # Higher brown-to-green ratio indicates more disease
        color_score = min(1.0, max(0.0, (brown_ratio - 0.5) / 1.5))

        # Lower green intensity suggests more damage
        green_score = max(0.0, 1.0 - green_intensity * 2)

        # More dark pixels means more necrosis
        necrosis_score = min(1.0, dark_ratio * 3)

        # Blend with prediction confidence as a weight
        confidence = prediction.get("confidence", 0.5)
        raw = (0.4 * color_score + 0.3 * green_score + 0.3 * necrosis_score)
        return raw * (0.5 + 0.5 * confidence)

    def _estimate_affected_area(
        self, image: torch.Tensor, severity_score: float
    ) -> float:
        """Estimate the percentage of leaf area showing disease symptoms."""
        # Use deviation from green as proxy for affected area
        r, g, b = image[:, 0], image[:, 1], image[:, 2]
        # Pixels where red exceeds green or brightness is very low
        unhealthy = ((r > g) | (image.mean(dim=1) < 0.15)).float()
        pixel_ratio = unhealthy.mean().item() * 100

        # Blend with severity score for more stable estimate
        return 0.5 * pixel_ratio + 0.5 * (severity_score * 80)

    @staticmethod
    def _score_to_level(score: float) -> SeverityLevel:
        """Map a continuous score to a categorical severity level."""
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
