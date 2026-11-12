# NS-Cache Phase 2-C — 512KiB model slice candidate

Exactly **eight new 512KiB/256bit L2-like model runs**: 14/7/5/3nm × ReadLatency/ReadDynamicEnergy. Each run includes both read and write metrics. The 7nm smoke is included in the eight. No other capacity, P0–P3 intervention, GPU validation or Rubin projection is executed.

- [Feasibility gate](reports/feasibility_gate.md)
- [Complete results, SF, capacity/organization comparison and validity table](reports/experiment_report.md)
- [Validation commands and evidence](reports/validation.md)
- [Exact config derivation/source/cell hashes and diffs](provenance/cases.json)
- [Draft PR description](reports/pr_description.md)

## Reproduce (repository root)

```bash
python3 NSCache_Phase2C/scripts/prepare.py
bash NSCache_Phase2C/scripts/build.sh
python3 NSCache_Phase2C/scripts/run.py --stage smoke --jobs 1
python3 NSCache_Phase2C/scripts/run.py --stage remaining --jobs 2
python3 NSCache_Phase2C/scripts/analyze.py
python3 -m unittest discover -s NSCache_Phase2C/tests -v
python3 NSCache_Phase2C/scripts/manifest.py
python3 NSCache_Phase2C/scripts/manifest.py --check --require-binary
```

`-Capacity (KB): 512` is exactly 524288 bytes. Only that line changes from the matched 1MiB Phase 2-A config. Never use fractional integer-MB input. Source/cells remain read-only in Phase 1; licenses including CC BY-NC 4.0 and inherited notices are unchanged. Model source is pinned to upstream `2fdcbf093f806bc9a28964aca8402c42738d58e5`, verified with 54 digests.

Runner supports **only these eight cases** and gates remaining/all on the 7nm smoke. `--stage all` verifies resume of all eight, not additional configurations. A shared file lock serializes CLI batches; maximum two workers and default 1800s per run. Resume requires matching config/cell/binary/environment/stdout/stderr hashes. Preserve failed/timeout attempts; do not rerun identical failures without a changed prerequisite. Build/runtime/caches are ignored; original build and run metadata stay under logs/provenance.

## Outputs and precision

`slice_512kib_energy.csv`: eight statuses, summary/fine read/write pJ/access, effective pJ/bit, latency ns, leakage mW, area mm², solutions and source/config/log/metadata identities. `slice_512kib_scaling.csv`: 12 matched operation/transition rows with separate summary and bank-sum SF. `capacity_comparison.csv`: 32 capacity/node/objective cells; 1/8/32MiB are read-only historical_verified records, with four 8MiB 14nm/3nm cells explicitly MISSING_NOT_RUN. `slice_vs_1mib_ratios.csv`: 16 matched read/write capacity ratios with both precisions. `energy_breakdown.csv` and `organization_comparison.json`: consistent bank totals/routing subsets and full printed data/tag/mat/mux/wire/buffer/activation detail.

Paths inside result rows are repository-root relative. Analysis regenerates everything directly from raw logs without a local binary or old analysis CSV/JSON input. Exit 0 means all eight completed and evidence passed, exit 1 means partial coverage, exit 2 rejects invalid evidence. Source stdout summary has 1pJ resolution; finer data+tag totals are separate, never mixed across ratio operands. Routing is already included in bank totals. Leakage is power, not per-access energy.

`provenance/SHA256SUMS.txt` hashes all retained Phase 2-C artifacts except itself; file_inventory includes itself and manifest. Manifest verification also checks all 576 historical files, 54 source digests, case/cell inputs, and local compiled binary when present. Use `--require-binary` for full post-build validation. Raw-only analysis/checks can run without binary; the recorded binary hash remains archived. No prior manifest is regenerated.

## Interpretation and boundaries

Use **512KiB NS-Cache single-cache proxy / model slice candidate**, not “actual A100 slice energy.” Effective pJ/bit=modeled cache access/256 is not physical bitcell energy or GPU 32B-sector access energy. The model line is 32B; real sector/shared 128B-line metadata is not implemented. Node SF includes Vdd, cells, wires and selected organization, not pure process scaling.

The task cites [NVIDIA A100 whitepaper p.35](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf): two partitions with 40 nominal512KB slices each. Binary arithmetic 80×512KiB=40MiB motivates size only. Direct retrieval returned 403; source reread remains unverified. Never multiply single-access dynamic energy by 80 or claim GPU circuit/port/associativity/energy-boundary matching. No confidential GPU coefficients are included.

Source/base is verified Phase 2-B remote HEAD `6609b1a`. Only `NSCache_Phase2C/` changes; prior files/branches/main remain unchanged. Draft PR base is `research/nscache-phase2b-l2-capacity-organization`; head is `research/nscache-phase2c-512kib-slice`. Existing PRs are not edited or merged. API Forbidden is reported as a creation blocker, never a successful PR.

Deferred (not executed): other capacity sweeps/non-power-of-two model extension, V100/H100 topology reconstruction, sector/line implementation or private coefficient comparison, fixed-organization/Vdd campaigns, hardware validation and Rubin projection.
