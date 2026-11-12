# NS-Cache Phase 2-B — L2 capacity / organization

A separate study on `research/nscache-phase2b-l2-capacity-organization`, branched from verified Phase 2-A `820fe02`. Existing `work`, main, Phase 1 and Phase 2-A files/branches are preserved. All outputs are generic NS-Cache model quantities, not GPU measurements or Pure Process Scaling. No private GPU coefficients are included.

Read first: [feasibility gate](reports/feasibility_gate.md), [experiment report](reports/experiment_report.md), [assumptions and source evidence](reports/model_assumptions_and_limits.md), [validation](reports/validation.md).

## Gate and scope

Uploaded 32MiB archive: CRC/listed hashes pass, eight config/log pairs, seven metadata files. Source/cell tree absent and binary hash differs from the current build, so it is retained under `baseline_32MiB/` as external exploratory evidence; all eight 32MiB cases are rerun under verified current source. The 1MiB baseline is read from verified Phase 2-A logs.

6/20/25/40/50MiB inputs parse but abort with capacity violations. Their failures are preserved; no GPU-nominal energy or SF is fabricated. The supported fixed 32MiB sweep and a separately labeled 32MiB=4×8MiB local-partition control are executed. The latter is not an actual GPU topology or a substitute for 40/50MiB partitions. All required native bridge pairs/objectives and optional local-size probes are represented in coverage, including failures.

Exact units: model `Capacity (MB)` uses MiB (1024² bytes). 256bit is a 32B **model line**, not a GPU sector with shared 128B metadata. V100/A100/H100 capacity/process/device labels and source URLs/verification limits are in the assumptions report. Raw source is reused read-only from `../NSCache_Experiment_DB/source`, revision `2fdcbf093f806bc9a28964aca8402c42738d58e5`; preserve its CC BY-NC and inherited license notices.

## Commands (repository root)

```bash
python3 NSCache_Phase2B/scripts/prepare.py
bash NSCache_Phase2B/scripts/build.sh
python3 NSCache_Phase2B/scripts/run.py --stage smoke --jobs 2 --timeout 1800
python3 NSCache_Phase2B/scripts/run.py --stage fixed32 --jobs 2
python3 NSCache_Phase2B/scripts/run.py --stage unsupported_diagnostics --jobs 2
python3 NSCache_Phase2B/scripts/run.py --stage partition_control --jobs 2
python3 NSCache_Phase2B/scripts/analyze.py
python3 -m unittest discover -s NSCache_Phase2B/tests -v
python3 NSCache_Phase2B/scripts/manifest.py
python3 NSCache_Phase2B/scripts/manifest.py --check
```

The smoke and unsupported_diagnostics commands intentionally exit 1 when geometry probes fail; continue the remaining stages and retain their raw failure evidence. Do not relabel those runs as passing.

Run stages sequentially to keep a global maximum of two workers. The actual first run overlapped a fixed32 and control/diagnostic batch on five CPUs; raw metadata records actual timestamps/resources and the gate documents this. `unsupported_diagnostics` runs only as-yet-unattempted native probes; it does not keep retrying known identical failures. `--case` permits a deliberate single-case retry after diagnosing/changing a prerequisite. Attempts preserve failure/timeout/raw data. Resume checks config/cell/binary/environment/stdout/stderr hashes and only reuses completed runs. Max RSS is measured per child with Linux wait4 in KiB.

`build/`, `runtime/`, caches are ignored. Future builds use the correct Phase 2-B environment recipe; the first capture used a Phase 2-A helper template, explicitly corrected in `provenance/kickoff.json` without modifying original snapshots. Actual compile/link commands are in build stdout.

## Results and reproducibility

`results/l2_capacity_energy.csv` contains native and baseline coverage, status, capacity, config/log/metadata paths, timing/resources and both summary/fine bank energy and normalized pJ/bit. Failed measurements remain blank. `fixed_capacity_sf.csv` uses the same capacity/objective and summary precision. `gpu_nominal_bridge.csv` records unavailable requested bridges; `bridge_control_1_32MiB.csv` is the explicitly non-GPU positive algebra control. `partition_scenarios.csv` distinguishes failed GPU-sized scenarios from local controls. `energy_breakdown.csv` uses consistent bank and routing-subset levels; complete data/tag/mat/mux/wire/buffer strings remain in `parsed_results.json`.

All paths in result rows are relative to repository root. Raw analysis requires no binary/rebuild. Analysis exit 0 means complete processing with documented geometry failures, not that every case succeeded. Exit 1 denotes pending/unrun/timeouts; exit 2 rejects missing/corrupt evidence. Repeated analyses must generate byte-identical outputs. The independent archive CSV is never used as analysis input. `provenance/archive_audit.json` distinguishes integrity from source authenticity.

Main and old PRs are never merged. GitHub PR queries currently return GraphQL Forbidden; base selection is supported by current remote refs (main still ZIP-only). Draft PR description and compare URL will be supplied if API creation remains blocked.
