# Phase 2-C validation

## Actual commands (repository root)

```bash
git ls-remote origin refs/heads/main refs/heads/research/nscache-phase1-reproduction refs/heads/research/nscache-phase2a-256bit refs/heads/research/nscache-phase2b-l2-capacity-organization
git fetch origin research/nscache-phase2b-l2-capacity-organization:refs/remotes/origin/research/nscache-phase2b-l2-capacity-organization
gh pr view 1 --repo jiyeechoi2021/Power_Modeling --json number,state,isDraft,mergedAt,headRefName,baseRefName
gh pr view 2 --repo jiyeechoi2021/Power_Modeling --json number,state,isDraft,mergedAt,headRefName,baseRefName
gh pr view 3 --repo jiyeechoi2021/Power_Modeling --json number,state,isDraft,mergedAt,headRefName,baseRefName
python3 NSCache_Phase2C/scripts/prepare.py
bash NSCache_Phase2C/scripts/build.sh
python3 NSCache_Phase2C/scripts/run.py --stage smoke --jobs 1
python3 NSCache_Phase2C/scripts/run.py --stage remaining --jobs 2
python3 NSCache_Phase2C/scripts/analyze.py
python3 -m unittest discover -s NSCache_Phase2C/tests -v
python3 NSCache_Phase2C/scripts/run.py --stage all --jobs 2
python3 NSCache_Phase2C/scripts/analyze.py
python3 NSCache_Phase2C/scripts/analyze.py
python3 NSCache_Phase2C/scripts/manifest.py
python3 NSCache_Phase2C/scripts/manifest.py --check --require-binary
cd NSCache_Phase2C
sha256sum -c provenance/SHA256SUMS.txt
```

## Results and gate

- Verified remote Phase 2-B HEAD **6609b1ac56d43fa7d06a5e3b79cd678f6d14a492**, exactly the expected base. Clean checkout; new branch research/nscache-phase2c-512kib-slice created from fetched Phase 2-B. PR #1/#2/#3 queries each returned GraphQL Forbidden; their UI state is not assumed and none is edited/merged.
- **8 planned configurations, 8 actual attempts, 8 FINISHED/exit 0/Finished!, 0 failed/timeouts, empty stderr**. Read/write are two metrics per run, not sixteen runs. Smoke at 7nm/ReadLatency was one of the eight; remaining stage launched exactly seven after its hash/header/full-summary gate passed.
- Configs change only `Capacity (MB): 1` to `Capacity (KB): 512`; parser integer ×1024 yields exactly 524288 bytes. No fractional MB, rounded capacity, source patch, cell substitution or modified organization constraints. All configs remain 16-way/256bit/Normal/LOP/300K/H-tree/data ForceBankA=4x4 and original inherited settings.
- **54 source/Makefile hashes verified**, cell hashes per case; GNU g++ 14.2.0 / make 4.4.1 / Python 3.12.14, C++17 -Wall -O3 -mtune=native. Correct Phase 2-C recipe recorded in build environment and stdout; original compiler warnings retained. Binary hash **038a0bd202c2497a735344a53a23e3c7cf1d11d665f53b25e29db11a12b0360a**, matching verified historical builds. Each attempt records config/source/cell/binary/environment identities, raw logs, UTC timestamps, elapsed/CPU/max RSS (Linux wait4, KiB) and status.
- Maximum **two** simultaneous model processes verified by timestamps. CLI invocations are serialized by a shared lock. Default timeout 1800s. Resume checked all eight without spawning any new process or adding attempts.
- **13 unit tests passed**: exact integer-KB parser/config derivation and eight-case matrix; eight real attempts/smoke/concurrency; independently raw-derived unit conversion and normalization; rounding audit; no routing double counting; matched-precision SF/capacity arithmetic; explicit missing historical cells; missing/failed-run no-energy behavior; idempotent resume; historical/source/cell/binary preservation; raw-only regeneration without binary; tamper rejection without overwriting output; manifest corruption detection. Failure injection uses only temporary copies, never actual data or model executions.
- **Seven generated files** were byte-identical across two actual analyses: six result CSV/JSON files plus reports/experiment_report.md. Tests repeat full regeneration in a copy without local binary, and rebuild deleted results from original logs. Analysis returns 0 for all eight valid results; partial evidence returns 1, invalid hashes return 2.
- Capacity comparison has **32 capacity/node/objective cells**: eight new 512KiB, twenty verified historical 1/8/32MiB, four explicitly missing 8MiB cells at 14/3nm. Missing records are not interpolated. Twelve SF rows carry both summary and fine bank-sum precision separately, sixteen matched-operation 512KiB/1MiB ratios, and 56 bank-level breakdown records cover the 28 available cases.
- **576 earlier tracked files** match exact verified Phase 2-B bytes. Only NSCache_Phase2C is added. Original ZIP, old source/cells/configs/logs/results/reports/manifests/main and earlier branch pointers are preserved.

## Precision and scientific validity

Cache summary prints 0.001nJ=1pJ resolution. Fine data+tag sums are recorded separately with rounding deltas; no mixed-precision operands. Routing is inside bank totals; nested subarray/mat/peripheral values are not added again. Effective pJ/bit is complete model access /256, not physical bitcell or real GPU-sector energy.

Observed non-monotonic write results are preserved: 7nm energy objective writes 26pJ vs latency objective 25pJ (fine 26.021 vs 24.612); ReadLatency 5→3nm write is 24→25pJ (fine 24.237→24.756). No values/cells are tuned to remove these findings. Report correlates them with optimizer-selected data/tag/routing changes without claiming isolated causes.

The task's A100 whitepaper p.35 citation motivates nominal 512KiB size (80×512KiB=40MiB) only. Direct source retrieval returned HTTP 403, so local reread/source-text verification remains pending and is labeled explicitly. No physical A100 slice/ports/associativity/sector/energy-boundary equivalence or dynamic energy×80 is claimed. No private GPU coefficient appears.

Explicitly NOT executed: additional capacity sweeps, non-power-of-two geometry extension, V100/H100 topology reconstruction, 128B-line/32B-sector implementation, private coefficient comparisons, fixed-organization/Vdd campaigns, hardware validation or Rubin projection. These are deferred P0–P3 follow-ups, not hidden additions to this eight-case task.

Final artifact scope: 71 Phase 2-C inventory entries, 70 artifact digests (manifest self-hash excluded). Full validation additionally checked all historical/source/cell hashes and the local compiled binary against its archived digest.
