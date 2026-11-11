#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../nscache_source"
make -C src -j "${JOBS:-2}"
printf 'Built %s\n' "$PWD/nsc"
