"""Pydantic data models for CROPDOC."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Categorical severity levels for disease progression."""

    HEALTHY = "healthy"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class TreatmentType(str, Enum):
    """Type of treatment approach."""

    ORGANIC = "organic"
    CHEMICAL = "chemical"


class LeafImage(BaseModel):
    """Represents a leaf image for analysis."""

    path: Optional[Path] = None
    width: int = Field(ge=1, description="Image width in pixels")
    height: int = Field(ge=1, description="Image height in pixels")
    channels: int = Field(default=3, ge=1, le=4)
    crop_hint: Optional[str] = Field(
        default=None, description="Optional hint about the crop type"
    )
    capture_date: Optional[datetime] = None

    model_config = {"arbitrary_types_allowed": True}


class Disease(BaseModel):
    """A plant disease with its characteristics."""

    name: str = Field(description="Common name of the disease")
    scientific_name: Optional[str] = None
    crop: str = Field(description="Affected crop type")
    pathogen_type: str = Field(
        description="Type of pathogen: fungal, bacterial, viral, etc."
    )
    symptoms: list[str] = Field(
        default_factory=list, description="Observable symptoms"
    )
    treatment_organic: list[str] = Field(
        default_factory=list, description="Organic treatment options"
    )
    treatment_chemical: list[str] = Field(
        default_factory=list, description="Chemical treatment options"
    )
    prevention: list[str] = Field(
        default_factory=list, description="Prevention strategies"
    )
    spread_rate: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Relative spread rate (0=slow, 1=fast)",
    )


class Diagnosis(BaseModel):
    """Result of analyzing a leaf image."""

    image: LeafImage
    disease: Disease
    confidence: float = Field(
        ge=0.0, le=1.0, description="Classification confidence"
    )
    severity_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Severity on 0-1 scale"
    )
    severity_level: SeverityLevel = SeverityLevel.HEALTHY
    affected_area_pct: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Estimated percentage of leaf area affected",
    )
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}


class TreatmentStep(BaseModel):
    """A single step in a treatment plan."""

    action: str
    product: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    treatment_type: TreatmentType = TreatmentType.ORGANIC
    safety_notes: list[str] = Field(default_factory=list)


class TreatmentPlan(BaseModel):
    """Complete treatment plan for a diagnosed disease."""

    diagnosis: Diagnosis
    steps: list[TreatmentStep] = Field(default_factory=list)
    estimated_recovery_days: Optional[int] = None
    spread_risk: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Estimated risk of spread to neighboring plants",
    )
    field_impact_pct: float = Field(
        default=0.0, ge=0.0, le=100.0,
        description="Estimated percentage of field that could be affected",
    )
    preventive_measures: list[str] = Field(default_factory=list)
    follow_up_days: Optional[int] = Field(
        default=14, description="Days until recommended follow-up inspection"
    )
