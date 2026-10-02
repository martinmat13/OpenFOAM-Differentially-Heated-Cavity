#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CSV_DIR = RESULTS / "csv"

def main():
    print("Project: Differentially Heated Cavity")
    print("Root:", ROOT)
    print()
    print("TODO:")
    print("1. Read OpenFOAM post-processing output.")
    print("2. Calculate engineering quantities.")
    print("3. Write CSV result files.")
    print("4. Generate publication-quality figures.")

if __name__ == "__main__":
    main()
