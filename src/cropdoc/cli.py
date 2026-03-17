"""Command-line interface for CROPDOC."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cropdoc import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="cropdoc")
def cli() -> None:
    """CROPDOC - AI Crop Disease Detector.

    Analyze leaf images to detect plant diseases, estimate severity,
    and get treatment recommendations.
    """


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--severity", is_flag=True, help="Include severity estimation.")
@click.option("--treatment", is_flag=True, help="Include treatment recommendations.")
@click.option("--top-k", default=3, help="Number of top predictions to show.")
@click.option("--organic", is_flag=True, help="Prefer organic treatments.")
def analyze(
    image_path: str,
    severity: bool,
    treatment: bool,
    top_k: int,
    organic: bool,
) -> None:
    """Analyze a leaf image for crop diseases."""
    from cropdoc.detector.model import CropDiseaseClassifier
    from cropdoc.detector.preprocessor import LeafImagePreprocessor
    from cropdoc.analyzer.severity import SeverityEstimator
    from cropdoc.analyzer.treatment import TreatmentRecommender
    from cropdoc.models import Diagnosis, LeafImage

    console.print(
        Panel(f"Analyzing: [bold]{image_path}[/bold]", title="CROPDOC")
    )

    preprocessor = LeafImagePreprocessor()
    with console.status("Loading and preprocessing image..."):
        tensor = preprocessor.load_and_preprocess(image_path)

    classifier = CropDiseaseClassifier()
    with console.status("Running disease classification..."):
        predictions = classifier.predict_top_k(tensor, k=top_k)

    # Show top predictions
    table = Table(title="Disease Predictions")
    table.add_column("Rank", justify="center", style="cyan")
    table.add_column("Disease", style="green")
    table.add_column("Crop", style="yellow")
    table.add_column("Confidence", justify="right", style="magenta")

    for i, pred in enumerate(predictions, 1):
        disease = pred["disease"]
        crop = disease.crop if disease else "unknown"
        table.add_row(
            str(i),
            pred["disease_name"],
            crop.title(),
            f"{pred['confidence']:.1%}",
        )
    console.print(table)

    # Primary prediction
    primary = predictions[0]
    disease = primary["disease"]

    if severity and disease:
        estimator = SeverityEstimator()
        sev_result = estimator.estimate(tensor, primary)
        console.print(f"\n[bold]Severity:[/bold] {sev_result['severity_level'].value.upper()}")
        console.print(f"  Score: {sev_result['severity_score']:.2f}")
        console.print(f"  Affected area: {sev_result['affected_area_pct']:.1f}%")

        if treatment:
            from PIL import Image
            img = Image.open(image_path)
            leaf = LeafImage(
                path=Path(image_path),
                width=img.width,
                height=img.height,
            )
            diagnosis = Diagnosis(
                image=leaf,
                disease=disease,
                confidence=primary["confidence"],
                severity_score=sev_result["severity_score"],
                severity_level=sev_result["severity_level"],
                affected_area_pct=sev_result["affected_area_pct"],
            )
            recommender = TreatmentRecommender()
            plan = recommender.recommend(
                diagnosis, prefer_organic=organic
            )

            console.print(f"\n[bold]Treatment Plan[/bold]")
            console.print(f"  Recovery estimate: {plan.estimated_recovery_days} days")
            console.print(f"  Follow-up in: {plan.follow_up_days} days")
            for step in plan.steps:
                tag = "green" if step.treatment_type.value == "organic" else "red"
                console.print(f"  [{tag}][{step.treatment_type.value}][/{tag}] {step.action}")


@cli.command()
@click.option("--crop", default=None, help="Filter by crop type.")
@click.option("--pathogen", default=None, help="Filter by pathogen type.")
def diseases(crop: str | None, pathogen: str | None) -> None:
    """List supported diseases in the database."""
    from cropdoc.detector.diseases import DiseaseDatabase

    db = DiseaseDatabase()

    if crop:
        entries = db.by_crop(crop)
    elif pathogen:
        entries = db.by_pathogen_type(pathogen)
    else:
        entries = db.all_diseases

    if not entries:
        console.print("[yellow]No diseases found matching the filter.[/yellow]")
        return

    table = Table(title="Crop Disease Database")
    table.add_column("Disease", style="green")
    table.add_column("Crop", style="yellow")
    table.add_column("Pathogen", style="cyan")
    table.add_column("Spread Rate", justify="right", style="magenta")
    table.add_column("Symptoms", style="white")

    for d in entries:
        table.add_row(
            d.name,
            d.crop.title(),
            d.pathogen_type.title(),
            f"{d.spread_rate:.0%}",
            d.symptoms[0] if d.symptoms else "-",
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(entries)} diseases[/dim]")


@cli.command()
@click.option("--count", default=10, help="Number of samples to generate.")
@click.option("--output", default="synthetic_data", help="Output directory.")
@click.option("--seed", default=None, type=int, help="Random seed.")
def simulate(count: int, output: str, seed: int | None) -> None:
    """Generate synthetic test data."""
    from cropdoc.simulator import CropSimulator

    console.print(
        Panel(
            f"Generating {count} synthetic samples...",
            title="CROPDOC Simulator",
        )
    )

    sim = CropSimulator(seed=seed)

    with console.status("Generating synthetic data..."):
        batch = sim.generate_batch(count=count, include_treatment=True)
        paths = sim.save_synthetic_images(output, count=count)

    table = Table(title="Generated Samples")
    table.add_column("#", justify="center", style="cyan")
    table.add_column("Disease", style="green")
    table.add_column("Severity", style="yellow")
    table.add_column("Confidence", justify="right", style="magenta")

    for i, case in enumerate(batch, 1):
        d = case["diagnosis"]
        table.add_row(
            str(i),
            d.disease.name,
            d.severity_level.value,
            f"{d.confidence:.1%}",
        )

    console.print(table)
    console.print(f"\n[green]Saved {len(paths)} image tensors to {output}/[/green]")


@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--output", default=None, help="Output file path for report.")
def report(image_path: str, output: str | None) -> None:
    """Generate a full diagnostic report for a leaf image."""
    from cropdoc.detector.model import CropDiseaseClassifier
    from cropdoc.detector.preprocessor import LeafImagePreprocessor
    from cropdoc.analyzer.severity import SeverityEstimator
    from cropdoc.analyzer.treatment import TreatmentRecommender
    from cropdoc.analyzer.spread import SpreadPredictor
    from cropdoc.report import DiagnosticReport
    from cropdoc.models import Diagnosis, LeafImage

    console.print(Panel("Generating diagnostic report...", title="CROPDOC"))

    preprocessor = LeafImagePreprocessor()
    tensor = preprocessor.load_and_preprocess(image_path)

    classifier = CropDiseaseClassifier()
    prediction = classifier.predict(tensor)

    disease = prediction["disease"]
    estimator = SeverityEstimator()
    sev = estimator.estimate(tensor, prediction)

    from PIL import Image
    img = Image.open(image_path)
    leaf = LeafImage(
        path=Path(image_path), width=img.width, height=img.height
    )
    diagnosis = Diagnosis(
        image=leaf,
        disease=disease,
        confidence=prediction["confidence"],
        severity_score=sev["severity_score"],
        severity_level=sev["severity_level"],
        affected_area_pct=sev["affected_area_pct"],
    )

    recommender = TreatmentRecommender()
    plan = recommender.recommend(diagnosis)

    predictor = SpreadPredictor()
    forecast = predictor.predict(diagnosis)

    reporter = DiagnosticReport()
    report_text = reporter.generate(diagnosis, plan, forecast)

    if output:
        reporter.save(report_text, output)
        console.print(f"[green]Report saved to {output}[/green]")
    else:
        console.print(report_text)


if __name__ == "__main__":
    cli()
