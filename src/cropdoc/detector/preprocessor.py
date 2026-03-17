"""Image preprocessing pipeline for leaf disease detection."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as F


class LeafImagePreprocessor:
    """Preprocesses leaf images for the CropDiseaseClassifier CNN.

    Handles loading, resizing, normalization, and augmentation of leaf
    images before they are fed into the classification model.
    """

    # ImageNet normalization values (standard for pretrained models)
    MEAN = (0.485, 0.456, 0.406)
    STD = (0.229, 0.224, 0.225)

    def __init__(
        self,
        target_size: tuple[int, int] = (224, 224),
        normalize: bool = True,
    ) -> None:
        self.target_size = target_size
        self.normalize = normalize

    def load_and_preprocess(self, image_path: str | Path) -> torch.Tensor:
        """Load an image from disk and return a preprocessed tensor.

        Args:
            image_path: Path to the leaf image file.

        Returns:
            Preprocessed tensor of shape (1, 3, H, W) ready for the model.

        Raises:
            FileNotFoundError: If image_path does not exist.
            ValueError: If the image cannot be read.
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        try:
            from PIL import Image
            img = Image.open(path).convert("RGB")
            tensor = self._pil_to_tensor(img)
        except ImportError:
            raise ImportError(
                "Pillow is required for image loading. "
                "Install it with: pip install Pillow"
            )

        return self.preprocess(tensor)

    def preprocess(self, tensor: torch.Tensor) -> torch.Tensor:
        """Preprocess a raw image tensor.

        Args:
            tensor: Image tensor of shape (3, H, W) with values in [0, 1].

        Returns:
            Preprocessed tensor of shape (1, 3, H, W).
        """
        if tensor.dim() == 3:
            tensor = tensor.unsqueeze(0)

        # Resize to target dimensions
        tensor = F.interpolate(
            tensor,
            size=self.target_size,
            mode="bilinear",
            align_corners=False,
        )

        # Normalize using ImageNet stats
        if self.normalize:
            tensor = self._normalize(tensor)

        return tensor

    def preprocess_batch(self, tensors: list[torch.Tensor]) -> torch.Tensor:
        """Preprocess a batch of images.

        Args:
            tensors: List of image tensors, each of shape (3, H, W).

        Returns:
            Batch tensor of shape (N, 3, H, W).
        """
        processed = [self.preprocess(t) for t in tensors]
        return torch.cat(processed, dim=0)

    def _normalize(self, tensor: torch.Tensor) -> torch.Tensor:
        """Apply ImageNet normalization."""
        mean = torch.tensor(self.MEAN, device=tensor.device).view(1, 3, 1, 1)
        std = torch.tensor(self.STD, device=tensor.device).view(1, 3, 1, 1)
        return (tensor - mean) / std

    def denormalize(self, tensor: torch.Tensor) -> torch.Tensor:
        """Reverse normalization for visualization."""
        mean = torch.tensor(self.MEAN, device=tensor.device).view(1, 3, 1, 1)
        std = torch.tensor(self.STD, device=tensor.device).view(1, 3, 1, 1)
        return tensor * std + mean

    @staticmethod
    def _pil_to_tensor(image) -> torch.Tensor:  # noqa: ANN001
        """Convert a PIL Image to a float tensor in [0, 1]."""
        import numpy as np

        arr = np.array(image, dtype=np.float32) / 255.0
        # HWC -> CHW
        tensor = torch.from_numpy(arr).permute(2, 0, 1)
        return tensor

    @staticmethod
    def create_synthetic_leaf(
        height: int = 224,
        width: int = 224,
        disease_severity: float = 0.0,
        seed: Optional[int] = None,
    ) -> torch.Tensor:
        """Generate a synthetic leaf image tensor for testing.

        Creates a green-dominant image with brownish spots simulating disease.

        Args:
            height: Image height.
            width: Image width.
            disease_severity: 0.0 (healthy) to 1.0 (fully diseased).
            seed: Random seed for reproducibility.

        Returns:
            Tensor of shape (3, H, W) with values in [0, 1].
        """
        if seed is not None:
            torch.manual_seed(seed)

        # Base green leaf color with some texture
        r = torch.rand(1, height, width) * 0.2 + 0.1
        g = torch.rand(1, height, width) * 0.3 + 0.4
        b = torch.rand(1, height, width) * 0.15 + 0.05
        leaf = torch.cat([r, g, b], dim=0)

        if disease_severity > 0:
            # Add disease spots
            num_spots = int(disease_severity * 30) + 1
            for _ in range(num_spots):
                cx = torch.randint(0, width, (1,)).item()
                cy = torch.randint(0, height, (1,)).item()
                radius = int(disease_severity * 20) + 3

                y_coords = torch.arange(height).unsqueeze(1).float()
                x_coords = torch.arange(width).unsqueeze(0).float()
                mask = ((x_coords - cx) ** 2 + (y_coords - cy) ** 2) < radius ** 2
                mask = mask.unsqueeze(0).float()

                # Brown/dark spot colors
                spot_color = torch.tensor([0.35, 0.2, 0.08]).view(3, 1, 1)
                leaf = leaf * (1 - mask * 0.8) + spot_color * mask * 0.8

        return leaf.clamp(0, 1)
