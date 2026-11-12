# Phase 2-B validation

## Commands actually executed (repository root)

```bash
git ls-remote origin refs/heads/main refs/heads/research/nscache-phase1-reproduction refs/heads/research/nscache-phase2a-256bit
gh pr view 1 --repo jiyeechoi2021/Power_Modeling --json number,state,mergedAt,headRefName,baseRefName
gh pr view 2 --repo jiyeechoi2021/Power_Modeling --json number,state,mergedAt,headRefName,baseRefName
python3 NSCache_Phase2B/scripts/prepare.py
bash NSCache_Phase2B/scripts/build.sh
python3 NSCache_Phase2B/scripts/run.py --stage smoke --jobs 2
python3 NSCache_Phase2B/scripts/run.py --stage fixed32 --jobs 2
python3 NSCache_Phase2B/scripts/run.py --stage unsupported_diagnostics --jobs 2
python3 NSCache_Phase2B/scripts/run.py --stage partition_control --jobs 2
python3 NSCache_Phase2B/scripts/analyze.py
python3 -m unittest discover -s NSCache_Phase2B/tests -v
python3 NSCache_Phase2B/scripts/run.py --stage fixed32 --jobs 2
python3 NSCache_Phase2B/scripts/run.py --stage partition_control --jobs 2
python3 NSCache_Phase2B/scripts/analyze.py
python3 NSCache_Phase2B/scripts/analyze.py
python3 NSCache_Phase2B/scripts/manifest.py
python3 NSCache_Phase2B/scripts/manifest.py --check
```

Initial `work` was clean at `5120872`. Current remote refs were read, not inferred from chat: main `5120872`, Phase 1 `26ba752`, Phase 2-A `820fe02`. PR #1/#2 both returned GraphQL Forbidden. Main is still the original ZIP-only tree; Phase 2-A is the safe verified source/base for a stacked Draft PR. PR UI state is not invented. No old branch/main is merged or pushed.

## Results

- **34 new attempts**: **12 completed** (8 current-source 32MiB cases + 4 independent 8MiB controls), **22 failed** with capacity violations and exit 255 (all 14 required GPU-native pairs/objectives plus 8 partition-size diagnostic cases). No timeouts; no missing or running attempts at final analysis.
- Eight existing 1MiB Phase 2-A L2 cases are independently hash-checked and reused. The analysis table therefore has **42 rows: 20 valid model results, 22 failures**. They are not described as 20 new executions.
- New 32MiB results exactly match the uploaded raw logs in **64/64** comparisons (summary read/write, fine bank-sum read/write, latency, area, leakage, feasible solutions). Matching values do not establish the upload's source provenance. Its binary digest differs and 14nm ReadLatency metadata is absent, so the fresh eight-run baseline is authoritative for this study.
- Uploaded ZIP SHA-256: `15742a30764d19e76ce48102910cd66a404b75f3ea248640e16ca576d95c659c`. CRC passes; all listed hashes and seven available metadata hash sets verify. Archive and extracted evidence remain byte-identical. Source tree/cell hashes are absent; unlisted README/self-manifest are identified in archive_audit.json.
- **11 tests passed**: raw units/precision, unsupported cases without fabricated values, routing hierarchy closure, exact bridge identities, independently raw-derived fixed-capacity SF, local partition dynamic not multiplied by N, uploaded mixed-precision CSV audit, real completed-run resume without execution, tamper rejection, output determinism, all historical tracked-file digests.
- **11 generated result/report files** have identical SHA-256 across two actual analyses (ten results CSV/JSON files and reports/experiment_report.md). Unit tests independently repeat this byte comparison. Analysis returns 0 for complete processing with explicitly failed geometry cases; this is not an all-experiments-pass claim.
- Twelve successful jobs were resumed without adding an attempt directory; original total remains 34. Failed inputs were not retried unchanged by unsupported_diagnostics. A deliberate future retry can use --case after diagnosis.
- `wait4` records each child exit code, RSS KiB, user/system CPU and elapsed time. Two workers per batch; the initial fixed32 and other batch overlapped on a 5-CPU/33GiB machine, with **peak four** active processes reconstructed from timestamps. Recommended reproduction commands run stages sequentially for a global maximum of two. No resource/timeout failure is hidden.
- Model source 54-file hashes match the previously verified upstream revision. Local binary SHA-256 is identical to Phase 2-A (`038a0bd202c2497a735344a53a23e3c7cf1d11d665f53b25e29db11a12b0360a`). Initial environment capture's generic Phase 2-A recipe is corrected in kickoff.json; actual build stdout and original run snapshots are preserved.
- **336 Phase 1/2-A tracked files** match the exact `820fe02a95009985510c4810c2044aaa8c7e610e` baseline; `work` remains at `5120872`. Only the new NSCache_Phase2B directory changes.

## Derived quantities and limitations

Fixed-capacity SF has 24 rows: C=1/32MiB × two objectives × read/write × three node transitions. Eight supported 1→32MiB bridge controls verify exact rational multiplicative identities for both orderings. Eight GPU-nominal bridge rows remain unavailable rather than fabricated; twelve partition scenarios include four valid local controls and eight unavailable native scenarios.

The uploaded derived CSV's capacity ratios match fine 32MiB numerator / rounded 1MiB denominator at four-decimal precision. The new analysis never uses them as model input. Consistent summary and consistent fine bank-sum capacity ratios are independently generated. Rounded/fine pJ/bit values are labeled separately, routing is a subset of bank energy, and no private GPU energy coefficients are read/published.

Official NVIDIA documentation and whitepaper requests returned HTTP 403. Primary-source links, SKU target labels and unverified physical partition claims are explicitly documented in model_assumptions_and_limits.md. Actual GPU-nominal comparison and native 20/25MiB partitioning require a separately reviewed model geometry extension, not removal of safety guards or capacity rounding.

Final integrity inventory: 240 Phase 2-B artifacts, 239 digests (manifest self-hash excluded); all listed hashes pass sha256sum verification.
