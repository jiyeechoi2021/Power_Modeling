## Problem and outcome

Phase 2-A's 1MiB L2 results do not describe capacity/organization effects at GPU-nominal totals. This stacked Phase 2-B study preserves all prior artifacts and adds an independently rerun 32MiB baseline, exact capacity diagnostics, raw-derived comparisons and explicit model limits.

Feasibility gate: 6/20/25/40/50MiB configs parse but abort with capacity violations (binary tag/data address geometry). No guard, source, bank constraint or capacity is changed to force a result. All 14 requested GPU-native pairs/objectives fail and remain without energy/SF; eight additional local-size probes also fail. Twelve new runs complete: eight 32MiB cases and four separately labeled 8MiB controls. Eight 1MiB raw baselines are reused after hash checks. All 64 fresh/uploaded 32MiB metric comparisons match, but the archive lacks one metadata record and source tree/cell provenance and has a different binary hash, so it is preserved as external evidence rather than assumed reproducible source.

## Analysis

Includes summary and fine bank-sum pJ/access/effective pJ/bit, fixed-capacity SF, latency/area/leakage, data/tag/routing and full organization, failed coverage, exact bridge identities and order dependence on supported 1/32MiB controls, and hypothetical 32=4×8 local-cache composition. Unsupported GPU-nominal bridges and 2×20/2×25/5×10/2×3 scenarios are explicitly unavailable. Local dynamic energy is not multiplied by partition count; fabric/global costs remain unknown. Uploaded derived capacity ratios mix precision; new like-for-like ratios are regenerated only from raw evidence.

No Pure Process Scaling, physical GPU-layout equivalence, private GPU coefficients or hardware validation is claimed. Node/device mappings are proxies. Official NVIDIA docs remain HTTP 403 blocked and unverified claims are labeled. CC BY-NC and inherited license notices remain in the unchanged source tree.

## Validation and review

11 tests pass; 11 generated files byte-identical over repeated analyses; resume preserves all 34 attempts; all 336 historical files unchanged; exact raw/config/source/binary hashes and per-child wait4 RSS/time/exit recorded. Recommended runs are sequential two-worker batches; initial batches overlapped to peak four on the five-CPU machine and metadata documents it. Initial environment-helper recipe mismatch is corrected in provenance without editing original snapshots.

Base: research/nscache-phase2a-256bit at verified 820fe02. Head: research/nscache-phase2b-l2-capacity-organization. Main remains ZIP-only; direct PR #1/#2 state queries are blocked by GraphQL Forbidden. Review as Draft; do not merge automatically. See NSCache_Phase2B/reports/experiment_report.md, feasibility_gate.md and validation.md.
