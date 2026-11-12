"""Fresh Phase 2 attempts, with verified resume and separate failure/stdout/stderr logs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
ROOT=Path(__file__).resolve().parents[1]
P1=ROOT.parent/'NSCache_Experiment_DB'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()

def run(config,timeout):
    name=config.stem;binary=ROOT/'build/nsc'
    cell=P1/'configs/New_Configs'/f'SRAM_cell_{name.split("_")[1]}.cell'
    identity=dict(config_sha256=sha(config),cell_sha256=sha(cell),binary_sha256=sha(binary))
    directory=ROOT/'logs/phase2_256bit'/name;directory.mkdir(parents=True,exist_ok=True)
    prior=sorted(directory.glob('*/metadata.json'))
    if prior:
        meta=json.loads(prior[-1].read_text())
        if meta.get('status')=='FINISHED' and meta.get('returncode')==0 and all(meta.get(k)==v for k,v in identity.items()):
            if all((prior[-1].parent/f).exists() and sha(prior[-1].parent/f)==meta[k] for f,k in [('stdout.log','stdout_sha256'),('stderr.log','stderr_sha256'),('environment.json','environment_sha256')]):
                print(f'{name}: resume verified Phase 2 attempt',flush=True);return meta
    attempt=directory/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');attempt.mkdir()
    runtime=ROOT/'runtime'/name;runtime.mkdir(parents=True,exist_ok=True)
    conf=runtime/'config';conf.mkdir(exist_ok=True)
    for target,source in [(conf/'phase2_256bit',ROOT/'configs/phase2_256bit'),(conf/'New_Configs',P1/'configs/New_Configs')]:
        if not target.exists():target.symlink_to(source,target_is_directory=True)
        if target.resolve()!=source.resolve():raise ValueError(f'unexpected runtime path {target}')
    (attempt/'environment.json').write_bytes((ROOT/'logs/build/environment.json').read_bytes())
    meta=dict(identity,run_id=name,phase='2-A',input_origin='new 256bit derivative; not historical original',
              config=str(config.relative_to(ROOT)),cell=str(cell.relative_to(ROOT.parent)),started_utc=now(),
              command=['build/nsc',f'config/phase2_256bit/{config.name}'],cwd=str(runtime.relative_to(ROOT)),
              environment_sha256=sha(attempt/'environment.json'),source_revision='2fdcbf093f806bc9a28964aca8402c42738d58e5')
    (attempt/'metadata.json').write_text(json.dumps(dict(meta,status='RUNNING'),indent=2)+'\n')
    start=time.monotonic()
    with (attempt/'stdout.log').open('wb') as out,(attempt/'stderr.log').open('wb') as err:
        try:
            result=subprocess.run([str(binary),f'config/phase2_256bit/{config.name}'],cwd=runtime,stdout=out,stderr=err,timeout=timeout)
            out.flush()
            meta.update(returncode=result.returncode,status='FINISHED' if result.returncode==0 and 'Finished!' in (attempt/'stdout.log').read_text() else 'FAILED')
        except subprocess.TimeoutExpired:
            meta.update(returncode=None,status='TIMEOUT',error=f'exceeded {timeout}s')
        except OSError as exc:
            meta.update(returncode=None,status='FAILED',error=str(exc))
    meta.update(finished_utc=now(),elapsed_seconds=time.monotonic()-start,stdout_sha256=sha(attempt/'stdout.log'),stderr_sha256=sha(attempt/'stderr.log'))
    (attempt/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(f'{name}: {meta["status"]} ({meta["elapsed_seconds"]:.2f}s)',flush=True)
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--jobs',type=int,default=2);p.add_argument('--timeout',type=float,default=1800);p.add_argument('--case')
    args=p.parse_args()
    configs=sorted((ROOT/'configs/phase2_256bit').glob('*.cfg'))
    if args.case:configs=[c for c in configs if c.stem==args.case]
    if not configs or args.jobs<1 or args.timeout<=0:p.error('invalid case/jobs/timeout')
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:results=list(pool.map(lambda c:run(c,args.timeout),configs))
    raise SystemExit(0 if all(r['status']=='FINISHED' for r in results) else 1)
