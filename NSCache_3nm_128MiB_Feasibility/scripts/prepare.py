"""Two controlled 3nm capacity-only derivatives, not a parameter fit."""
import difflib,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
BASE='ac34dfad49a0ed33ab368ac50d438022f557df41'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 cases=[]
 for opt in ('ReadLatency','ReadDynamicEnergy'):
  source=P/'NSCache_Phase2B/configs'/f'L2_3nm_32MiB_{opt}.cfg';raw=source.read_bytes();assert raw.count(b'-Capacity (MB): 32')==1
  derived=raw.replace(b'-Capacity (MB): 32',b'-Capacity (MB): 128');cfg=R/'configs'/f'L2_3nm_128MiB_{opt}.cfg'
  if cfg.exists() and cfg.read_bytes()!=derived:raise ValueError('preserve existing config')
  cfg.write_bytes(derived);cell=P/'NSCache_Experiment_DB/configs/New_Configs/SRAM_cell_3nm.cell'
  cases.append(dict(run_id=cfg.stem,node_nm=3,objective=opt,capacity_mib=128,capacity_bytes=134217728,width_bits=256,config=str(cfg.relative_to(R)),config_sha256=sha(cfg),source_config=str(source.relative_to(P)),source_config_sha256=sha(source),cell=str(cell.relative_to(P)),cell_sha256=sha(cell),source_revision='2fdcbf093f806bc9a28964aca8402c42738d58e5',derivation='Capacity (MB): 32 -> 128 only; reconstruction, not author configuration',diff=''.join(difflib.unified_diff(raw.decode().splitlines(True),derived.decode().splitlines(True),fromfile=str(source.relative_to(P)),tofile=str(cfg.relative_to(P))))))
 (R/'provenance/cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 hashes={}
 for n in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=P,text=True).splitlines():
  original=subprocess.check_output(['git','show',BASE+':'+n],cwd=P);assert (P/n).read_bytes()==original,n;hashes[n]=hashlib.sha256(original).hexdigest()
 (R/'provenance/protected.json').write_text(json.dumps(dict(base=BASE,sha256=hashes),indent=2)+'\n')
 src=json.loads((P/'NSCache_Experiment_DB/provenance/upstream_source_comparison.json').read_text())
 for f in src['files']:assert sha(P/'NSCache_Experiment_DB'/f['file'])==f['sha256']
 (R/'provenance/source_identity.json').write_text(json.dumps(src,indent=2)+'\n')
 print('Prepared 2 capacity-only cases; protected',len(hashes),'historical files; 54 source files verified')
if __name__=='__main__':prepare()
