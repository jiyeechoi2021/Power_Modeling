"""Bounded NS-Cache executions with per-child wait4 RSS, preserved attempts and resume."""
import argparse,hashlib,json,os,signal,subprocess,time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(case,timeout):
 cfg=R/case['config'];binary=R/'build/nsc';cell=P/'NSCache_Experiment_DB/configs/New_Configs'/f"SRAM_cell_{case['node_nm']}nm.cell"
 identity=dict(config_sha256=sha(cfg),binary_sha256=sha(binary),cell_sha256=sha(cell))
 folder=R/'logs'/case['run_id'];folder.mkdir(parents=True,exist_ok=True);prior=sorted(folder.glob('*/metadata.json'))
 if prior:
  old=json.loads(prior[-1].read_text())
  if old.get('status')=='FINISHED' and all(old.get(k)==v for k,v in identity.items()) and all((prior[-1].parent/f).exists() and sha(prior[-1].parent/f)==old.get(k) for f,k in [('stdout.log','stdout_sha256'),('stderr.log','stderr_sha256'),('environment.json','environment_sha256')]):
   print('resume',case['run_id'],flush=True);return old
 attempt=folder/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');attempt.mkdir()
 cwd=R/'runtime'/case['run_id'];(cwd/'config').mkdir(parents=True,exist_ok=True)
 for dest,source in [(cwd/'config/cases',R/'configs'),(cwd/'config/New_Configs',P/'NSCache_Experiment_DB/configs/New_Configs')]:
  if not dest.exists():dest.symlink_to(source,target_is_directory=True)
  assert dest.resolve()==source.resolve()
 (attempt/'environment.json').write_bytes((R/'logs/build/environment.json').read_bytes())
 meta=dict(case,**{k:v for k,v in identity.items() if k!='config_sha256'},environment_sha256=sha(attempt/'environment.json'),source_revision='2fdcbf093f806bc9a28964aca8402c42738d58e5',started_utc=datetime.now(timezone.utc).isoformat(),command=['build/nsc',f'config/cases/{cfg.name}'],cwd=str(cwd.relative_to(R)),status='RUNNING')
 (attempt/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');start=time.monotonic();timed=False
 with (attempt/'stdout.log').open('wb') as out,(attempt/'stderr.log').open('wb') as err:
  proc=subprocess.Popen([str(binary),f'config/cases/{cfg.name}'],cwd=cwd,stdout=out,stderr=err,start_new_session=True)
  while True:
   pid,status,usage=os.wait4(proc.pid,os.WNOHANG)
   if pid:break
   if time.monotonic()-start>timeout and not timed:os.killpg(proc.pid,signal.SIGKILL);timed=True
   time.sleep(.2)
  proc.returncode=os.waitstatus_to_exitcode(status)
 meta.update(returncode=proc.returncode,elapsed_seconds=time.monotonic()-start,max_rss_kib=usage.ru_maxrss,user_cpu_seconds=usage.ru_utime,system_cpu_seconds=usage.ru_stime,finished_utc=datetime.now(timezone.utc).isoformat(),stdout_sha256=sha(attempt/'stdout.log'),stderr_sha256=sha(attempt/'stderr.log'))
 raw=(attempt/'stdout.log').read_text(errors='replace');meta['status']='TIMEOUT' if timed else 'FINISHED' if proc.returncode==0 and 'Finished!' in raw else 'FAILED'
 (attempt/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(case['run_id'],meta['status'],round(meta['elapsed_seconds'],2),'s RSS',usage.ru_maxrss,flush=True);return meta
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=2);p.add_argument('--timeout',type=float,default=1800);p.add_argument('--stage',choices=['smoke','fixed32','partition_control','unsupported_diagnostics','all'],default='smoke');p.add_argument('--case');a=p.parse_args();cases=json.loads((R/'provenance/cases.json').read_text())
 if a.case:cases=[c for c in cases if c['run_id']==a.case]
 elif a.stage=='smoke':cases=[c for c in cases if c['objective']=='ReadLatency' and (c['node_nm'],c['capacity_mib']) in [(14,6),(7,40),(5,50),(7,20),(5,25)]]
 elif a.stage=='unsupported_diagnostics':cases=[c for c in cases if c['group'] in ('bridge','partition') and not list((R/'logs'/c['run_id']).glob('*/metadata.json'))]
 elif a.stage!='all':cases=[c for c in cases if c['group']==a.stage]
 if a.jobs not in (1,2) or not cases or a.timeout<=0:p.error('jobs must be 1/2, valid cases and timeout required')
 with ThreadPoolExecutor(max_workers=a.jobs) as pool:result=list(pool.map(lambda c:run(c,a.timeout),cases))
 raise SystemExit(0 if all(c['status']=='FINISHED' for c in result) else 1)
