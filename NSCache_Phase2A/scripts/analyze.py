"""Regenerate Phase 2 comparisons from verified fresh logs and immutable Phase 1 logs."""
import csv
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
P1=ROOT.parent/'NSCache_Experiment_DB'
sys.path.insert(0,str(P1/'scripts'))
from analyze import parse, METRICS
from scaling import load_sources,case_name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def require(ok,message):
    if not ok:raise ValueError(message)


def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def breakdown(raw):
    """Preserve printed detail and per-subarray/per-mat scope; do not sum nested levels."""
    sections=re.split(r'CACHE (?:DATA|TAG) ARRAY DETAILS',raw)
    require(len(sections)==3,'missing data/tag detail sections')
    result={}
    for label,text in zip(('data','tag'),sections[1:]):
        power=text.split('    Power:',1)[1]
        read,write=power.split('     - Write Dynamic Energy = ',1)
        orgtext=text.split('CONFIGURATION',1)[1].split('RESULT',1)[0]
        entry={'configuration_detail':orgtext.strip(),'read':{},'write':{}}
        for kind,block in [('read',read),('write','     - Write Dynamic Energy = '+write)]:
            for line in block.splitlines():
                m=re.search(r'([A-Za-z][A-Za-z &-]*Dynamic Energy)\s*=\s*([\d.]+)(pJ|nJ|fJ)(.*)',line)
                if m:
                    key=m.group(1).strip()
                    value=D(m.group(2))*{'pJ':D(1),'nJ':D(1000),'fJ':D('.001')}[m.group(3)]
                    entry[kind][key]={'pj':str(value),'scope':m.group(4).strip() or 'as printed; see raw hierarchy'}
        for kind in ('read','write'):
            key='Read Dynamic Energy' if kind=='read' else 'Write Dynamic Energy'
            require(key in entry[kind],f'missing {label} {kind} bank energy')
        result[label]=entry
    return result


def parse_phase2():
    derivation=json.loads((ROOT/'provenance/configuration_derivation.json').read_text())
    require(len(derivation)==16,'expected 16 derived configurations')
    result=[]
    for cache in ('L1','L2'):
        for opt in ('ReadLatency','ReadDynamicEnergy'):
            for node in (14,7,5,3):
                name=case_name(cache,opt,node)
                d=next(x for x in derivation if x['run_id']==name)
                config=ROOT/d['config'];source=ROOT.parent/d['source']
                require(sha(config)==d['config_sha256'] and sha(source)==d['source_sha256'],'derivation hash mismatch')
                require(config.read_bytes()==source.read_bytes().replace(b'-WordWidth (bit): 512',b'-WordWidth (bit): 256'),'configuration change beyond width')
                attempts=sorted((ROOT/'logs/phase2_256bit'/name).glob('*/metadata.json'))
                require(bool(attempts),f'{name}: UNRUN')
                meta_path=attempts[-1];m=json.loads(meta_path.read_text())
                require(m['status']=='FINISHED' and m['returncode']==0,f'{name}: unfinished/failed')
                out,err=meta_path.parent/'stdout.log',meta_path.parent/'stderr.log'
                for path,key in [(config,'config_sha256'),(out,'stdout_sha256'),(err,'stderr_sha256'),(ROOT.parent/m['cell'],'cell_sha256'),(meta_path.parent/'environment.json','environment_sha256')]:
                    require(sha(path)==m[key],f'{name}: {key} mismatch')
                require(m['config']==d['config'],'config path mismatch')
                raw=out.read_text();require('Finished!' in raw,'missing completion')
                require('Cache Line Size: 32Bytes' in raw,'unexpected modeled line size')
                values,org=parse(raw)
                result.append(dict(run_id=name,cache=cache,node_nm=node,optimization=opt,width_bits=256,
                    status='FINISHED',elapsed_seconds=m['elapsed_seconds'],**{k:str(v) for k,v in values.items()},
                    config=d['config'],stdout=str(out.relative_to(ROOT)),stderr=str(err.relative_to(ROOT)),metadata=str(meta_path.relative_to(ROOT)),
                    binary_sha256=m['binary_sha256'],config_sha256=m['config_sha256'],stdout_sha256=m['stdout_sha256'],
                    organization=org,breakdown=breakdown(raw)))
    return result


def sf_rows(rows,width):
    by={(r['cache'],r['optimization'],r['node_nm']):r for r in rows};result=[]
    for cache in ('L1','L2'):
        for opt in ('ReadLatency','ReadDynamicEnergy'):
            for metric in ('read_pj_per_access','write_pj_per_access'):
                for a,b in ((14,7),(7,5),(5,3)):
                    before,after=by[cache,opt,a],by[cache,opt,b]
                    first,second=D(before[metric]),D(after[metric]);sf=second/first
                    result.append(dict(cache=cache,optimization=opt,metric=metric,width_bits=width,from_nm=a,to_nm=b,
                        energy_from_pj=first,energy_to_pj=second,scaling_factor=sf,reduction_percent=100*(1-sf),
                        formula=f'SF=E_b/E_a={second}/{first}',from_config=before['config'],to_config=after['config'],
                        from_log=before['stdout'],to_log=after['stdout']))
    return result


def component_comparisons(org_comparison):
    rows=[]
    for r in org_comparison:
        for kind in ('read','write'):
            row=dict(run_id=r['run_id'],energy=kind,log_256=r['log_256'],log_512=r['log_512'])
            for width in (256,512):
                detail=r['breakdown_'+str(width)]
                key='Read Dynamic Energy' if kind=='read' else 'Write Dynamic Energy'
                data=D(detail['data'][kind][key]['pj']);tag=D(detail['tag'][kind][key]['pj'])
                route=sum(D(detail[label][kind]['H-Tree Dynamic Energy']['pj']) for label in ('data','tag'))
                total=data+tag
                require(D(0)<=route<=total,'routing energy outside bank total')
                row.update({f'data_bank_{width}_pj':data,f'tag_bank_{width}_pj':tag,
                    f'bank_total_{width}_pj':total,f'routing_{width}_pj':route,
                    f'nonrouting_residual_{width}_pj':total-route,
                    f'tag_share_{width}_percent':100*tag/total,f'routing_share_{width}_percent':100*route/total})
            row['scope']='bank totals=data+tag; routing is a subset; residual is not cell-only'
            rows.append(row)
    return rows


def main():
    try:
        new=parse_phase2();old_sources=load_sources(P1,parse)
        old=[]
        for r in new:
            s=old_sources[('D-' if r['node_nm']==7 else 'S-')+r['run_id']]
            require(s['width']==512,'Phase 1 selection is not width-aligned')
            raw=(P1/s['log']).read_text()
            old.append(dict(run_id=r['run_id'],cache=r['cache'],node_nm=r['node_nm'],optimization=r['optimization'],
                **{k:str(v) for k,v in s['values'].items()},organization=s['organization'],breakdown=breakdown(raw),
                config='../NSCache_Experiment_DB/'+s['config'],stdout='../NSCache_Experiment_DB/'+s['log']))
        identities={r['binary_sha256'] for r in new}|{s['meta']['binary_sha256'] for s in old_sources.values()}
        require(len(identities)==1,'Phase 1/2 binary identities differ; investigate build before comparing')
    except (OSError,KeyError,ValueError,StopIteration) as exc:
        print(f'Invalid/incomplete Phase 2 input: {exc}',file=sys.stderr);return 2
    comparisons=[];org_comparison=[];seven=[]
    for r,s in zip(new,old):
        row={k:r[k] for k in ('run_id','cache','node_nm','optimization')}
        for metric,short in [('read_pj_per_access','read'),('write_pj_per_access','write')]:
            a,b=D(r[metric]),D(s[metric])
            row.update({f'{short}_256_pj_access':a,f'{short}_512_pj_access':b,
                f'{short}_E256_div_E512':a/b,f'{short}_E512_div_E256':b/a,
                f'{short}_reduction_512_to_256_percent':100*(1-a/b),
                f'{short}_256_effective_pj_bit':a/256,f'{short}_512_effective_pj_bit':b/512,
                f'{short}_Ebit256_div_Ebit512':(a/256)/(b/512)})
        for metric in ('leakage_mw','hit_latency_ns','area_mm2','feasible_solutions'):
            row[metric+'_256']=r[metric];row[metric+'_512']=s[metric];row[metric+'_delta_256_minus_512']=D(r[metric])-D(s[metric])
        row.update(log_256=r['stdout'],config_256=r['config'],log_512=s['stdout'],config_512=s['config'],
            ratio_formula='E256/E512; inverse also provided',normalization_formula='E_effective_pj_bit=E_pj_access/width_bits')
        comparisons.append(row)
        org_comparison.append(dict(run_id=r['run_id'],organization_256=r['organization'],organization_512=s['organization'],
            breakdown_256=r['breakdown'],breakdown_512=s['breakdown'],log_256=r['stdout'],log_512=s['stdout']))
        if r['node_nm']==7:
            prior=old_sources['S-'+r['run_id']]
            seven.append(dict(run_id=r['run_id'],phase2_log=r['stdout'],phase1_log='../NSCache_Experiment_DB/'+prior['log'],
                all_six_exact=all(D(r[k])==prior['values'][k] for k in METRICS),
                organization_exact=r['organization']==prior['organization']))
    scales=sf_rows(new,256);old_scales=sf_rows(old,512);scale_compare=[]
    for a,b in zip(scales,old_scales):
        scale_compare.append({k:a[k] for k in ('cache','optimization','metric','from_nm','to_nm')}|dict(
            sf_256=a['scaling_factor'],sf_512=b['scaling_factor'],delta_sf_256_minus_512=a['scaling_factor']-b['scaling_factor'],
            reduction_256_percent=a['reduction_percent'],reduction_512_percent=b['reduction_percent'],
            from_log_256=a['from_log'],to_log_256=a['to_log'],from_log_512=b['from_log'],to_log_512=b['to_log'],
            from_config_256=a['from_config'],to_config_256=a['to_config'],from_config_512=b['from_config'],to_config_512=b['to_config'],
            formula_256=a['formula'],formula_512=b['formula']))
    (ROOT/'results').mkdir(exist_ok=True);(ROOT/'reports').mkdir(exist_ok=True)
    write_csv(ROOT/'results/phase2_256bit_energy.csv',[{k:v for k,v in r.items() if k not in ('organization','breakdown')} for r in new])
    write_csv(ROOT/'results/phase2_256bit_scaling.csv',scales)
    write_csv(ROOT/'results/width_256_vs_512_comparison.csv',comparisons)
    write_csv(ROOT/'results/width_256_vs_512_scaling.csv',scale_compare)
    write_csv(ROOT/'results/phase1_7nm_replay_comparison.csv',seven)
    (ROOT/'results/parsed_results.json').write_text(json.dumps(new,indent=2)+'\n')
    (ROOT/'results/organization_breakdown_comparison.json').write_text(json.dumps(org_comparison,indent=2)+'\n')
    components=component_comparisons(org_comparison)
    write_csv(ROOT/'results/breakdown_width_comparison.csv',components)
    report(new,comparisons,scales,scale_compare,org_comparison,seven,components)
    print(f'Phase 2: {len(new)}/16 fresh FINISHED; 24 SF; 16 width comparisons; 24 SF comparisons; 7nm matches {sum(x["all_six_exact"] for x in seven)}/4')
    return 0


def report(new,comparisons,scales,scale_compare,org_comparison,seven,components):
    lines=['# Phase 2-A: 256bit L1/L2 energy scaling','',
        '## 배경과 실험 조건','',
        'GPU 32B sector 단위와 비교할 모델 기준을 만들기 위해 Phase 1의 512bit 설정에서 WordWidth만 256bit로 바꿨다. L1=128KiB/8-way, L2=1MiB/16-way; 14/7/5/3nm; ReadLatency/ReadDynamicEnergy; 300K/LOP/Normal/H-tree/단일 die 및 나머지 옵션은 유지했다. 7nm도 새 실행이며 기존 로그를 재사용하지 않았다. 원본 Phase 1 자료와 모델 소스는 수정하지 않았다.',
        '설정 diff·원본·SHA-256: [derivation](../provenance/configuration_derivation.json). 실행 환경/실제 빌드: [environment](../logs/build/environment.json), [build stdout](../logs/build/stdout.log). 각 로그 옆 metadata에 종료 코드/시간/해시가 있다.',
        '', '## 실행 상태 및 256bit 절대 Energy Matrix','',
        '| Run | Status | Read pJ/access | Write pJ/access | Leakage mW | Hit ns | Area mm² | Solutions | Raw log |',
        '|---|---|---:|---:|---:|---:|---:|---:|---|']
    for r in new:lines.append('| '+r['run_id']+' | FINISHED | '+' | '.join(str(r[k]) for k in METRICS)+f" | [stdout](../{r['stdout']}) |")
    lines+=['','## 256bit SF Matrix','', '`SF(a→b)=E_b/E_a`; `Reduction%=100×(1−SF)`. Read/Write는 별도이며 SF는 무차원이다. CSV의 각 행에 raw log/configuration/대입식을 기록했다. [256bit SF](../results/phase2_256bit_scaling.csv).',
            '', '| Cache | Optimization | Energy | 14→7 | 7→5 | 5→3 |','|---|---|---|---:|---:|---:|']
    for cache in ('L1','L2'):
        for opt in ('ReadLatency','ReadDynamicEnergy'):
            for metric in ('read_pj_per_access','write_pj_per_access'):
                values=[r['scaling_factor'] for r in scales if r['cache']==cache and r['optimization']==opt and r['metric']==metric]
                lines.append(f"| {cache} | {opt} | {'Read' if metric.startswith('read') else 'Write'} | "+' | '.join(f'{v:.6f}' for v in values)+' |')
    lines+=['','## Table A: 256bit/512bit Absolute Energy Comparison','',
        'E256/E512와 E512/E256을 구분해 CSV에 기록했다. 아래 비율은 E256/E512다. Effective pJ/bit=Eaccess/WordWidth이며 물리적 단일 SRAM cell bit energy가 아니다.',
        '[전체 energy·pJ/bit·latency/leakage/area 차이 CSV](../results/width_256_vs_512_comparison.csv).',
        '', '| Run | Read256 / 512 pJ | Read ratio | Read256 / 512 pJ/bit | Write256 / 512 pJ | Write ratio | Write256 / 512 pJ/bit |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in comparisons:
        lines.append(f"| {r['run_id']} | {r['read_256_pj_access']} / {r['read_512_pj_access']} | {r['read_E256_div_E512']:.4f} | {r['read_256_effective_pj_bit']:.6f} / {r['read_512_effective_pj_bit']:.6f} | {r['write_256_pj_access']} / {r['write_512_pj_access']} | {r['write_E256_div_E512']:.4f} | {r['write_256_effective_pj_bit']:.6f} / {r['write_512_effective_pj_bit']:.6f} |")
    lines+=['','## Table B: 256bit/512bit Read/Write SF Comparison','',
        '[24개 SF 비교: 양 폭의 모든 log/configuration/수식](../results/width_256_vs_512_scaling.csv). ΔSF=SF256−SF512.',
        '', '| Cache | Optimization | Energy | Transition | SF256 | SF512 | ΔSF |','|---|---|---|---|---:|---:|---:|']
    for r in scale_compare:lines.append(f"| {r['cache']} | {r['optimization']} | {'Read' if r['metric'].startswith('read') else 'Write'} | {r['from_nm']}→{r['to_nm']} | {r['sf_256']:.6f} | {r['sf_512']:.6f} | {r['delta_sf_256_minus_512']:.6f} |")
    lines+=['', '### Latency / Leakage / Area 비교', '',
        '| Run | Hit ns 256 / 512 | Leakage mW 256 / 512 | Area mm² 256 / 512 |',
        '|---|---:|---:|---:|']
    for r in comparisons:
        lines.append(f"| {r['run_id']} | {r['hit_latency_ns_256']} / {r['hit_latency_ns_512']} | {r['leakage_mw_256']} / {r['leakage_mw_512']} | {r['area_mm2_256']} / {r['area_mm2_512']} |")
    largest=max(scale_compare,key=lambda r:abs(r['delta_sf_256_minus_512']))
    lines+=['', f"가장 큰 |ΔSF|는 {largest['cache']}/{largest['optimization']}/{largest['metric']} {largest['from_nm']}→{largest['to_nm']}의 {largest['delta_sf_256_minus_512']:.6f}이다. 폭에 따라 SF 자체도 달라진다.",
        'Cache summary energy는 0.001nJ=1pJ 간격으로 출력된다. 작은 pJ/bit·SF 차이의 통계적 유의성이나 내부 계산 정밀도를 이 표만으로 주장하지 않는다.']
    lines+=['','## Width 영향: 관측과 원인 분석','']
    for cache in ('L1','L2'):
        rows=[r for r in comparisons if r['cache']==cache]
        for kind in ('read','write'):
            reductions=[r[kind+'_reduction_512_to_256_percent'] for r in rows]
            bitratios=[r[kind+'_Ebit256_div_Ebit512'] for r in rows]
            lines.append(f"- 관측: {cache} {kind} energy 감소율(512→256)은 {min(reductions):.2f}–{max(reductions):.2f}%; effective pJ/bit의 256/512 비는 {min(bitratios):.4f}–{max(bitratios):.4f}. 정확한 선형 반감이라면 각각 50%, 1이어야 한다.")
    lines+=['', '### 선택된 조직과 printed breakdown','',
        '[data/tag별 전체 조직·mux·wire/buffer와 breakdown JSON](../results/organization_breakdown_comparison.json). 아래 bank read energy는 cache summary보다 높은 출력 정밀도지만 여전히 반올림된 값이다. Routing은 bank energy에 포함된 하위 항목이며 다시 더하면 안 된다. Per-subarray와 per-mat 값은 전체 접근 에너지가 아니므로 단순 합산하지 않는다.',
        '', '| Run | Data subarray/mat 256→512 | Tag bank/mat 256→512 | Data bank read pJ 256→512 | Tag bank read pJ 256→512 | Data H-tree read pJ 256→512 |',
        '|---|---|---|---:|---:|---:|']
    for r in org_comparison:
        a,b=r['organization_256'],r['organization_512'];x,y=r['breakdown_256'],r['breakdown_512']
        get=lambda z,label,key:z[label]['read'].get(key,{}).get('pj','NOT PRINTED')
        lines.append(f"| {r['run_id']} | {a['data']['subarray']}/{a['data']['mat']} → {b['data']['subarray']}/{b['data']['mat']} | {a['tag']['bank']}/{a['tag']['mat']} → {b['tag']['bank']}/{b['tag']['mat']} | {get(x,'data','Read Dynamic Energy')} → {get(y,'data','Read Dynamic Energy')} | {get(x,'tag','Read Dynamic Energy')} → {get(y,'tag','Read Dynamic Energy')} | {get(x,'data','H-Tree Dynamic Energy')} → {get(y,'data','H-Tree Dynamic Energy')} |")
    lines+=['', '### Tag / routing 비중: 중복 없는 bank 기준', '',
        '[Read/Write 32개 component 비교 CSV](../results/breakdown_width_comparison.csv). `bank_total=data_bank+tag_bank`, `tag_share=tag_bank/bank_total`, `routing_share=(data_Htree+tag_Htree)/bank_total`, `nonrouting_residual=bank_total−routing`. Routing share와 tag share는 서로 겹치므로 더하지 않는다. Residual은 cell-only가 아니다.']
    for kind in ('read','write'):
        selected=[r for r in components if r['energy']==kind]
        for width in (256,512):
            tags=[r[f'tag_share_{width}_percent'] for r in selected]
            routes=[r[f'routing_share_{width}_percent'] for r in selected]
            lines.append(f"- 관측: {width}bit {kind}에서 tag bank 비중 {min(tags):.2f}–{max(tags):.2f}%, routing 비중 {min(routes):.2f}–{max(routes):.2f}%. 분모는 출력된 두 bank의 합이다.")
    lines+=['',
        '구체적 사례: L1/14nm/ReadLatency의 data subarray/mat 형태는 두 폭에서 같지만 tag bank와 mat는 달라진다. Data bank read는 68.252→35.615pJ(512→256), tag는 5.394→2.318pJ, data H-tree는 48.115→25.547pJ다. 같은 data 조직 표기에서도 활성 bit 수·wire load가 달라지므로 energy가 정확히 반감되지 않는다. 이 수치는 관측이며, 개별 transistor/셀 기여의 인과 분해를 완료한 것은 아니다.']
    lines+=['',
        '- 확인된 모델 구조: WordWidth 변경은 출력 데이터 폭만 줄이지 않고 cache line/line 수/tag array capacity와 wire broadcast/distribute bit 수에도 영향을 준다. 태그와 주변 회로의 overhead는 payload bit 수에 비례하지 않는다.',
        '- 관측: 위 표와 JSON에서 선택 조직 및 라우팅·bank energy의 변화 여부를 직접 비교할 수 있다. Optimizer가 독립적으로 재선택한 tag bank/mat/mux/buffer 변화와 고정/공유 overhead가 비선형성을 설명할 수 있다.',
        '- 가설과 한계: 개별 회로의 인과 기여율은 고정 조직 대조 실험 없이 확정하지 않는다. tag+data는 cache-hit 식에서 합산되지만 summary는 1pJ 간격이라 세부 pJ 합과 미세하게 다를 수 있다. Routing/peripheral/cell 분해는 겹치는 계층이며 전체를 서로 배타적인 기여도로 제시하지 않는다.',
        '- Width별 SF 차이는 상대 overhead와 재최적화 조직 변화가 node마다 달라 생길 수 있다. 전압·cell 모델 차이도 남아 있으므로 어느 폭의 SF도 Pure Process Scaling이 아니다.',
        '', '## 재현성·정규화·결론','',
        f"새 7nm 실행 4개의 6개 지표는 기존 Phase 1 256bit 실행과 {sum(x['all_six_exact'] for x in seven)}/4 일치했다. [기존 로그와의 비교](../results/phase1_7nm_replay_comparison.csv).",
        '`E_NS_bit=E_NS_access/256`, `E_GPU_sector=E_GPU_bit×256`은 단위 정렬이다. 동일한 물리 경계라는 뜻이 아니다. GPU read/write·hit/miss counter, multi-sector tag 재사용, coalescing/replay, miss fill/writeback 및 energy coefficient의 측정/회귀 경계를 먼저 확인해야 한다.',
        '내부 GPU 계수·실측 에너지·회사 자료·비공개 검증 결과는 사용하거나 저장하지 않았다. GPU sector 구조의 근거/미확인 사항과 Phase 2-B 제안은 [feasibility 보고서](gpu_sector_modeling_feasibility.md)를 따른다.']
    (ROOT/'reports/phase2_256bit_energy_analysis.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':raise SystemExit(main())
