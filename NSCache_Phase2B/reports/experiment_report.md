# Phase 2-B: L2 capacity and organization

## Scope and feasibility

All energies are exploratory NS-Cache model results. Model nodes 14/7/5nm are proxies for V100/A100/H100 process families, not foundry-equivalent nodes. No private GPU coefficients were used. See [gate](feasibility_gate.md) and [assumptions](model_assumptions_and_limits.md). Native non-power-of-two capacity jobs fail an unmodified model capacity assertion; failed cases have no energy values. No source patches, rounded capacities or relaxed constraints are substituted.
The uploaded archive is preserved separately; missing metadata and differing binary provenance require fresh 32MiB runs. Existing 1MiB runs are verified from Phase 2-A raw evidence. Each successful row exposes summary and fine bank-sum precision separately.
Precision audit: the uploaded derived CSV ratios match a fine 32MiB numerator divided by a rounded 1MiB denominator at its displayed precision. Those ratios are not reused. [Audit](../results/uploaded_csv_precision_audit.csv), [consistent summary and bank-sum capacity ratios](../results/capacity_sensitivity.csv).

## Native coverage and 1/32/6/40/50MiB side-by-side

| MiB | Node | Objective | Origin/status | Read pJ/access | Write pJ/access | Read pJ/bit | Write pJ/bit | Latency ns | Area mm² | Leakage mW | Raw |
|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 3 | ReadDynamicEnergy | verified_phase2a/VALID | 35.000 | 24.000 | 0.13671875 | 0.09375 | 3.387 | 0.209 | 0.244 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_3nm_ReadEnergy/20261111T095837.427048Z/stdout.log) |
| 1 | 3 | ReadLatency | verified_phase2a/VALID | 37.000 | 27.000 | 0.14453125 | 0.10546875 | 2.072 | 0.217 | 0.257 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_3nm/20261111T095836.172778Z/stdout.log) |
| 1 | 5 | ReadDynamicEnergy | verified_phase2a/VALID | 39.000 | 28.000 | 0.15234375 | 0.109375 | 3.598 | 0.255 | 0.234 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_5nm_ReadEnergy/20261111T095916.961744Z/stdout.log) |
| 1 | 5 | ReadLatency | verified_phase2a/VALID | 44.000 | 32.000 | 0.171875 | 0.125 | 2.140 | 0.276 | 0.246 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_5nm/20261111T095916.559895Z/stdout.log) |
| 1 | 7 | ReadDynamicEnergy | verified_phase2a/VALID | 43.000 | 30.000 | 0.16796875 | 0.1171875 | 1.387 | 0.305 | 0.246 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_7nm_ReadEnergy/20261111T095958.504262Z/stdout.log) |
| 1 | 7 | ReadLatency | verified_phase2a/VALID | 46.000 | 33.000 | 0.1796875 | 0.12890625 | 0.770 | 0.317 | 0.258 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_7nm/20261111T095955.392894Z/stdout.log) |
| 1 | 14 | ReadDynamicEnergy | verified_phase2a/VALID | 98.000 | 76.000 | 0.3828125 | 0.296875 | 1.850 | 0.922 | 0.191 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_14nm_ReadEnergy/20261111T095757.832618Z/stdout.log) |
| 1 | 14 | ReadLatency | verified_phase2a/VALID | 103.000 | 81.000 | 0.40234375 | 0.31640625 | 1.103 | 0.947 | 0.201 | [stdout](../../NSCache_Phase2A/logs/phase2_256bit/L2_14nm/20261111T095755.830625Z/stdout.log) |
| 6 | 7 | ReadDynamicEnergy | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_7nm_6MiB_ReadDynamicEnergy/20261112T044241.152645Z/stdout.log) |
| 6 | 7 | ReadLatency | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_7nm_6MiB_ReadLatency/20261112T044241.152466Z/stdout.log) |
| 6 | 14 | ReadDynamicEnergy | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_14nm_6MiB_ReadDynamicEnergy/20261112T044241.775949Z/stdout.log) |
| 6 | 14 | ReadLatency | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_14nm_6MiB_ReadLatency/20261112T044114.025257Z/stdout.log) |
| 32 | 3 | ReadDynamicEnergy | new/VALID | 177.000 | 115.000 | 0.69140625 | 0.44921875 | 25.540 | 6.119 | 7.314 | [stdout](../../NSCache_Phase2B/logs/L2_3nm_32MiB_ReadDynamicEnergy/20261112T044142.771354Z/stdout.log) |
| 32 | 3 | ReadLatency | new/VALID | 186.000 | 124.000 | 0.7265625 | 0.484375 | 14.773 | 6.194 | 7.441 | [stdout](../../NSCache_Phase2B/logs/L2_3nm_32MiB_ReadLatency/20261112T044142.771062Z/stdout.log) |
| 32 | 5 | ReadDynamicEnergy | new/VALID | 195.000 | 128.000 | 0.76171875 | 0.500 | 24.425 | 7.134 | 6.996 | [stdout](../../NSCache_Phase2B/logs/L2_5nm_32MiB_ReadDynamicEnergy/20261112T044337.887434Z/stdout.log) |
| 32 | 5 | ReadLatency | new/VALID | 207.000 | 138.000 | 0.80859375 | 0.5390625 | 13.609 | 7.331 | 7.118 | [stdout](../../NSCache_Phase2B/logs/L2_5nm_32MiB_ReadLatency/20261112T044324.671981Z/stdout.log) |
| 32 | 7 | ReadDynamicEnergy | new/VALID | 215.000 | 141.000 | 0.83984375 | 0.55078125 | 8.839 | 8.720 | 7.369 | [stdout](../../NSCache_Phase2B/logs/L2_7nm_32MiB_ReadDynamicEnergy/20261112T044527.586277Z/stdout.log) |
| 32 | 7 | ReadLatency | new/VALID | 228.000 | 152.000 | 0.890625 | 0.59375 | 5.830 | 8.804 | 7.484 | [stdout](../../NSCache_Phase2B/logs/L2_7nm_32MiB_ReadLatency/20261112T044511.566974Z/stdout.log) |
| 32 | 14 | ReadDynamicEnergy | new/VALID | 460.000 | 337.000 | 1.796875 | 1.31640625 | 11.279 | 27.155 | 5.703 | [stdout](../../NSCache_Phase2B/logs/L2_14nm_32MiB_ReadDynamicEnergy/20261112T044717.886647Z/stdout.log) |
| 32 | 14 | ReadLatency | new/VALID | 490.000 | 365.000 | 1.9140625 | 1.42578125 | 6.934 | 26.812 | 5.793 | [stdout](../../NSCache_Phase2B/logs/L2_14nm_32MiB_ReadLatency/20261112T044653.064329Z/stdout.log) |
| 40 | 5 | ReadDynamicEnergy | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_5nm_40MiB_ReadDynamicEnergy/20261112T044240.946918Z/stdout.log) |
| 40 | 5 | ReadLatency | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_5nm_40MiB_ReadLatency/20261112T044240.740736Z/stdout.log) |
| 40 | 7 | ReadDynamicEnergy | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_7nm_40MiB_ReadDynamicEnergy/20261112T044241.359038Z/stdout.log) |
| 40 | 7 | ReadLatency | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_7nm_40MiB_ReadLatency/20261112T044113.820088Z/stdout.log) |
| 40 | 14 | ReadDynamicEnergy | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_14nm_40MiB_ReadDynamicEnergy/20261112T044241.980957Z/stdout.log) |
| 40 | 14 | ReadLatency | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_14nm_40MiB_ReadLatency/20261112T044241.978218Z/stdout.log) |
| 50 | 5 | ReadDynamicEnergy | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_5nm_50MiB_ReadDynamicEnergy/20261112T044240.947586Z/stdout.log) |
| 50 | 5 | ReadLatency | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_5nm_50MiB_ReadLatency/20261112T044113.612405Z/stdout.log) |
| 50 | 7 | ReadDynamicEnergy | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_7nm_50MiB_ReadDynamicEnergy/20261112T044241.564571Z/stdout.log) |
| 50 | 7 | ReadLatency | new/UNSUPPORTED_GEOMETRY | — | — | — | — | — | — | — | [stdout](../../NSCache_Phase2B/logs/L2_7nm_50MiB_ReadLatency/20261112T044241.366015Z/stdout.log) |

## Fixed-capacity SF (summary precision)

| MiB | Objective | Operation | Node transition | SF | Reduction % |
|---:|---|---|---|---:|---:|
| 1 | ReadLatency | read | 14→7 | 0.446602 | 55.340 |
| 1 | ReadLatency | read | 7→5 | 0.956522 | 4.348 |
| 1 | ReadLatency | read | 5→3 | 0.840909 | 15.909 |
| 1 | ReadLatency | write | 14→7 | 0.407407 | 59.259 |
| 1 | ReadLatency | write | 7→5 | 0.969697 | 3.030 |
| 1 | ReadLatency | write | 5→3 | 0.843750 | 15.625 |
| 1 | ReadDynamicEnergy | read | 14→7 | 0.438776 | 56.122 |
| 1 | ReadDynamicEnergy | read | 7→5 | 0.906977 | 9.302 |
| 1 | ReadDynamicEnergy | read | 5→3 | 0.897436 | 10.256 |
| 1 | ReadDynamicEnergy | write | 14→7 | 0.394737 | 60.526 |
| 1 | ReadDynamicEnergy | write | 7→5 | 0.933333 | 6.667 |
| 1 | ReadDynamicEnergy | write | 5→3 | 0.857143 | 14.286 |
| 32 | ReadLatency | read | 14→7 | 0.465306 | 53.469 |
| 32 | ReadLatency | read | 7→5 | 0.907895 | 9.211 |
| 32 | ReadLatency | read | 5→3 | 0.898551 | 10.145 |
| 32 | ReadLatency | write | 14→7 | 0.416438 | 58.356 |
| 32 | ReadLatency | write | 7→5 | 0.907895 | 9.211 |
| 32 | ReadLatency | write | 5→3 | 0.898551 | 10.145 |
| 32 | ReadDynamicEnergy | read | 14→7 | 0.467391 | 53.261 |
| 32 | ReadDynamicEnergy | read | 7→5 | 0.906977 | 9.302 |
| 32 | ReadDynamicEnergy | read | 5→3 | 0.907692 | 9.231 |
| 32 | ReadDynamicEnergy | write | 14→7 | 0.418398 | 58.160 |
| 32 | ReadDynamicEnergy | write | 7→5 | 0.907801 | 9.220 |
| 32 | ReadDynamicEnergy | write | 5→3 | 0.898438 | 10.156 |

SF_C=E(C,b)/E(C,a) always uses identical capacity/objective/precision. It is not pure process scaling: Vdd, cells, wires and independently chosen organization change. [CSV with raw endpoints and substitutions](../results/fixed_capacity_sf.csv).

## Capacity effect: 32MiB / 1MiB

| Node | Objective | Read ratio | Write ratio | Read pJ/bit 1→32 | Write pJ/bit 1→32 |
|---:|---|---:|---:|---:|---:|
| 14 | ReadLatency | 4.757282 | 4.506173 | 0.40234375→1.9140625 | 0.31640625→1.42578125 |
| 14 | ReadDynamicEnergy | 4.693878 | 4.434211 | 0.3828125→1.796875 | 0.296875→1.31640625 |
| 7 | ReadLatency | 4.956522 | 4.606061 | 0.1796875→0.890625 | 0.12890625→0.59375 |
| 7 | ReadDynamicEnergy | 5.000000 | 4.700000 | 0.16796875→0.83984375 | 0.1171875→0.55078125 |
| 5 | ReadLatency | 4.704545 | 4.312500 | 0.171875→0.80859375 | 0.125→0.5390625 |
| 5 | ReadDynamicEnergy | 5.000000 | 4.571429 | 0.15234375→0.76171875 | 0.109375→0.500 |
| 3 | ReadLatency | 5.027027 | 4.592593 | 0.14453125→0.7265625 | 0.10546875→0.484375 |
| 3 | ReadDynamicEnergy | 5.057143 | 4.791667 | 0.13671875→0.69140625 | 0.09375→0.44921875 |

### Observed bank components and organization

| Node | Objective | Operation | Data bank pJ 1→32 | Tag bank pJ 1→32 | Routing subset pJ 1→32 |
|---:|---|---|---:|---:|---:|
| 14 | ReadLatency | read | 98.371→467.750 | 4.849→21.898 | 75.538→359.044 |
| 14 | ReadLatency | write | 77.621→348.420 | 3.419→16.746 | 75.538→359.044 |
| 14 | ReadDynamicEnergy | read | 95.382→451.783 | 2.946→8.686 | 71.084→330.783 |
| 14 | ReadDynamicEnergy | write | 74.667→332.483 | 1.520→4.937 | 71.084→330.783 |
| 7 | ReadLatency | read | 43.178→218.528 | 2.804→9.256 | 29.951→148.087 |
| 7 | ReadLatency | write | 31.264→145.921 | 1.997→6.031 | 29.951→148.087 |
| 7 | ReadDynamicEnergy | read | 41.287→210.426 | 1.771→5.069 | 27.403→137.127 |
| 7 | ReadDynamicEnergy | write | 29.401→137.839 | 1.036→3.156 | 27.403→137.127 |
| 5 | ReadLatency | read | 40.056→198.786 | 3.455→8.046 | 29.253→135.221 |
| 5 | ReadLatency | write | 29.207→132.857 | 2.802→5.617 | 29.253→135.221 |
| 5 | ReadDynamicEnergy | read | 37.820→190.677 | 1.536→4.568 | 25.349→124.326 |
| 5 | ReadDynamicEnergy | write | 26.995→124.764 | 0.886→2.812 | 25.349→124.326 |
| 3 | ReadLatency | read | 34.476→179.016 | 3.001→7.085 | 24.906→121.190 |
| 3 | ReadLatency | write | 24.922→119.079 | 2.459→5.049 | 24.906→121.190 |
| 3 | ReadDynamicEnergy | read | 33.189→172.688 | 1.329→3.994 | 22.168→112.391 |
| 3 | ReadDynamicEnergy | write | 23.657→112.765 | 0.789→2.555 | 22.168→112.391 |

| Node | Objective | Data bank/subarray/mat 1→32 | Tag bank/subarray/mat 1→32 |
|---:|---|---|---|
| 14 | ReadLatency | 4 x 4/2 x 2/512 Rows x 256 Columns → 4 x 4/2 x 2/4096 Rows x 1024 Columns | 16 x 1/2 x 2/64 Rows x 272 Columns → 16 x 1/2 x 2/512 Rows x 928 Columns |
| 14 | ReadDynamicEnergy | 4 x 4/2 x 1/512 Rows x 512 Columns → 4 x 4/2 x 1/4096 Rows x 2048 Columns | 8 x 1/2 x 2/64 Rows x 544 Columns → 64 x 1/2 x 2/64 Rows x 1856 Columns |
| 7 | ReadLatency | 4 x 4/2 x 2/512 Rows x 256 Columns → 4 x 4/2 x 2/4096 Rows x 1024 Columns | 16 x 1/2 x 2/64 Rows x 272 Columns → 32 x 1/2 x 2/128 Rows x 1856 Columns |
| 7 | ReadDynamicEnergy | 4 x 4/2 x 1/512 Rows x 512 Columns → 4 x 4/2 x 1/4096 Rows x 2048 Columns | 16 x 1/2 x 2/32 Rows x 544 Columns → 64 x 1/2 x 2/64 Rows x 1856 Columns |
| 5 | ReadLatency | 4 x 4/2 x 2/512 Rows x 256 Columns → 4 x 4/2 x 2/4096 Rows x 1024 Columns | 32 x 1/2 x 2/32 Rows x 272 Columns → 64 x 1/2 x 2/64 Rows x 1856 Columns |
| 5 | ReadDynamicEnergy | 4 x 4/2 x 1/512 Rows x 512 Columns → 4 x 4/2 x 1/4096 Rows x 2048 Columns | 16 x 1/2 x 2/32 Rows x 544 Columns → 64 x 1/2 x 2/64 Rows x 1856 Columns |
| 3 | ReadLatency | 4 x 4/2 x 2/512 Rows x 256 Columns → 4 x 4/2 x 2/4096 Rows x 1024 Columns | 32 x 1/2 x 2/32 Rows x 272 Columns → 64 x 1/2 x 2/64 Rows x 1856 Columns |
| 3 | ReadDynamicEnergy | 4 x 4/2 x 1/512 Rows x 512 Columns → 4 x 4/2 x 1/4096 Rows x 2048 Columns | 16 x 1/2 x 2/32 Rows x 544 Columns → 64 x 1/2 x 2/64 Rows x 1856 Columns |

Observed larger model cache energy includes bank routing, tag storage and optimizer geometry changes. It does not establish hardware GPU energy scaling. 1MiB and 32MiB are both single modeled cache objects with their own data/tag geometry. [Full data/tag/mat/mux/wire/buffer detail](../results/parsed_results.json), [consistent bank-level breakdown](../results/energy_breakdown.csv). Routing is already inside data/tag bank energy; residual is not cell-only. No overlapping hierarchy is summed.

## GPU-nominal and counterfactual bridge

Required E(14,6), E(7,40), E(5,50), fixed-capacity node factors and same-node capacity factors are unavailable: all requested native pairs fail. Both reference node-first/resize-second and alternate capacity-first identities are preserved in [gpu_nominal_bridge.csv](../results/gpu_nominal_bridge.csv), with failed endpoint logs/configs. No numeric ratio or GPU causal attribution is fabricated.
For a supported **1→32MiB positive algebra control**, [bridge_control_1_32MiB.csv](../results/bridge_control_1_32MiB.csv) verifies both factorizations using exact rational arithmetic from raw summary energies. These controls are not substitutions for GPU-nominal results. Their reference ordering is node at old capacity, then capacity at new node.

| Node transition | Objective | Operation | Total ratio | Node-first | Resize after node | Resize-first | Node after resize | Interaction |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 14→7 | ReadLatency | read | 2.213592 | 0.446602 | 4.956522 | 4.757282 | 0.465306 | 1.041881 |
| 14→7 | ReadLatency | write | 1.876543 | 0.407407 | 4.606061 | 4.506173 | 0.416438 | 1.022167 |
| 14→7 | ReadDynamicEnergy | read | 2.193878 | 0.438776 | 5.000000 | 4.693878 | 0.467391 | 1.065217 |
| 14→7 | ReadDynamicEnergy | write | 1.855263 | 0.394737 | 4.700000 | 4.434211 | 0.418398 | 1.059941 |
| 7→5 | ReadLatency | read | 4.500000 | 0.956522 | 4.704545 | 4.956522 | 0.907895 | 0.949163 |
| 7→5 | ReadLatency | write | 4.181818 | 0.969697 | 4.312500 | 4.606061 | 0.907895 | 0.936266 |
| 7→5 | ReadDynamicEnergy | read | 4.534884 | 0.906977 | 5.000000 | 5.000000 | 0.906977 | 1.000000 |
| 7→5 | ReadDynamicEnergy | write | 4.266667 | 0.933333 | 4.571429 | 4.700000 | 0.907801 | 0.972644 |

The total ratio is identical for either ordering; individual factors differ when interaction ≠1. These are algebraic allocations, not experimentally isolated process or architecture causes. Exact identities are checked without mixing fine and rounded energy.

## Partition sensitivity

| Scenario | Node | Objective | Status | Read local / mono pJ | Write local / mono pJ | Sum local leakage mW | Sum local area mm² |
|---|---:|---|---|---:|---:|---:|---:|
| A100 hypothetical two equal partitions | 7 | ReadLatency | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| A100 hypothetical two equal partitions | 7 | ReadDynamicEnergy | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| H100 illustrative N=2 not verified | 5 | ReadLatency | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| H100 illustrative N=2 not verified | 5 | ReadDynamicEnergy | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| H100 illustrative N=5 not verified | 5 | ReadLatency | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| H100 illustrative N=5 not verified | 5 | ReadDynamicEnergy | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| V100 illustrative N=2 not verified | 14 | ReadLatency | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| V100 illustrative N=2 not verified | 14 | ReadDynamicEnergy | UNAVAILABLE_GEOMETRY | — / — | — / — | — | — |
| supported 32MiB synthetic control | 7 | ReadLatency | VALID_LOCAL_CONTROL | 117.000 / 228.000 | 78.000 / 152.000 | 7.688 | 9.188 |
| supported 32MiB synthetic control | 7 | ReadDynamicEnergy | VALID_LOCAL_CONTROL | 113.000 / 215.000 | 91.000 / 141.000 | 7.460 | 8.940 |
| supported 32MiB synthetic control | 5 | ReadLatency | VALID_LOCAL_CONTROL | 107.000 / 207.000 | 71.000 / 138.000 | 7.304 | 7.672 |
| supported 32MiB synthetic control | 5 | ReadDynamicEnergy | VALID_LOCAL_CONTROL | 103.000 / 195.000 | 83.000 / 128.000 | 7.084 | 7.312 |

40=2×20, 50=2×25, 50=5×10 and 6=2×3 cannot supply local energies under this source. The supported 32=4×8 control is explicitly hypothetical, not an actual GPU partition count. If exactly one partition activates, local candidate E is E(8), **not 4×E(8)**; weighted traffic gives Σw_jE_j plus unknown fabric/control energy. Summed local leakage/area omit shared costs; local latency excludes global network. [Scenario CSV](../results/partition_scenarios.csv).

## Precision, provenance and unresolved work

Effective pJ/bit=Eaccess/256 is a normalized model access, not an SRAM cell bit energy. Summary energy prints 1pJ steps; separate data+tag totals have finer printed precision. Both are retained with their differences; each SF/bridge uses summary precision consistently. Matching external rerun metrics do not prove external source provenance. [Upload comparison](../results/uploaded_32MiB_comparison.csv).
The model uses a 32B line, not shared metadata for a 32B GPU sector within a 128B line. No direct private GPU coefficient comparison is published. GPU SKU specifications and A100 high-level partition statements require primary-source verification; current network denies NVIDIA docs. H100 physical partition count remains unknown.
Next: supported non-power-of-two address mapping/tag geometry in a separately reviewed model change; fixed-organization and Vdd sensitivity; independently parameterized line/sector width and shared tag/fabric costs; complete public GPU/NCU evidence. Existing sources/inputs/results remain untouched.
