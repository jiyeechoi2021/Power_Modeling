"""Rebuild 512KiB results and historical trajectories from raw evidence, no simulator."""
import csv,hashlib,json,sys
from decimal import Decimal as D
from pathlib import Path
from common import read_raw,require
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def protected():
 saved=json.loads((R/'provenance/protected.json').read_text())
 for n,h in saved['sha256'].items():require(sha(P/n)==h,'historical file changed: '+n)
 return len(saved['sha256'])

def validate_matrix():
 cases=json.loads((R/'provenance/cases.json').read_text())
 require(len(cases)==8 and {(c['node_nm'],c['objective']) for c in cases}=={(n,o) for n in (14,7,5,3) for o in ('ReadLatency','ReadDynamicEnergy')},'expected exact 8-case matrix')
 for c in cases:
  cfg=R/c['config'];source=P/c['source_config'];cell=P/c['cell']
  for p,key in ((cfg,'config_sha256'),(source,'source_config_sha256'),(cell,'cell_sha256')):require(sha(p)==c[key],'case/source/cell digest mismatch')
  require(cfg.read_bytes()==source.read_bytes().replace(b'-Capacity (MB): 1',b'-Capacity (KB): 512'),'change beyond capacity')
  require(c['capacity_bytes']==524288 and c['capacity_kib']==512 and c['width_bits']==256,'capacity/width metadata mismatch')
 return cases

def case_record(name,node,opt,kib,config,folder,origin):
 row=dict(run_id=name,node_nm=node,objective=opt,capacity_kib=kib,capacity_bytes=kib*1024,width_bits=256,associativity=16,temperature_k=300,origin=origin,energy_unit='pJ/model_access',normalized_unit='effective_pJ/bit_32B_model_line',leakage_unit='mW',latency_unit='ns',area_unit='mm2',source_revision='2fdcbf093f806bc9a28964aca8402c42738d58e5',source_derived_vdd_v={14:'0.8',7:'0.7',5:'0.7',3:'0.7'}[node],cell_read_voltage_v={14:'0.277',7:'0.264',5:'0.253',3:'0.248'}[node])
 if folder is None:return dict(row,status='MISSING_NOT_RUN',analysis_status='MISSING_NOT_RUN',note='8MiB at 14/3nm was not run; no interpolation')
 attempts=sorted(folder.glob('*/metadata.json'))
 if not attempts:return dict(row,status='UNRUN',analysis_status='UNRUN',config=str(config.relative_to(P)))
 meta=attempts[-1];m=json.loads(meta.read_text())
 if m['status']=='RUNNING':return dict(row,status='RUNNING',analysis_status='RUNNING',metadata=str(meta.relative_to(P)),config=str(config.relative_to(P)),stdout=str((meta.parent/'stdout.log').relative_to(P)))
 cell=P/'NSCache_Experiment_DB/configs/New_Configs'/f'SRAM_cell_{node}nm.cell'
 values=read_raw(meta,config,cell,origin)
 if values['status']=='FINISHED':
  raw=(P/values['stdout']).read_text()
  header=f'Capacity   : {kib}KB' if kib<1024 else f'Capacity   : {kib//1024}MB'
  require(header in raw and 'Cache Line Size: 32Bytes' in raw and 'Cache Associativity: 16 Ways' in raw,'capacity/width/way stdout header mismatch')
 return dict(row,**values)

def load():
 protected();cases=validate_matrix();current=[];history=[]
 for c in cases:
  current.append(case_record(c['run_id'],c['node_nm'],c['objective'],512,R/c['config'],R/'logs'/c['run_id'],'new_phase2c'))
 for kib in (1024,8192,32768):
  for n in (14,7,5,3):
   for opt in ('ReadLatency','ReadDynamicEnergy'):
    if kib==1024:
     old=f'L2_{n}nm'+('_ReadEnergy' if opt=='ReadDynamicEnergy' else '')
     config=P/'NSCache_Phase2A/configs/phase2_256bit'/(old+'.cfg');folder=P/'NSCache_Phase2A/logs/phase2_256bit'/old
    elif kib==8192 and n in (14,3):config=folder=None
    else:
     old=f'L2_{n}nm_{kib//1024}MiB_{opt}';config=P/'NSCache_Phase2B/configs'/(old+'.cfg');folder=P/'NSCache_Phase2B/logs'/old
    history.append(case_record(f'L2_{n}nm_{kib}KiB_{opt}',n,opt,kib,config,folder,'historical_verified' if folder else 'historical_missing'))
 binary=(R/'provenance/binary.sha256').read_text().split()[0]
 for r in current+history:
  if r['status']=='FINISHED':require(r['binary_sha256']==binary,'runtime binary identities differ')
 return current,history

def scaling(current):
 by={(r['node_nm'],r['objective']):r for r in current};rows=[]
 for opt in ('ReadLatency','ReadDynamicEnergy'):
  for op in ('read','write'):
   for a,b in ((14,7),(7,5),(5,3)):
    x,y=by[a,opt],by[b,opt];valid=x['status']==y['status']=='FINISHED'
    row=dict(capacity_kib=512,objective=opt,operation=op,from_nm=a,to_nm=b,status='VALID' if valid else 'UNAVAILABLE',sf_unit='dimensionless',from_log=x.get('stdout',''),to_log=y.get('stdout',''),from_config=x.get('config',''),to_config=y.get('config',''),interpretation='node/cell/Vdd/selected-organization sensitivity; not pure process scaling')
    if valid:
     for precision in ('summary','bank_sum'):
      first,second=D(x[f'{op}_{precision}_pj']),D(y[f'{op}_{precision}_pj']);sf=second/first
      row.update({precision+'_from_pj':str(first),precision+'_to_pj':str(second),precision+'_sf':str(sf),precision+'_reduction_percent':str(100*(1-sf)),precision+'_formula':f'{second}/{first}'})
    rows.append(row)
 return rows

def ratios(current,history):
 by={(r['node_nm'],r['objective']):r for r in history if r['capacity_kib']==1024};rows=[]
 for c in current:
  h=by[c['node_nm'],c['objective']];valid=c['status']==h['status']=='FINISHED'
  for op in ('read','write'):
   r=dict(node_nm=c['node_nm'],objective=c['objective'],operation=op,status='VALID' if valid else 'UNAVAILABLE',formula='E_512KiB/E_1MiB, same node/objective/operation/precision',log_512=c.get('stdout',''),log_1mib=h.get('stdout',''),config_512=c.get('config',''),config_1mib=h.get('config',''))
   if valid:
    for precision in ('summary','bank_sum'):
     a,b=D(c[f'{op}_{precision}_pj']),D(h[f'{op}_{precision}_pj']);r.update({precision+'_512_pj':str(a),precision+'_1mib_pj':str(b),precision+'_ratio':str(a/b),precision+'_substitution':f'{a}/{b}'})
   rows.append(r)
 return rows

def write_csv(path,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
 try:current,history=load();sf=scaling(current);ratio=ratios(current,history)
 except (OSError,ValueError,KeyError) as e:print('Invalid evidence:',e,file=sys.stderr);return 2
 (R/'results').mkdir(exist_ok=True);(R/'reports').mkdir(exist_ok=True)
 flat=lambda r:{k:v for k,v in r.items() if k not in ('organization','breakdown')}
 write_csv(R/'results/slice_512kib_energy.csv',[flat(r) for r in current])
 write_csv(R/'results/slice_512kib_scaling.csv',sf)
 write_csv(R/'results/capacity_comparison.csv',[flat(r) for r in current+history])
 write_csv(R/'results/slice_vs_1mib_ratios.csv',ratio)
 components=[]
 for r in current+history:
  if r['status']!='FINISHED':continue
  for op in ('read','write'):
   components.append(dict(run_id=r['run_id'],node_nm=r['node_nm'],capacity_kib=r['capacity_kib'],objective=r['objective'],operation=op,origin=r['origin'],summary_pj=r[op+'_summary_pj'],bank_sum_pj=r[op+'_bank_sum_pj'],data_bank_pj=r[op+'_data_bank_pj'],tag_bank_pj=r[op+'_tag_bank_pj'],routing_subset_pj=r[op+'_routing_pj'],nonrouting_residual_pj=r[op+'_nonrouting_residual_pj'],rounding_delta_pj=r[op+'_rounding_delta_bank_minus_summary_pj'],unit='pJ/model_access',stdout=r['stdout'],config=r['config'],scope='routing is included in data/tag bank totals; per-subarray/mat levels not added'))
 write_csv(R/'results/energy_breakdown.csv',components)
 (R/'results/organization_comparison.json').write_text(json.dumps(current+history,indent=2)+'\n')
 report(current,history,sf,ratio)
 good=sum(r['status']=='FINISHED' for r in current);print(f'512KiB: {good}/8 FINISHED; {8-good} failed/missing; 12 SF rows; 32 capacity records (4 historical cells explicitly absent)')
 return 0 if good==8 else 1

def report(current,history,sf,ratios):
 lines=['# Phase 2-C — 512KiB NS-Cache single-cache proxy','',
 '## Background, gate and scope','',
 'This study executes only eight 512KiB/256bit L2-like configurations: 14/7/5/3nm × ReadLatency/ReadDynamicEnergy. Each run supplies read AND write results. The 7nm/ReadLatency smoke counts as one of the eight. Other capacities are historical references only; no P0–P3 campaign, model source change, GPU validation or Rubin prediction is run.',
 'Only capacity changes relative to matching Phase 2-A inputs: integer `-Capacity (KB): 512`=524288 bytes. Controls remain 16-way/Normal/LOP/300K/H-tree/ForceBankA=4x4/internal sensing/pruning/latency buffer and original node cells/wires. See [gate](feasibility_gate.md) and [config diffs](../provenance/cases.json).',
 '', '## Complete 512KiB results (summary energy precision)','',
 '| Node | Objective | Status | Read pJ/access | Write pJ/access | Read pJ/bit | Write pJ/bit | Hit ns | Leakage mW | Area mm² | Solutions | Raw |',
 '|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
 for r in current:
  values=[r.get(k,'—') for k in ('read_summary_pj','write_summary_pj','read_summary_effective_pj_bit','write_summary_effective_pj_bit','hit_latency_ns','leakage_mw','area_mm2','feasible_solutions')]
  lines.append(f"| {r['node_nm']} | {r['objective']} | {r['status']} | "+' | '.join(values)+(f" | [log](../../{r['stdout']}) |" if r.get('stdout') else ' | missing |'))
 lines+=['', '`E_effective,bit=E_model_access/256` normalizes the complete modeled 32B line access, not a physical SRAM bit or GPU sector transaction. [Complete summary/fine fields and metadata](../results/slice_512kib_energy.csv). Leakage is power and is never added to dynamic energy/access.',
 '', '## 512KiB node sensitivity SF','',
 '`SF_E(a→b)=E(512KiB,b)/E(512KiB,a)`. Same capacity/objective/operation/precision. SF is dimensionless. [CSV](../results/slice_512kib_scaling.csv) contains both summary and fine bank-sum operands, ratios and formulas separately.',
 '', '| Objective | Operation | Transition | Summary SF | Fine bank-sum SF |','|---|---|---|---:|---:|']
 for r in sf:lines.append(f"| {r['objective']} | {r['operation']} | {r['from_nm']}→{r['to_nm']} | "+(f"{D(r['summary_sf']):.6f} | {D(r['bank_sum_sf']):.6f} |" if r['status']=='VALID' else 'unavailable | unavailable |'))
 lines+=['', '**SF reflects node/cell/Vdd/wire/optimizer-selected organization, not pure process scaling.** Source Vdd is 0.8/0.7/0.7/0.7V at 14/7/5/3nm; cell read-voltage is a separate quantity. These values are inherited source parameters, not measured GPU voltages.',
 '', '## Capacity trajectory (summary read/write pJ per model access)','',
 'Historical records are hash-verified, labeled historical_verified and never rerun. Missing 8MiB at 14/3nm remains missing. [Capacity CSV](../results/capacity_comparison.csv), [512KiB/1MiB ratios with both precisions](../results/slice_vs_1mib_ratios.csv).',
 '', '| Node | Objective | 512KiB new R/W | 1MiB historical R/W | 8MiB historical R/W | 32MiB historical R/W |','|---:|---|---:|---:|---:|---:|']
 by={(r['node_nm'],r['objective'],r['capacity_kib']):r for r in current+history}
 for n in (14,7,5,3):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   cells=[]
   for kib in (512,1024,8192,32768):
    r=by[n,opt,kib];cells.append(f"{r['read_summary_pj']} / {r['write_summary_pj']}" if r['status']=='FINISHED' else r['status'])
   lines.append(f"| {n} | {opt} | "+' | '.join(cells)+' |')
 lines+=['', '| Node | Objective | Operation | Summary E512/E1MiB | Fine bank-sum E512/E1MiB |','|---:|---|---|---:|---:|']
 for r in ratios:lines.append(f"| {r['node_nm']} | {r['objective']} | {r['operation']} | "+(f"{D(r['summary_ratio']):.6f} | {D(r['bank_sum_ratio']):.6f} |" if r['status']=='VALID' else 'unavailable | unavailable |'))
 lines+=['', 'Summary uses 0.001nJ=1pJ output resolution. Fine bank sums use the separately printed data/tag precision. Each precision is normalized and divided like-for-like; no ratio mixes rounded and fine operands. Small SF differences can be rounding-sensitive. Capacity does not imply linear dynamic energy or identical organization.',
 '', '## Data / Tag / Routing and selected organization','',
 '[Breakdown CSV](../results/energy_breakdown.csv) uses data+tag bank totals with routing as an included subset. Full activation, subarray/mat, mux, wire and buffer details are retained in [organization JSON](../results/organization_comparison.json). Missing detail is not estimated. Nonrouting residual is not cell-only, and nested mat/subarray values are not added again.',
 '', '| Node | Objective | Read Data/Tag/Routing pJ | Write Data/Tag/Routing pJ | Data bank/subarray/mat | Tag bank/subarray/mat |','|---:|---|---:|---:|---|---|']
 for r in current:
  if r['status']!='FINISHED':continue
  desc=lambda k:'/'.join(r['organization'][k][v] for v in ('bank','subarray','mat'))
  comp=lambda op:'/'.join(r[op+'_'+v] for v in ('data_bank_pj','tag_bank_pj','routing_pj'))
  lines.append(f"| {r['node_nm']} | {r['objective']} | {comp('read')} | {comp('write')} | {desc('data')} | {desc('tag')} |")
 lines+=['', '### Optimization / capacity trade-offs','', '| Node | Read energy reduction energy-objective vs latency % | Hit latency ns: latency→energy objective | Area mm²: latency→energy objective | Data mat latency→energy | Tag bank latency→energy |','|---:|---:|---:|---:|---|---|']
 for n in (14,7,5,3):
  a,b=by[n,'ReadLatency',512],by[n,'ReadDynamicEnergy',512]
  if a['status']!= 'FINISHED' or b['status']!='FINISHED':continue
  reduction=100*(1-D(b['read_summary_pj'])/D(a['read_summary_pj']))
  lines.append(f"| {n} | {reduction:.3f} | {a['hit_latency_ns']}→{b['hit_latency_ns']} | {a['area_mm2']}→{b['area_mm2']} | {a['organization']['data']['mat']}→{b['organization']['data']['mat']} | {a['organization']['tag']['bank']}→{b['organization']['tag']['bank']} |")
 lines+=['', '### Observed non-monotonic write behavior', '',
  'ReadDynamicEnergy optimizes read energy, not write energy. At 7nm/512KiB the energy objective prints 26pJ write vs 25pJ under the latency objective; fine bank sums also increase (26.021 vs 24.612pJ). Thus this observation is not solely a 1pJ-summary rounding artifact. The selected data mat changes from 512×128 to 256×512 and tag bank 16×1 to 8×1; printed routing changes too. These are correlated optimizer choices, not isolated causal attribution.',
  'Under ReadLatency, 5→3nm write summary is 24→25pJ (SF=1.041667), while fine bank sum is 24.237→24.756pJ (SF≈1.021414). The increase persists in fine output but its magnitude is resolution-sensitive. Tag geometry changes (including the selected tag bank), and cell/Vdd/wire models are node-specific. No fitting or alternate cell was used to remove the increase.']
 lines+=['', 'Observed organizations and trade-offs above show independent optimizer choices; they are not controlled topology/Vdd interventions. Compare historical rows in the JSON before attributing capacity differences solely to SRAM bit count. Increased tag count, activation and H-tree/decoder/mux load can contribute, but their isolated causal shares are unverified.',
 '', '## A100-oriented size rationale and validity','',
 'The task cites NVIDIA A100 Architecture Whitepaper p.35: two high-level partitions, 40 slices each, nominal 512KB per slice. In this study binary arithmetic is explicit: 80×512KiB=40MiB. [Official whitepaper](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf). Direct retrieval returned HTTP 403, so the source text was not independently reread here; the supplied page-specific citation is the evidence premise, not a new hardware verification.',
 'This motivates a **512KiB NS-Cache single-cache proxy / model slice candidate**, not circuit, port-count, 16-way associativity, banking, metadata/sector or energy-boundary equivalence. Never multiply single-access dynamic energy by 80 to claim GPU energy. Replicated leakage/area and shared costs are outside scope.',
 '', '| Category | Evidence/status | Allowed interpretation |','|---|---|---|',
 '| Direct run | Eight planned configs; actual completion/status and raw logs above | Current model output only |',
 '| Derived arithmetic | pJ/bit, matched-precision SF and capacity ratios | Algebra on printed model values |',
 '| Externally documented A100 hierarchy | Task-supplied whitepaper p.35 citation; direct retrieval 403 | Nominal-size rationale; local source reread pending |',
 '| Physical equivalence | Unvalidated | No GPU slice/sector/port/energy match claimed |',
 '| Deferred work | Explicitly not executed | Separate future P0–P3 tasks only |',
 '', '## Limitations and explicitly deferred work','',
 'No extra capacity sweeps or new non-power-of-two model extension; no V100/H100 topology reconstruction; no 128B-line/32B-sector implementation or confidential coefficient comparison; no fixed-organization/Vdd campaigns; no hardware validation or Rubin projection. Official-source reread and PR API operations remain subject to documented network restrictions.']
 (R/'reports/experiment_report.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':raise SystemExit(main())
