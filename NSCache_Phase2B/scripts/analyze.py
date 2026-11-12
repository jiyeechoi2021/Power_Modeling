"""Raw-derived capacity analysis; failed geometry never receives fabricated energy."""
import csv,hashlib,importlib.util,json,math,re,sys
from decimal import Decimal as D
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
spec=importlib.util.spec_from_file_location('phase2a_reader',P/'NSCache_Phase2A/scripts/analyze.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
parse=reader.parse;breakdown=reader.breakdown
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def csvwrite(name,rows):
 with (R/'results'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator='\n');w.writeheader();w.writerows(rows)
def energy(values,org,detail):
 result={k:str(v) for k,v in values.items()}
 for op,metric in [('read','read_pj_per_access'),('write','write_pj_per_access')]:
  label='Read Dynamic Energy' if op=='read' else 'Write Dynamic Energy'
  data=D(detail['data'][op][label]['pj']);tag=D(detail['tag'][op][label]['pj']);route=sum(D(detail[a][op]['H-Tree Dynamic Energy']['pj']) for a in ('data','tag'));total=data+tag
  require(0<=route<=total,'routing outside bank total')
  result.update({op+'_summary_pj':str(values[metric]),op+'_summary_effective_pj_bit':str(values[metric]/256),op+'_bank_sum_pj':str(total),op+'_bank_effective_pj_bit':str(total/256),op+'_rounding_delta_bank_minus_summary_pj':str(total-values[metric]),op+'_data_bank_pj':str(data),op+'_tag_bank_pj':str(tag),op+'_routing_pj':str(route),op+'_nonrouting_residual_pj':str(total-route)})
  require(abs(total-values[metric])<=D('.501'),'summary/bank precision inconsistency')
 return result

def read_raw(meta_path,config,cell,origin):
 m=json.loads(meta_path.read_text());out=meta_path.parent/'stdout.log';err=meta_path.parent/'stderr.log'
 for p,k in [(config,'config_sha256'),(cell,'cell_sha256'),(out,'stdout_sha256'),(err,'stderr_sha256')]:require(sha(p)==m[k],f'hash mismatch {p}')
 if 'environment_sha256' in m:require(sha(meta_path.parent/'environment.json')==m['environment_sha256'],'environment hash mismatch')
 raw=out.read_text();status=m['status']
 base=dict(origin=origin,status=status,returncode=m.get('returncode'),elapsed_seconds=m.get('elapsed_seconds'),max_rss_kib=m.get('max_rss_kib'),metadata=str(meta_path.relative_to(P)),config=str(config.relative_to(P)),stdout=str(out.relative_to(P)),stderr=str(err.relative_to(P)),binary_sha256=m['binary_sha256'],config_sha256=m['config_sha256'],stdout_sha256=m['stdout_sha256'])
 if status=='FINISHED':
  require(m['returncode']==0 and 'Finished!' in raw,'invalid completion');values,org=parse(raw);detail=breakdown(raw);base.update(energy(values,org,detail),organization=org,breakdown=detail,analysis_status='VALID')
 else:
  base.update(analysis_status='UNSUPPORTED_GEOMETRY' if 'capacity violation' in raw else status,error='capacity violation' if 'capacity violation' in raw else 'see raw output')
 return base

def protected():
 b=json.loads((R/'provenance/protected.json').read_text())
 for n,h in b['sha256'].items():require(sha(P/n)==h,'historical file changed: '+n)
 return len(b['sha256'])

def load():
 protected();cases=json.loads((R/'provenance/cases.json').read_text());rows=[]
 for c in cases:
  require(sha(R/c['config'])==c['config_sha256'],'case input changed')
  source=P/c['source'];require(sha(source)==c['source_sha256'],'source input changed')
  expected=re.sub(r'^-Capacity \(MB\): 1$',f"-Capacity (MB): {c['capacity_mib']}",source.read_text(),flags=re.M)
  require((R/c['config']).read_text()==expected,'unrecorded config change')
  meta=sorted((R/'logs'/c['run_id']).glob('*/metadata.json'))
  if not meta:rows.append(dict(c,origin='new',status='UNRUN',analysis_status='UNRUN'));continue
  cell=P/'NSCache_Experiment_DB/configs/New_Configs'/f"SRAM_cell_{c['node_nm']}nm.cell"
  rows.append(dict(c,**read_raw(meta[-1],R/c['config'],cell,'new')))
 for n in (14,7,5,3):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   name=f'L2_{n}nm'+('_ReadEnergy' if opt=='ReadDynamicEnergy' else '')
   meta=sorted((P/'NSCache_Phase2A/logs/phase2_256bit'/name).glob('*/metadata.json'))[-1]
   config=P/'NSCache_Phase2A/configs/phase2_256bit'/(name+'.cfg');cell=P/'NSCache_Experiment_DB/configs/New_Configs'/f'SRAM_cell_{n}nm.cell'
   rows.append(dict(run_id=f'L2_{n}nm_1MiB_{opt}',node_nm=n,capacity_mib=1,objective=opt,group='baseline1',**read_raw(meta,config,cell,'verified_phase2a')))
 for r in rows:
  n=r['node_nm'];r.update(verified_source_revision='2fdcbf093f806bc9a28964aca8402c42738d58e5',width_bits=256,temperature_k=300,device_roadmap='LOP',source_derived_vdd_v={14:'0.8',7:'0.7',5:'0.7',3:'0.7'}[n],cell_read_voltage_v={14:'0.277',7:'0.264',5:'0.253',3:'0.248'}[n],associativity=16,force_data_bank='4x4',port_count=None,explicit_timing_constraint=None,precision_note='summary 1pJ; fine bank sums separately labeled')
 require(len({r['binary_sha256'] for r in rows if r.get('binary_sha256')})==1,'different runtime binaries')
 return rows

def fixed_sf(rows):
 by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows};out=[]
 for c in (1,32):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   for op in ('read','write'):
    for a,b in ((14,7),(7,5),(5,3)):
     x,y=by[a,c,opt],by[b,c,opt];valid=x['status']==y['status']=='FINISHED'
     r=dict(capacity_mib=c,objective=opt,operation=op,from_nm=a,to_nm=b,status='VALID' if valid else 'UNAVAILABLE',precision='summary_1pJ',from_log=x.get('stdout',''),to_log=y.get('stdout',''),from_config=x.get('config',''),to_config=y.get('config',''))
     if valid:
      first,second=D(x[op+'_summary_pj']),D(y[op+'_summary_pj']);sf=second/first;r.update(energy_from_pj=str(first),energy_to_pj=str(second),sf=str(sf),reduction_percent=str(100*(1-sf)),formula=f'{second}/{first}')
     out.append(r)
 return out

def factorization(e_a_c1,e_b_c1,e_a_c2,e_b_c2):
 a,b,c,d=map(F,(e_a_c1,e_b_c1,e_a_c2,e_b_c2))
 total=d/a;nodefirst=b/a;capafter=d/b;capfirst=c/a;nodeafter=d/c
 require(total==nodefirst*capafter==capfirst*nodeafter,'multiplicative identity failed')
 return dict(total_ratio=str(total),node_first=str(nodefirst),capacity_after_node=str(capafter),capacity_first=str(capfirst),node_after_capacity=str(nodeafter),interaction_node_after_div_node_first=str(nodeafter/nodefirst),identity_exact=True)

def bridges(rows,control=False):
 by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows};out=[]
 transitions=[(14,7,1,32),(7,5,1,32)] if control else [(14,7,6,40),(7,5,40,50)]
 for a,b,c,d in transitions:
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   for op in ('read','write'):
    endpoints=[by.get((a,c,opt)),by.get((b,c,opt)),by.get((a,d,opt)),by.get((b,d,opt))]
    valid=all(x and x['status']=='FINISHED' for x in endpoints)
    item=dict(from_nm=a,to_nm=b,capacity_from_mib=c,capacity_to_mib=d,objective=opt,operation=op,precision='summary_1pJ',status='VALID_CONTROL_NOT_GPU_NOMINAL' if valid and control else 'VALID' if valid else 'UNAVAILABLE_GEOMETRY',reference_order='node at old capacity, then resize at new node',formula='E(b,d)/E(a,c)=[E(b,c)/E(a,c)]*[E(b,d)/E(b,c)]; alternative=[E(a,d)/E(a,c)]*[E(b,d)/E(a,d)]')
    for label,x in zip(('a_c1','b_c1','a_c2','b_c2'),endpoints):item[label+'_log']=x.get('stdout','') if x else '';item[label+'_config']=x.get('config','') if x else ''
    if valid:item.update(factorization(*(x[op+'_summary_pj'] for x in endpoints)))
    out.append(item)
 return out

def partitions(rows):
 by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows};out=[]
 for node,total,count,local,label in [(7,40,2,20,'A100 hypothetical two equal partitions'),(5,50,2,25,'H100 illustrative N=2 not verified'),(5,50,5,10,'H100 illustrative N=5 not verified'),(14,6,2,3,'V100 illustrative N=2 not verified'),(7,32,4,8,'supported 32MiB synthetic control'),(5,32,4,8,'supported 32MiB synthetic control')]:
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   mono=by.get((node,total,opt));part=by.get((node,local,opt));valid=mono and part and mono['status']==part['status']=='FINISHED'
   item=dict(node_nm=node,total_mib=total,partitions=count,local_mib=local,objective=opt,scenario=label,status='VALID_LOCAL_CONTROL' if valid else 'UNAVAILABLE_GEOMETRY',activity_assumption='one local partition active per transaction; equal traffic weights',shared_fabric_energy_pj=None,shared_leakage_mw=None,global_latency_ns=None,monolithic_log=mono.get('stdout','') if mono else '',local_log=part.get('stdout','') if part else '')
   if valid:
    for op in ('read','write'):
     e=D(part[op+'_summary_pj']);m=D(mono[op+'_summary_pj']);item.update({op+'_local_pj_access':str(e),op+'_local_effective_pj_bit':str(e/256),op+'_monolithic_pj_access':str(m),op+'_local_div_monolithic':str(e/m)})
    item.update(local_latency_ns=part['hit_latency_ns'],sum_local_leakage_mw=str(count*D(part['leakage_mw'])),sum_local_area_mm2=str(count*D(part['area_mm2'])))
   out.append(item)
 return out

def archive_comparison(rows):
 out=[];by={(r['node_nm'],r['objective']):r for r in rows if r['capacity_mib']==32}
 for n in (14,7,5,3):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   label='ReadEnergy' if opt=='ReadDynamicEnergy' else opt
   path=R/'baseline_32MiB/uploaded/logs'/f'L2_{n}nm_32MB_{label}.stdout.log';values,org=parse(path.read_text());details=breakdown(path.read_text());imported=energy(values,org,details);new=by[n,opt]
   for metric in ('read_summary_pj','write_summary_pj','read_bank_sum_pj','write_bank_sum_pj','hit_latency_ns','area_mm2','leakage_mw','feasible_solutions'):
    actual=new.get(metric);delta=D(actual)-D(imported[metric]) if actual is not None else None
    out.append(dict(node_nm=n,objective=opt,metric=metric,uploaded=imported[metric],fresh=actual,difference=str(delta) if delta is not None else None,status='EXACT_MATCH' if delta==0 else 'DIFFERENT' if delta is not None else 'UNTESTED',uploaded_log=str(path.relative_to(P)),fresh_log=new.get('stdout',''),note='matching values do not establish uploaded source provenance'))
 return out

def capacity_sensitivity(rows):
 by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows};out=[]
 for n in (14,7,5,3):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   a,b=by[n,1,opt],by[n,32,opt]
   for op in ('read','write'):
    r=dict(node_nm=n,objective=opt,operation=op,status='VALID' if b['status']=='FINISHED' else 'UNAVAILABLE',from_log=a['stdout'],to_log=b.get('stdout',''),from_config=a['config'],to_config=b.get('config',''))
    if b['status']=='FINISHED':
     for precision in ('summary','bank_sum'):
      first,second=D(a[op+'_'+precision+'_pj']),D(b[op+'_'+precision+'_pj'])
      r.update({precision+'_1MiB_pj':str(first),precision+'_32MiB_pj':str(second),precision+'_ratio_32_over_1':str(second/first),precision+'_formula':f'{second}/{first}'})
    out.append(r)
 return out

def csv_precision_audit(rows):
 by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows};out=[]
 with (R/'baseline_32MiB/uploaded/results/capacity_comparison_256bit.csv').open() as f:arch=list(csv.DictReader(f))
 for x in arch:
  n=int(x['node_nm']);opt=x['objective'];a,b=by[n,1,opt],by[n,32,opt]
  if b['status']!='FINISHED':continue
  for op in ('read','write'):
   stored=D(x[op+'_ratio_32MB_to_1MB_rounded']);summary=D(b[op+'_summary_pj'])/D(a[op+'_summary_pj']);fine=D(b[op+'_bank_sum_pj'])/D(a[op+'_bank_sum_pj']);mixed=D(b[op+'_bank_sum_pj'])/D(a[op+'_summary_pj'])
   out.append(dict(node_nm=n,objective=opt,operation=op,uploaded_ratio=str(stored),consistent_summary_ratio=str(summary),consistent_bank_sum_ratio=str(fine),mixed_fine_numerator_summary_denominator_ratio=str(mixed),matches_mixed_at_4dp=abs(stored-mixed)<=D('.00005'),note='uploaded derived ratio is not an experiment input; use like-for-like precision'))
 return out


def main():
 try:
  rows=load();sf=fixed_sf(rows);bridge=bridges(rows);control=bridges(rows,True);parts=partitions(rows);comparison=archive_comparison(rows);capacity=capacity_sensitivity(rows);precision_audit=csv_precision_audit(rows)
 except (OSError,ValueError,KeyError) as e:print('Invalid input:',e,file=sys.stderr);return 2
 (R/'results').mkdir(exist_ok=True)
 csvwrite('l2_capacity_energy.csv',[{k:v for k,v in x.items() if k not in ('organization','breakdown')} for x in rows])
 csvwrite('capacity_sensitivity.csv',capacity);csvwrite('uploaded_csv_precision_audit.csv',precision_audit)
 csvwrite('fixed_capacity_sf.csv',sf);csvwrite('gpu_nominal_bridge.csv',bridge);csvwrite('bridge_control_1_32MiB.csv',control);csvwrite('partition_scenarios.csv',parts);csvwrite('uploaded_32MiB_comparison.csv',comparison)
 components=[]
 for r in rows:
  if r['status']!='FINISHED':continue
  for op in ('read','write'):components.append(dict(run_id=r['run_id'],node_nm=r['node_nm'],capacity_mib=r['capacity_mib'],objective=r['objective'],operation=op,summary_pj=r[op+'_summary_pj'],bank_sum_pj=r[op+'_bank_sum_pj'],summary_pj_bit=r[op+'_summary_effective_pj_bit'],bank_sum_pj_bit=r[op+'_bank_effective_pj_bit'],data_bank_pj=r[op+'_data_bank_pj'],tag_bank_pj=r[op+'_tag_bank_pj'],routing_subset_pj=r[op+'_routing_pj'],nonrouting_residual_pj=r[op+'_nonrouting_residual_pj'],rounding_delta_pj=r[op+'_rounding_delta_bank_minus_summary_pj'],stdout=r['stdout'],scope='bank=data+tag; routing already included; nested per-mat/subarray not added'))
 csvwrite('energy_breakdown.csv',components)
 (R/'results/parsed_results.json').write_text(json.dumps(rows,indent=2)+'\n')
 report(rows,sf,bridge,control,parts,comparison)
 pending=sum(r['status'] in ('UNRUN','RUNNING','TIMEOUT') for r in rows)
 print('Analysis:',len(rows),'cases;',sum(r['status']=='FINISHED' for r in rows),'finished;',sum(r['status']=='FAILED' for r in rows),'failed;',pending,'pending/timeout')
 return 1 if pending else 0

def report(rows,sf,bridge,control,parts,comparison):
 lines=['# Phase 2-B: L2 capacity and organization','',
 '## Scope and feasibility','',
 'All energies are exploratory NS-Cache model results. Model nodes 14/7/5nm are proxies for V100/A100/H100 process families, not foundry-equivalent nodes. No private GPU coefficients were used. See [gate](feasibility_gate.md) and [assumptions](model_assumptions_and_limits.md). Native non-power-of-two capacity jobs fail an unmodified model capacity assertion; failed cases have no energy values. No source patches, rounded capacities or relaxed constraints are substituted.',
 'The uploaded archive is preserved separately; missing metadata and differing binary provenance require fresh 32MiB runs. Existing 1MiB runs are verified from Phase 2-A raw evidence. Each successful row exposes summary and fine bank-sum precision separately.',
 'Precision audit: the uploaded derived CSV ratios match a fine 32MiB numerator divided by a rounded 1MiB denominator at its displayed precision. Those ratios are not reused. [Audit](../results/uploaded_csv_precision_audit.csv), [consistent summary and bank-sum capacity ratios](../results/capacity_sensitivity.csv).',
 '', '## Native coverage and 1/32/6/40/50MiB side-by-side','',
 '| MiB | Node | Objective | Origin/status | Read pJ/access | Write pJ/access | Read pJ/bit | Write pJ/bit | Latency ns | Area mm² | Leakage mW | Raw |','|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
 for r in sorted(rows,key=lambda x:(x['capacity_mib'],x['node_nm'],x['objective'])):
  if r['capacity_mib'] not in (1,32,6,40,50):continue
  vals=[r.get(k,'—') for k in ('read_summary_pj','write_summary_pj','read_summary_effective_pj_bit','write_summary_effective_pj_bit','hit_latency_ns','area_mm2','leakage_mw')]
  lines.append(f"| {r['capacity_mib']} | {r['node_nm']} | {r['objective']} | {r['origin']}/{r['analysis_status']} | "+' | '.join(vals)+f" | [stdout](../../{r['stdout']}) |" if r.get('stdout') else f"| {r['capacity_mib']} | {r['node_nm']} | {r['objective']} | UNRUN | — | — | — | — | — | — | — | — |")
 lines+=['','## Fixed-capacity SF (summary precision)','',
 '| MiB | Objective | Operation | Node transition | SF | Reduction % |','|---:|---|---|---|---:|---:|']
 for r in sf:lines.append(f"| {r['capacity_mib']} | {r['objective']} | {r['operation']} | {r['from_nm']}→{r['to_nm']} | {format(D(r['sf']),'.6f') if r.get('sf') else 'UNAVAILABLE'} | {format(D(r['reduction_percent']),'.3f') if r.get('reduction_percent') else '—'} |")
 lines+=['', 'SF_C=E(C,b)/E(C,a) always uses identical capacity/objective/precision. It is not pure process scaling: Vdd, cells, wires and independently chosen organization change. [CSV with raw endpoints and substitutions](../results/fixed_capacity_sf.csv).',
 '', '## Capacity effect: 32MiB / 1MiB','', '| Node | Objective | Read ratio | Write ratio | Read pJ/bit 1→32 | Write pJ/bit 1→32 |','|---:|---|---:|---:|---:|---:|']
 by={(r['node_nm'],r['capacity_mib'],r['objective']):r for r in rows}
 for n in (14,7,5,3):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   a,b=by[n,1,opt],by[n,32,opt]
   if b['status']=='FINISHED':lines.append(f"| {n} | {opt} | {D(b['read_summary_pj'])/D(a['read_summary_pj']):.6f} | {D(b['write_summary_pj'])/D(a['write_summary_pj']):.6f} | {a['read_summary_effective_pj_bit']}→{b['read_summary_effective_pj_bit']} | {a['write_summary_effective_pj_bit']}→{b['write_summary_effective_pj_bit']} |")
 lines+=['', '### Observed bank components and organization', '',
  '| Node | Objective | Operation | Data bank pJ 1→32 | Tag bank pJ 1→32 | Routing subset pJ 1→32 |',
  '|---:|---|---|---:|---:|---:|']
 for n in (14,7,5,3):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   a,b=by[n,1,opt],by[n,32,opt]
   if b['status']!='FINISHED':continue
   for op in ('read','write'):
    lines.append(f"| {n} | {opt} | {op} | {a[op+'_data_bank_pj']}→{b[op+'_data_bank_pj']} | {a[op+'_tag_bank_pj']}→{b[op+'_tag_bank_pj']} | {a[op+'_routing_pj']}→{b[op+'_routing_pj']} |")
 lines+=['', '| Node | Objective | Data bank/subarray/mat 1→32 | Tag bank/subarray/mat 1→32 |', '|---:|---|---|---|']
 for n in (14,7,5,3):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   a,b=by[n,1,opt],by[n,32,opt]
   if b['status']!='FINISHED':continue
   desc=lambda r,k:'/'.join(r['organization'][k][v] for v in ('bank','subarray','mat'))
   lines.append(f"| {n} | {opt} | {desc(a,'data')} → {desc(b,'data')} | {desc(a,'tag')} → {desc(b,'tag')} |")
 lines+=['', 'Observed larger model cache energy includes bank routing, tag storage and optimizer geometry changes. It does not establish hardware GPU energy scaling. 1MiB and 32MiB are both single modeled cache objects with their own data/tag geometry. [Full data/tag/mat/mux/wire/buffer detail](../results/parsed_results.json), [consistent bank-level breakdown](../results/energy_breakdown.csv). Routing is already inside data/tag bank energy; residual is not cell-only. No overlapping hierarchy is summed.',
 '', '## GPU-nominal and counterfactual bridge','',
 'Required E(14,6), E(7,40), E(5,50), fixed-capacity node factors and same-node capacity factors are unavailable: all requested native pairs fail. Both reference node-first/resize-second and alternate capacity-first identities are preserved in [gpu_nominal_bridge.csv](../results/gpu_nominal_bridge.csv), with failed endpoint logs/configs. No numeric ratio or GPU causal attribution is fabricated.',
 'For a supported **1→32MiB positive algebra control**, [bridge_control_1_32MiB.csv](../results/bridge_control_1_32MiB.csv) verifies both factorizations using exact rational arithmetic from raw summary energies. These controls are not substitutions for GPU-nominal results. Their reference ordering is node at old capacity, then capacity at new node.',
 '', '| Node transition | Objective | Operation | Total ratio | Node-first | Resize after node | Resize-first | Node after resize | Interaction |','|---|---|---|---:|---:|---:|---:|---:|---:|']
 for r in control:
  if r['status'].startswith('VALID'):lines.append(f"| {r['from_nm']}→{r['to_nm']} | {r['objective']} | {r['operation']} | "+' | '.join(f"{float(F(r[k])):.6f}" for k in ('total_ratio','node_first','capacity_after_node','capacity_first','node_after_capacity','interaction_node_after_div_node_first'))+' |')
 lines+=['', 'The total ratio is identical for either ordering; individual factors differ when interaction ≠1. These are algebraic allocations, not experimentally isolated process or architecture causes. Exact identities are checked without mixing fine and rounded energy.',
 '', '## Partition sensitivity','',
 '| Scenario | Node | Objective | Status | Read local / mono pJ | Write local / mono pJ | Sum local leakage mW | Sum local area mm² |','|---|---:|---|---|---:|---:|---:|---:|']
 for r in parts:lines.append(f"| {r['scenario']} | {r['node_nm']} | {r['objective']} | {r['status']} | {r.get('read_local_pj_access','—')} / {r.get('read_monolithic_pj_access','—')} | {r.get('write_local_pj_access','—')} / {r.get('write_monolithic_pj_access','—')} | {r.get('sum_local_leakage_mw','—')} | {r.get('sum_local_area_mm2','—')} |")
 lines+=['', '40=2×20, 50=2×25, 50=5×10 and 6=2×3 cannot supply local energies under this source. The supported 32=4×8 control is explicitly hypothetical, not an actual GPU partition count. If exactly one partition activates, local candidate E is E(8), **not 4×E(8)**; weighted traffic gives Σw_jE_j plus unknown fabric/control energy. Summed local leakage/area omit shared costs; local latency excludes global network. [Scenario CSV](../results/partition_scenarios.csv).',
 '', '## Precision, provenance and unresolved work','',
 'Effective pJ/bit=Eaccess/256 is a normalized model access, not an SRAM cell bit energy. Summary energy prints 1pJ steps; separate data+tag totals have finer printed precision. Both are retained with their differences; each SF/bridge uses summary precision consistently. Matching external rerun metrics do not prove external source provenance. [Upload comparison](../results/uploaded_32MiB_comparison.csv).',
 'The model uses a 32B line, not shared metadata for a 32B GPU sector within a 128B line. No direct private GPU coefficient comparison is published. GPU SKU specifications and A100 high-level partition statements require primary-source verification; current network denies NVIDIA docs. H100 physical partition count remains unknown.',
 'Next: supported non-power-of-two address mapping/tag geometry in a separately reviewed model change; fixed-organization and Vdd sensitivity; independently parameterized line/sector width and shared tag/fabric costs; complete public GPU/NCU evidence. Existing sources/inputs/results remain untouched.']
 (R/'reports/experiment_report.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':raise SystemExit(main())
