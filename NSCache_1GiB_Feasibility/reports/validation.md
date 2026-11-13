# Actual validation record

## Baselines and scope

Remote refs were read before work: main `51208723a98c9df7a267126b3477a59837b14812`, Phase 2-C `ac34dfad49a0ed33ab368ac50d438022f557df41`, and prior 128MiB study `a8d07dfc79266d5a33fb32f71ed20f30fe492d96`. A new branch `research/nscache-7nm-3nm-1gib-feasibility` was created from the latter in the existing checkout. All **686 prior tracked files** are protected byte-for-byte. No prior branch or main is modified or merged.

Four baseline configs/raw log sets (3nm/128MiB and 7nm/32MiB, both objectives) passed hash, source revision, completion, raw parse and binary identity checks. They were verified, not simulated again. Four new configs differ only in Capacity. Source 54-file identity, cell hashes and selected data capacity remain checked. The newly built binary SHA-256 is `038a0bd202c2497a735344a53a23e3c7cf1d11d665f53b25e29db11a12b0360a`, identical to the baselines. Exact toolchain/platform/build output is retained in logs/build/.

## Commands actually executed

From repository root:

```bash
git ls-remote origin refs/heads/main refs/heads/research/nscache-3nm-128mib-feasibility refs/heads/research/nscache-phase2c-512kib-slice
git switch -c research/nscache-7nm-3nm-1gib-feasibility
python3 NSCache_1GiB_Feasibility/scripts/prepare.py
bash NSCache_1GiB_Feasibility/scripts/build.sh
python3 NSCache_1GiB_Feasibility/scripts/run.py --node 3 --jobs 2 --timeout 1800
python3 NSCache_1GiB_Feasibility/scripts/run.py --node 7 --jobs 2 --timeout 1800
python3 NSCache_1GiB_Feasibility/scripts/analyze.py
python3 -m unittest discover -s NSCache_1GiB_Feasibility/tests -v
```

Both runner commands were repeated to verify resume: all four returned their original completed metadata without launching a new model process; exactly four actual attempt directories remain. Analysis was run twice consecutively and seven generated files (six result CSV/JSON files and experiment_report.md) were byte-identical; hashes are recorded in provenance/regeneration_validation.json.

Manifest generation/check commands:

```bash
python3 NSCache_1GiB_Feasibility/scripts/manifest.py
python3 NSCache_1GiB_Feasibility/scripts/manifest.py --check --require-binary
```

## Actual execution coverage

- **4/4 primary 1GiB cases FINISHED**, exit 0, Finished!, empty stderr, no timeout or missing energy. 3nm ReadLatency 173.99s; 3nm ReadDynamicEnergy 175.79s; 7nm objectives approximately 169.94s each. max RSS 15148KiB (3nm), 15132KiB (7nm), measured per child by Linux wait4; CPU and UTC timestamps retained.
- Both 3nm attempts finished before either 7nm started. Timestamp-derived concurrency never exceeds two. Timeout is 1800s per case; configurable, no hard memory cap claimed.
- No 512MiB/256MiB diagnostics were justified or executed because all primary cases succeeded. No source patch, bank relaxation, capacity guard bypass or arbitrary parameter search was performed.
- Selected full bank×subarray×mat capacity independently equals **1073741824 bytes** in every primary case. Printed “1GB” is the model's binary-unit display, not a confirmation of the paper unit convention.
- Energy/latency/area/leakage/feasible count and full Data/Tag organization, activation, MUX, wires/buffers are parsed from raw logs. H-tree routing is a subset of bank energy; nested Mat/Subarray totals are not added again. Bank print resolution is derived separately for pJ/nJ/fJ; summary/bank rounding bounds are not tuned to a discrepancy.

## Tests and interpretation

**14 tests passed**: capacity-only matrix and binary units; actual execution status/order; concurrency; printed bank resolution; historical baselines not rerun; independent raw energy conversion/data capacity/write latency; hierarchy closure; matched-precision raw SF and capacity ratios; completed resume without launching; source/cell/binary/history identity and reference exclusion from run/prepare; raw-only regeneration without binary and determinism; corrupt-log rejection without modifying outputs; timeout fixture with missing energy/SF; manifest tamper detection. Failure fixtures run only in temporary copies and are not actual model failures.

The analyzer's exit 0 means valid processing of terminal evidence and can include failed experiments; actual coverage is separately reported. The published scalar comparison is numeric only: author config, operation, access width, normalization, energy boundary and GB convention remain unconfirmed. 1024MiB is an explicitly labeled approximation to paper 1GB. No LLMET, hardware or pure-process validation claim follows.

Before every push, review staged artifacts and outgoing commit content/scope. Only independently generated NS-Cache results, public model/tool metadata and the task-described public LLMET scalars are allowed. No user GPU measurement/coefficient/calibration/normalization/scaling inputs or recoverable private derivatives are used or published. See provenance/publication_review.json.
