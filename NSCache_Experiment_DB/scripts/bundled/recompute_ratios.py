#!/usr/bin/env python3
"""Recompute technology-node scaling ratios for a recorded NS-Cache model dataset.

No NS-Cache binary is invoked. Input is the derived 16-run CSV from a study
workbook; missing raw cfg/logs limit direct experiment reproducibility.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "recorded_results" / "nscache_16_runs.csv"

with CSV.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == 16, f"Expected 16 runs; found {len(rows)}"

by = {(r["cache"], r["optimization"], int(r["node_nm"])): r for r in rows}
assert len(by) == 16 and all(r["run_status"] == "PASS" for r in rows)
for cache in ("L1", "L2"):
    for opt in ("ReadLatency", "ReadDynamicEnergy"):
        values = [float(by[cache, opt, n]["read_pj_per_access"]) for n in (14, 7, 5, 3)]
        sfs = [values[i+1]/values[i] for i in range(3)]
        reductions = [100*(1-r) for r in sfs]
        print(f"{cache:2} | {opt:17} | read pJ/access: {values!s:28} | "
              f"SF(14>7,7>5,5>3): {sfs[0]:.4f}, {sfs[1]:.4f}, {sfs[2]:.4f} | "
              f"energy reduction (%): {reductions[0]:.1f}, {reductions[1]:.1f}, {reductions[2]:.1f}")
