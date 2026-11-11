"""Audit preserved archive members and explicit input conditions before execution."""
import csv
import hashlib
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def options(p):
    result={}
    for line in p.read_text().splitlines():
        if line.startswith('-') and ':' in line:
            k,v=line[1:].split(':',1)
            if k in result: raise ValueError(f'duplicate {k} in {p}')
            result[k]=v.strip()
    return result

def audit():
    archive=ROOT.parent/'NSCache_Experiment_DB_20261110_Reconstructed_PartialRawLogs.zip'
    rows=[]
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for n in z.namelist():
            parts=Path(n).parts[1:]
            if not parts: continue
            if parts[0]=='nscache_source':
                p=ROOT/('source' if parts[1]=='src' else 'configs')/Path(*parts[2:])
                category='reconstructed configuration' if parts[1]=='config' and parts[2]=='study_reconstructed' else 'recovered source/configuration'
            else:
                mapping={'recorded_results':'results/recorded','rerun_logs':'logs/bundled','provenance':'provenance/bundled','scripts':'scripts/bundled'}
                p=ROOT/mapping.get(parts[0],'provenance/archive')/Path(*parts[1:]) if len(parts)>1 else ROOT/'provenance/archive'/parts[0]
                category={'recorded_results':'previously recorded derived results','rerun_logs':'previous package rerun; not historical original'}.get(parts[0],'archive documentation/generated script')
            original=z.read(n)
            assert p.read_bytes()==original,p
            rows.append({'archive_member':n,'path':str(p.relative_to(ROOT)),'origin':category,'sha256':hashlib.sha256(original).hexdigest()})
    with (ROOT/'provenance/archive_manifest.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (ROOT/'provenance/archive_sha256.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
    configs=[]
    for p in sorted((ROOT/'configs/study_reconstructed').glob('*.cfg')):
        o=options(p)
        cell=ROOT/'configs'/o['MemoryCellInputFile'].removeprefix('config/')
        configs.append({'run_id':p.stem,'config':o,'cell':options(cell),'config_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                        'cell_sha256':hashlib.sha256(cell.read_bytes()).hexdigest(),
                        'port_count':None,'port_count_status':'not exposed as a configurable count in InputParameter; not independently established',
                        'explicit_timing_constraint':any('Constraint' in k for k in o),
                        'default_clock_hz':3e9,'default_clock_evidence':'source/InputParameter.cpp constructor; not a user-specified hit-latency requirement'})
    assert len(configs)==16
    (ROOT/'results/configuration_audit.json').write_text(json.dumps(configs,indent=2)+'\n')
    keys=sorted(set().union(*(r['config'] for r in configs)))
    with (ROOT/'results/configuration_audit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['run_id',*keys]);w.writeheader()
        w.writerows(dict(run_id=r['run_id'],**r['config']) for r in configs)
    print(f'Archive preserved: {len(rows)} byte-identical members; audited {len(configs)} inputs')

if __name__=='__main__':
    (ROOT/'results').mkdir(exist_ok=True)
    audit()
