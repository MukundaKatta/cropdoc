"""CLI for cropdoc."""
import sys, json, argparse
from .core import Cropdoc

def main():
    parser = argparse.ArgumentParser(description="CropDoc — AI Crop Disease Detector. Computer vision for plant disease identification from leaf photos.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Cropdoc()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.detect(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"cropdoc v0.1.0 — CropDoc — AI Crop Disease Detector. Computer vision for plant disease identification from leaf photos.")

if __name__ == "__main__":
    main()
