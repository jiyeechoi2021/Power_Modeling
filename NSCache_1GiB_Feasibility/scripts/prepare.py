"""Capacity-only derivation from verified baselines; no parameter search."""
import difflib,hashlib,json,subprocess
from pathlib import Path
from common import read_raw,require
R=Path(__file__).resolve().parents[1];P=R.parent
BASE='a8d07dfc79266d5a33fb32f71ed20f30fe492d96'
REV='2fdcbf093f806bc9a28964aca8402c42738d58e5'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 cases=[];baselines=[]
 for node,capacity,study in [(3,128,'NSCache_3nm_128MiB_Feasibility'),(7,32,'NSCache_Phase2B')]:
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   name=f'L2_{node}nm_{capacity}MiB_{opt}';source=P/study/'configs'/(name+'.cfg');cell=P/'NSCache_Experiment_DB/configs/New_Configs'/f'SRAM_cell_{node}nm.cell'
   attempts=sorted((P/study/'logs'/name).glob('*/metadata.json'));require(bool(attempts),'missing validated baseline')
   m=json.loads(attempts[-1].read_text());require(m['source_revision']==REV,'baseline source revision')
   r=read_raw(attempts[-1],source,cell,'verified_historical_baseline');require(r['status']=='FINISHED','incomplete baseline')
   baselines.append(dict(node_nm=node,capacity_mib=capacity,objective=opt,metadata_sha256=sha(attempts[-1]),**r))
   raw=source.read_bytes();token=f'-Capacity (MB): {capacity}'.encode();require(raw.count(token)==1,'ambiguous capacity')
   derived=raw.replace(token,b'-Capacity (MB): 1024');cfg=R/'configs'/f'L2_{node}nm_1024MiB_{opt}.cfg'
   if cfg.exists():require(cfg.read_bytes()==derived,'preserve existing config')
   else:cfg.write_bytes(derived)
   cases.append(dict(run_id=cfg.stem,node_nm=node,objective=opt,capacity_mib=1024,capacity_bytes=1024**3,width_bits=256,group='primary_1gib',config=str(cfg.relative_to(R)),config_sha256=sha(cfg),source_config=str(source.relative_to(P)),source_config_sha256=sha(source),baseline_capacity_mib=capacity,baseline_metadata=str(attempts[-1].relative_to(P)),cell=str(cell.relative_to(P)),cell_sha256=sha(cell),source_revision=REV,derivation=f'Capacity (MB): {capacity} -> 1024 only; reconstructed, not author input',diff=''.join(difflib.unified_diff(raw.decode().splitlines(True),derived.decode().splitlines(True),fromfile=str(source.relative_to(P)),tofile=str(cfg.relative_to(P))))))
 (R/'provenance/cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 (R/'provenance/verified_baselines.json').write_text(json.dumps(baselines,indent=2)+'\n')
 hashes={}
 for n in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=P,text=True).splitlines():
  original=subprocess.check_output(['git','show',BASE+':'+n],cwd=P);require((P/n).read_bytes()==original,'historical changed '+n);hashes[n]=hashlib.sha256(original).hexdigest()
 (R/'provenance/protected.json').write_text(json.dumps(dict(base=BASE,sha256=hashes),indent=2)+'\n')
 src=json.loads((P/'NSCache_Experiment_DB/provenance/upstream_source_comparison.json').read_text())
 for f in src['files']:require(sha(P/'NSCache_Experiment_DB'/f['file'])==f['sha256'],'source mismatch')
 (R/'provenance/source_identity.json').write_text(json.dumps(src,indent=2)+'\n')
 print('Verified 4 baselines; derived 4 capacity-only cases; protected',len(hashes),'old files')
if __name__=='__main__':prepare()
