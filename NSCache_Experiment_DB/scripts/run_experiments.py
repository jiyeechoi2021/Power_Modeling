"""Run reconstructed inputs unchanged; preserve attempts and resume verified completions."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def run(cfg, timeout, suite='study_reconstructed'):
    binary = ROOT / 'build/nsc'
    identity = {'config_sha256': sha(cfg), 'binary_sha256': sha(binary),
                'cell_sha256': sha(ROOT / 'configs/New_Configs' / f'SRAM_cell_{cfg.stem.split("_")[1]}.cell')}
    group = 'new' if suite == 'study_reconstructed' else suite
    directory = ROOT / 'logs' / group / cfg.stem
    directory.mkdir(parents=True, exist_ok=True)
    for previous in sorted(directory.glob('*/metadata.json'))[-1:]:
        meta = json.loads(previous.read_text())
        out, err = previous.parent/'stdout.log', previous.parent/'stderr.log'
        if (all(meta.get(k) == v for k, v in identity.items())
                and meta.get('status') == 'FINISHED' and out.exists() and err.exists()
                and meta.get('stdout_sha256') == sha(out) and meta.get('stderr_sha256') == sha(err)):
            print(f'{cfg.stem}: resume {previous.parent.name}', flush=True)
            return meta
    attempt = directory / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    attempt.mkdir()
    # Simulator paths in the archive are relative to the original source root.
    runtime = ROOT / 'runtime' / group / cfg.stem
    runtime.mkdir(parents=True, exist_ok=True)
    link = runtime/'config'
    if not link.exists():
        link.symlink_to(ROOT/'configs', target_is_directory=True)
    meta = dict(identity, run_id=cfg.stem, started_utc=now(),
                config=str(cfg.relative_to(ROOT)), command=[str(binary.relative_to(ROOT)), f'config/{suite}/{cfg.name}'],
                cwd=str(runtime.relative_to(ROOT)), input_origin='reconstructed; not historical original')
    (attempt/'environment.json').write_bytes((ROOT/'logs/build/environment.json').read_bytes())
    meta['environment_sha256'] = sha(attempt/'environment.json')
    (attempt/'metadata.json').write_text(json.dumps(dict(meta,status='RUNNING'),indent=2)+'\n')
    start = time.monotonic()
    with (attempt/'stdout.log').open('wb') as stdout, (attempt/'stderr.log').open('wb') as stderr:
        try:
            result = subprocess.run([str(binary), f'config/{suite}/{cfg.name}'],
                                    cwd=runtime, stdout=stdout, stderr=stderr, timeout=timeout)
            meta['returncode'] = result.returncode
            stdout.flush()
            meta['status'] = 'FINISHED' if result.returncode == 0 and 'Finished!' in (attempt/'stdout.log').read_text() else 'FAILED'
        except subprocess.TimeoutExpired:
            meta.update(returncode=None, status='TIMEOUT', error=f'exceeded {timeout} seconds')
        except OSError as exc:
            meta.update(returncode=None, status='FAILED', error=str(exc))
    meta.update(finished_utc=now(), elapsed_seconds=time.monotonic()-start,
                stdout_sha256=sha(attempt/'stdout.log'), stderr_sha256=sha(attempt/'stderr.log'))
    (attempt/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(f'{cfg.stem}: {meta["status"]} ({meta["elapsed_seconds"]:.2f}s)', flush=True)
    return meta

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--timeout',type=float,default=1800)
    parser.add_argument('--case',help='Exact configuration stem; default: all 16')
    parser.add_argument('--suite', choices=['study_reconstructed','diagnostic_512bit'], default='study_reconstructed')
    args=parser.parse_args()
    configs=sorted((ROOT/'configs'/args.suite).glob('*.cfg'))
    if args.case:
        configs=[p for p in configs if p.stem==args.case]
    if not configs or args.jobs<1 or args.timeout<=0:
        parser.error('no matching configurations or invalid jobs/timeout')
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results=list(pool.map(lambda p:run(p,args.timeout,args.suite),configs))
    raise SystemExit(0 if all(r['status']=='FINISHED' for r in results) else 1)
