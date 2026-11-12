#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build logs/build
python3 scripts/environment.py "${JOBS:-2}" > logs/build/environment.json
make -C ../NSCache_Experiment_DB/source -j "${JOBS:-2}" target="$PWD/build/nsc" OUTDIR="$PWD/build/obj" > logs/build/stdout.log 2> logs/build/stderr.log
sha256sum build/nsc > logs/build/binary.sha256
