"""Prepare exactly eight capacity-only 512KiB derivatives and protect the remote base."""
import difflib,hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
BASE='6609b1ac56d43fa7d06a5e3b79cd678f6d14a492'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 cases=[]
 for n in (14,7,5,3):
  cell=P/'NSCache_Experiment_DB/configs/New_Configs'/f'SRAM_cell_{n}nm.cell'
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   source=P/'NSCache_Phase2A/configs/phase2_256bit'/f"L2_{n}nm{('_ReadEnergy' if opt=='ReadDynamicEnergy' else '')}.cfg"
   raw=source.read_bytes();assert raw.count(b'-Capacity (MB): 1')==1
   derived=raw.replace(b'-Capacity (MB): 1',b'-Capacity (KB): 512');name=f'L2_{n}nm_512KiB_{opt}';cfg=R/'configs'/(name+'.cfg')
   if cfg.exists() and cfg.read_bytes()!=derived:raise ValueError('preserve unexpected file: '+str(cfg))
   cfg.write_bytes(derived)
   cases.append(dict(run_id=name,node_nm=n,objective=opt,capacity_kib=512,capacity_bytes=524288,width_bits=256,group='slice512',config=str(cfg.relative_to(R)),config_sha256=sha(cfg),source_config=str(source.relative_to(P)),source_config_sha256=sha(source),cell=str(cell.relative_to(P)),cell_sha256=sha(cell),change='Only -Capacity (MB): 1 -> -Capacity (KB): 512',diff=''.join(difflib.unified_diff(raw.decode().splitlines(True),derived.decode().splitlines(True),fromfile=str(source.relative_to(P)),tofile=str(cfg.relative_to(P))))))
 (R/'provenance/cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 baseline={}
 for name in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=P,text=True).splitlines():
  original=subprocess.check_output(['git','show',BASE+':'+name],cwd=P);assert(P/name).read_bytes()==original,name;baseline[name]=hashlib.sha256(original).hexdigest()
 (R/'provenance/protected.json').write_text(json.dumps(dict(base=BASE,sha256=baseline),indent=2)+'\n')
 source_files=json.loads((P/'NSCache_Experiment_DB/provenance/upstream_source_comparison.json').read_text())
 for f in source_files['files']:assert sha(P/'NSCache_Experiment_DB'/f['file'])==f['sha256']
 (R/'provenance/source_identity.json').write_text(json.dumps(source_files,indent=2)+'\n')
 print('Prepared',len(cases),'cases; protected',len(baseline),'historical files; 54 source hashes verified')
if __name__=='__main__':prepare()
