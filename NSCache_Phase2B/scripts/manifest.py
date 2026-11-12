"""Verify frozen historical study; refresh/check Phase 2-B-only artifact hashes."""
import argparse,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(check=False):
 saved=json.loads((R/'provenance/protected.json').read_text())
 for n,h in saved['sha256'].items():
  if sha(P/n)!=h:raise ValueError('historical file changed: '+n)
 out=R/'provenance/SHA256SUMS.txt';inv=R/'provenance/file_inventory.txt'
 files=sorted(set([p for p in R.rglob('*') if p.is_file() and p.relative_to(R).parts[0] not in ('build','runtime') and '__pycache__' not in p.relative_to(R).parts[:-1]]+[out,inv]))
 if any(p.is_symlink() for p in files):raise ValueError('unexpected artifact symlink')
 listing=''.join(str(p.relative_to(R))+'\n' for p in files)
 if check:
  if inv.read_text()!=listing:raise ValueError('inventory stale')
 else:inv.write_text(listing)
 sums=''.join(f'{sha(p)}  {p.relative_to(R)}\n' for p in files if p!=out)
 if check:
  if out.read_text()!=sums:raise ValueError('hash manifest stale')
 else:out.write_text(sums)
 return len(saved['sha256']),len(files),len(files)-1
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
 try:old,files,hashes=snapshot(a.check)
 except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')
 print('Protected',old,'historical files; inventory',files,'hashes',hashes,'verified' if a.check else 'updated')
