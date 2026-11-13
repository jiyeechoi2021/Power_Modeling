# NS-Cache 3nm 128MiB feasibility / LLMET reference study

This is a controlled capacity study, **not parameter fitting or validation of the LLMET paper**. Both validated 3nm/32MiB Phase 2-B objectives are verified from existing raw logs. Two new 128MiB configs change only Capacity=32→128MiB, with source, SRAM cell, WordWidth=256bit, 16-way/Normal/300K/LOP/H-tree/bank/wire/pruning/buffer controls unchanged. No author-original configuration is available.

- [Method, actual results, organization, public-reference comparison and next steps](reports/experiment_report.md)
- [Validation and provenance](reports/validation.md)
- [Config-only diffs and hashes](provenance/cases.json)
- [Reference inventory and missing author materials](provenance/reference_inventory.json)

## Scope and results

Both new 128MiB executions finish with exit 0 and Finished!, no guard bypass or structural input changes. ReadLatency summary read/write are 369/246pJ per 256bit model access; ReadDynamicEnergy gives 349/228pJ. Both 32MiB historical baselines are verified, not rerun. Full read/hit/write latency, area/leakage, bank/mat/activation/mux/wire/buffer and hierarchy-safe data/tag/routing breakdown are retained. Large selected mat geometries pass logical bit-capacity accounting but do not establish physical macro accuracy.

0.917pJ/bit is the **reported public LLMET Table 2 reference supplied in the task**, not a private GPU coefficient. The original paper URL/DOI/PDF and author config/output are unavailable locally; public arXiv lookup returned 403. Reference operation/aggregation/WordWidth and MB-versus-MiB remain unknown. All model/reference comparisons are labeled numeric only. No close row is selected as “reproduced,” no normalization denominator is fitted, and no read/write averaging is used to match the scalar.

## Reproduce (repository root)

```bash
python3 NSCache_3nm_128MiB_Feasibility/scripts/prepare.py
bash NSCache_3nm_128MiB_Feasibility/scripts/build.sh
python3 NSCache_3nm_128MiB_Feasibility/scripts/run.py --jobs 2 --timeout 1800
python3 NSCache_3nm_128MiB_Feasibility/scripts/analyze.py
python3 -m unittest discover -s NSCache_3nm_128MiB_Feasibility/tests -v
python3 NSCache_3nm_128MiB_Feasibility/scripts/manifest.py
python3 NSCache_3nm_128MiB_Feasibility/scripts/manifest.py --check --require-binary
```

Only the two predefined 128MiB objectives can run; shared lock prevents overlapping CLI pools. Two-worker maximum, 1800s wall timeout, Linux wait4 per-child CPU/max RSS/elapsed and exit status. No hard memory cap is claimed. Attempts preserve stdout/stderr/environment/metadata/hashes. Resume reuses only completed identical input/cell/binary/output/environment identities. Failed/timeout cases are not assigned energy. Historical 32MiB is read-only.

Raw analysis needs no local binary, no existing derived result files and no GPU/author measurement inputs. `energy_results.csv` holds both summary/fine pJ/access and pJ/bit, read/hit+write latency, area, leakage and status; `capacity_comparison.csv` preserves precision-matched operands/ratios; `llmet_reference_comparison.csv` explicitly records unknown reference semantics; `energy_breakdown.csv` and `organization_and_metadata.json` preserve component scopes and organization. Row paths are repository-root relative.

Cache-summary energy is printed at 1pJ resolution. Fine data+tag sums are separately normalized by 256; neither precision is substituted for the other. Routing is already included in bank totals; nested mat/subarray values are not added again. Effective pJ/bit is complete model-access normalization, not SRAM bitcell energy, GPU measurements or a 128B-line sector implementation.

Source/cells are reused read-only from Phase 1, revision `2fdcbf093f806bc9a28964aca8402c42738d58e5`, 54 hashes verified. GNU g++14.2.0, C++17 -Wall -O3 -mtune=native. Retain CC BY-NC 4.0 and inherited notices in the existing source; no relicensing. Binary, config, cell, source, environment and raw artifacts have recorded hashes. Full validation checks the local binary when requested; raw-only regeneration works without it.

All **647** files in the verified Phase 2-C base `ac34dfad49a0ed33ab368ac50d438022f557df41` remain unchanged. New work is confined to NSCache_3nm_128MiB_Feasibility and branch research/nscache-3nm-128mib-feasibility. No old branch/main is modified or merged.

## Confidentiality and publication

Public artifacts contain independently generated NS-Cache outputs, model inputs/source identities and the task-described published LLMET scalar only. No private GPU measurement, fitted coefficient, calibration, normalization or reconstructible derivative is read, committed or disclosed. Author email contents are not retained. Review staged contents and outgoing commit diffs before any push; numerical result lineage must resolve exclusively to verified NS-Cache raw logs or the clearly labeled reported public reference.

Recommended next work is author-original config/output/source/normalization confirmation followed by a separately scoped replay. No arbitrary parameter grid, source patch, alternative architectural setting, GPU hardware validation or Rubin prediction is performed here.
