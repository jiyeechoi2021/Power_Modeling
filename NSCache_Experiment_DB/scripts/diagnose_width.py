"""A separate 7nm one-factor diagnostic; never replace reproduction inputs or rows."""
import json
from pathlib import Path
import subprocess
import sys
from analyze import ROOT,parse,write_csv
from run_experiments import sha

if __name__=='__main__':
    dest=ROOT/'configs/diagnostic_512bit';dest.mkdir(exist_ok=True)
    changes=[]
    for p in sorted((ROOT/'configs/study_reconstructed').glob('*_7nm*.cfg')):
        old=p.read_text();assert old.count('-WordWidth (bit): 256')==1
        new=old.replace('-WordWidth (bit): 256','-WordWidth (bit): 512')
        target=dest/p.name
        if target.exists() and target.read_text()!=new: raise ValueError(f'preserve user file: {target}')
        target.write_text(new)
        changes.append(dict(original=str(p.relative_to(ROOT)),diagnostic=str(target.relative_to(ROOT)),
                            change='WordWidth (bit): 256 -> 512; all other bytes unchanged',
                            original_sha256=sha(p),diagnostic_sha256=sha(target)))
    (ROOT/'provenance/width_diagnostic_changes.json').write_text(json.dumps(changes,indent=2)+'\n')
    subprocess.run([sys.executable,str(ROOT/'scripts/run_experiments.py'),'--suite','diagnostic_512bit','--jobs','2'],check=True)
    recorded=json.loads((ROOT/'results/recorded/nscache_16_runs.json').read_text())['runs']
    rows=[]
    for c in changes:
        name=Path(c['diagnostic']).stem
        m=sorted((ROOT/'logs/diagnostic_512bit'/name).glob('*/metadata.json'))[-1]
        meta=json.loads(m.read_text())
        assert meta['status']=='FINISHED' and meta['returncode']==0
        stdout=m.parent/'stdout.log'
        assert sha(stdout)==meta['stdout_sha256'] and sha(ROOT/c['diagnostic'])==meta['config_sha256']
        values,org=parse(stdout.read_text())
        prior=next(r for r in recorded if r['cache']==name.split('_')[0] and r['node_nm']==7 and r['optimization']==('ReadDynamicEnergy' if name.endswith('ReadEnergy') else 'ReadLatency'))
        rows.append(dict(run_id=name,suite='diagnostic_512bit',**{k:float(v) for k,v in values.items()},
                         all_six_recorded_exact=all(v==__import__('decimal').Decimal(str(prior[k])) for k,v in values.items()),
                         stdout=str(stdout.relative_to(ROOT)),organization=org))
    (ROOT/'results/width_diagnostic.json').write_text(json.dumps(rows,indent=2)+'\n')
    write_csv(ROOT/'results/width_diagnostic.csv',[{k:v for k,v in r.items() if k!='organization'} for r in rows])
    for r in rows: print(r['run_id'],'all_six_recorded_exact=',r['all_six_recorded_exact'])
