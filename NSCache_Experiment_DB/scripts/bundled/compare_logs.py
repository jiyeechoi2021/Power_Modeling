#!/usr/bin/env python3
"""Parse real NS-Cache stdout logs and compare against the recorded study data."""
import json,csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
runs=json.loads((ROOT/'recorded_results/nscache_16_runs.json').read_text())['runs']
fields={
 'read_pj_per_access':(r'^\s*- Cache Hit Dynamic Energy\s*=\s*([\d.]+)nJ per access',1000),
 'write_pj_per_access':(r'^\s*- Cache Write Dynamic Energy\s*=\s*([\d.]+)nJ per access',1000),
 'leakage_mw':(r'^\s*- Cache Total Leakage Power\s*=\s*([\d.]+)mW',1),
 'hit_latency_ns':(r'^\s*- Cache Hit Latency\s*=\s*([\d.]+)ns',1),
 'area_mm2':(r'^\s*- Total Area\s*=\s*([\d.]+)mm\^2',1),
 'feasible_solutions':(r'numSolutions\s*=\s*(\d+)',1),
}
rows=[]
for r in runs:
 name=f"{r['cache']}_{r['node_nm']}nm"+('_ReadEnergy' if r['optimization']=='ReadDynamicEnergy' else '')
 p=ROOT/'rerun_logs/replayed'/f'{name}.log'
 if not p.exists(): p=ROOT/'rerun_logs'/f'{name}.log'
 if not p.exists():
  rows.append({'run_id':name,'rerun_status':'MISSING','equality':'NOT_TESTED'})
  continue
 raw=p.read_text(errors='replace')
 vals={}
 for field,(pat,mult) in fields.items():
  match=re.search(pat,raw,re.MULTILINE)
  if match: vals[field]=float(match.group(1))*mult
 same='Finished!' in raw and len(vals)==len(fields) and all(abs(vals[k]-float(r[k]))<1e-8 for k in fields)
 rows.append({'run_id':name,'rerun_status':'FINISHED' if 'Finished!' in raw else 'INCOMPLETE','equality':'MATCH' if same else 'DIFFERENT',**{k:vals.get(k) for k in fields}})
with (ROOT/'provenance/replay_comparison.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['run_id','rerun_status','equality',*fields]);writer.writeheader();writer.writerows(rows)
for r in rows:print(f"{r['run_id']:30s} {r['rerun_status']:12s} {r['equality']}")
