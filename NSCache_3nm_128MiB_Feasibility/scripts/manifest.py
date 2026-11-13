"""3nm 128MiB study artifact manifest plus historical/source/cell and optional binary verification."""
import argparse,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify_inputs(require_binary=False):
 saved=json.loads((R/'provenance/protected.json').read_text())
 for n,h in saved['sha256'].items():
  if sha(P/n)!=h:raise ValueError('historical file changed: '+n)
 for c in json.loads((R/'provenance/cases.json').read_text()):
  for p,k in [(R/c['config'],'config_sha256'),(P/c['cell'],'cell_sha256'),(P/c['source_config'],'source_config_sha256')]:
   if sha(p)!=c[k]:raise ValueError('config/cell/source mismatch: '+str(p))
 for item in json.loads((R/'provenance/source_identity.json').read_text())['files']:
  if sha(P/'NSCache_Experiment_DB'/item['file'])!=item['sha256']:raise ValueError('source identity mismatch')
 binary=R/'build/nsc'
 if require_binary and not binary.exists():raise ValueError('local binary required for full validation')
 if binary.exists() and sha(binary)!=(R/'provenance/binary.sha256').read_text().split()[0]:raise ValueError('compiled binary digest mismatch')
 return len(saved['sha256'])
def snapshot(check=False,require_binary=False):
 old=verify_inputs(require_binary)
 out=R/'provenance/SHA256SUMS.txt';inv=R/'provenance/file_inventory.txt'
 files=sorted(set([p for p in R.rglob('*') if p.is_file() and p.relative_to(R).parts[0] not in ('build','runtime') and '__pycache__' not in p.relative_to(R).parts[:-1]]+[out,inv]))
 if any(p.is_symlink() for p in files):raise ValueError('unexpected artifact symlink')
 listing=''.join(str(p.relative_to(R))+'\n' for p in files)
 if check:
  if inv.read_text()!=listing:raise ValueError('inventory stale')
 else:inv.write_text(listing)
 sums=''.join(f'{sha(p)}  {p.relative_to(R)}\n' for p in files if p!=out)
 if check:
  if out.read_text()!=sums:raise ValueError('artifact hashes stale')
 else:out.write_text(sums)
 return old,len(files),len(files)-1
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--require-binary',action='store_true');a=p.parse_args()
 try:old,files,hashes=snapshot(a.check,a.require_binary)
 except (OSError,ValueError) as e:p.exit(1,str(e)+'\n')
 print('Protected',old,'historical files; inventory',files,'digests',hashes,'verified' if a.check else 'updated')
