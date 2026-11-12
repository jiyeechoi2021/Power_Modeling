# Phase 2-C Feasibility Gate

## Verified kickoff and protected baseline

Actual remote refs were read before branching: main `51208723a98c9df7a267126b3477a59837b14812`, Phase 1 `26ba7529fcb356c82b1813b6030f54746ccb3cc3`, Phase 2-A `820fe02a95009985510c4810c2044aaa8c7e610e`, Phase 2-B **`6609b1ac56d43fa7d06a5e3b79cd678f6d14a492`**. The latter exactly matches the supplied expected commit; diff to fetched remote head is empty. A new `research/nscache-phase2c-512kib-slice` branch was created from that verified remote. Existing `work` and earlier branch refs were not reset/rebased/edited/merged. PR #1/#2/#3 GraphQL queries each returned Forbidden; their UI state is not claimed as verified.

The clean worktree and `provenance/protected.json` protect **576 historical tracked files**, including the original ZIP and all prior source/config/log/result/report/manifest files. The 54 source/Makefile digests match upstream `2fdcbf093f806bc9a28964aca8402c42738d58e5`. Existing CC BY-NC 4.0 and inherited notices remain intact. All new committed paths are under NSCache_Phase2C.

## Exact input and recipe

`InputParameter.cpp:318–321` reads `-Capacity (KB)` as integer ×1024; `-Capacity (MB)` uses an integer too. The derived line is **`-Capacity (KB): 512`**, exactly **524288 bytes**, not `MB: 0.5` or rounded 1MiB. Each of eight configs is byte-identical to its matching Phase 2-A 1MiB config except for that capacity line. `provenance/cases.json` retains source/derived/cell hashes and full unified diffs.

Controls: WordWidth=256bit, model line=32B, associativity 16, cache/Normal, LOP, 300K, H-tree, internal sensing, ForceBankA=4x4, original pruning/buffer/wire settings and node cells. No source, Vdd, organization or constraint intervention. No additional capacity jobs are configured.

Unmodified source was compiled separately into NSCache_Phase2C/build using GNU g++ 14.2.0, C++17 `-Wall -O3 -mtune=native`, two build workers. The exact recipe/environment are in `logs/build/environment.json`; compile/link stdout and original warnings in stderr are retained. Binary SHA-256 is `038a0bd202c2497a735344a53a23e3c7cf1d11d665f53b25e29db11a12b0360a`, matching previous verified builds.

## Smoke gate result

**7nm / ReadLatency / 512KiB: PASS as a model execution.** Exit 0, Finished!, Capacity 512KB, line 32Bytes, 16 ways; full cache summary and data/tag organization parse. Summary read/write are 37/25pJ/access; fine bank sums are separately 37.416/24.612pJ. The exact config/binary/hash-matching smoke is one of the eight, not an extra ninth run.

Only after this gate were the remaining seven cases launched. Final coverage: **8 planned, 8 actual completed, 0 failed/timeout/missing**. Maximum two live model processes, 1800s timeout, wait4 per-child CPU/RSS/elapsed/exit, per-attempt stdout/stderr/environment/config/source/cell/binary hashes. A file lock serializes CLI batches to prevent overlapping worker pools. No historical capacity runs are launched.

## Scientific interpretation gate

512KiB is a **NS-Cache single-cache proxy / model slice candidate**. The task cites A100 whitepaper p.35 for two partitions ×40 slices ×nominal512KB. Direct PDF retrieval returned HTTP 403: this is a supplied page-specific citation, not independently reread source text. The size rationale does not establish physical A100 slice topology, 16-way/port/bank choices, sector semantics or energy boundary. No dynamic energy is multiplied by 80, and no actual GPU energy/Rubin result is claimed.
