# NS-Cache L2 32MiB / 256-bit archive — exploratory 8-run evidence

This handoff package was assembled from a local 2026-11-12 exploratory study, **not** a verified GitHub Phase 2-A run. It contains eight 32MiB (14/7/5/3nm × ReadLatency/ReadDynamicEnergy) input `.cfg` files, their original stdout/stderr, available run JSON metadata, an analysis CSV and SHA-256 listing. No recovered source tree is included; NS-Cache source/binary provenance must be verified against the current GitHub source before importing as a reproducibility baseline. Missing metadata must be marked as missing; do not fabricate.

Config `-WordWidth (bit): 256` is a **32-byte model cache-line access**, not a GPU 32-byte sector within a 128-byte line.

**Precision warning:** `capacity_comparison_256bit.csv` has `read_summary_pj` from NS-Cache's rounded 0.001nJ cache summary; `read_bank_sum_pj` is Data+Tag bank energy printed at a finer precision. `read_pj_per_bit` was computed using *bank-sum energy/256*. Therefore 103.220/256 = 0.403203125 (displayed 0.4032) at 1MiB and 489.648/256 = 1.9126875 (displayed 1.9127) at 32MiB for 14nm/ReadLatency. Compare like with like.

All data is NS-Cache modeled output, NOT measured GPU energy. The source snapshot in the original local study is a recovered copy; independently verify byte equivalence and license before any public redistribution. Preserve this imported archive unchanged.

Source used in local study: recovered NS-Cache C++/configuration tree, see original upstream: https://github.com/neurosim/NS-Cache ; source revision should be checked (not assumed) against `2fdcbf093f806bc9a28964aca8402c42738d58e5`.
