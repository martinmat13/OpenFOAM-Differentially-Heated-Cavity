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

buoyantBoussinesqSimpleFoam -case case

echo "=== Finished ==="
