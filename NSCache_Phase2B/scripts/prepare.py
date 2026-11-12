"""Derive capacity-only inputs; archive and baseline source bytes remain immutable."""
import hashlib,json,re,subprocess,zipfile,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
BASE='820fe02a95009985510c4810c2044aaa8c7e610e'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 cases=[]
 pairs={(n,32,'fixed32') for n in (14,7,5,3)}|{(n,c,'bridge') for n,c in [(14,6),(14,40),(7,6),(7,40),(7,50),(5,40),(5,50)]}|{(7,20,'partition'),(5,25,'partition'),(5,10,'partition'),(14,3,'partition'),(7,8,'partition_control'),(5,8,'partition_control')}
 for node,cap,group in sorted(pairs):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   source=P/'NSCache_Phase2A/configs/phase2_256bit'/('L2_'+str(node)+'nm'+('_ReadEnergy' if opt=='ReadDynamicEnergy' else '')+'.cfg')
   original=source.read_text();raw=re.sub(r'^-Capacity \(MB\): 1$',f'-Capacity (MB): {cap}',original,flags=re.M)
   assert raw!=original
   name=f'L2_{node}nm_{cap}MiB_{opt}';target=R/'configs'/(name+'.cfg')
   if target.exists() and target.read_text()!=raw:raise ValueError(f'preserve {target}')
   target.write_text(raw)
   cases.append(dict(run_id=name,node_nm=node,capacity_mib=cap,objective=opt,group=group,config=str(target.relative_to(R)),config_sha256=sha(target),source=str(source.relative_to(P)),source_sha256=sha(source),change=f'Capacity (MB): 1 -> {cap}; binary MiB; all other settings unchanged'))
 (R/'provenance/cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 baseline={}
 for name in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=P,text=True).splitlines():
  b=subprocess.check_output(['git','show',BASE+':'+name],cwd=P);assert(P/name).read_bytes()==b
  baseline[name]=hashlib.sha256(b).hexdigest()
 (R/'provenance/protected.json').write_text(json.dumps({'base':BASE,'work_branch':'51208723a98c9df7a267126b3477a59837b14812','sha256':baseline},indent=2)+'\n')
 print('Prepared',len(cases),'cases; protected',len(baseline),'historical files')
if __name__=='__main__':prepare()
