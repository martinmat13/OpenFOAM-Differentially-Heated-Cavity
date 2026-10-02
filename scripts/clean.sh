#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

find case -maxdepth 1 -type d     ! -name case     ! -name 0     ! -name constant     ! -name system     -exec rm -rf {} +

rm -rf case/postProcessing
rm -rf case/constant/polyMesh

echo "Clean complete."
