# Provenance and limitations

## Recovered original artifacts

- `nscache_source/src/` and `nscache_source/config/New_Configs/` were recovered from a temporary Google Drive document named `_temporary_NSCache_source_transfer_20261110`; each record held the exact file path and content of the source snapshot used around the original study. These files were **not independently byte-verified against upstream Git commit**.
- The 16 reported output rows were recovered from `NSCache_14_7_5_3_L1_L2_Experiment_20261110.xlsx`; their CSV/JSON rendering preserves the recorded numbers. This is a **derived table**, not the original console output.

## Reconstructed (new) artifacts

- 16 `.cfg` files were reconstructed by editing the recovered upstream configuration templates according to the workbook's recorded capacity (L1 128 KiB, L2 1 MiB), associativity (L1 8-way, L2 16-way), word width 512-bit, 4x4 bank, H-tree routing, 300K, node-specific `.cell`, and optimization objective.
- Actual NS-Cache execution on the reconstructed files generated the `rerun_logs/` console logs. **These are new 2026-11-10 rerun outputs, NOT the historical original logs.**
- `run_inventory.csv` names each run, whether the rerun log exists, and whether every selected metric matches the workbook. Missing rerun logs must not be described as executed here.

## Not recovered

- Original 16 generated `config/study/*.cfg` files.
- Original 16 console logs and original execution timestamps.
- Historical machine's exact binary artifact and immutable version-control tree identity. A commit ID is reported in the workbook but the recovered snapshot has not been hash-verified against it.

## Copyright

The model's upstream project is `neurosim/NS-Cache` (CC BY-NC 4.0). Review upstream license and comply with attribution/non-commercial restrictions before using or publishing the bundled source. https://github.com/neurosim/NS-Cache
