# Phase 1 outcome

- Repository base: `51208723a98c9df7a267126b3477a59837b14812`; research branch `research/nscache-phase1-reproduction`.
- Original ZIP unchanged. All 108 members preserved with mapping and SHA-256. Original historical experiment configs/logs and workbook are still missing; recorded CSV/JSON remain derived data.
- All 54 recovered source/Makefile files exactly match upstream `2fdcbf093f806bc9a28964aca8402c42738d58e5`. License and inherited notices were retrieved verbatim from that revision. No source patch was needed.
- GNU g++ 14.2.0, make 4.4.1, Python 3.12.14, Linux x86-64; C++17, -Wall -O3 -mtune=native; build/run parallelism 2. Existing compiler warnings preserved. No external Python packages or credentials required for experiments.
- Fresh reproduction: 16/16 exit 0, Finished!, all six summaries and separate data/tag configurations parsed. 12/16 cases match recorded values; 74/96 metrics match, 22/96 differ, zero untested. All four mismatched cases are 7nm.
- Original 7nm configs specify 256bit, whereas other nodes and the package narrative specify 512bit. Separate one-factor 512bit diagnostics for all four 7nm cases exactly match all six recorded metrics. This strongly explains the discrepancy but does not recover historical originals. Original reproduction rows and configs remain unchanged.
- Both raw suites retain separate stdout/stderr, timestamps, durations, return status and hashes. All 16 original attempts were reused successfully by the resume workflow without extra execution. Four diagnostic attempts are separately labeled.
- Eight workflow unit tests passed, covering units, missing/duplicate summaries, missing organization, changed-cell/log resume invalidation, retained failures/retry, and timeout preservation. Analyzer exit 1 is intentional and verified because it detects the four mismatches; it is not reported as a passing reproduction comparison.
- Read/write scaling, L1/L2 differences, energy/area/latency trade-offs and selected data/tag organizations are documented in process_scaling_analysis.md. Original 7→5 dynamic energy increases are confounded by doubled line width. Even same-width comparisons retain node-specific cell/voltage and organization changes; no process-only causal claim is supported.
- Next steps: separate controlled 512bit sweep with explicit port/latency requirements; fixed-vs-reoptimized organization study; voltage/cell/model sensitivity and unrounded output validation; original evidence recovery. No private GPU data or Rubin prediction was introduced.

See [reproducibility_validation.md](reproducibility_validation.md), [process_scaling_analysis.md](process_scaling_analysis.md), and [provenance](../provenance/README.md) for underlying tables, logs and limits.
