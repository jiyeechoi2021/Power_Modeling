# NS-Cache Phase 2-C — 512KiB Slice Baseline (Codex execution specification)

**Scope is deliberately limited to this first Phase 2-C slice baseline. Do not execute the remaining P0–P3 roadmap items, GPU nominal-size experiments, 128B/32B sector implementation, Vdd/organization intervention, hardware validation, or Rubin forecasting in this task.**

## 0. Goal and scientific interpretation

Produce an independently reproducible **512KiB single-cache-model baseline** under four generic NS-Cache nodes (14/7/5/3nm), two objectives (`ReadLatency`, `ReadDynamicEnergy`), `WordWidth=256bit`, for L2-like model settings inherited from Phase 2-A. The eight successful runs (if feasible) each generate read AND write metrics; there are **8 configurations/runs, not 16**.

Why 512KiB? NVIDIA's A100 architecture whitepaper p.35 states the 40MB L2 comprises two partitions, each with 40 L2 cache slices, and each slice is 512KB (80×512KB = 40MB). Original: https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf . This justifies the nominal size of an exploratory **A100-oriented slice proxy**, NOT equivalence to an actual A100 L2 slice circuit, access topology, sector size, port count, 16-way associativity, banking, or energy boundary. The whitepaper source text should be cited in reports, not copied verbatim at length. Use the terms `512KiB NS-Cache single-cache proxy` and `model slice candidate`.

## 1. Source of truth, branch and protection

Repository: `jiyeechoi2021/Power_Modeling`.

At task start, fetch actual remote refs and PR states. Expected (verify rather than assume):
- Phase 1 `research/nscache-phase1-reproduction` → `26ba7529fcb356c82b1813b6030f54746ccb3cc3`
- Phase 2-A `research/nscache-phase2a-256bit` → `820fe02a95009985510c4810c2044aaa8c7e610e`
- Phase 2-B `research/nscache-phase2b-l2-capacity-organization` → `6609b1ac56d43fa7d06a5e3b79cd678f6d14a492`
- PR #1/#2/#3: separate existing draft PRs; never merge, rebase, reset, force-push, or edit.

If remote Phase 2-B head has changed, log actual head and inspect the diff before proceeding; if the expected source/results cannot be grounded, stop safely and report. Start a new branch **from the verified Phase 2-B remote head** named `research/nscache-phase2c-512kib-slice`. Do not build on a default Codex `work` branch; preserve that branch and all historical paths. All new committed files must reside in `NSCache_Phase2C/`. Existing files of Phase 1, Phase 2-A, Phase 2-B, root ZIP, `main`, and all earlier branches must remain bitwise unchanged. No PR merge.

The Phase 2-B source provenance is original NS-Cache upstream revision `2fdcbf093f806bc9a28964aca8402c42738d58e5`, matched by 54 source/Makefile hashes; same recovered source and SRAM cells are read-only. Licenses (including CC BY-NC 4.0 and inherited notices) must remain intact. Do not copy NVIDIA proprietary material or confidential GPU coefficients into this public repository.

## 2. Feasibility gate first

1. Confirm clean worktree, `git remote -v`, branch HEADs, and relevant previous PR states (indicate API restrictions if any).
2. Inspect `NSCache_Phase2A/configs/phase2_256bit/L2_7nm.cfg`, equivalent 14/5/3nm L2 configs, `NSCache_Phase2B` scripts/validation, source parser, and cell files. Check SHA-256 against Phase 2-B provenance.
3. Verify the input parser accepts `-Capacity (KB): 512` (in `InputParameter.cpp`, `-Capacity (KB)` is an integer times 1024); **do not** use `-Capacity (MB): 0.5` because the parser reads integer MB. For 512KiB use EXACTLY `524288 bytes` and do not round to 1MiB.
4. Confirm `WordWidth=256bit` so the modeled line/access is 32B, `Associativity=16`, `CacheAccessMode=Normal`, `DeviceRoadmap=LOP`, `Temperature=300K`, H-tree, `ForceBankA=4x4`, internal sensing and original pruning/buffer/wires/cell/node-specific options. **Only the capacity should change** relative to the matching 1MiB Phase 2-A configuration, except provenance comments identifying the derived experiment. Verify the diff programmatically and retain it.
5. Compile the unmodified source using the existing Phase 2-B recipe and record compiler, flags, source/cell/binary hashes. Use a smoke test for `7nm / ReadLatency / 512KiB`; check exit 0, `Finished!`, expected capacity/width and a parsed full results summary. If it fails, preserve stdout/stderr/error/metadata; diagnose without removing capacity guards, changing organization constraints, or altering source. Do not invent data. Only execute remaining combinations if feasible as specified below; mark blocked cases explicitly.

## 3. Actual experiment matrix — strictly 8 configurations

| Case group | Nodes | Capacity | WordWidth | Objectives | Executions |
|---|---|---|---|---|---:|
| Phase 2-C / L2 512KiB | 14, 7, 5, 3 nm | **512KiB** | 256bit | ReadLatency, ReadDynamicEnergy | **4 × 2 = 8** |

The smoke run counts as one of the eight if its configuration, source/binary and hash provenance agree; never create duplicate fake attempts. Keep exactly two concurrent workers maximum, 1800s timeout per run initially, capture exit, elapsed time, CPU and max RSS; retry a true failure only after identifying a changed prerequisite, keeping the earlier failure log. If any case is unsupported, report as failed/unsupported, not 0pJ or skipped-with-success. Avoid changing per-case node SRAM cells or optimization setting to obtain a desired answer.

Each run must parse:
- Summary cache-hit **Read** and **Write Dynamic Energy** (pJ/model access, source stdout is nJ/access ×1000)
- Separately displayed Data bank and Tag bank Read/Write energy, and **routing subsets** (avoid double counting routing within bank totals)
- Summary-vs-fine `Data+Tag` difference due to output rounding (store both, do not mix precision in ratios)
- Effective energy pJ/bit = `E_model_access / 256`, clearly labeled as an effective **32B model line**, NOT physical bitcell energy or GPU 32B sector-access energy
- Hit latency (ns), leakage **power** (mW), area (mm²), feasible design solutions
- Data/Tag bank, subarray, mat, mux, wire, buffer/activation information printed in stdout; note source limitations if an item is absent
- Complete raw logs/configs/checksums, binary/source/cell/environment metadata.

## 4. Comparison and reporting — analysis only, no extra runs

Automatically read existing verified data without modifying it:
- Phase 2-A L2 **1MiB/256bit** runs for four nodes × two objectives.
- Phase 2-B L2 **8MiB/256bit** local controls for 7 and 5nm, and **32MiB/256bit** runs for four nodes × two objectives.

For matched node/objective/operation and like precision, report:
1. New 512KiB absolute Read/Write energy and pJ/bit, latency, leakage, area, full Data/Tag/Routing breakdown.
2. 512KiB Fixed-Capacity read/write node SF: `SF_E(a→b)=E(512KiB,b)/E(512KiB,a)` for 14→7, 7→5, 5→3; SF is dimensionless. **This is node/cell/Vdd/selected-organization sensitivity, not pure process scaling.**
3. Capacity ratio `E(512KiB,node)/E(1MiB,node)` on identical node/objective/operation and precision. Existing 8/32MiB should be shown as a reference capacity trajectory where records exist, with provenance labels `historical_verified`; do not silently interpolate missing 8MiB 14nm/3nm.
4. Organization/latency tradeoff across optimization objectives and capacity. Explain whether the optimizer selects different Data/Tag topology, without attributing all change to SRAM bit count.
5. A100 40MiB ≈ 80 × 512KiB high-level hardware hierarchy from official source. **Do not multiply 512KiB single-access dynamic energy by 80** or claim it predicts A100 GPU energy. Total leakage and area would require explicit replicated hardware counts and shared overhead (outside scope).
6. An explicit interpretation/validity table: direct run result / derived arithmetic / externally documented A100 hierarchy / unvalidated physical equivalence / deferred work.

Precision policy: all model stdout summary energies have 0.001nJ = 1pJ resolution; track the finer bank sums separately. Never calculate a ratio with one operand rounded and the other operand from a fine bank sum. Check equality and identity to the precision supported by sources.

## 5. Directory and output contract

Create only `NSCache_Phase2C/` with logically minimal but complete subdirectories:

```
NSCache_Phase2C/
  README.md
  configs/                         # 8 cfgs, each derived from verified matching Phase 2-A cfg
  scripts/                         # self-contained prepare/build/run/analyze/manifest/test helpers
  logs/                            # stdout, stderr, metadata for each attempt
  provenance/                      # refs/commit, source/cell/config/binary/checksums, environment
  results/
    slice_512kib_energy.csv        # all 8 statuses; summary & fine values + units
    slice_512kib_scaling.csv       # matched node transitions and evidence
    capacity_comparison.csv        # 512KiB vs 1/8/32MiB with missing cells explicit
    energy_breakdown.csv           # Data/Tag/Routing nested accounting
    organization_comparison.json  # full parsed structures and raw paths
  reports/
    feasibility_gate.md
    experiment_report.md
    validation.md
    pr_description.md
  tests/
```

Actual filenames may change where warranted; list the final inventory precisely. CSVs must contain source/config/log references, status flags and units; no unsuccessful values should be fabricated. All results must be reproducible by analyzing raw logs alone, without a local NS-Cache binary. Preserve read/write separation. Make generated files deterministic across two consecutive analysis runs. Add tests for correct KB parsing, 512KiB config derivation, exactly 8-case matrix, correct unit conversion, missing/failed-run behavior, no double counting routing, scaling/matched-precision arithmetic, checksum/tamper handling, historical-file preservation, and resume idempotence.

## 6. Stop conditions, quality gate and delivery

Mandatory validations:
- Every configured case has exactly one final status + raw evidence; report actual successful/failed counts.
- All successful runs exit 0 and contain `Finished!`; data/tag summation and rounding audits pass.
- Prior Phase 1/2-A/2-B tracked-file hashes identical to verified Phase 2-B head (not only `git status clean`).
- SHA-256 manifest verifies config/logs/source/cells/binary/results, excluding manifest self-hash.
- Unit tests pass, result generation repeated with byte-identical hashes, provenance and source version recorded.
- If any condition fails, preserve logs, isolate the limitation and report partial results; do not claim full success.
- Write a professional research report distinguishing model result, algebraic SF, source-verified A100 hardware fact, modeling assumptions, and unresolved work. Do not publish confidential GPU unit-energy coefficient values to GitHub.

Commit and push **only** the new Phase 2-C branch. Create a Draft PR **base = `research/nscache-phase2b-l2-capacity-organization`**, head = `research/nscache-phase2c-512kib-slice`; never merge. If GitHub API returns `Forbidden`, provide the verified head SHA, comparison URL and the full PR description for the user/ChatGPT to create it. Do not modify earlier PRs.

**Final report to user must include:** (a) Feasibility and count of 8 planned runs, (b) complete 512KiB energy/SF data or failures, (c) capacity/organization comparison from verified references, (d) validation counts and protected artifact counts, (e) new branch/commit/PR URL or creation blocker, (f) precise deferred P0–P3 items, explicitly NOT executed.

## 7. Work that must remain deferred

No additional Cache Capacity sweeps beyond the 512KiB configurations; no new non-power-of-two capacity model extension; no V100/H100 slice topology reconstruction; no GPU L2 sector/line implementation or confidential energy coefficient comparison; no fixed-organization/Vdd sensitivity campaigns; no Rubin projection. These are later separate P0/P1/P2/P3 follow-ups, not part of this eight-run Phase 2-C task.
