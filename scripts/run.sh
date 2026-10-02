#!/usr/bin/env bash
set -e

# Source your OpenFOAM installation before running this script if necessary.
# Example:
# source /opt/openfoam*/etc/bashrc

cd "$(dirname "$0")/.."

command -v blockMesh >/dev/null || {
    echo "ERROR: OpenFOAM commands are not available."
    echo "Source your OpenFOAM bashrc and run again."
    exit 1
}

echo "=== Mesh generation ==="
blockMesh -case case

echo "=== Solver ==="
# Replace this with the selected solver:
# buoyantBoussinesqSimpleFoam -case case

echo "Solver command intentionally left project-specific."
echo "Edit scripts/run.sh after configuring the case."

echo "=== Finished ==="
