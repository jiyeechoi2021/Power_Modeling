"""Raw-only comparison of controlled capacity derivatives and a reported public scalar."""
import csv,hashlib,json,math,re,sys
from decimal import Decimal as D
from pathlib import Path
from common import read_raw,require
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REFERENCE=D('0.917')

def protected():
 saved=json.loads((R/'provenance/protected.json').read_text())
 for n,h in saved['sha256'].items():require(sha(P/n)==h,'historical file changed: '+n)
 return len(saved['sha256'])

def record(name,opt,capacity,config,folder,origin):
 row=dict(run_id=name,node_nm=3,objective=opt,capacity_mib=capacity,capacity_bytes=capacity*1024**2,width_bits=256,associativity=16,temperature_k=300,roadmap='LOP',source_derived_vdd_v='0.7',cell_read_voltage_v='0.248',source_revision='2fdcbf093f806bc9a28964aca8402c42738d58e5',origin=origin,energy_unit='pJ/model_access',normalized_unit='effective_pJ/bit_32B_model_line',latency_unit='ns',area_unit='mm2',leakage_unit='mW',config=str(config.relative_to(P)))
 attempts=sorted(folder.glob('*/metadata.json'))
 if not attempts:return dict(row,status='UNRUN',analysis_status='UNRUN')
 meta=attempts[-1];m=json.loads(meta.read_text());out=meta.parent/'stdout.log'
 if m['status']=='RUNNING':return dict(row,status='RUNNING',analysis_status='RUNNING',metadata=str(meta.relative_to(P)),stdout=str(out.relative_to(P)))
 cell=P/'NSCache_Experiment_DB/configs/New_Configs/SRAM_cell_3nm.cell';r=read_raw(meta,config,cell,origin)
 if r['status']=='FINISHED':
  raw=out.read_text();require(f'Capacity   : {capacity}MB' in raw and 'Cache Line Size: 32Bytes' in raw,'capacity/width header mismatch')
  dimensions=[int(v) for key in ('bank','subarray','mat') for v in re.findall(r'\d+',r['organization']['data'][key])]
  physical_bits=math.prod(dimensions)
  require(physical_bits==capacity*1024**2*8,'derived data-array capacity mismatch')
  r['derived_data_array_bytes']=physical_bits//8
  values=re.findall(r'^\s*- Cache Write Latency\s*=\s*([\d.]+)ns',raw,re.M);require(len(values)==1,'missing write latency');r['write_latency_ns']=values[0]
  for label,section in zip(('data','tag'),re.split(r'CACHE (?:DATA|TAG) ARRAY DETAILS',raw)[1:]):
   timing={}
   for kind in ('Read','Write'):
    m1=re.search(r'-\s*'+kind+r' Latency\s*=\s*([\d.]+)(ps|ns|us|ms|s)',section)
    if m1:timing[kind.lower()+'_latency_ns']=str(D(m1.group(1))*{'ps':D('.001'),'ns':D(1),'us':D(1000),'ms':D(1000000),'s':D(1000000000)}[m1.group(2)])
   r.setdefault('bank_timing',{})[label]=timing
 return dict(row,**r)

def load():
 protected();cases=json.loads((R/'provenance/cases.json').read_text());require(len(cases)==2 and {c['objective'] for c in cases}=={'ReadLatency','ReadDynamicEnergy'},'unexpected matrix');rows=[]
 for c in cases:
  source=P/c['source_config'];cfg=R/c['config'];cell=P/c['cell']
  for path,key in ((source,'source_config_sha256'),(cfg,'config_sha256'),(cell,'cell_sha256')):require(sha(path)==c[key],'input/cell hash mismatch')
  require(c['capacity_bytes']==134217728 and c['width_bits']==256,'invalid requested capacity/width')
  require(cfg.read_bytes()==source.read_bytes().replace(b'-Capacity (MB): 32',b'-Capacity (MB): 128'),'change beyond capacity')
  opt=c['objective'];baseline=record('L2_3nm_32MiB_'+opt,opt,32,source,P/'NSCache_Phase2B/logs'/('L2_3nm_32MiB_'+opt),'verified_phase2b_raw')
  require(baseline['status']=='FINISHED','32MiB baseline not verified')
  rows.extend([baseline,record(c['run_id'],opt,128,cfg,R/'logs'/c['run_id'],'capacity_only_reconstruction')])
 digest=(R/'provenance/binary.sha256').read_text().split()[0]
 for r in rows:
  if r['status']=='FINISHED':require(r['binary_sha256']==digest,'different binary identity; investigate')
 return rows

def csvwrite(name,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with (R/'results'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

def compare(rows):
 by={(r['capacity_mib'],r['objective']):r for r in rows};ratios=[];paper=[]
 for opt in ('ReadLatency','ReadDynamicEnergy'):
  a,b=by[32,opt],by[128,opt];valid=b['status']=='FINISHED'
  for op in ('read','write'):
   row=dict(objective=opt,operation=op,node_nm=3,status='VALID' if valid else b['status'],capacity_from_mib=32,capacity_to_mib=128,from_log=a['stdout'],to_log=b.get('stdout',''),from_config=a['config'],to_config=b['config'])
   if valid:
    for precision in ('summary','bank_sum'):
     x,y=D(a[f'{op}_{precision}_pj']),D(b[f'{op}_{precision}_pj']);row.update({precision+'_32_pj':str(x),precision+'_128_pj':str(y),precision+'_ratio_128_over_32':str(y/x),precision+'_formula':f'{y}/{x}'})
    for k in ('hit_latency_ns','write_latency_ns','leakage_mw','area_mm2'):row[k+'_32']=a[k];row[k+'_128']=b[k];row[k+'_delta']=str(D(b[k])-D(a[k]))
   ratios.append(row)
 for r in rows:
  for op in ('read','write'):
   for precision in ('summary','bank_sum'):
    key=f'{op}_{precision}_pj';value=D(r[key])/256 if r['status']=='FINISHED' else None
    paper.append(dict(capacity_mib=r['capacity_mib'],objective=r['objective'],operation=op,precision=precision,status='NUMERIC_COMPARISON_ONLY' if value is not None else r['status'],model_effective_pj_bit=str(value) if value is not None else None,reported_public_reference_pj_bit=str(REFERENCE),difference_model_minus_reference=str(value-REFERENCE) if value is not None else None,model_div_reference=str(value/REFERENCE) if value is not None else None,difference_percent=str(100*(value/REFERENCE-1)) if value is not None else None,model_denominator_bits=256,reference_operation='unconfirmed',reference_wordwidth_bits=None,reference_capacity_unit='paper says 128MB; binary/decimal unconfirmed',reference_provenance='LLMET Table 2 reported in task; source text not independently retrieved',model_config=r['config'],model_log=r.get('stdout',''),interpretation='not a reproduction or validation verdict; read/write reference mapping unknown'))
 return ratios,paper

def main():
 try:rows=load();ratios,paper=compare(rows)
 except (OSError,ValueError,KeyError) as e:print('Invalid evidence:',e,file=sys.stderr);return 2
 (R/'results').mkdir(exist_ok=True);(R/'reports').mkdir(exist_ok=True)
 csvwrite('energy_results.csv',[{k:v for k,v in r.items() if k not in ('organization','breakdown','bank_timing')} for r in rows])
 csvwrite('capacity_comparison.csv',ratios);csvwrite('llmet_reference_comparison.csv',paper)
 components=[]
 for r in rows:
  if r['status']!='FINISHED':continue
  for op in ('read','write'):
   components.append(dict(capacity_mib=r['capacity_mib'],objective=r['objective'],operation=op,summary_pj=r[op+'_summary_pj'],bank_sum_pj=r[op+'_bank_sum_pj'],summary_effective_pj_bit=r[op+'_summary_effective_pj_bit'],bank_effective_pj_bit=r[op+'_bank_effective_pj_bit'],data_bank_pj=r[op+'_data_bank_pj'],tag_bank_pj=r[op+'_tag_bank_pj'],routing_subset_pj=r[op+'_routing_pj'],nonrouting_residual_pj=r[op+'_nonrouting_residual_pj'],rounding_delta_pj=r[op+'_rounding_delta_bank_minus_summary_pj'],stdout=r['stdout'],scope='bank=data+tag; routing already included; nested mat/subarray not added'))
 csvwrite('energy_breakdown.csv',components)
 (R/'results/organization_and_metadata.json').write_text(json.dumps(rows,indent=2)+'\n')
 report(rows,ratios,paper)
 done=sum(r['capacity_mib']==128 and r['status']=='FINISHED' for r in rows)
 print('128MiB:',done,'/ 2 FINISHED; 32MiB: 2 historical raw baselines verified; no tuning')
 return 0 if done==2 else 1

def report(rows,ratios,paper):
 lines=['# 3nm 128MiB feasibility and controlled LLMET-reference comparison','',
 '## Method and evidence classes','',
 'Two validated Phase 2-B 3nm/32MiB raw baselines (ReadLatency and ReadDynamicEnergy) are verified rather than re-executed. Each objective supplies a new 128MiB configuration changing **only Capacity (MB): 32→128**. Both objectives were selected before running because both exist in the baseline, not to search for the nearest reference. No other parameters/source/guards/architecture are changed. [Exact diffs and input/cell hashes](../provenance/cases.json).',
 'Source upstream 2fdcbf093f806bc9a28964aca8402c42738d58e5 (54 source/Makefile hashes); SRAM_cell_3nm.cell; cache/Normal, 256bit/32B model line, 16-way, 300K/LOP, H-tree/internal sensing, data ForceBankA=4x4, pruning and latency buffer design, one die, original wires. Source Vdd=0.7V is distinct from cell read voltage=0.248V. Cell area=2047.8F², aspect ratio=0.4395, stitching=16. Port count and explicit timing constraint are not separately specified. Exact parameters remain in configs.',
 'Three evidence classes remain separate: (1) verified historical NS-Cache raw outputs; (2) new capacity-only reconstructed configurations and their actual results; (3) reported **public** LLMET Table 2 reference 0.917pJ/bit. The author config/output is unavailable, pending the user\'s author request. No correspondence or private GPU data is copied.',
 '', '## Existing reference-material inventory','',
 'The repository tracked configs and config members of tracked ZIPs were inspected before creating new cases; no existing 3nm/128MiB author/public config was found. The recovered generic SRAM_cache_3nm.cfg is 32MiB, 512bit, WriteLatency, and is **not** a 128MiB LLMET config. It was not executed or altered. [Inventory](../provenance/reference_inventory.json). No full LLMET URL/DOI/PDF is available locally; arXiv API lookup returned HTTP403. The public scalar is therefore task-reported, not an independently reread Table 2 or confidential measurement.',
 '', '## Actual execution and results','',
 '| MiB | Objective | Evidence/status | Read pJ | Write pJ | Read pJ/bit | Write pJ/bit | Read/hit ns | Write ns | Leakage mW | Area mm² | Solutions | Raw |',
 '|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
 for r in rows:
  vals=[r.get(k,'—') for k in ('read_summary_pj','write_summary_pj','read_summary_effective_pj_bit','write_summary_effective_pj_bit','hit_latency_ns','write_latency_ns','leakage_mw','area_mm2','feasible_solutions')]
  lines.append(f"| {r['capacity_mib']} | {r['objective']} | {r['origin']}/{r['status']} | "+' | '.join(vals)+(f" | [stdout](../../{r['stdout']}) |" if r.get('stdout') else ' | pending |'))
 lines+=['', 'Above energy uses the cache summary (0.001nJ=1pJ resolution). Effective pJ/bit divides complete modeled cache-access energy by WordWidth=256; it is not SRAM bitcell or actual GPU-sector energy. Fine bank sums and normalized values are separate in [results CSV](../results/energy_results.csv). No averaging or denominator change is used to approach 0.917.',
 '', '## Capacity-only comparison and organization','',
 '[32→128 ratios and timing/area/leakage deltas](../results/capacity_comparison.csv) keep each objective/operation/precision matched. [Data/tag/routing](../results/energy_breakdown.csv) and [full organization/activation/mux/wires/buffer and metadata](../results/organization_and_metadata.json) are traceable to raw stdout.',
 '', '| Objective | Operation | Summary 128/32 | Fine bank-sum 128/32 |','|---|---|---:|---:|']
 for r in ratios:lines.append(f"| {r['objective']} | {r['operation']} | "+(f"{D(r['summary_ratio_128_over_32']):.6f} | {D(r['bank_sum_ratio_128_over_32']):.6f} |" if r['status']=='VALID' else 'unavailable | unavailable |'))
 lines+=['', '| MiB | Objective | Data bank/subarray/mat | Tag bank/subarray/mat | Read Data/Tag/Routing pJ | Write Data/Tag/Routing pJ |','|---:|---|---|---|---:|---:|']
 for r in rows:
  if r['status']!='FINISHED':continue
  desc=lambda k:'/'.join(r['organization'][k][v] for v in ('bank','subarray','mat'))
  comp=lambda op:'/'.join(r[op+'_'+v] for v in ('data_bank_pj','tag_bank_pj','routing_pj'))
  lines.append(f"| {r['capacity_mib']} | {r['objective']} | {desc('data')} | {desc('tag')} | {comp('read')} | {comp('write')} |")
 lines+=['', 'Observed structural response: at fixed data bank 4×4, ReadLatency data mat grows from 4096×1024 to 8192×2048, and ReadDynamicEnergy from 4096×2048 to 8192×4096. Selected data subarray row activation decreases 2/2→1/2. Full bank×subarray×mat bit counts equal the requested 32/128MiB in an independent arithmetic check. Internal optimizer choices change naturally despite identical architectural input controls; these are not manually fitted changes.',
  'Read routing subset grows 121.190→242.597pJ for latency objective and 112.391→224.318pJ for energy objective. This observed near-doubling accompanies the approximately 2× access energy, while storage capacity is 4×. It does not isolate a routing-only causal contribution. Large selected mat dimensions and timing require physical-model validation beyond logical capacity feasibility.']
 lines+=['', 'Data+tag bank totals already include H-tree routing. Per-subarray/mat/peripheral outputs overlap the hierarchy and are not added again. Nonrouting residual is not cell-only. Observed organization changes reflect normal optimizer selection under unchanged controls; they do not isolate bit-count, routing or process causality.',
 '', '## Comparison with reported LLMET Table 2 value','',
 'Reference: **0.917pJ/bit**, described as published 3nm/128MB SRAM energy in the task. The table below is only numerical comparison. Author operation, denominator, aggregation, capacity-unit convention and architecture are not confirmed. The model uses exact 128MiB=134217728 bytes; paper “128MB” may have a different convention.',
 '', '| Model MiB | Objective | Operation | Precision | Model pJ/bit | Reported reference | Difference pJ/bit | Model/reference |','|---:|---|---|---|---:|---:|---:|---:|']
 for r in paper:
  if r['capacity_mib']!=128:continue
  lines.append(f"| 128 | {r['objective']} | {r['operation']} | {r['precision']} | "+(f"{D(r['model_effective_pj_bit']):.9f} | 0.917 | {D(r['difference_model_minus_reference']):.9f} | {D(r['model_div_reference']):.6f} |" if r['model_effective_pj_bit'] is not None else 'unavailable | 0.917 | unavailable | unavailable |'))
 lines+=['', 'No row is labeled “LLMET reproduced.” Comparing both read and write to an operation-unspecified scalar does not assert that both correspond to the paper. Numerical proximity alone does not validate source/config/normalization or hardware. [Comparison CSV](../results/llmet_reference_comparison.csv).',
 '', '## Failure analysis and limits','']
 for r in rows:
  if r['capacity_mib']==128 and r['status']!='FINISHED':lines.append(f"- {r['objective']}: {r['status']}; {r.get('error','no completed output')}. Preserve stdout/stderr/exit/RSS/timeout; no energy filled. Distinguish guard violation, no valid design, timeout and resource signal before proposing a separate diagnostic.")
 if all(r['status']=='FINISHED' for r in rows):lines.append('Both capacity-only 128MiB objectives complete under the unchanged geometry/bank constraints; no capacity bypass, unsupported-design workaround or structural change was required. This establishes current-model feasibility for these settings only, not the author\'s setup.')
 lines+=['', 'The cache model includes tag/data and routing and may differ from the paper\'s SRAM boundary. 256bit here is a 32B model line, not a sector with shared 128B metadata. Summary and finer bank precision are not interchanged. Missing author configs/output/source hash and original normalization remain unresolved. Private GPU measurements/coefficients/calibration/scaling data are neither inputs nor outputs.',
 '', '## Recommended separate next steps (not executed)','',
 '1. Obtain author-original config, SRAM cell, source revision/binary/build flags and raw output; preserve unchanged with provenance and replay directly. Confirm Table 2 operation, cache/RAM design target, MB/MiB convention, WordWidth and pJ/bit denominator, read/write aggregation, Vdd/T/ways/bank/wire constraints.',
 '2. If a public reference config is supplied, compare exact source/config/cell hashes before any numerical claim. A supplied original config belongs in a separate reference namespace, never relabeled as this reconstruction.',
 '3. Only after documenting a concrete discrepancy, propose a separate controlled diagnostic such as cache-tag boundary versus SRAM-array boundary or the author\'s documented access width. Obtain a separate scope decision before structural changes. Do not search arbitrary combinations for 0.917.',
 '4. If future runs fail, first preserve guard/no-solution/resource/timeout evidence and check limits. Do not remove verification or silently change banking/organization. No hardware/GPU equivalence or Rubin forecast is established here.']
 (R/'reports/experiment_report.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':raise SystemExit(main())
