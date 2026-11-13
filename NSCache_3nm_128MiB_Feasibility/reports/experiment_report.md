# 3nm 128MiB feasibility and controlled LLMET-reference comparison

## Method and evidence classes

Two validated Phase 2-B 3nm/32MiB raw baselines (ReadLatency and ReadDynamicEnergy) are verified rather than re-executed. Each objective supplies a new 128MiB configuration changing **only Capacity (MB): 32→128**. Both objectives were selected before running because both exist in the baseline, not to search for the nearest reference. No other parameters/source/guards/architecture are changed. [Exact diffs and input/cell hashes](../provenance/cases.json).
Source upstream 2fdcbf093f806bc9a28964aca8402c42738d58e5 (54 source/Makefile hashes); SRAM_cell_3nm.cell; cache/Normal, 256bit/32B model line, 16-way, 300K/LOP, H-tree/internal sensing, data ForceBankA=4x4, pruning and latency buffer design, one die, original wires. Source Vdd=0.7V is distinct from cell read voltage=0.248V. Cell area=2047.8F², aspect ratio=0.4395, stitching=16. Port count and explicit timing constraint are not separately specified. Exact parameters remain in configs.
Three evidence classes remain separate: (1) verified historical NS-Cache raw outputs; (2) new capacity-only reconstructed configurations and their actual results; (3) reported **public** LLMET Table 2 reference 0.917pJ/bit. The author config/output is unavailable, pending the user's author request. No correspondence or private GPU data is copied.

## Existing reference-material inventory

The repository tracked configs and config members of tracked ZIPs were inspected before creating new cases; no existing 3nm/128MiB author/public config was found. The recovered generic SRAM_cache_3nm.cfg is 32MiB, 512bit, WriteLatency, and is **not** a 128MiB LLMET config. It was not executed or altered. [Inventory](../provenance/reference_inventory.json). No full LLMET URL/DOI/PDF is available locally; arXiv API lookup returned HTTP403. The public scalar is therefore task-reported, not an independently reread Table 2 or confidential measurement.

## Actual execution and results

| MiB | Objective | Evidence/status | Read pJ | Write pJ | Read pJ/bit | Write pJ/bit | Read/hit ns | Write ns | Leakage mW | Area mm² | Solutions | Raw |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 32 | ReadLatency | verified_phase2b_raw/FINISHED | 186.000 | 124.000 | 0.7265625 | 0.484375 | 14.773 | 12.036 | 7.441 | 6.194 | 873 | [stdout](../../NSCache_Phase2B/logs/L2_3nm_32MiB_ReadLatency/20261112T044142.771062Z/stdout.log) |
| 128 | ReadLatency | capacity_only_reconstruction/FINISHED | 369.000 | 246.000 | 1.44140625 | 0.9609375 | 44.903 | 38.089 | 28.956 | 24.061 | 1440 | [stdout](../../NSCache_3nm_128MiB_Feasibility/logs/L2_3nm_128MiB_ReadLatency/20261113T061848.769717Z/stdout.log) |
| 32 | ReadDynamicEnergy | verified_phase2b_raw/FINISHED | 177.000 | 115.000 | 0.69140625 | 0.44921875 | 25.540 | 20.283 | 7.314 | 6.119 | 873 | [stdout](../../NSCache_Phase2B/logs/L2_3nm_32MiB_ReadDynamicEnergy/20261112T044142.771354Z/stdout.log) |
| 128 | ReadDynamicEnergy | capacity_only_reconstruction/FINISHED | 349.000 | 228.000 | 1.36328125 | 0.890625 | 85.464 | 68.747 | 28.700 | 23.911 | 1440 | [stdout](../../NSCache_3nm_128MiB_Feasibility/logs/L2_3nm_128MiB_ReadDynamicEnergy/20261113T061848.770073Z/stdout.log) |

Above energy uses the cache summary (0.001nJ=1pJ resolution). Effective pJ/bit divides complete modeled cache-access energy by WordWidth=256; it is not SRAM bitcell or actual GPU-sector energy. Fine bank sums and normalized values are separate in [results CSV](../results/energy_results.csv). No averaging or denominator change is used to approach 0.917.

## Capacity-only comparison and organization

[32→128 ratios and timing/area/leakage deltas](../results/capacity_comparison.csv) keep each objective/operation/precision matched. [Data/tag/routing](../results/energy_breakdown.csv) and [full organization/activation/mux/wires/buffer and metadata](../results/organization_and_metadata.json) are traceable to raw stdout.

| Objective | Operation | Summary 128/32 | Fine bank-sum 128/32 |
|---|---|---:|---:|
| ReadLatency | read | 1.983871 | 1.980457 |
| ReadLatency | write | 1.983871 | 1.985499 |
| ReadDynamicEnergy | read | 1.971751 | 1.974576 |
| ReadDynamicEnergy | write | 1.982609 | 1.977680 |

| MiB | Objective | Data bank/subarray/mat | Tag bank/subarray/mat | Read Data/Tag/Routing pJ | Write Data/Tag/Routing pJ |
|---:|---|---|---|---:|---:|
| 32 | ReadLatency | 4 x 4/2 x 2/4096 Rows x 1024 Columns | 64 x 1/2 x 2/64 Rows x 1856 Columns | 179.016/7.085/121.190 | 119.079/5.049/121.190 |
| 128 | ReadLatency | 4 x 4/2 x 2/8192 Rows x 2048 Columns | 64 x 1/2 x 2/128 Rows x 3456 Columns | 354.758/13.807/242.597 | 237.196/9.260/242.597 |
| 32 | ReadDynamicEnergy | 4 x 4/2 x 1/4096 Rows x 2048 Columns | 64 x 1/2 x 2/64 Rows x 1856 Columns | 172.688/3.994/112.391 | 112.765/2.555/112.391 |
| 128 | ReadDynamicEnergy | 4 x 4/2 x 1/8192 Rows x 4096 Columns | 64 x 1/2 x 2/128 Rows x 3456 Columns | 341.991/6.881/224.318 | 224.437/3.629/224.318 |

Observed structural response: at fixed data bank 4×4, ReadLatency data mat grows from 4096×1024 to 8192×2048, and ReadDynamicEnergy from 4096×2048 to 8192×4096. Selected data subarray row activation decreases 2/2→1/2. Full bank×subarray×mat bit counts equal the requested 32/128MiB in an independent arithmetic check. Internal optimizer choices change naturally despite identical architectural input controls; these are not manually fitted changes.
Read routing subset grows 121.190→242.597pJ for latency objective and 112.391→224.318pJ for energy objective. This observed near-doubling accompanies the approximately 2× access energy, while storage capacity is 4×. It does not isolate a routing-only causal contribution. Large selected mat dimensions and timing require physical-model validation beyond logical capacity feasibility.

Data+tag bank totals already include H-tree routing. Per-subarray/mat/peripheral outputs overlap the hierarchy and are not added again. Nonrouting residual is not cell-only. Observed organization changes reflect normal optimizer selection under unchanged controls; they do not isolate bit-count, routing or process causality.

## Comparison with reported LLMET Table 2 value

Reference: **0.917pJ/bit**, described as published 3nm/128MB SRAM energy in the task. The table below is only numerical comparison. Author operation, denominator, aggregation, capacity-unit convention and architecture are not confirmed. The model uses exact 128MiB=134217728 bytes; paper “128MB” may have a different convention.

| Model MiB | Objective | Operation | Precision | Model pJ/bit | Reported reference | Difference pJ/bit | Model/reference |
|---:|---|---|---|---:|---:|---:|---:|
| 128 | ReadLatency | read | summary | 1.441406250 | 0.917 | 0.524406250 | 1.571872 |
| 128 | ReadLatency | read | bank_sum | 1.439707031 | 0.917 | 0.522707031 | 1.570019 |
| 128 | ReadLatency | write | summary | 0.960937500 | 0.917 | 0.043937500 | 1.047914 |
| 128 | ReadLatency | write | bank_sum | 0.962718750 | 0.917 | 0.045718750 | 1.049857 |
| 128 | ReadDynamicEnergy | read | summary | 1.363281250 | 0.917 | 0.446281250 | 1.486675 |
| 128 | ReadDynamicEnergy | read | bank_sum | 1.362781250 | 0.917 | 0.445781250 | 1.486130 |
| 128 | ReadDynamicEnergy | write | summary | 0.890625000 | 0.917 | -0.026375000 | 0.971238 |
| 128 | ReadDynamicEnergy | write | bank_sum | 0.890882812 | 0.917 | -0.026117188 | 0.971519 |

No row is labeled “LLMET reproduced.” Comparing both read and write to an operation-unspecified scalar does not assert that both correspond to the paper. Numerical proximity alone does not validate source/config/normalization or hardware. [Comparison CSV](../results/llmet_reference_comparison.csv).

## Failure analysis and limits

Both capacity-only 128MiB objectives complete under the unchanged geometry/bank constraints; no capacity bypass, unsupported-design workaround or structural change was required. This establishes current-model feasibility for these settings only, not the author's setup.

The cache model includes tag/data and routing and may differ from the paper's SRAM boundary. 256bit here is a 32B model line, not a sector with shared 128B metadata. Summary and finer bank precision are not interchanged. Missing author configs/output/source hash and original normalization remain unresolved. Private GPU measurements/coefficients/calibration/scaling data are neither inputs nor outputs.

## Recommended separate next steps (not executed)

1. Obtain author-original config, SRAM cell, source revision/binary/build flags and raw output; preserve unchanged with provenance and replay directly. Confirm Table 2 operation, cache/RAM design target, MB/MiB convention, WordWidth and pJ/bit denominator, read/write aggregation, Vdd/T/ways/bank/wire constraints.
2. If a public reference config is supplied, compare exact source/config/cell hashes before any numerical claim. A supplied original config belongs in a separate reference namespace, never relabeled as this reconstruction.
3. Only after documenting a concrete discrepancy, propose a separate controlled diagnostic such as cache-tag boundary versus SRAM-array boundary or the author's documented access width. Obtain a separate scope decision before structural changes. Do not search arbitrary combinations for 0.917.
4. If future runs fail, first preserve guard/no-solution/resource/timeout evidence and check limits. Do not remove verification or silently change banking/organization. No hardware/GPU equivalence or Rubin forecast is established here.
