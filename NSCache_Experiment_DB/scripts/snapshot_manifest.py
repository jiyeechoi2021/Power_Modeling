"""Hash reviewable DB artifacts; omit transient build/runtime state and this manifest."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'provenance/artifact_SHA256SUMS.txt'
files=[]
for p in sorted(ROOT.rglob('*')):
    parts=p.relative_to(ROOT).parts
    if p.is_file() and parts[0] not in ('build','runtime') and '__pycache__' not in parts and p!=OUT:
        files.append(p)
OUT.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in files))
(ROOT/'provenance/directory_inventory.txt').write_text('\n'.join(str(p.relative_to(ROOT)) for p in files if p.name!='directory_inventory.txt')+'\n')
# Recompute after writing the inventory so every stored digest describes current bytes.
files=sorted(set(files+[ROOT/'provenance/directory_inventory.txt']))
OUT.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in files))
print(f'Hashed {len(files)} artifacts')
