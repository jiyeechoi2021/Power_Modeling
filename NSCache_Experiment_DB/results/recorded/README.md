# NS-Cache L1/L2 14/7/5/3 nm node sweep — 2026-11-10

## Dataset purpose

This directory contains a **public-safe, derived dataset** of 16 completed NS-Cache experiments:

- Cache sizes: L1-like **128 KiB, 8-way**, L2-like **1 MiB, 16-way**.
- Technology models: **14, 7, 5 and 3 nm**.
- Optimizer objectives: **ReadLatency** and **ReadDynamicEnergy**.
- Reported values: modeled cache-hit read/write dynamic energy (pJ/access), leakage (mW), hit latency (ns), area (mm²), feasible solution count, and recorded configuration path.
- Recorded setup: 512-bit word / 64-byte line, bank arrangement 4×4, H-tree, 300 K; node-specific SRAM `.cell` files. Details are from the supplied study workbook and are **not independently verified** against missing raw inputs.

16/16 experiment rows are marked `PASS` in the study workbook. Results are model outputs, **not** measurements on NVIDIA GPUs. Technology-node aliases (V100 12FFN~14nm, A100 N7~7nm, H100 4N~5nm, Rubin 3nm~3nm) are approximations and must not be presented as foundry-macro equivalences.

## Source and provenance

- Upstream implementation: https://github.com/neurosim/NS-Cache
- Upstream revision recorded by experiment: [`2fdcbf093f806bc9a28964aca8402c42738d58e5`](https://github.com/neurosim/NS-Cache/commit/2fdcbf093f806bc9a28964aca8402c42738d58e5)
- Runtime as recorded: Linux / g++ 14.2.0 / C++17.
- Local source of this derived public dataset: `NSCache_14_7_5_3_L1_L2_Experiment_20261110.xlsx`, sheet `01_Results`, cells `A11:K27`.
- The upstream NS-Cache source is NOT redistributed here. Follow the upstream license (CC BY-NC 4.0 for the model) if cloning, using or modifying it.

**Provenance limitation:** The original 16 `.cfg` files, `.cell` revisions, console logs, and the original result JSON mentioned in the source workbook were **not part of the materials available to prepare this upload**. The CSV/JSON reproduce the workbook's consolidated model outputs, **not the original raw logs**. Consequently, this folder provides data and post-processing reproducibility; it does not yet provide fully reproducible NS-Cache runs. In particular, paths in `cfg_path_recorded` are historical references, not runnable files in this package.

## Files

- `data/nscache_16_runs.csv`: long-form model outputs, 16 runs.
- `data/nscache_16_runs.json`: same model outputs with provenance metadata.
- `scripts/recompute_ratios.py`: standard-library Python post-processor; checks the 16-run grid and computes energy scaling factors.

## Rerun the derived analysis

```bash
python3 scripts/recompute_ratios.py
```

The script does **not** re-execute NS-Cache; it recomputes the read-energy ratios using the recorded model results.

## Interpretation rules

For a given cache configuration and optimization objective:

```
Technology-node SF(a -> b) = ReadEnergy(b) / ReadEnergy(a)
```

Read/write energy and leakage are different categories and must not be summed as if leakage were a per-access energy. The logical cache configuration was held approximately constant across technology nodes, but NS-Cache may select different internal mats/subarrays. Therefore the modeled sweep is a **fixed-logical-configuration technology sweep**, not a purified transistor-process factor at identical physical topology.

The reported V100/A100/H100 measured unit-energy values and unpublished residual/H100 prediction-validation results have been **intentionally excluded** from this public dataset. They appear only in the locally generated private research report and supplied workbook.
