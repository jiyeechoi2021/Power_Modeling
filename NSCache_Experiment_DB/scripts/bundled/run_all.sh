#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../nscache_source"
mkdir -p ../rerun_logs/replayed
for cfg in config/study_reconstructed/*.cfg; do
  name="$(basename "$cfg" .cfg)"
  echo "running $name"
  ./nsc "$cfg" > "../rerun_logs/replayed/${name}.log" 2>&1
  echo "completed $name"
done
