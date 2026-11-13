# Validation and controlled-study evidence

## Actual commands

From repository root:

```bash
git ls-remote origin refs/heads/main refs/heads/research/nscache-phase2a-256bit refs/heads/research/nscache-phase2b-l2-capacity-organization refs/heads/research/nscache-phase2c-512kib-slice
git fetch origin research/nscache-phase2c-512kib-slice:refs/remotes/origin/research/nscache-phase2c-512kib-slice
python3 NSCache_3nm_128MiB_Feasibility/scripts/prepare.py
bash NSCache_3nm_128MiB_Feasibility/scripts/build.sh
python3 NSCache_3nm_128MiB_Feasibility/scripts/run.py --jobs 2 --timeout 1800
python3 NSCache_3nm_128MiB_Feasibility/scripts/analyze.py
python3 -m unittest discover -s NSCache_3nm_128MiB_Feasibility/tests -v
python3 NSCache_3nm_128MiB_Feasibility/scripts/manifest.py
python3 NSCache_3nm_128MiB_Feasibility/scripts/manifest.py --check --require-binary
```

## Coverage and provenance

- Clean current checkout; actual remote Phase 2-C HEAD verified as **ac34dfad49a0ed33ab368ac50d438022f557df41**. New branch research/nscache-3nm-128mib-feasibility created from that remote; all **647 earlier tracked files** protected byte-for-byte. Work/main/old study branches remain unchanged.
- Available references: 136 tracked/config-archive records inspected; no existing 3nm/128MiB author reference config found. The generic recovered 3nm config is 32MiB/512bit/WriteLatency, not an author 128MiB input. Author-original config/output is unavailable and requested by the user; no email contents are copied. Full paper URL/DOI/PDF is absent locally; public arXiv lookup returned HTTP403. The task's declared published 0.917pJ/bit is labeled unverified-public-reference provenance, not private GPU measurement data.
- Verified **two existing Phase 2-B 3nm/32MiB raw baselines**, including config/cell/stdout/stderr/environment hashes, exit 0, Finished!, six summary fields, write latency and full organization. No baseline simulation is re-executed.
- **Two new 128MiB capacity-only reconstructions executed; both FINISHED, exit 0, empty stderr.** ReadLatency elapsed 134.92s, ReadDynamicEnergy 144.52s. Per-child max RSS 14336KiB (Linux wait4); user/system CPU and UTC timestamps retained in metadata. Two concurrent workers, 1800s timeout, no timeout/resource/geometry failure. No hard memory limit is claimed.
- Current logical data capacity independently equals requested **134217728 bytes**: product of printed data bank/subarray/mat dimensions divided by eight. 32MiB gives 33554432 bytes similarly. Both source guards remain enabled; no source/bank/wordwidth/way/voltage/cell constraint is changed.
- 54 source/Makefile hashes match revision **2fdcbf093f806bc9a28964aca8402c42738d58e5**. Cell SRAM_cell_3nm.cell hash verified. g++14.2.0 / make4.4.1 / Python3.12.14, C++17 -Wall -O3 -mtune=native. Binary hash **038a0bd202c2497a735344a53a23e3c7cf1d11d665f53b25e29db11a12b0360a**, identical to the historical baseline binary. Correct build recipe/environment and original stdout/stderr retained.
- **14 tests pass**: capacity-only/two-case scope; two real completed attempts; baseline verification without re-execution; independent raw unit conversion/read-write latency; physical data-bit capacity; no routing double counting/fine precision; matched-precision capacity ratios/public-reference arithmetic; real resume without launch; source/cell/binary/history hashes; public reference absent from run/prepare parameter selection; raw-only deterministic regeneration without binary; tamper rejection without changing results; timeout fixture without fabricated energy; manifest corruption detection. Failure injection is only in temporary copies, not actual data or new model runs.

## Reproducibility, precision and publication

Generated files are results/energy_results.csv, results/capacity_comparison.csv, results/llmet_reference_comparison.csv, results/energy_breakdown.csv, results/organization_and_metadata.json and reports/experiment_report.md. Two consecutive actual analyses produced six byte-identical generated files; tests also rebuild deleted outputs in a copy without binary. Successful resume retained exactly two original attempt directories. Manifest verifies source/cells/647 prior files and local binary identity (when required), plus retained new config/log/result artifacts; self-manifest hash is excluded.

Summary energy has 1pJ printed granularity; finer bank sums are separate. pJ/bit divides each by modeled WordWidth=256. No ratio mixes operands from different precision classes. Reported 0.917 has unknown original operation/aggregation/normalization and MB/MiB convention; numeric proximity is never a reproduction verdict. Large mat geometry passes logical capacity but physical macro accuracy remains unvalidated.

Before any push, review all staged artifacts and the outgoing commit diff. Allowed numeric lineage: two independent historical NS-Cache baselines, two independent new NS-Cache runs, verified model/config/tool metadata and the declared public-paper scalar. No private GPU measurement, fitted coefficient, normalization/calibration factor, confidential scaling factor, author correspondence or reconstructible private derivative may be published. Confidentiality review must be recorded without printing any suspected confidential values.
