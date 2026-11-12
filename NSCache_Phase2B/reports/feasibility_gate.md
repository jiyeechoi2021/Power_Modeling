# Phase 2-B Feasibility Gate

## Gate outcome

**Proceed with native power-of-two controls; native GPU-nominal/partition requests fail.** No model source patches, relaxed constraints or silent capacity substitutions are authorized by this result.

- Actual remote refs: main `5120872`, Phase 1 `26ba752`, Phase 2-A `820fe02`. The current checkout began on clean `work` at `5120872`; that branch was preserved. New branch `research/nscache-phase2b-l2-capacity-organization` starts from verified Phase 2-A HEAD. Main still contains only the original ZIP; the PR base is Phase 2-A. PR #1/#2 queries returned GitHub GraphQL Forbidden, so UI merge/closed state remains unverified. Evidence: `provenance/kickoff.json`.
- Eight 1MiB Phase 2-A L2 raw runs are available. Source 54-file digests match the previously verified upstream `2fdcbf093f806bc9a28964aca8402c42738d58e5`; GNU g++ 14.2.0 builds unchanged source and produces the same binary digest as Phase 2-A.
- Uploaded 32MiB ZIP CRC and all listed SHA-256 entries pass. There are eight configs/stdout/stderr sets but only seven metadata files: 14nm ReadLatency metadata is missing. Exact source tree/cell hashes are absent. The provided binary digest differs from the local build. Thus this is preserved **external exploratory evidence**, not an independently established current-source baseline. All eight 32MiB cases are re-executed; no chat figures are input to analysis.

## Capacity support and actual tests

`InputParameter.cpp:324–327` parses `-Capacity (MB)` as integer ×1024×1024: these are MiB, not decimal MB. All 6/20/25/40/50MiB smoke inputs parse successfully and print correct cache/width/ways headers. However every smoke exits **255**, lacks Finished!, and reports `ERROR: DATA capacity violation. Shouldn't happen`. The 6MiB/14nm and 40MiB/7nm cases were executed before the large sweep. 50MiB/5nm, 20MiB/7nm and 25MiB/5nm also fail immediately. Remaining requested native pairs/objectives and optional 3/10MiB diagnostic cases are retained as failed runs, not successful experiments.

Reason: `main.cpp:434–451` derives tag sets/index via integer log2; `BankWithHtree.cpp:176–178` and `SubArray.cpp:77–111` similarly derive binary geometry. `macros.h:138–175` compares physical array bits with target capacity and exits on mismatch. Both data and tag macros print the same DATA error text; a smoke can fail during tag search. The diagnostic Saw/Expected values are internal capacity-bit quantities, not necessarily the user-facing MiB capacity. Input syntax support is therefore distinct from feasible representable geometry.

`ForceBankA=4x4` sets data search bank geometry; tag search uses `REDUCE_SEARCH_SIZE` with its own 1..64 limits (`macros.h:179+`). It is neither GPU partition count nor an independent distributed L2 composition. No port count parameter or explicit latency/area constraint is added. Other controls: cache/Normal, 16 ways, WordWidth=256bit (32B modeled line), LOP, 300K, internal sensing, H-tree, latency buffer design, pruning, one stacked die. Cell/Vdd remain node-specific.

The first 32MiB/3nm/ReadLatency control completed with exit 0 and Finished!, establishing a successful large native test under the same source. Final per-case coverage is regenerated in `results/l2_capacity_energy.csv` and the experiment report. Pending/failed jobs are never filled with estimates.

## Partition fallback boundary

Required 40MiB=2×20MiB and 50MiB=2×25MiB still require unsupported local sizes. Illustrative 5×10MiB and 2×3MiB do too. These scenarios are marked unavailable, not replaced by different capacities. A separately labeled **32MiB synthetic control = 4×8MiB** is run at 7nm/5nm, both objectives, to study independent-cache composition at supported sizes. It is not a claim about A100/H100 physical partitions and does not satisfy missing GPU-nominal scenarios.

Resource policy: per-run timeout default 1800s, two workers per batch, wait4 records per-child max RSS/CPU/elapsed/exit code; failed and timeout output is preserved. Two batches overlap for part of the run on the five-CPU, 33GiB machine (maximum four live processes); final metadata permits reconstruction of the actual overlap. No original baseline files are modified.
