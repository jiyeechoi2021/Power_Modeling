## Outcome

Add a separate Phase 2-C **512KiB NS-Cache single-cache proxy / model slice candidate** baseline: exactly eight new configurations (14/7/5/3nm × ReadLatency/ReadDynamicEnergy), WordWidth=256bit, inherited L2-like controls. Each supplies read and write results. Exact capacity uses integer `Capacity (KB): 512`=524288 bytes; only that line changes relative to matching Phase 2-A inputs. Source/cells remain unchanged and licensed under existing CC BY-NC/inherited notices.

7nm/ReadLatency smoke passes full hash/header/summary gate and counts as one of the eight. All eight finish with exit 0 and empty stderr, max two workers. No additional capacities or P0–P3 model interventions are run. Old 1/8/32MiB data are read-only historical references; missing 14/3nm 8MiB cells remain explicit.

Includes complete summary/fine read/write energy/effective pJ-bit, twelve matched node-SF rows, capacity trajectory/ratios, bank-level data/tag/routing with hierarchy scopes, latency/leakage/area/solutions and full selected organization. Ratios never mix rounded summary and finer bank sums. Unexpected writes are retained: 7nm read-energy objective writes more than latency objective; 5→3nm latency-optimized write increases. Report distinguishes observations from causal hypotheses.

## Validation

13 tests pass; seven generated files byte-identical on repeated raw-only analysis; eight-attempt resume is idempotent; source/cell/config/environment/binary/raw hashes verified; source revision 2fdcbf093f806bc9a28964aca8402c42738d58e5 (54 hashes); all 576 historical files unchanged. Manifest/inventory cover new artifacts, verify historical/source/cell and optional full local binary identity. Build is unmodified g++14 C++17 -O3 -mtune=native.

Task-supplied A100 whitepaper p.35 hierarchy supports a nominal-size rationale only; direct PDF retrieval was HTTP 403 and independent source reread remains pending. No A100 circuit/ports/sector/energy-boundary equivalence, GPU energy×80, confidential coefficient, hardware validation or Rubin prediction is claimed.

Base: research/nscache-phase2b-l2-capacity-organization at actual verified 6609b1ac56d43fa7d06a5e3b79cd678f6d14a492. Head: research/nscache-phase2c-512kib-slice. Review as Draft; do not merge or edit prior PRs. Prior PR #1/#2/#3 status queries are GraphQL Forbidden, not reported as verified. See NSCache_Phase2C/reports/experiment_report.md and validation.md.
