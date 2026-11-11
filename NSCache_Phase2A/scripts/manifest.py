"""Check immutable Phase 1 baseline and snapshot only Phase 2 artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def preserve():
    saved=json.loads((ROOT/'provenance/phase1_preservation.json').read_text())
    for name,digest in saved['sha256'].items():
        if sha(ROOT.parent/name)!=digest:raise ValueError(f'Phase 1 file changed: {name}')
    return len(saved['sha256'])


def snapshot(check=False):
    protected=preserve()
    out=ROOT/'provenance/SHA256SUMS.txt';inventory=ROOT/'provenance/file_inventory.txt'
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(x in ('build','runtime','__pycache__') for x in p.relative_to(ROOT).parts[:-1]))
    files=sorted(set(files+[out,inventory]))
    if any(p.is_symlink() for p in files):raise ValueError('unexpected artifact symlink')
    listing=''.join(str(p.relative_to(ROOT))+'\n' for p in files)
    if check:
        if inventory.read_text()!=listing:raise ValueError('Phase 2 inventory is stale')
    else:inventory.write_text(listing)
    sums=''.join(f'{sha(p)}  {p.relative_to(ROOT)}\n' for p in files if p!=out)
    if check:
        if out.read_text()!=sums:raise ValueError('Phase 2 SHA-256 manifest is stale')
    else:out.write_text(sums)
    return protected,len(files),len(files)-1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    try:protected,files,digests=snapshot(args.check)
    except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')
    print(f'Phase 1 protected {protected}; Phase 2 inventory {files}, hashes {digests}; '+('verified' if args.check else 'updated'))
