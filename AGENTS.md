# Research rules

- Use the existing checkout; do not create a worktree unless requested. Work on a research branch and never merge directly into main.
- Preserve the original ZIP and recovered source/configuration bytes. Register every derived input and change separately with provenance and hashes.
- NS-Cache outputs are modeled generic SRAM/cache quantities, not NVIDIA GPU measurements or validated process-only ground truth.
- Distinguish recovered source/default cells, reconstructed experiment inputs, recorded workbook-derived results, bundled prior reruns, and newly executed attempts.
- Never fabricate missing metrics, logs, execution success, original historical provenance, or source revision evidence. Preserve failed and timed-out attempts.
- Keep original 256bit 7nm reproduction inputs. The separate 512bit diagnostic is not a historical reconstruction claim and must never replace the reproduction rows silently.
- Check access/line width, capacity, associativity, data/tag organization, ports, voltage, temperature, constraints and optimization before comparing nodes. Record unknown conditions as unknown.
- Separate L1/L2, read/write dynamic energy, leakage power, area and latency. Always label units, formulas, printed precision and tolerance.
- Do not tune inputs to match recorded numbers. Isolate causes using documented one-factor experiments and retain original failures/disagreements.
- Do not add private GPU measurements, unpublished correction factors or confidential material. Do not produce Rubin final predictions in Phase 1.
- Retain source copyrights, CC BY-NC 4.0 notices and inherited license files. This is noncommercial research; do not relicense upstream source.
- Standard workflow: see NSCache_Experiment_DB/README.md. Python standard library, GNU g++ and make suffice. Analyzer exit 1 is expected for this dataset's four documented mismatches; do not suppress or relabel it as a pass.
