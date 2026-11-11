# Phase 2-A validation and provenance

## Performed

From the repository root:

```bash
python3 NSCache_Phase2A/scripts/prepare.py
bash NSCache_Phase2A/scripts/build.sh
python3 NSCache_Phase2A/scripts/run.py --jobs 2
python3 NSCache_Phase2A/scripts/analyze.py
python3 -m unittest discover -s NSCache_Phase2A/tests -v
python3 NSCache_Phase2A/scripts/run.py --jobs 2
python3 NSCache_Phase2A/scripts/analyze.py
python3 NSCache_Phase2A/scripts/analyze.py
python3 NSCache_Phase2A/scripts/manifest.py
python3 NSCache_Phase2A/scripts/manifest.py --check
cd NSCache_Phase2A
sha256sum -c provenance/SHA256SUMS.txt
```

- Prepared 16 configs by copying Phase 1 width-aligned 512bit sources and changing only WordWidth to 256bit. Seven-nanometer copies exactly match the old reconstructed 256bit inputs; they were nevertheless freshly executed.
- Built with unmodified source/Makefile, GNU g++ 14.2.0, C++17 -Wall -O3 -mtune=native, two compilation jobs. The resulting binary hash exactly matches Phase 1 (`038a0bd202c2497a735344a53a23e3c7cf1d11d665f53b25e29db11a12b0360a`). Initial metadata helper's generic build_command field is explicitly corrected by provenance/build_recipe.json; actual build commands are retained in logs/build/stdout.log. Original environment snapshots were not edited.
- **16/16 new attempts FINISHED, return code 0, Finished!, empty stderr.** No historical logs were relabeled as new. Each attempt has timestamp/duration, configuration/cell/binary/environment/stdout/stderr identities.
- Four fresh 7nm runs match all six summary metrics of their Phase 1 256bit counterparts. Detailed organization text also compares separately in phase1_7nm_replay_comparison.csv.
- Resume verified all 16 latest Phase 2 attempts and produced no additional attempt directories (still exactly 16).
- **Seven tests passed**, covering raw regeneration with poisoned Phase 1 analysis cache, repeatability, independent raw-derived SF/normalization arithmetic, corrupted raw rejection, unintended configuration change rejection, component scopes, preparation overwrite protection and full Phase 1 baseline preservation and complete tracked-file inventory coverage (including build logs). Failure injection occurs only in temporary copies.
- Repeated actual analysis twice: all **nine generated outputs** were byte-identical by SHA-256 (eight results CSV/JSON files plus the generated energy analysis report). Analyzer exits 0 for a complete valid Phase 2 dataset; this does not mean the model is validated against GPU measurements.
- Phase 1's **226 tracked files**, including original ZIP, configs, source, logs, results, reports and manifests, are checked against the immutable `26ba7529fcb356c82b1813b6030f54746ccb3cc3` baseline. No changes are allowed outside the new Phase 2 directory.
- A Phase 2-only manifest/inventory is generated and verified; the manifest omits its own hash. The preserved Phase 1 manifest is not regenerated. Manifest refresh is checked for byte-identical repeat output.

All SF and energy comparisons use raw parsed values, not workbook values or guessed coefficients. Cache summary energy has 1pJ printed granularity; detail values are printed with their own units/scopes. Tag/data bank sums and H-tree subset shares are distinguished from overlapping subarray/mat/peripheral values. No source-level model modification, GPU simulator, private GPU coefficient or Rubin prediction was introduced.

## External access limits and PR base

A read-only request to the official NVIDIA Nsight Compute Profiling Guide returned HTTP 403. Related official guide URLs and the precise unconfirmed claims are recorded in gpu_sector_modeling_feasibility.md. NVIDIA/nsight-training was inspected at b17c40eef23929d08ec42e66667b29ae336ea8ac; relevant notebooks did not establish the requested V100/A100 line/sector specifics. These are recorded as unknown, not assumed.

`gh pr view 1` returned `Post https://api.github.com/graphql: Forbidden`. The current remote main still points to the original ZIP-only commit `51208723a98c9df7a267126b3477a59837b14812`; the Phase 1 source branch points to `26ba752`. The Phase 1 changes are absent from main, so the Phase 2 review PR is prepared with base `research/nscache-phase1-reproduction`, head `research/nscache-phase2a-256bit`. Neither existing PR #1 nor main is merged by this task. Actual PR creation is reported only if the API operation succeeds.
