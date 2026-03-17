"""Spread prediction for crop diseases at field level."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from cropdoc.models import Disease, Diagnosis, SeverityLevel


@dataclass
class EnvironmentalConditions:
    """Environmental factors that influence disease spread."""

    temperature_c: float = 25.0
    humidity_pct: float = 70.0
    rainfall_mm_per_week: float = 20.0
    wind_speed_kmh: float = 10.0
    plant_density_per_hectare: int = 10000


@dataclass
class SpreadForecast:
    """Prediction of disease spread over time."""

    current_infection_pct: float
    day_7_pct: float
    day_14_pct: float
    day_30_pct: float
    peak_infection_pct: float
    days_to_peak: int
    risk_level: str  # low, moderate, high, critical
    recommendations: list[str]


class SpreadPredictor:
    """Estimates field-level disease spread based on disease characteristics,
    current severity, and environmental conditions.

    Uses a logistic growth model adjusted for environmental favorability
    and disease-specific spread rates.
    """

    # Optimal conditions for most fungal pathogens
    OPTIMAL_TEMP_RANGE = (18.0, 28.0)
    OPTIMAL_HUMIDITY_MIN = 80.0

    def predict(
        self,
        diagnosis: Diagnosis,
        conditions: Optional[EnvironmentalConditions] = None,
        field_size_hectares: float = 1.0,
    ) -> SpreadForecast:
        """Predict disease spread across a field.

        Args:
            diagnosis: Current diagnosis with severity info.
            conditions: Environmental conditions (defaults assumed if None).
            field_size_hectares: Size of the field in hectares.

        Returns:
            SpreadForecast with timeline predictions.
        """
        if conditions is None:
            conditions = EnvironmentalConditions()

        disease = diagnosis.disease
        current_pct = diagnosis.affected_area_pct

        # Calculate environmental favorability (0 to 1)
        env_factor = self._environmental_favorability(disease, conditions)

        # Effective spread rate combining disease rate and environment
        effective_rate = disease.spread_rate * (0.3 + 0.7 * env_factor)

        # Carrying capacity: maximum infection percentage
        carrying_capacity = self._carrying_capacity(disease, conditions)

        # Project using logistic growth
        day_7 = self._logistic_growth(
            current_pct, effective_rate, carrying_capacity, days=7
        )
        day_14 = self._logistic_growth(
            current_pct, effective_rate, carrying_capacity, days=14
        )
        day_30 = self._logistic_growth(
            current_pct, effective_rate, carrying_capacity, days=30
        )

        peak_pct = carrying_capacity
        days_to_peak = self._days_to_threshold(
            current_pct, effective_rate, carrying_capacity,
            threshold=carrying_capacity * 0.95,
        )

        risk_level = self._assess_risk(effective_rate, current_pct, day_14)
        recommendations = self._generate_recommendations(
            disease, diagnosis.severity_level, risk_level, conditions
        )

        return SpreadForecast(
            current_infection_pct=round(current_pct, 2),
            day_7_pct=round(day_7, 2),
            day_14_pct=round(day_14, 2),
            day_30_pct=round(day_30, 2),
            peak_infection_pct=round(peak_pct, 2),
            days_to_peak=days_to_peak,
            risk_level=risk_level,
            recommendations=recommendations,
        )

    def _environmental_favorability(
        self,
        disease: Disease,
        conditions: EnvironmentalConditions,
    ) -> float:
        """Calculate how favorable conditions are for disease spread."""
        # Temperature factor (bell curve around optimal range)
        temp = conditions.temperature_c
        opt_low, opt_high = self.OPTIMAL_TEMP_RANGE
        if opt_low <= temp <= opt_high:
            temp_factor = 1.0
        else:
            dist = min(abs(temp - opt_low), abs(temp - opt_high))
            temp_factor = max(0.0, 1.0 - dist / 20.0)

        # Humidity factor
        humidity_factor = min(
            1.0, conditions.humidity_pct / self.OPTIMAL_HUMIDITY_MIN
        )

        # Rainfall promotes spread of many diseases
        rain_factor = min(1.0, conditions.rainfall_mm_per_week / 50.0)

        # Wind aids spore dispersal
        wind_factor = min(1.0, conditions.wind_speed_kmh / 30.0)

        # Plant density increases contact spread
        density_factor = min(
            1.0, conditions.plant_density_per_hectare / 15000
        )

        # Weighted combination
        favorability = (
            0.3 * temp_factor
            + 0.25 * humidity_factor
            + 0.2 * rain_factor
            + 0.15 * wind_factor
            + 0.1 * density_factor
        )
        return min(1.0, max(0.0, favorability))

    @staticmethod
    def _logistic_growth(
        current_pct: float,
        rate: float,
        capacity: float,
        days: int,
    ) -> float:
        """Project infection percentage using logistic growth model."""
        if current_pct <= 0:
            current_pct = 0.1  # minimum seed infection
        if current_pct >= capacity:
            return capacity

        # Logistic growth: P(t) = K / (1 + ((K - P0)/P0) * exp(-r*t))
        k = capacity
        p0 = current_pct
        try:
            ratio = (k - p0) / p0
            result = k / (1.0 + ratio * math.exp(-rate * days * 0.1))
        except (OverflowError, ZeroDivisionError):
            result = capacity

        return min(capacity, max(current_pct, result))

    @staticmethod
    def _days_to_threshold(
        current_pct: float,
        rate: float,
        capacity: float,
        threshold: float,
    ) -> int:
        """Estimate days until infection reaches a given threshold."""
        if current_pct >= threshold:
            return 0
        if rate <= 0:
            return 365

        p0 = max(0.1, current_pct)
        k = capacity
        target = min(threshold, k * 0.999)

        try:
            ratio_now = (k - p0) / p0
            ratio_target = (k - target) / target
            if ratio_target <= 0 or ratio_now <= 0:
                return 365
            t = math.log(ratio_now / ratio_target) / (rate * 0.1)
            return max(1, int(math.ceil(t)))
        except (ValueError, ZeroDivisionError, OverflowError):
            return 365

    @staticmethod
    def _carrying_capacity(
        disease: Disease,
        conditions: EnvironmentalConditions,
    ) -> float:
        """Determine maximum infection percentage for the scenario."""
        base = 30 + disease.spread_rate * 60  # 30-90% range
        # High humidity increases max spread
        if conditions.humidity_pct > 85:
            base *= 1.1
        return min(100.0, base)

    @staticmethod
    def _assess_risk(
        effective_rate: float,
        current_pct: float,
        day_14_pct: float,
    ) -> str:
        """Classify spread risk level."""
        growth = day_14_pct - current_pct
        if growth < 2 and effective_rate < 0.3:
            return "low"
        elif growth < 10 and effective_rate < 0.5:
            return "moderate"
        elif growth < 25:
            return "high"
        else:
            return "critical"

    @staticmethod
    def _generate_recommendations(
        disease: Disease,
        severity: SeverityLevel,
        risk_level: str,
        conditions: EnvironmentalConditions,
    ) -> list[str]:
        """Generate actionable recommendations based on spread risk."""
        recs = []

        if risk_level in ("high", "critical"):
            recs.append(
                "URGENT: Begin treatment immediately to slow disease spread"
            )
            recs.append(
                "Consider prophylactic treatment of adjacent healthy plants"
            )

        if conditions.humidity_pct > 80:
            recs.append(
                "Reduce irrigation to lower humidity around foliage"
            )

        if severity in (SeverityLevel.SEVERE, SeverityLevel.CRITICAL):
            recs.append(
                "Remove and destroy heavily infected plants to reduce inoculum"
            )

        if disease.pathogen_type == "fungal" and conditions.rainfall_mm_per_week > 30:
            recs.append(
                "Rain is promoting spore dispersal; apply protective fungicide"
            )

        recs.append(f"Monitor field every {3 if risk_level == 'critical' else 7} days")
        recs.extend(disease.prevention[:2])

        return recs
