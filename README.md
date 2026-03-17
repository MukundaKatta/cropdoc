# CROPDOC - AI Crop Disease Detector

CROPDOC is an AI-powered crop disease detection system that analyzes leaf images to
identify plant diseases, estimate severity, and recommend treatments.

## Features

- **Disease Detection**: CNN-based classifier supporting 15+ plant diseases across
  multiple crop types (tomato, potato, corn, apple, grape, citrus, rice, wheat).
- **Severity Estimation**: Scores disease progression on a 0-1 scale with categorical
  labels (healthy, mild, moderate, severe, critical).
- **Treatment Recommendations**: Provides both organic and chemical treatment options
  with application schedules and safety considerations.
- **Spread Prediction**: Estimates field-level impact based on disease characteristics,
  current severity, and environmental conditions.
- **Disease Database**: Comprehensive database of 15+ diseases with symptoms, treatments,
  and prevention strategies.
- **Synthetic Data Simulation**: Generate synthetic leaf images and diagnoses for
  testing and development.

## Installation

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Usage

### CLI

```bash
# Analyze a single leaf image
cropdoc analyze path/to/leaf.jpg

# Analyze with severity estimation and treatment plan
cropdoc analyze path/to/leaf.jpg --severity --treatment

# List all supported diseases
cropdoc diseases

# Show details for a specific disease
cropdoc diseases --crop tomato

# Generate synthetic test data
cropdoc simulate --count 10 --output synthetic_data/

# Generate a full diagnostic report
cropdoc report path/to/leaf.jpg --output report.txt
```

### Python API

```python
from cropdoc.detector.model import CropDiseaseClassifier
from cropdoc.detector.preprocessor import LeafImagePreprocessor
from cropdoc.analyzer.severity import SeverityEstimator

# Load and preprocess an image
preprocessor = LeafImagePreprocessor()
tensor = preprocessor.load_and_preprocess("leaf.jpg")

# Classify
classifier = CropDiseaseClassifier()
prediction = classifier.predict(tensor)

# Estimate severity
estimator = SeverityEstimator()
severity = estimator.estimate(tensor, prediction)
```

## Project Structure

```
cropdoc/
  src/cropdoc/
    cli.py                  # Click CLI interface
    models.py               # Pydantic data models
    simulator.py            # Synthetic data generation
    report.py               # Diagnostic report generation
    detector/
      model.py              # CropDiseaseClassifier CNN
      preprocessor.py       # LeafImagePreprocessor
      diseases.py           # DiseaseDatabase (15+ diseases)
    analyzer/
      severity.py           # SeverityEstimator
      treatment.py          # TreatmentRecommender
      spread.py             # SpreadPredictor
  tests/
    test_models.py
    test_detector.py
    test_analyzer.py
    test_simulator.py
```

## Supported Diseases

| Crop   | Disease                  |
|--------|--------------------------|
| Tomato | Early Blight             |
| Tomato | Late Blight              |
| Tomato | Leaf Mold                |
| Potato | Early Blight             |
| Potato | Late Blight              |
| Corn   | Northern Leaf Blight     |
| Corn   | Common Rust              |
| Apple  | Apple Scab               |
| Apple  | Cedar Apple Rust         |
| Grape  | Black Rot                |
| Grape  | Esca (Black Measles)     |
| Citrus | Citrus Canker            |
| Citrus | Huanglongbing (Greening) |
| Rice   | Rice Blast               |
| Rice   | Brown Spot               |
| Wheat  | Wheat Rust               |

## License

MIT
