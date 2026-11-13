# NS-Cache 7nm/3nm 1GiB feasibility

Controlled independent model study, derived from verified 3nm/128MiB and 7nm/32MiB baselines. Only Capacity changes; both ReadLatency and ReadDynamicEnergy are retained. Original author configurations are unavailable. This is not parameter fitting or LLMET validation.

Exact modeled capacity: **1024MiB = 1073741824 bytes**. The paper's “1GB” convention is unconfirmed; 1024MiB is an explicitly documented approximation. WordWidth=256bit is a 32B model cache line, not GPU sector modeling with shared 128B metadata.

See [report](reports/experiment_report.md), [validation](reports/validation.md), [protocol](provenance/protocol.json), [capacity-only diffs](provenance/cases.json), [raw energy table](results/energy_results.csv), [cross-node SF](results/cross_node_sf.csv), [public-reference comparison](results/llmet_reference_comparison.csv), and [full organization/breakdown](results/organization_and_metadata.json).

## Reproduction

From repository root, using Python standard library, GNU g++ and make:

```bash
python3 NSCache_1GiB_Feasibility/scripts/prepare.py
bash NSCache_1GiB_Feasibility/scripts/build.sh
python3 NSCache_1GiB_Feasibility/scripts/run.py --node 3 --jobs 2 --timeout 1800
python3 NSCache_1GiB_Feasibility/scripts/run.py --node 7 --jobs 2 --timeout 1800
python3 NSCache_1GiB_Feasibility/scripts/analyze.py
python3 -m unittest discover -s NSCache_1GiB_Feasibility/tests -v
python3 NSCache_1GiB_Feasibility/scripts/manifest.py --check --require-binary
```

Existing completed runs resume only after config/cell/binary/stdout/stderr/environment hash checks. Each new model attempt is separately timestamped. The default is at most two simultaneous processes and 1800s per case; timeout is configurable. A hard memory cap is not applied. The runner enforces completion of both 3nm primary attempts before 7nm. Do not rerun build merely to analyze logs; build logs/environment are retained evidence. Source and prior study bytes are verified, never edited.

Raw-only regeneration requires no binary: run `scripts/analyze.py` from the command above, followed by `scripts/manifest.py --check` without `--require-binary`. After intentional new artifacts/results changes, regenerate the manifest with `scripts/manifest.py` and review changes; do not use manifest regeneration to conceal changes to existing evidence.

A failed run has no fabricated energy/SF. Analyzer exit 0 means valid processing of terminal evidence, which may include explicit failures; consult status columns. Exit 1 denotes unfinished coverage and exit 2 invalid evidence. If a primary fails, separately justify/register 512/256MiB capacity-only diagnostic inputs, retaining the primary failures and their metadata. These smaller cases must never replace missing 1GiB values or be described as the paper capacity. No structural/source/bank relaxation is authorized by this protocol.

## Precision and interpretation

E_effective_bit = E_model_access / 256. SF(7→3) = E_3nm/E_7nm, matched capacity, objective, operation and precision. Read and write remain separate. Summary energy has 1pJ resolution; bank energy resolution depends on the printed pJ/nJ/fJ unit. The bank sum is a separate printed estimate, with rounding bounds, not universally a higher-precision truth. Routing is already included in Data+Tag banks; nested Mat/Subarray energy is not added again.

Task-described public LLMET Table 2 references are 7nm 2.780 and 3nm 2.420pJ/bit (ratio 2.420/2.780). Original operation, architecture, normalization and capacity convention remain unconfirmed. Numerical agreement would not establish reproduction, pure process scaling or hardware accuracy. Physical validity of the large selected organizations is unverified.

Public artifacts contain only independent NS-Cache outputs, public model/tool metadata and the task-described published reference scalars. No private GPU measurements, fitted coefficients, calibration/normalization factors or reconstructible private derivatives are inputs or outputs. Review staged changes and outgoing commits before every push.

Inherited NS-Cache [license and provenance](../NSCache_Experiment_DB/README.md) and CC BY-NC notices continue to apply; no source is relicensed or modified. Earlier studies and main remain unchanged; no merges.
