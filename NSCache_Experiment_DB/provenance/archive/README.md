# NS-Cache L1/L2 experiment database – recovered source + reconstructed inputs

**Status: PARTIALLY RECONSTRUCTED, NOT AN ORIGINAL COMPLETE RAW-LOG ARCHIVE.**

The November 10, 2026 study reported 16 NS-Cache runs (2 caches × 4 technology nodes × 2 optimization objectives). The original consolidated output table survives. The recovered historical source snapshot survives. The original study-specific `.cfg` and 16 original log files do not survive in the presently accessible materials.

We **reconstructed** all 16 study inputs, recompiled the recovered C++ source with GNU g++ 14.2.0 on Linux x86-64, and ran a subset to produce true raw console output. All 5 available rerun logs reproduce the workbook's reported 6 numerical metrics precisely at the recorded resolution. The other 11 runs were not verified by rerun in this package.

| Content | Status | Location |
|---|---|---|
| Original source snapshot from Drive transfer (C++ and default `.cfg/.cell`) | RECOVERED | `nscache_source/src`, `nscache_source/config/New_Configs` |
| Original per-experiment 16 configs | NOT RECOVERED | — |
| Experiment-specific configurations, 16 `.cfg` | RECONSTRUCTED, NOT ORIGINAL | `nscache_source/config/study_reconstructed/` |
| Original 16 raw execution logs | NOT RECOVERED | — |
| New genuine rerun console logs | 5 / 16 FINISHED AND MATCHED | `rerun_logs/` |
| Recorded NS-Cache values of all 16 cases | RECOVERED DERIVED VALUES | `recorded_results/` |
| Record-by-record completeness audit | GENERATED | `provenance/run_inventory.csv` |
| Rebuild, replay, compare | GENERATED | `scripts/` |
| Source provenance / missing evidence | DOCUMENTED | `provenance/original_vs_reconstructed.md` |

## Reproduction

```bash
bash scripts/build.sh
# May take substantial CPU time depending on machine:
bash scripts/run_all.sh
python3 scripts/compare_logs.py
python3 scripts/recompute_ratios.py
```

All recorded results are **NS-Cache modeled cache energy**, not physical NVIDIA GPU measurements. Modeled L1=128 KiB/8-way and L2=1 MiB/16-way do not represent actual full-chip NVIDIA cache sizes; the 14/7/5/3nm nodes are generic proxies, not validated NVIDIA foundry process equivalents.

A PASS in the historical workbook means that prior study reported successful execution; it is **not proof that the original stdout log has been recovered or that the present rerun was completed**.

## Upstream / license

[neurosim/NS-Cache](https://github.com/neurosim/NS-Cache), [reported commit](https://github.com/neurosim/NS-Cache/commit/2fdcbf093f806bc9a28964aca8402c42738d58e5). The source project notes Creative Commons Attribution–NonCommercial 4.0 restrictions. Do not redistribute code to a commercial repository without checking the license conditions; attribution required. This snapshot's byte-for-byte fidelity to the referenced commit has **not** been independently validated.
