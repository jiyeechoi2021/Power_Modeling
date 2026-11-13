# 7nm/3nm 1GiB feasibility and LLMET Table 2 comparison

## Method and evidence

Verified Phase 2-C descendant a8d07dfc79266d5a33fb32f71ed20f30fe492d96 is the study base. Existing 3nm/128MiB and 7nm/32MiB baselines, both ReadLatency and ReadDynamicEnergy, are hash-verified rather than rerun. New inputs change Capacity only. Both 3nm objectives are attempted before either 7nm objective. Source, cell, objectives, 256bit WordWidth, 16-way, 300K, Normal cache, LOP, ForceBankA=4x4, H-tree, internal sensing, pruning, wires/buffer settings and one die are preserved. [Exact diffs/hashes](../provenance/cases.json).
The source revision is 2fdcbf093f806bc9a28964aca8402c42738d58e5; all 54 source/Makefile hashes are checked. InputParameter.cpp:324–327 parses the MB field in binary units; capacity is int64_t (InputParameter.h:45); main.cpp:434,451,506 and macros.h:138–180 retain original tag/data capacity verification. 1024MiB = 1073741824 bytes. This is an explicitly documented approximation to paper 1GB until its convention is confirmed, not proof of decimal/binary equivalence.
Source-derived nominal Vdd is 0.7V for both nodes. Cell read voltages differ (7nm 0.264V, 3nm 0.248V); SRAM cell area/aspect and transistor/wire parameters also differ. These are cache-model outputs, not isolated SRAM bitcell or GPU hardware measurements. Original author configs/output and operation/aggregation/normalization are unavailable. The task-reported public reference values are 7nm 2.780 and 3nm 2.420pJ/bit; their ratio is 0.8705035971223021582733812950. Neither reference is used to select execution parameters.

## Execution and full results

Bounded runs use at most two children, 1800s wall timeout per case, retained stdout/stderr/exit/timestamps/CPU/max-RSS/environment and config/cell/binary hashes. No hard memory cap is claimed. Failed/timeout cases retain missing energy; completion requires exit 0, Finished!, parseable metrics and independent selected-capacity arithmetic.

| Node | MiB | Objective | Evidence/status | Read pJ | Write pJ | Read pJ/bit | Write pJ/bit | Hit ns | Write ns | Leakage mW | Area mm² | Solutions |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 | 128 | ReadLatency | verified_historical_raw/FINISHED | 369.000 | 246.000 | 1.44140625 | 0.9609375 | 44.903 | 38.089 | 28.956 | 24.061 | 1440 |
| 3 | 1024 | ReadLatency | primary_1gib/FINISHED | 1805.000 | 806.000 | 7.05078125 | 3.1484375 | 317.792 | 254.945 | 225.752 | 187.375 | 1287 |
| 3 | 128 | ReadDynamicEnergy | verified_historical_raw/FINISHED | 349.000 | 228.000 | 1.36328125 | 0.890625 | 85.464 | 68.747 | 28.700 | 23.911 | 1440 |
| 3 | 1024 | ReadDynamicEnergy | primary_1gib/FINISHED | 1175.000 | 692.000 | 4.58984375 | 2.703125 | 317.794 | 254.947 | 225.710 | 187.524 | 1287 |
| 7 | 32 | ReadLatency | verified_historical_raw/FINISHED | 228.000 | 152.000 | 0.890625 | 0.59375 | 5.830 | 4.386 | 7.484 | 8.804 | 873 |
| 7 | 1024 | ReadLatency | primary_1gib/FINISHED | 2241.000 | 980.000 | 8.75390625 | 3.828125 | 101.704 | 74.422 | 227.436 | 264.144 | 1287 |
| 7 | 32 | ReadDynamicEnergy | verified_historical_raw/FINISHED | 215.000 | 141.000 | 0.83984375 | 0.55078125 | 8.839 | 6.414 | 7.369 | 8.720 | 873 |
| 7 | 1024 | ReadDynamicEnergy | primary_1gib/FINISHED | 1426.000 | 843.000 | 5.5703125 | 3.29296875 | 119.902 | 83.092 | 227.436 | 264.632 | 1287 |

Cache summary energy is printed to 0.001nJ (1pJ); the printed Data+Tag bank sum is retained separately with per-bank resolution and combined rounding bounds; large bank energies printed in nJ need not be finer than the summary. E_effective_bit = E_access/256. SF = E_3nm/E_7nm at the same capacity/objective/operation/precision. No mixed-precision ratios. [Energy and log/config links](../results/energy_results.csv), [capacity sensitivities](../results/capacity_comparison.csv).

## Cross-node scaling and paper-reference comparison

| Objective | Operation | Precision | 3nm/7nm model SF | Reported paper ratio | Difference |
|---|---|---|---:|---:|---:|
| ReadLatency | read | summary | 0.80544400 | 0.87050360 | -0.06505960 |
| ReadLatency | read | bank_sum | 0.80535274 | 0.87050360 | -0.06515086 |
| ReadLatency | write | summary | 0.82244898 | 0.87050360 | -0.04805462 |
| ReadLatency | write | bank_sum | 0.82244031 | 0.87050360 | -0.04806329 |
| ReadDynamicEnergy | read | summary | 0.82398317 | 0.87050360 | -0.04652043 |
| ReadDynamicEnergy | read | bank_sum | 0.82378170 | 0.87050360 | -0.04672190 |
| ReadDynamicEnergy | write | summary | 0.82087782 | 0.87050360 | -0.04962578 |
| ReadDynamicEnergy | write | bank_sum | 0.82127809 | 0.87050360 | -0.04922551 |

| Node | Objective | Read model pJ/bit | Write model pJ/bit | Reported reference pJ/bit | Read/reference | Write/reference |
|---:|---|---:|---:|---:|---:|---:|
| 3 | ReadLatency | 7.05078125 | 3.14843750 | 2.420 | 2.913546 | 1.301007 |
| 3 | ReadDynamicEnergy | 4.58984375 | 2.70312500 | 2.420 | 1.896630 | 1.116994 |
| 7 | ReadLatency | 8.75390625 | 3.82812500 | 2.780 | 3.148887 | 1.377023 |
| 7 | ReadDynamicEnergy | 5.57031250 | 3.29296875 | 2.780 | 2.003710 | 1.184521 |

[Per-node pJ/bit comparison](../results/llmet_reference_comparison.csv) reports both read and write without assuming the reference operation. [Cross-node CSV](../results/cross_node_sf.csv) retains formulas and both raw-log/config operands. A numeric match does not validate LLMET. The model boundary includes data/tag/routing and a 32B model line; the paper boundary, access width and normalization are unconfirmed. Cross-node changes include cell/wires/optimizer, even if nominal Vdd matches; do not label these pure process scaling.

## Organization and energy structure

| Node | MiB | Objective | Data bank/subarray/mat | Tag bank/subarray/mat | Read Data/Tag/Routing pJ | Write Data/Tag/Routing pJ |
|---:|---:|---|---|---|---:|---:|
| 3 | 128 | ReadLatency | 4 x 4/2 x 2/8192 Rows x 2048 Columns | 64 x 1/2 x 2/128 Rows x 3456 Columns | 354.758/13.807/242.597 | 237.196/9.260/242.597 |
| 3 | 1024 | ReadLatency | 4 x 4/2 x 2/16384 Rows x 8192 Columns | 64 x 1/2 x 2/512 Rows x 6144 Columns | 1656.000/148.843/790.111 | 722.165/83.940/790.111 |
| 3 | 128 | ReadDynamicEnergy | 4 x 4/2 x 1/8192 Rows x 4096 Columns | 64 x 1/2 x 2/128 Rows x 3456 Columns | 341.991/6.881/224.318 | 224.437/3.629/224.318 |
| 3 | 1024 | ReadDynamicEnergy | 4 x 4/2 x 2/16384 Rows x 8192 Columns | 64 x 1/2 x 2/256 Rows x 12288 Columns | 1151.000/23.730/683.843 | 684.917/7.234/683.843 |
| 7 | 32 | ReadLatency | 4 x 4/2 x 2/4096 Rows x 1024 Columns | 32 x 1/2 x 2/128 Rows x 1856 Columns | 218.528/9.256/148.087 | 145.921/6.031/148.087 |
| 7 | 1024 | ReadLatency | 4 x 4/2 x 2/16384 Rows x 8192 Columns | 32 x 1/2 x 2/1024 Rows x 6144 Columns | 2006.000/235.059/959.188 | 879.293/100.845/959.188 |
| 7 | 32 | ReadDynamicEnergy | 4 x 4/2 x 1/4096 Rows x 2048 Columns | 64 x 1/2 x 2/64 Rows x 1856 Columns | 210.426/5.069/137.127 | 137.839/3.156/137.127 |
| 7 | 1024 | ReadDynamicEnergy | 4 x 4/2 x 2/16384 Rows x 8192 Columns | 64 x 1/2 x 2/256 Rows x 12288 Columns | 1396.000/30.021/832.003 | 833.597/9.176/832.003 |

Data+Tag bank sums already contain H-tree routing. Routing is a subset, never an extra addend; nested subarray/mat/peripheral outputs overlap. [Breakdown](../results/energy_breakdown.csv) and [full organization/metadata](../results/organization_and_metadata.json) preserve printed hierarchy and timing. Large selected mats establish logical model feasibility only; physical accuracy is unvalidated. Changes in selected internal geometry occur through the unchanged optimizer, not manually altered constraints. Baseline-to-target capacity multipliers differ (3nm 8×, 7nm 32×), so their growth ratios are not isolated cross-node effects.

Observed capacity growth (summary precision):
- 3nm ReadLatency: 128→1024MiB; Read energy 4.8916×, Write 3.2764×.
- 3nm ReadDynamicEnergy: 128→1024MiB; Read energy 3.3668×, Write 3.0351×.
- 7nm ReadLatency: 32→1024MiB; Read energy 9.8289×, Write 6.4474×.
- 7nm ReadDynamicEnergy: 32→1024MiB; Read energy 6.6326×, Write 5.9787×.

At 1GiB the selected data geometry is 4×4 banks, 2×2 subarrays and 16384×8192-bit mats in all four cases; matching these dimensions alone does not imply matching active circuitry or optimizer choices. The tag geometry and full activation/MUX/wire/buffer details differ. Observed read energies change substantially with objective despite almost identical 3nm hit latency; the printed Data and Tag totals both change. Reoptimization and routing/peripheral choices are plausible explanations, not experimentally isolated causes. All model values remain above the task-reported same-node reference in both operations. The SF comparison is therefore distinct from reproducing absolute paper energies.

## Failure evidence, limitations and next steps

- L2_3nm_1024MiB_ReadLatency: FINISHED; elapsed 173.98652791999984s; max RSS 15148KiB; exit 0; [stdout](../../NSCache_1GiB_Feasibility/logs/L2_3nm_1024MiB_ReadLatency/20261113T065413.783440Z/stdout.log); [metadata](../../NSCache_1GiB_Feasibility/logs/L2_3nm_1024MiB_ReadLatency/20261113T065413.783440Z/metadata.json).
- L2_3nm_1024MiB_ReadDynamicEnergy: FINISHED; elapsed 175.78864075699994s; max RSS 15148KiB; exit 0; [stdout](../../NSCache_1GiB_Feasibility/logs/L2_3nm_1024MiB_ReadDynamicEnergy/20261113T065413.783268Z/stdout.log); [metadata](../../NSCache_1GiB_Feasibility/logs/L2_3nm_1024MiB_ReadDynamicEnergy/20261113T065413.783268Z/metadata.json).
- L2_7nm_1024MiB_ReadLatency: FINISHED; elapsed 169.9408169960002s; max RSS 15132KiB; exit 0; [stdout](../../NSCache_1GiB_Feasibility/logs/L2_7nm_1024MiB_ReadLatency/20261113T065746.886853Z/stdout.log); [metadata](../../NSCache_1GiB_Feasibility/logs/L2_7nm_1024MiB_ReadLatency/20261113T065746.886853Z/metadata.json).
- L2_7nm_1024MiB_ReadDynamicEnergy: FINISHED; elapsed 169.9395963410002s; max RSS 15132KiB; exit 0; [stdout](../../NSCache_1GiB_Feasibility/logs/L2_7nm_1024MiB_ReadDynamicEnergy/20261113T065746.889629Z/stdout.log); [metadata](../../NSCache_1GiB_Feasibility/logs/L2_7nm_1024MiB_ReadDynamicEnergy/20261113T065746.889629Z/metadata.json).

All four primary cases completed; no 512/256MiB diagnostic is justified or executed. No source patch, bank/geometry relaxation or capacity verification bypass was needed.

Recommended next experiment: obtain the author-original config/cell/source/raw output and confirm operation, denominator, cache-vs-SRAM boundary, GB convention and access width before an exact replay. Any structural diagnostic requires a separately described discrepancy and experiment. Do not search arbitrary parameters to fit reference values. No actual GPU equivalence, hardware validation or private GPU data comparison is established. Earlier studies/main remain unchanged; no merges.
