"""Raw-only 1GiB feasibility, capacity and cross-node comparison; no model fitting."""
import csv,hashlib,json,math,re,sys
from decimal import Decimal as D
from pathlib import Path
from common import read_raw,require
from manifest import verify_inputs
R=Path(__file__).resolve().parents[1];P=R.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REFERENCES={7:D('2.780'),3:D('2.420')}
REFERENCE_SF=REFERENCES[3]/REFERENCES[7]
def record(name,node,opt,capacity,config,folder,origin):
 row=dict(run_id=name,node_nm=node,objective=opt,capacity_mib=capacity,capacity_bytes=capacity*1024**2,width_bits=256,associativity=16,temperature_k=300,roadmap='LOP',source_derived_vdd_v='0.7',cell_read_voltage_v='0.248' if node==3 else '0.264',source_revision='2fdcbf093f806bc9a28964aca8402c42738d58e5',origin=origin,energy_unit='pJ/model_access',normalized_unit='effective_pJ/bit_32B_model_line',latency_unit='ns',area_unit='mm2',leakage_unit='mW',config=str(config.relative_to(P)))
 attempts=sorted(folder.glob('*/metadata.json'))
 if not attempts:return dict(row,status='UNRUN',analysis_status='UNRUN')
 meta=attempts[-1];m=json.loads(meta.read_text());out=meta.parent/'stdout.log'
 if m['status']=='RUNNING':return dict(row,status='RUNNING',analysis_status='RUNNING',metadata=str(meta.relative_to(P)),stdout=str(out.relative_to(P)))
 cell=P/'NSCache_Experiment_DB/configs/New_Configs'/f'SRAM_cell_{node}nm.cell';r=read_raw(meta,config,cell,origin)
 if r['status']=='FINISHED':
  raw=out.read_text();require(('Capacity   : 1GB' if capacity==1024 else f'Capacity   : {capacity}MB') in raw and 'Cache Line Size: 32Bytes' in raw,'capacity/width header mismatch')
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
 verify_inputs();cases=json.loads((R/'provenance/cases.json').read_text());rows=[];seen=set()
 require(sum(c['capacity_mib']==1024 for c in cases)==4,'four primary cases required')
 for c in cases:
  key=(c['node_nm'],c['objective'],c['capacity_mib']);require(key not in seen,'duplicate case');seen.add(key)
  source=P/c['source_config'];cfg=R/c['config'];node=c['node_nm'];capacity=c['capacity_mib'];basecap=c['baseline_capacity_mib'];opt=c['objective']
  require(node in (3,7) and capacity in (1024,512,256) and c['width_bits']==256,'unsupported case matrix')
  require(cfg.read_bytes()==source.read_bytes().replace(f'-Capacity (MB): {basecap}'.encode(),f'-Capacity (MB): {capacity}'.encode()),'change beyond capacity')
  if not any(r['node_nm']==node and r['capacity_mib']==basecap and r['objective']==opt for r in rows):
   meta=P/c['baseline_metadata'];b=record(meta.parent.parent.name,node,opt,basecap,source,meta.parent.parent,'verified_historical_raw')
   require(b['status']=='FINISHED','baseline not valid');rows.append(b)
  row=record(c['run_id'],node,opt,capacity,cfg,R/'logs'/c['run_id'],c['group']);rows.append(row)
 digest=(R/'provenance/binary.sha256').read_text().split()[0]
 for r in rows:
  if r['status']=='FINISHED':require(r['binary_sha256']==digest,'binary mismatch')
 return rows

def csvwrite(name,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r)) or ['status']
 with (R/'results'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

def comparisons(rows):
 by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows};sf=[];paper=[];capacity=[]
 for opt in ('ReadLatency','ReadDynamicEnergy'):
  for op in ('read','write'):
   for precision in ('summary','bank_sum'):
    a,b=by[7,1024,opt],by[3,1024,opt];valid=a['status']==b['status']=='FINISHED';key=op+'_'+precision+'_pj'
    x,y=(D(a[key]),D(b[key])) if valid else (None,None)
    sf.append(dict(objective=opt,operation=op,precision=precision,status='VALID_MODEL_RATIO' if valid else 'UNAVAILABLE',capacity_mib=1024,energy_7nm_pj=str(x) if valid else None,energy_3nm_pj=str(y) if valid else None,model_sf_7_to_3=str(y/x) if valid else None,formula=f'{y}/{x}' if valid else None,reported_reference_sf=str(REFERENCE_SF),difference_sf=str(y/x-REFERENCE_SF) if valid else None,relative_difference_percent=str(100*((y/x)/REFERENCE_SF-1)) if valid else None,from_log=a.get('stdout'),to_log=b.get('stdout'),from_config=a['config'],to_config=b['config'],limitation='node sensitivity includes cell/wire/Vdd and reoptimization; not pure process or paper validation'))
 for r in rows:
  if r['origin']=='verified_historical_raw':continue
  for op in ('read','write'):
   for precision in ('summary','bank_sum'):
    valid=r['status']=='FINISHED';key=op+'_'+precision+'_pj';v=D(r[key])/256 if valid else None
    paper.append(dict(node_nm=r['node_nm'],capacity_mib=r['capacity_mib'],objective=r['objective'],operation=op,precision=precision,status='NUMERIC_COMPARISON_ONLY' if valid else r['status'],effective_pj_bit=str(v) if valid else None,reported_reference_pj_bit=str(REFERENCES[r['node_nm']]),model_over_reference=str(v/REFERENCES[r['node_nm']]) if valid else None,reference_capacity='1GB; unit convention unconfirmed; modeled 1024MiB is an approximation',reference_provenance='LLMET Table 2 values explicitly supplied as public references in task; original config and normalization unavailable',reference_operation='unconfirmed',config=r['config'],stdout=r.get('stdout'),interpretation='diagnostics below 1024MiB are not the paper capacity' if r['capacity_mib']!=1024 else 'independent modeled comparison, not reproduction validation'))
    basecap=128 if r['node_nm']==3 else 32;a=by[r['node_nm'],basecap,r['objective']]
    capacity.append(dict(node_nm=r['node_nm'],objective=r['objective'],operation=op,precision=precision,status='VALID' if valid else r['status'],baseline_mib=basecap,target_mib=r['capacity_mib'],baseline_pj=a[key],target_pj=r.get(key),capacity_energy_ratio=str(D(r[key])/D(a[key])) if valid else None,formula=f"{r[key]}/{a[key]}" if valid else None,baseline_log=a['stdout'],target_log=r.get('stdout'),baseline_config=a['config'],target_config=r['config']))
 return sf,paper,capacity

def report(rows,sf):
 lines=['# 7nm/3nm 1GiB feasibility and LLMET Table 2 comparison','',
 '## Method and evidence','',
 'Verified Phase 2-C descendant a8d07dfc79266d5a33fb32f71ed20f30fe492d96 is the study base. Existing 3nm/128MiB and 7nm/32MiB baselines, both ReadLatency and ReadDynamicEnergy, are hash-verified rather than rerun. New inputs change Capacity only. Both 3nm objectives are attempted before either 7nm objective. Source, cell, objectives, 256bit WordWidth, 16-way, 300K, Normal cache, LOP, ForceBankA=4x4, H-tree, internal sensing, pruning, wires/buffer settings and one die are preserved. [Exact diffs/hashes](../provenance/cases.json).',
 'The source revision is 2fdcbf093f806bc9a28964aca8402c42738d58e5; all 54 source/Makefile hashes are checked. InputParameter.cpp:324–327 parses the MB field in binary units; capacity is int64_t (InputParameter.h:45); main.cpp:434,451,506 and macros.h:138–180 retain original tag/data capacity verification. 1024MiB = 1073741824 bytes. This is an explicitly documented approximation to paper 1GB until its convention is confirmed, not proof of decimal/binary equivalence.',
 'Source-derived nominal Vdd is 0.7V for both nodes. Cell read voltages differ (7nm 0.264V, 3nm 0.248V); SRAM cell area/aspect and transistor/wire parameters also differ. These are cache-model outputs, not isolated SRAM bitcell or GPU hardware measurements. Original author configs/output and operation/aggregation/normalization are unavailable. The task-reported public reference values are 7nm 2.780 and 3nm 2.420pJ/bit; their ratio is '+str(REFERENCE_SF)+'. Neither reference is used to select execution parameters.',
 '', '## Execution and full results','',
 'Bounded runs use at most two children, 1800s wall timeout per case, retained stdout/stderr/exit/timestamps/CPU/max-RSS/environment and config/cell/binary hashes. No hard memory cap is claimed. Failed/timeout cases retain missing energy; completion requires exit 0, Finished!, parseable metrics and independent selected-capacity arithmetic.',
 '', '| Node | MiB | Objective | Evidence/status | Read pJ | Write pJ | Read pJ/bit | Write pJ/bit | Hit ns | Write ns | Leakage mW | Area mm² | Solutions |','|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
 for r in rows:
  vals=[r.get(k,'—') for k in ('read_summary_pj','write_summary_pj','read_summary_effective_pj_bit','write_summary_effective_pj_bit','hit_latency_ns','write_latency_ns','leakage_mw','area_mm2','feasible_solutions')]
  lines.append(f"| {r['node_nm']} | {r['capacity_mib']} | {r['objective']} | {r['origin']}/{r['status']} | "+' | '.join(vals)+' |')
 lines+=['', 'Cache summary energy is printed to 0.001nJ (1pJ); the printed Data+Tag bank sum is retained separately with per-bank resolution and combined rounding bounds; large bank energies printed in nJ need not be finer than the summary. E_effective_bit = E_access/256. SF = E_3nm/E_7nm at the same capacity/objective/operation/precision. No mixed-precision ratios. [Energy and log/config links](../results/energy_results.csv), [capacity sensitivities](../results/capacity_comparison.csv).',
 '', '## Cross-node scaling and paper-reference comparison','',
 '| Objective | Operation | Precision | 3nm/7nm model SF | Reported paper ratio | Difference |','|---|---|---|---:|---:|---:|']
 for r in sf:lines.append('| '+' | '.join((f'{D(r[k]):.8f}' if k in ('model_sf_7_to_3','reported_reference_sf','difference_sf') else str(r[k])) if r.get(k) is not None else 'unavailable' for k in ('objective','operation','precision','model_sf_7_to_3','reported_reference_sf','difference_sf'))+' |')
 lines+=['', '| Node | Objective | Read model pJ/bit | Write model pJ/bit | Reported reference pJ/bit | Read/reference | Write/reference |','|---:|---|---:|---:|---:|---:|---:|']
 for r in rows:
  if r['capacity_mib']!=1024 or r['status']!='FINISHED':continue
  read=D(r['read_summary_effective_pj_bit']);write=D(r['write_summary_effective_pj_bit']);ref=REFERENCES[r['node_nm']]
  lines.append(f"| {r['node_nm']} | {r['objective']} | {read:.8f} | {write:.8f} | {ref} | {read/ref:.6f} | {write/ref:.6f} |")
 lines+=['', '[Per-node pJ/bit comparison](../results/llmet_reference_comparison.csv) reports both read and write without assuming the reference operation. [Cross-node CSV](../results/cross_node_sf.csv) retains formulas and both raw-log/config operands. A numeric match does not validate LLMET. The model boundary includes data/tag/routing and a 32B model line; the paper boundary, access width and normalization are unconfirmed. Cross-node changes include cell/wires/optimizer, even if nominal Vdd matches; do not label these pure process scaling.',
 '', '## Organization and energy structure','', '| Node | MiB | Objective | Data bank/subarray/mat | Tag bank/subarray/mat | Read Data/Tag/Routing pJ | Write Data/Tag/Routing pJ |','|---:|---:|---|---|---|---:|---:|']
 for r in rows:
  if r['status']!='FINISHED':continue
  org=lambda label:'/'.join(r['organization'][label][k] for k in ('bank','subarray','mat'))
  comp=lambda op:'/'.join(r[op+'_'+k] for k in ('data_bank_pj','tag_bank_pj','routing_pj'))
  lines.append(f"| {r['node_nm']} | {r['capacity_mib']} | {r['objective']} | {org('data')} | {org('tag')} | {comp('read')} | {comp('write')} |")
 lines+=['', 'Data+Tag bank sums already contain H-tree routing. Routing is a subset, never an extra addend; nested subarray/mat/peripheral outputs overlap. [Breakdown](../results/energy_breakdown.csv) and [full organization/metadata](../results/organization_and_metadata.json) preserve printed hierarchy and timing. Large selected mats establish logical model feasibility only; physical accuracy is unvalidated. Changes in selected internal geometry occur through the unchanged optimizer, not manually altered constraints. Baseline-to-target capacity multipliers differ (3nm 8×, 7nm 32×), so their growth ratios are not isolated cross-node effects.',
 '', 'Observed capacity growth (summary precision):']
 for r in rows:
  if r['capacity_mib']!=1024 or r['status']!='FINISHED':continue
  baseline=next(x for x in rows if x['node_nm']==r['node_nm'] and x['objective']==r['objective'] and x['origin']=='verified_historical_raw')
  rr=D(r['read_summary_pj'])/D(baseline['read_summary_pj']);wr=D(r['write_summary_pj'])/D(baseline['write_summary_pj'])
  lines.append(f"- {r['node_nm']}nm {r['objective']}: {baseline['capacity_mib']}→1024MiB; Read energy {rr:.4f}×, Write {wr:.4f}×.")
 lines+=['', 'At 1GiB the selected data geometry is 4×4 banks, 2×2 subarrays and 16384×8192-bit mats in all four cases; matching these dimensions alone does not imply matching active circuitry or optimizer choices. The tag geometry and full activation/MUX/wire/buffer details differ. Observed read energies change substantially with objective despite almost identical 3nm hit latency; the printed Data and Tag totals both change. Reoptimization and routing/peripheral choices are plausible explanations, not experimentally isolated causes. All model values remain above the task-reported same-node reference in both operations. The SF comparison is therefore distinct from reproducing absolute paper energies.',
 '', '## Failure evidence, limitations and next steps','']
 for r in rows:
  if r['origin']=='verified_historical_raw':continue
  lines.append(f"- {r['run_id']}: {r['status']}; elapsed {r.get('elapsed_seconds','unknown')}s; max RSS {r.get('max_rss_kib','unknown')}KiB; exit {r.get('returncode','unknown')}; [stdout](../../{r.get('stdout','')}); [metadata](../../{r.get('metadata','')}).")
 primary=[r for r in rows if r['capacity_mib']==1024]
 if all(r['status']=='FINISHED' for r in primary):lines+=['', 'All four primary cases completed; no 512/256MiB diagnostic is justified or executed. No source patch, bank/geometry relaxation or capacity verification bypass was needed.']
 else:lines+=['', 'Primary failures are not successful designs; 512/256MiB capacity-only diagnostics, if present, are separately labeled and never substitute for 1GiB. Full guard/no-solution/resource evidence must be interpreted before proposing architecture changes.']
 lines+=['', 'Recommended next experiment: obtain the author-original config/cell/source/raw output and confirm operation, denominator, cache-vs-SRAM boundary, GB convention and access width before an exact replay. Any structural diagnostic requires a separately described discrepancy and experiment. Do not search arbitrary parameters to fit reference values. No actual GPU equivalence, hardware validation or private GPU data comparison is established. Earlier studies/main remain unchanged; no merges.']
 (R/'reports/experiment_report.md').write_text('\n'.join(lines)+'\n')

def main():
 try:rows=load();sf,paper,capacity=comparisons(rows)
 except (OSError,ValueError,KeyError) as e:print('Invalid evidence:',e,file=sys.stderr);return 2
 for d in ('results','reports'):(R/d).mkdir(exist_ok=True)
 csvwrite('energy_results.csv',[{k:v for k,v in r.items() if k not in ('organization','breakdown','bank_timing')} for r in rows])
 csvwrite('cross_node_sf.csv',sf);csvwrite('llmet_reference_comparison.csv',paper);csvwrite('capacity_comparison.csv',capacity)
 components=[]
 for r in rows:
  if r['status']!='FINISHED':continue
  for op in ('read','write'):
   components.append(dict(node_nm=r['node_nm'],capacity_mib=r['capacity_mib'],objective=r['objective'],operation=op,summary_pj=r[op+'_summary_pj'],bank_sum_pj=r[op+'_bank_sum_pj'],data_bank_pj=r[op+'_data_bank_pj'],tag_bank_pj=r[op+'_tag_bank_pj'],routing_subset_pj=r[op+'_routing_pj'],nonrouting_residual_pj=r[op+'_nonrouting_residual_pj'],rounding_delta_pj=r[op+'_rounding_delta_bank_minus_summary_pj'],data_resolution_pj=r[op+'_data_bank_resolution_pj'],tag_resolution_pj=r[op+'_tag_bank_resolution_pj'],bank_sum_rounding_bound_pj=r[op+'_bank_sum_rounding_bound_pj'],stdout=r['stdout'],scope='routing included in data+tag; no nested sums'))
 csvwrite('energy_breakdown.csv',components)
 (R/'results/organization_and_metadata.json').write_text(json.dumps(rows,indent=2)+'\n');report(rows,sf)
 primary=[r for r in rows if r['capacity_mib']==1024];print('Primary 1GiB status:',{s:sum(r['status']==s for r in primary) for s in sorted({r['status'] for r in primary})})
 return 0 if all(r['status'] in ('FINISHED','FAILED','TIMEOUT') for r in primary) else 1
if __name__=='__main__':raise SystemExit(main())
