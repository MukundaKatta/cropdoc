"""Treatment recommendation engine for diagnosed crop diseases."""

from __future__ import annotations

from cropdoc.models import (
    Disease,
    Diagnosis,
    SeverityLevel,
    TreatmentPlan,
    TreatmentStep,
    TreatmentType,
)


class TreatmentRecommender:
    """Generates treatment plans based on diagnosis, severity, and preferences.

    Provides both organic and chemical treatment options, tailored to the
    severity level of the detected disease.
    """

    # Recovery time multipliers by severity
    RECOVERY_MULTIPLIERS = {
        SeverityLevel.HEALTHY: 0,
        SeverityLevel.MILD: 1.0,
        SeverityLevel.MODERATE: 1.5,
        SeverityLevel.SEVERE: 2.5,
        SeverityLevel.CRITICAL: 4.0,
    }

    # Follow-up intervals by severity (days)
    FOLLOWUP_DAYS = {
        SeverityLevel.HEALTHY: 30,
        SeverityLevel.MILD: 14,
        SeverityLevel.MODERATE: 10,
        SeverityLevel.SEVERE: 7,
        SeverityLevel.CRITICAL: 3,
    }

    def recommend(
        self,
        diagnosis: Diagnosis,
        prefer_organic: bool = False,
        include_both: bool = True,
    ) -> TreatmentPlan:
        """Generate a treatment plan for a given diagnosis.

        Args:
            diagnosis: The diagnosis including disease and severity info.
            prefer_organic: If True, prioritize organic treatments.
            include_both: If True, include both organic and chemical options.

        Returns:
            A complete TreatmentPlan.
        """
        disease = diagnosis.disease
        severity = diagnosis.severity_level
        steps: list[TreatmentStep] = []

        # Always start with immediate actions for moderate+ severity
        if severity in (
            SeverityLevel.MODERATE,
            SeverityLevel.SEVERE,
            SeverityLevel.CRITICAL,
        ):
            steps.append(TreatmentStep(
                action="Isolate affected plants to prevent further spread",
                treatment_type=TreatmentType.ORGANIC,
                frequency="Immediate",
                safety_notes=[
                    "Wear gloves when handling infected plant material",
                    "Dispose of removed tissue in sealed bags, do not compost",
                ],
            ))

        # Add organic treatments
        if prefer_organic or include_both:
            for treatment_text in disease.treatment_organic:
                step = self._parse_treatment(
                    treatment_text, TreatmentType.ORGANIC, severity
                )
                steps.append(step)

        # Add chemical treatments
        if not prefer_organic or include_both:
            for treatment_text in disease.treatment_chemical:
                step = self._parse_treatment(
                    treatment_text, TreatmentType.CHEMICAL, severity
                )
                steps.append(step)

        # Critical severity: add emergency measures
        if severity == SeverityLevel.CRITICAL:
            steps.append(TreatmentStep(
                action="Consider removing severely infected plants entirely",
                treatment_type=TreatmentType.ORGANIC,
                frequency="As needed",
                safety_notes=[
                    "Document plant condition before removal",
                    "Sterilize tools after removal",
                ],
            ))

        # Build the plan
        base_recovery = 14  # base recovery days
        multiplier = self.RECOVERY_MULTIPLIERS.get(severity, 1.0)
        recovery_days = int(base_recovery * multiplier) if multiplier > 0 else None

        prevention = list(disease.prevention)

        return TreatmentPlan(
            diagnosis=diagnosis,
            steps=steps,
            estimated_recovery_days=recovery_days,
            spread_risk=disease.spread_rate * self._severity_factor(severity),
            field_impact_pct=self._estimate_field_impact(disease, severity),
            preventive_measures=prevention,
            follow_up_days=self.FOLLOWUP_DAYS.get(severity, 14),
        )

    def _parse_treatment(
        self,
        text: str,
        treatment_type: TreatmentType,
        severity: SeverityLevel,
    ) -> TreatmentStep:
        """Parse a treatment description into a structured TreatmentStep."""
        safety_notes = []
        if treatment_type == TreatmentType.CHEMICAL:
            safety_notes = [
                "Wear appropriate PPE including gloves and mask",
                "Follow label directions for mixing and application rates",
                "Observe pre-harvest interval (PHI) before harvesting",
            ]

        frequency = self._suggest_frequency(severity, treatment_type)
        duration = self._suggest_duration(severity)

        return TreatmentStep(
            action=text,
            treatment_type=treatment_type,
            frequency=frequency,
            duration_days=duration,
            safety_notes=safety_notes,
        )

    @staticmethod
    def _suggest_frequency(
        severity: SeverityLevel, treatment_type: TreatmentType
    ) -> str:
        """Suggest application frequency based on severity."""
        if severity in (SeverityLevel.HEALTHY, SeverityLevel.MILD):
            return "Every 10-14 days" if treatment_type == TreatmentType.CHEMICAL else "Every 7-10 days"
        elif severity == SeverityLevel.MODERATE:
            return "Every 7-10 days" if treatment_type == TreatmentType.CHEMICAL else "Every 5-7 days"
        elif severity == SeverityLevel.SEVERE:
            return "Every 5-7 days"
        else:
            return "Every 3-5 days"

    @staticmethod
    def _suggest_duration(severity: SeverityLevel) -> int:
        """Suggest treatment duration in days."""
        durations = {
            SeverityLevel.HEALTHY: 0,
            SeverityLevel.MILD: 14,
            SeverityLevel.MODERATE: 21,
            SeverityLevel.SEVERE: 35,
            SeverityLevel.CRITICAL: 56,
        }
        return durations.get(severity, 21)

    @staticmethod
    def _severity_factor(severity: SeverityLevel) -> float:
        """Convert severity to a multiplicative factor."""
        factors = {
            SeverityLevel.HEALTHY: 0.0,
            SeverityLevel.MILD: 0.3,
            SeverityLevel.MODERATE: 0.6,
            SeverityLevel.SEVERE: 0.85,
            SeverityLevel.CRITICAL: 1.0,
        }
        return factors.get(severity, 0.5)

    @staticmethod
    def _estimate_field_impact(
        disease: Disease, severity: SeverityLevel
    ) -> float:
        """Estimate potential field-level impact as a percentage."""
        base_impact = disease.spread_rate * 40  # max ~40% from spread rate alone
        severity_boost = {
            SeverityLevel.HEALTHY: 0.0,
            SeverityLevel.MILD: 5.0,
            SeverityLevel.MODERATE: 15.0,
            SeverityLevel.SEVERE: 30.0,
            SeverityLevel.CRITICAL: 50.0,
        }
        total = base_impact + severity_boost.get(severity, 10.0)
        return min(100.0, round(total, 1))
