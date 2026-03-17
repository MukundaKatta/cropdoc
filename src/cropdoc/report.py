"""Diagnostic report generation for crop disease analysis."""

from __future__ import annotations

from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

from cropdoc.models import Diagnosis, TreatmentPlan, TreatmentType


class DiagnosticReport:
    """Generates formatted diagnostic reports from analysis results.

    Produces human-readable text reports summarizing disease detection,
    severity assessment, treatment recommendations, and spread predictions.
    """

    SEPARATOR = "=" * 72
    SUB_SEPARATOR = "-" * 72

    def generate(
        self,
        diagnosis: Diagnosis,
        treatment_plan: Optional[TreatmentPlan] = None,
        spread_forecast: Optional[dict] = None,
    ) -> str:
        """Generate a complete diagnostic report.

        Args:
            diagnosis: The disease diagnosis.
            treatment_plan: Optional treatment plan.
            spread_forecast: Optional spread prediction data.

        Returns:
            Formatted report as a string.
        """
        buf = StringIO()

        self._write_header(buf)
        self._write_diagnosis_section(buf, diagnosis)

        if treatment_plan:
            self._write_treatment_section(buf, treatment_plan)

        if spread_forecast:
            self._write_spread_section(buf, spread_forecast)

        self._write_footer(buf, diagnosis)

        return buf.getvalue()

    def save(
        self,
        report: str,
        output_path: str | Path,
    ) -> Path:
        """Save a report to a file.

        Args:
            report: Report text.
            output_path: Destination file path.

        Returns:
            Path to the saved file.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
        return path

    def _write_header(self, buf: StringIO) -> None:
        buf.write(f"\n{self.SEPARATOR}\n")
        buf.write("  CROPDOC - AI Crop Disease Diagnostic Report\n")
        buf.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        buf.write(f"{self.SEPARATOR}\n\n")

    def _write_diagnosis_section(
        self, buf: StringIO, diagnosis: Diagnosis
    ) -> None:
        disease = diagnosis.disease

        buf.write(f"DISEASE IDENTIFICATION\n")
        buf.write(f"{self.SUB_SEPARATOR}\n")
        buf.write(f"  Disease:          {disease.name}\n")
        if disease.scientific_name:
            buf.write(f"  Scientific Name:  {disease.scientific_name}\n")
        buf.write(f"  Crop:             {disease.crop.title()}\n")
        buf.write(f"  Pathogen Type:    {disease.pathogen_type.title()}\n")
        buf.write(f"  Confidence:       {diagnosis.confidence:.1%}\n")
        buf.write(f"\n")

        buf.write(f"SEVERITY ASSESSMENT\n")
        buf.write(f"{self.SUB_SEPARATOR}\n")
        buf.write(f"  Severity Score:   {diagnosis.severity_score:.2f} / 1.00\n")
        buf.write(f"  Severity Level:   {diagnosis.severity_level.value.upper()}\n")
        buf.write(f"  Affected Area:    {diagnosis.affected_area_pct:.1f}%\n")
        buf.write(f"\n")

        buf.write(f"SYMPTOMS\n")
        buf.write(f"{self.SUB_SEPARATOR}\n")
        for symptom in disease.symptoms:
            buf.write(f"  * {symptom}\n")
        buf.write(f"\n")

    def _write_treatment_section(
        self, buf: StringIO, plan: TreatmentPlan
    ) -> None:
        buf.write(f"TREATMENT PLAN\n")
        buf.write(f"{self.SUB_SEPARATOR}\n")

        if plan.estimated_recovery_days:
            buf.write(
                f"  Estimated Recovery: {plan.estimated_recovery_days} days\n"
            )
        buf.write(f"  Follow-up In:      {plan.follow_up_days} days\n")
        buf.write(f"  Spread Risk:       {plan.spread_risk:.1%}\n")
        buf.write(f"  Field Impact:      {plan.field_impact_pct:.1f}%\n")
        buf.write(f"\n")

        organic_steps = [
            s for s in plan.steps
            if s.treatment_type == TreatmentType.ORGANIC
        ]
        chemical_steps = [
            s for s in plan.steps
            if s.treatment_type == TreatmentType.CHEMICAL
        ]

        if organic_steps:
            buf.write(f"  Organic Treatments:\n")
            for i, step in enumerate(organic_steps, 1):
                buf.write(f"    {i}. {step.action}\n")
                if step.frequency:
                    buf.write(f"       Frequency: {step.frequency}\n")
                if step.duration_days:
                    buf.write(f"       Duration:  {step.duration_days} days\n")
            buf.write(f"\n")

        if chemical_steps:
            buf.write(f"  Chemical Treatments:\n")
            for i, step in enumerate(chemical_steps, 1):
                buf.write(f"    {i}. {step.action}\n")
                if step.frequency:
                    buf.write(f"       Frequency: {step.frequency}\n")
                if step.duration_days:
                    buf.write(f"       Duration:  {step.duration_days} days\n")
                if step.safety_notes:
                    buf.write(f"       Safety:\n")
                    for note in step.safety_notes:
                        buf.write(f"         - {note}\n")
            buf.write(f"\n")

        if plan.preventive_measures:
            buf.write(f"  Prevention:\n")
            for measure in plan.preventive_measures:
                buf.write(f"    * {measure}\n")
            buf.write(f"\n")

    def _write_spread_section(self, buf: StringIO, forecast: dict) -> None:
        buf.write(f"SPREAD FORECAST\n")
        buf.write(f"{self.SUB_SEPARATOR}\n")

        if hasattr(forecast, "current_infection_pct"):
            # SpreadForecast dataclass
            buf.write(f"  Current Infection: {forecast.current_infection_pct:.1f}%\n")
            buf.write(f"  7-Day Forecast:    {forecast.day_7_pct:.1f}%\n")
            buf.write(f"  14-Day Forecast:   {forecast.day_14_pct:.1f}%\n")
            buf.write(f"  30-Day Forecast:   {forecast.day_30_pct:.1f}%\n")
            buf.write(f"  Peak Infection:    {forecast.peak_infection_pct:.1f}%\n")
            buf.write(f"  Days to Peak:      {forecast.days_to_peak}\n")
            buf.write(f"  Risk Level:        {forecast.risk_level.upper()}\n")
            buf.write(f"\n")
            if forecast.recommendations:
                buf.write(f"  Recommendations:\n")
                for rec in forecast.recommendations:
                    buf.write(f"    * {rec}\n")
        else:
            # Plain dict fallback
            for key, value in forecast.items():
                buf.write(f"  {key}: {value}\n")

        buf.write(f"\n")

    def _write_footer(self, buf: StringIO, diagnosis: Diagnosis) -> None:
        buf.write(f"{self.SEPARATOR}\n")
        buf.write(
            "  DISCLAIMER: This report is generated by an AI system and\n"
            "  should be used as a decision-support tool only. Always consult\n"
            "  a qualified agronomist for critical crop management decisions.\n"
        )
        buf.write(f"{self.SEPARATOR}\n")
