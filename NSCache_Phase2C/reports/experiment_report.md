# Phase 2-C — 512KiB NS-Cache single-cache proxy

## Background, gate and scope

This study executes only eight 512KiB/256bit L2-like configurations: 14/7/5/3nm × ReadLatency/ReadDynamicEnergy. Each run supplies read AND write results. The 7nm/ReadLatency smoke counts as one of the eight. Other capacities are historical references only; no P0–P3 campaign, model source change, GPU validation or Rubin prediction is run.
Only capacity changes relative to matching Phase 2-A inputs: integer `-Capacity (KB): 512`=524288 bytes. Controls remain 16-way/Normal/LOP/300K/H-tree/ForceBankA=4x4/internal sensing/pruning/latency buffer and original node cells/wires. See [gate](feasibility_gate.md) and [config diffs](../provenance/cases.json).

## Complete 512KiB results (summary energy precision)

| Node | Objective | Status | Read pJ/access | Write pJ/access | Read pJ/bit | Write pJ/bit | Hit ns | Leakage mW | Area mm² | Solutions | Raw |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 14 | ReadLatency | FINISHED | 79.000 | 57.000 | 0.30859375 | 0.22265625 | 0.755 | 0.111 | 0.509 | 15 | [log](../../NSCache_Phase2C/logs/L2_14nm_512KiB_ReadLatency/20261112T105750.553245Z/stdout.log) |
| 14 | ReadDynamicEnergy | FINISHED | 73.000 | 51.000 | 0.28515625 | 0.19921875 | 1.433 | 0.101 | 0.488 | 15 | [log](../../NSCache_Phase2C/logs/L2_14nm_512KiB_ReadDynamicEnergy/20261112T105750.552918Z/stdout.log) |
| 7 | ReadLatency | FINISHED | 37.000 | 25.000 | 0.14453125 | 0.09765625 | 0.566 | 0.142 | 0.177 | 72 | [log](../../NSCache_Phase2C/logs/L2_7nm_512KiB_ReadLatency/20261112T105641.319820Z/stdout.log) |
| 7 | ReadDynamicEnergy | FINISHED | 34.000 | 26.000 | 0.1328125 | 0.1015625 | 0.806 | 0.124 | 0.157 | 72 | [log](../../NSCache_Phase2C/logs/L2_7nm_512KiB_ReadDynamicEnergy/20261112T105820.187352Z/stdout.log) |
| 5 | ReadLatency | FINISHED | 36.000 | 24.000 | 0.140625 | 0.09375 | 1.490 | 0.139 | 0.170 | 72 | [log](../../NSCache_Phase2C/logs/L2_5nm_512KiB_ReadLatency/20261112T105820.388773Z/stdout.log) |
| 5 | ReadDynamicEnergy | FINISHED | 31.000 | 24.000 | 0.12109375 | 0.09375 | 2.494 | 0.118 | 0.130 | 72 | [log](../../NSCache_Phase2C/logs/L2_5nm_512KiB_ReadDynamicEnergy/20261112T105848.214114Z/stdout.log) |
| 3 | ReadLatency | FINISHED | 35.000 | 25.000 | 0.13671875 | 0.09765625 | 1.432 | 0.148 | 0.127 | 72 | [log](../../NSCache_Phase2C/logs/L2_3nm_512KiB_ReadLatency/20261112T105850.416684Z/stdout.log) |
| 3 | ReadDynamicEnergy | FINISHED | 27.000 | 21.000 | 0.10546875 | 0.08203125 | 2.413 | 0.123 | 0.106 | 72 | [log](../../NSCache_Phase2C/logs/L2_3nm_512KiB_ReadDynamicEnergy/20261112T105915.840025Z/stdout.log) |

`E_effective,bit=E_model_access/256` normalizes the complete modeled 32B line access, not a physical SRAM bit or GPU sector transaction. [Complete summary/fine fields and metadata](../results/slice_512kib_energy.csv). Leakage is power and is never added to dynamic energy/access.

## 512KiB node sensitivity SF

`SF_E(a→b)=E(512KiB,b)/E(512KiB,a)`. Same capacity/objective/operation/precision. SF is dimensionless. [CSV](../results/slice_512kib_scaling.csv) contains both summary and fine bank-sum operands, ratios and formulas separately.

| Objective | Operation | Transition | Summary SF | Fine bank-sum SF |
|---|---|---|---:|---:|
| ReadLatency | read | 14→7 | 0.468354 | 0.471912 |
| ReadLatency | read | 7→5 | 0.972973 | 0.957211 |
| ReadLatency | read | 5→3 | 0.972222 | 0.977384 |
| ReadLatency | write | 14→7 | 0.438596 | 0.432929 |
| ReadLatency | write | 7→5 | 0.960000 | 0.984764 |
| ReadLatency | write | 5→3 | 1.041667 | 1.021414 |
| ReadDynamicEnergy | read | 14→7 | 0.465753 | 0.468720 |
| ReadDynamicEnergy | read | 7→5 | 0.911765 | 0.915535 |
| ReadDynamicEnergy | read | 5→3 | 0.870968 | 0.869236 |
| ReadDynamicEnergy | write | 14→7 | 0.509804 | 0.509008 |
| ReadDynamicEnergy | write | 7→5 | 0.923077 | 0.917259 |
| ReadDynamicEnergy | write | 5→3 | 0.875000 | 0.872675 |

**SF reflects node/cell/Vdd/wire/optimizer-selected organization, not pure process scaling.** Source Vdd is 0.8/0.7/0.7/0.7V at 14/7/5/3nm; cell read-voltage is a separate quantity. These values are inherited source parameters, not measured GPU voltages.

## Capacity trajectory (summary read/write pJ per model access)

Historical records are hash-verified, labeled historical_verified and never rerun. Missing 8MiB at 14/3nm remains missing. [Capacity CSV](../results/capacity_comparison.csv), [512KiB/1MiB ratios with both precisions](../results/slice_vs_1mib_ratios.csv).

| Node | Objective | 512KiB new R/W | 1MiB historical R/W | 8MiB historical R/W | 32MiB historical R/W |
|---:|---|---:|---:|---:|---:|
| 14 | ReadLatency | 79.000 / 57.000 | 103.000 / 81.000 | MISSING_NOT_RUN | 490.000 / 365.000 |
| 14 | ReadDynamicEnergy | 73.000 / 51.000 | 98.000 / 76.000 | MISSING_NOT_RUN | 460.000 / 337.000 |
| 7 | ReadLatency | 37.000 / 25.000 | 46.000 / 33.000 | 117.000 / 78.000 | 228.000 / 152.000 |
| 7 | ReadDynamicEnergy | 34.000 / 26.000 | 43.000 / 30.000 | 113.000 / 91.000 | 215.000 / 141.000 |
| 5 | ReadLatency | 36.000 / 24.000 | 44.000 / 32.000 | 107.000 / 71.000 | 207.000 / 138.000 |
| 5 | ReadDynamicEnergy | 31.000 / 24.000 | 39.000 / 28.000 | 103.000 / 83.000 | 195.000 / 128.000 |
| 3 | ReadLatency | 35.000 / 25.000 | 37.000 / 27.000 | MISSING_NOT_RUN | 186.000 / 124.000 |
| 3 | ReadDynamicEnergy | 27.000 / 21.000 | 35.000 / 24.000 | MISSING_NOT_RUN | 177.000 / 115.000 |

| Node | Objective | Operation | Summary E512/E1MiB | Fine bank-sum E512/E1MiB |
|---:|---|---|---:|---:|
| 14 | ReadLatency | read | 0.766990 | 0.768126 |
| 14 | ReadLatency | write | 0.703704 | 0.701505 |
| 14 | ReadDynamicEnergy | read | 0.744898 | 0.744701 |
| 14 | ReadDynamicEnergy | write | 0.671053 | 0.670994 |
| 7 | ReadLatency | read | 0.804348 | 0.813710 |
| 7 | ReadLatency | write | 0.757576 | 0.739966 |
| 7 | ReadDynamicEnergy | read | 0.790698 | 0.797111 |
| 7 | ReadDynamicEnergy | write | 0.866667 | 0.854913 |
| 5 | ReadLatency | read | 0.818182 | 0.823125 |
| 5 | ReadLatency | write | 0.750000 | 0.757193 |
| 5 | ReadDynamicEnergy | read | 0.794872 | 0.798430 |
| 5 | ReadDynamicEnergy | write | 0.857143 | 0.856067 |
| 3 | ReadLatency | read | 0.945946 | 0.934040 |
| 3 | ReadLatency | write | 0.925926 | 0.904131 |
| 3 | ReadDynamicEnergy | read | 0.771429 | 0.791297 |
| 3 | ReadDynamicEnergy | write | 0.875000 | 0.852041 |

Summary uses 0.001nJ=1pJ output resolution. Fine bank sums use the separately printed data/tag precision. Each precision is normalized and divided like-for-like; no ratio mixes rounded and fine operands. Small SF differences can be rounding-sensitive. Capacity does not imply linear dynamic energy or identical organization.

## Data / Tag / Routing and selected organization

[Breakdown CSV](../results/energy_breakdown.csv) uses data+tag bank totals with routing as an included subset. Full activation, subarray/mat, mux, wire and buffer details are retained in [organization JSON](../results/organization_comparison.json). Missing detail is not estimated. Nonrouting residual is not cell-only, and nested mat/subarray values are not added again.

| Node | Objective | Read Data/Tag/Routing pJ | Write Data/Tag/Routing pJ | Data bank/subarray/mat | Tag bank/subarray/mat |
|---:|---|---:|---:|---|---|
| 14 | ReadLatency | 73.335/5.951/51.500 | 52.431/4.419/51.500 | 4 x 4/2 x 2/512 Rows x 128 Columns | 16 x 1/2 x 2/64 Rows x 144 Columns |
| 14 | ReadDynamicEnergy | 70.473/2.752/45.518 | 49.723/1.398/45.518 | 4 x 4/2 x 1/512 Rows x 256 Columns | 8 x 1/2 x 2/32 Rows x 560 Columns |
| 7 | ReadLatency | 35.179/2.237/21.426 | 23.157/1.455/21.426 | 4 x 4/2 x 2/512 Rows x 128 Columns | 16 x 1/2 x 2/32 Rows x 288 Columns |
| 7 | ReadDynamicEnergy | 32.681/1.641/23.028 | 25.136/0.885/23.028 | 4 x 4/2 x 1/256 Rows x 512 Columns | 8 x 1/2 x 2/32 Rows x 560 Columns |
| 5 | ReadLatency | 32.792/3.023/21.594 | 21.856/2.381/21.594 | 4 x 4/2 x 2/512 Rows x 128 Columns | 64 x 1/2 x 2/8 Rows x 288 Columns |
| 5 | ReadDynamicEnergy | 30.010/1.413/21.373 | 23.124/0.744/21.373 | 4 x 4/2 x 1/256 Rows x 512 Columns | 8 x 1/2 x 2/32 Rows x 560 Columns |
| 3 | ReadLatency | 27.892/7.113/22.414 | 18.259/6.497/22.414 | 4 x 4/2 x 2/512 Rows x 128 Columns | 64 x 4/2 x 2/8 Rows x 80 Columns |
| 3 | ReadDynamicEnergy | 26.087/1.227/18.587 | 20.157/0.672/18.587 | 4 x 4/2 x 1/256 Rows x 512 Columns | 8 x 1/2 x 2/32 Rows x 560 Columns |

### Optimization / capacity trade-offs

| Node | Read energy reduction energy-objective vs latency % | Hit latency ns: latency→energy objective | Area mm²: latency→energy objective | Data mat latency→energy | Tag bank latency→energy |
|---:|---:|---:|---:|---|---|
| 14 | 7.595 | 0.755→1.433 | 0.509→0.488 | 512 Rows x 128 Columns→512 Rows x 256 Columns | 16 x 1→8 x 1 |
| 7 | 8.108 | 0.566→0.806 | 0.177→0.157 | 512 Rows x 128 Columns→256 Rows x 512 Columns | 16 x 1→8 x 1 |
| 5 | 13.889 | 1.490→2.494 | 0.170→0.130 | 512 Rows x 128 Columns→256 Rows x 512 Columns | 64 x 1→8 x 1 |
| 3 | 22.857 | 1.432→2.413 | 0.127→0.106 | 512 Rows x 128 Columns→256 Rows x 512 Columns | 64 x 4→8 x 1 |

### Observed non-monotonic write behavior

ReadDynamicEnergy optimizes read energy, not write energy. At 7nm/512KiB the energy objective prints 26pJ write vs 25pJ under the latency objective; fine bank sums also increase (26.021 vs 24.612pJ). Thus this observation is not solely a 1pJ-summary rounding artifact. The selected data mat changes from 512×128 to 256×512 and tag bank 16×1 to 8×1; printed routing changes too. These are correlated optimizer choices, not isolated causal attribution.
Under ReadLatency, 5→3nm write summary is 24→25pJ (SF=1.041667), while fine bank sum is 24.237→24.756pJ (SF≈1.021414). The increase persists in fine output but its magnitude is resolution-sensitive. Tag geometry changes (including the selected tag bank), and cell/Vdd/wire models are node-specific. No fitting or alternate cell was used to remove the increase.

Observed organizations and trade-offs above show independent optimizer choices; they are not controlled topology/Vdd interventions. Compare historical rows in the JSON before attributing capacity differences solely to SRAM bit count. Increased tag count, activation and H-tree/decoder/mux load can contribute, but their isolated causal shares are unverified.

## A100-oriented size rationale and validity

The task cites NVIDIA A100 Architecture Whitepaper p.35: two high-level partitions, 40 slices each, nominal 512KB per slice. In this study binary arithmetic is explicit: 80×512KiB=40MiB. [Official whitepaper](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf). Direct retrieval returned HTTP 403, so the source text was not independently reread here; the supplied page-specific citation is the evidence premise, not a new hardware verification.
This motivates a **512KiB NS-Cache single-cache proxy / model slice candidate**, not circuit, port-count, 16-way associativity, banking, metadata/sector or energy-boundary equivalence. Never multiply single-access dynamic energy by 80 to claim GPU energy. Replicated leakage/area and shared costs are outside scope.

| Category | Evidence/status | Allowed interpretation |
|---|---|---|
| Direct run | Eight planned configs; actual completion/status and raw logs above | Current model output only |
| Derived arithmetic | pJ/bit, matched-precision SF and capacity ratios | Algebra on printed model values |
| Externally documented A100 hierarchy | Task-supplied whitepaper p.35 citation; direct retrieval 403 | Nominal-size rationale; local source reread pending |
| Physical equivalence | Unvalidated | No GPU slice/sector/port/energy match claimed |
| Deferred work | Explicitly not executed | Separate future P0–P3 tasks only |

## Limitations and explicitly deferred work

No extra capacity sweeps or new non-power-of-two model extension; no V100/H100 topology reconstruction; no 128B-line/32B-sector implementation or confidential coefficient comparison; no fixed-organization/Vdd campaigns; no hardware validation or Rubin projection. Official-source reread and PR API operations remain subject to documented network restrictions.
