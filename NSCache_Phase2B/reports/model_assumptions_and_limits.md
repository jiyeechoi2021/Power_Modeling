# Model assumptions, source evidence and limits

## Units and process/device labels

1MiB=1024KiB=1,048,576 bytes. The input spelling `-Capacity (MB)` is multiplied by 1024² in `InputParameter.cpp:324–327`, so all study capacities are exact binary MiB. Every model access uses WordWidth=256bit and the model prints Cache Line Size=32Bytes (`InputParameter.cpp:931`). This is not a 32B sector sharing a 128B line's metadata.

The requested GPU-nominal targets are **Tesla V100 SXM2 (16/32GB family), 6MiB / 12FFN; NVIDIA A100 SXM4 (40/80GB family), 40MiB / N7; NVIDIA H100 SXM (80GB), 50MiB / customized 4N**. Capacity/process values are task-specified published targets; primary-source links below are supplied for verification. The model uses 14/7/5nm proxies, never physical node equivalence or SKU-accurate cache layout. No GPU energy coefficient is provided or published.

Primary sources to verify:

- NVIDIA, *Tesla V100 GPU Architecture*: https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf
- NVIDIA, *A100 Tensor Core GPU Architecture*: https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf
- NVIDIA, *Ampere Tuning Guide*, L2 cache: https://docs.nvidia.com/cuda/ampere-tuning-guide/index.html
- NVIDIA, *H100 Tensor Core GPU Architecture*: https://resources.nvidia.com/en-us-tensor-core/nvidia-hopper-architecture-whitepaper
- NVIDIA, *Nsight Compute Profiling Guide*, memory workload: https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#memory-workload-analysis

**Access limit:** live requests to NVIDIA docs and the Volta whitepaper returned HTTP 403 in this environment. These citations are verification targets, not claims that their text was fetched/read in this task. A100's two high-level L2 partitions are a supplied documented premise, not independently reverified here and not a physical slice/bank count. H100's actual partition count remains unknown. Sector size=32B and typical line=128B are measurement-context premises; exact generation/level/operation behavior still requires the primary docs/NCU version. No new hardware observation is inferred from the model.

## Source and controls

Recovered source files match all 54 recorded hashes for upstream `2fdcbf093f806bc9a28964aca8402c42738d58e5`; the entire Phase 2-A base is protected by 336 file digests. Model source/Makefile and all Phase 1/2-A artifacts are unchanged. Retain CC BY-NC 4.0 and LICENSE_NVSim/LICENSE_DESTINY/LICENSE_CACTI3DD notices in the existing source directory. This study does not relicense the model or redistribute new proprietary inputs.

All cases inherit Phase 2-A L2: cache/Normal, 16 ways, 256bit, 300K, LOP, H-tree, internal sensing, data ForceBankA=4x4, latency-oriented buffer design, pruning on, one die. Only capacity changes. No new port-count assumption or timing/area constraint is added. Defaults printed by the model include bank aspect ratio limit 3 and relaxed SRAM cell. No unsupported-capacity guard is removed.

Voltage is node-dependent: source-derived non-HP Vdd at 14/7/5/3nm is 0.8/0.7/0.7/0.7V (`Technology.cpp:1573–1905`), while SRAM cell read-voltage fields are 0.277/0.264/0.253/0.248V (node-specific `.cell`). These are different quantities. Cell area F²/aspect ratio, wires and optimizer-selected geometry also vary. `initializeTechnology` in main.cpp uses node interpolation; the selected integer nodes have zero interpolation weight toward the next node. These source-derived parameters are not GPU physical measurements.

ForceBankA constrains data bank subarray geometry; `REDUCE_SEARCH_SIZE` replaces tag search bounds independently (`macros.h:179+`). The model's bank/mat/subarray hierarchy must not be relabeled as GPU slices or top-level partitions.

## Why 6/20/25/40/50MiB fail

Input syntax accepts the integer capacities but geometry derives set/index counts using integer log2 (`main.cpp:434–451`, `BankWithHtree.cpp:176–178`) and rows from `1 << addressBits` (`SubArray.cpp:77–111`). The actual data/tag capacity guards (`macros.h:138–175`) terminate with exit 255 and a capacity violation. The tag guard shares the text “DATA capacity violation,” so the printed label alone does not locate the failure. Smoke raw logs and all native diagnostic attempts are retained. No energy, SF or latency is assigned to these failures.

This is an unsupported representation under the **current unmodified source/settings**, not evidence that a real GPU cannot implement such capacities. Exact support requires separately reviewed non-power-of-two addressing/banking/tag geometry and tests; deleting the guard or silently rounding capacities would invalidate the requested experiment.

## Consistent energy accounting

`Result::printAsCache` (`Result.cpp:1596–1760`) uses `E_hit=tag.read+data.read`, `E_write=tag.write+data.write`. Cache summary prints 0.001nJ=1pJ steps. The data/tag bank details use finer printed pJ; both precisions are retained and labeled in every capacity row and breakdown CSV. SF/bridge tables consistently use **summary** energy; fine bank sums are separately available, not mixed into the same ratio. Rounded summary vs bank-sum differences are not silently treated as physics or measurement errors.

H-tree energy is part of bank energy (`BankWithHtree.cpp:667–735`). Bank=data+tag is a consistent total; routing is a subset, nonrouting residual is not cell-only. Per-subarray/per-mat/decoder/senseamp/mux/precharge values overlap the hierarchy and have activation scopes. Detailed strings and units remain in parsed JSON; nested values are not added to bank totals.

`E_effective_bit=E_model_access/256` normalizes the complete modeled access, not one SRAM cell bit. Real GPU miss/fill/writeback, ECC, crossbar/control, coalescing, replay and tag reuse may have different boundaries. The Normal miss formula itself has an accuracy TODO in source. No public absolute model/GPU energy ratio or private measured coefficient is computed.

## Counterfactual order and partition composition

Reference bridge order: change node at old capacity, then resize at new node. Alternative: resize at old node, then change node. Both products equal the end-to-end modeled ratio algebraically. Their individual factors depend on ordering; interaction=NodeFactor_at_new_capacity/NodeFactor_at_old_capacity. These factors are not causal process/architecture shares. GPU-nominal identities cannot be numerically verified when endpoints fail; supported 1/32MiB controls verify the algebra with exact rational arithmetic and explicit labels.

For N independently modeled equal partitions, if one local partition activates per transaction, candidate local dynamic energy is E_local; with weights, Σw_jE_j. Do not multiply by N. Shared fabric/global control is an unknown addend. If multiple partitions activate, activity must be separately specified. Sum local leakage and area by N only as partial powered-system approximations, with shared costs unknown. Local latency excludes network delay. Independent caches do not guarantee identical hit/miss behavior, address interleaving or tag sharing with a monolithic object.

40=2×20 and 50=2×25 require native sizes that fail; 50=5×10 and 6=2×3 also fail. A supported 32=4×8 control is a distinct synthetic scenario, not an A100/H100 partition claim and not a replacement for the failed requested sizes.
