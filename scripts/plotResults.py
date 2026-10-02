#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    print("Plotting results for:", ROOT)
    print("Add project-specific matplotlib plots here.")

if __name__ == "__main__":
    main()
