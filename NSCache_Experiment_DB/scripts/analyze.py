"""Parse fresh attempts only; compare rounded output and calculate descriptive scaling."""
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
NUMBER=r'([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)'
METRICS={
 'read_pj_per_access':(r'^\s*- Cache Hit Dynamic Energy\s*=\s*'+NUMBER+r'nJ per access',Decimal(1000),Decimal('.5')),
 'write_pj_per_access':(r'^\s*- Cache Write Dynamic Energy\s*=\s*'+NUMBER+r'nJ per access',Decimal(1000),Decimal('.5')),
 'leakage_mw':(r'^\s*- Cache Total Leakage Power\s*=\s*'+NUMBER+r'mW',Decimal(1),Decimal('.0005')),
 'hit_latency_ns':(r'^\s*- Cache Hit Latency\s*=\s*'+NUMBER+r'ns',Decimal(1),Decimal('.0005')),
 'area_mm2':(r'^\s*- Total Area\s*=\s*'+NUMBER+r'mm\^2',Decimal(1),Decimal('.0005')),
 'feasible_solutions':(r'^numSolutions\s*=\s*(\d+)',Decimal(1),Decimal(0)),
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def parse(raw):
    values={}
    for field,(pattern,mult,tol) in METRICS.items():
        matches=re.findall(pattern,raw,re.M)
        if len(matches)!=1: raise ValueError(f'{field}: expected 1 summary, found {len(matches)}')
        values[field]=Decimal(matches[0])*mult
    blocks=re.findall(r'\n\s*CONFIGURATION\s*\n\s*=+\n(.*?)\n\s*=+\n\s*RESULT',raw,re.S)
    if len(blocks)!=2: raise ValueError(f'expected data/tag configuration blocks, got {len(blocks)}')
    organizations={label:{'raw_configuration':block.strip(),
         'bank':re.search(r'Bank Organization:\s*(\d+ x \d+)',block).group(1),
         'subarray':re.search(r'SubArray Organization:\s*(\d+ x \d+)',block).group(1),
         'mat':re.search(r'Mat Size\s*:\s*(\d+ Rows x \d+ Columns)',block).group(1)}
         for label,block in zip(('data','tag'),blocks)}
    return values,organizations

def write_csv(path,rows):
    if not rows: raise ValueError(f'no rows for {path}')
    with path.open('w',newline='') as f:
        fields=list(dict.fromkeys(k for row in rows for k in row))
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
    expected=json.loads((ROOT/'results/recorded/nscache_16_runs.json').read_text())['runs']
    audit={r['run_id']:r for r in json.loads((ROOT/'results/configuration_audit.json').read_text())}
    parsed=[]; comparison=[]
    for r in expected:
        name=f"{r['cache']}_{r['node_nm']}nm"+('_ReadEnergy' if r['optimization']=='ReadDynamicEnergy' else '')
        attempts=sorted((ROOT/'logs/new'/name).glob('*/metadata.json'))
        item=dict(run_id=name,cache=r['cache'],node_nm=r['node_nm'],optimization=r['optimization'],status='UNRUN')
        values={}
        if attempts:
            meta_path=attempts[-1];meta=json.loads(meta_path.read_text());item.update(metadata=str(meta_path.relative_to(ROOT)),status=meta['status'],elapsed_seconds=meta.get('elapsed_seconds'))
            out=meta_path.parent/'stdout.log';err=meta_path.parent/'stderr.log'
            try:
                assert meta['config_sha256']==audit[name]['config_sha256'],'configuration identity changed'
                assert meta['cell_sha256']==audit[name]['cell_sha256'],'cell identity changed'
                assert meta['stdout_sha256']==sha(out) and meta['stderr_sha256']==sha(err),'log integrity mismatch'
                assert meta['binary_sha256']==sha(ROOT/'build/nsc'),'binary identity mismatch'
                assert meta['returncode']==0 and meta['status']=='FINISHED','execution did not finish'
                raw=out.read_text();assert 'Finished!' in raw,'missing completion marker'
                values,org=parse(raw)
                item.update({k:float(v) for k,v in values.items()})
                item.update(organization=org,stdout=str(out.relative_to(ROOT)),stderr=str(err.relative_to(ROOT)))
            except (AssertionError,KeyError,ValueError,OSError) as exc:
                item.update(status='INVALID',error=str(exc))
        statuses=[]
        for k,(_,_,tol) in METRICS.items():
            recorded=Decimal(str(r[k]));actual=values.get(k) if item['status']=='FINISHED' else None
            difference=actual-recorded if actual is not None else None
            status='UNTESTED' if difference is None else ('MATCH' if abs(difference)<=tol else 'DIFFERENT')
            statuses.append(status)
            comparison.append(dict(run_id=name,metric=k,recorded=str(recorded),reexecuted=str(actual) if actual is not None else '',difference=str(difference) if difference is not None else '',absolute_tolerance=str(tol),status=status))
        item['comparison']='MATCH' if all(x=='MATCH' for x in statuses) else ('DIFFERENT' if 'DIFFERENT' in statuses else 'UNTESTED')
        parsed.append(item)
    (ROOT/'results/parsed_results.json').write_text(json.dumps(parsed,indent=2)+'\n')
    write_csv(ROOT/'results/comparison.csv',comparison)
    write_csv(ROOT/'results/run_summary.csv',[{k:v for k,v in r.items() if k not in ('organization',)} for r in parsed])
    scales=[]
    by={(r['cache'],r['optimization'],r['node_nm']):r for r in parsed}
    for cache in ('L1','L2'):
        for opt in ('ReadLatency','ReadDynamicEnergy'):
            for metric in ('read_pj_per_access','write_pj_per_access'):
                for a,b in ((14,7),(7,5),(5,3)):
                    before,after=by[cache,opt,a],by[cache,opt,b]
                    valid=before['status']==after['status']=='FINISHED'
                    ratio=after[metric]/before[metric] if valid else None
                    scales.append(dict(cache=cache,optimization=opt,metric=metric,from_nm=a,to_nm=b,
                        energy_from=before.get(metric),energy_to=after.get(metric),scaling_factor=ratio,
                        reduction_percent=100*(1-ratio) if ratio is not None else None,
                        width_from_bits=audit[before['run_id']]['config']['WordWidth (bit)'],
                        width_to_bits=audit[after['run_id']]['config']['WordWidth (bit)'],
                        interpretation='descriptive reconstructed-input ratio; not process-only',
                        from_log=before.get('stdout',''),to_log=after.get('stdout','')))
    write_csv(ROOT/'results/scaling.csv',scales)
    reports(parsed,comparison,scales,audit)
    print(f"Fresh runs: {sum(r['status']=='FINISHED' for r in parsed)}/16; all-metric matches: {sum(r['comparison']=='MATCH' for r in parsed)}/16")
    return 0 if all(r['status']=='FINISHED' and r['comparison']=='MATCH' for r in parsed) else 1

def reports(parsed,comparison,scales,audit):
    directory=ROOT/'reports';directory.mkdir(exist_ok=True)
    validation=['# 재현성 검증','',
      '새 실행만 비교에 사용한다. 원본 historical 로그/설정은 복구되지 않았으며, bundled 로그는 새 실행으로 집계하지 않는다.',
      '원본 ZIP과 추출 파일은 `provenance/archive_manifest.csv`의 SHA-256으로 추적한다. 복구된 소스 54개는 보고된 upstream commit의 대응 파일과 모두 byte-identical이며, 소스 변경 없이 빌드했다.',
      '', '## 비교 방법','',
      'stdout의 cache summary에서 read/write nJ를 ×1000 하여 pJ/access로 변환한다. leakage=mW, latency=ns, area=mm². 0.001 nJ 출력 간격에 대해 에너지는 ±0.5 pJ, 나머지 세 연속 지표는 ±0.0005, solution count는 정확히 비교한다. 이는 출력 해상도 기준이며 내부 계산 정밀도의 동등성을 증명하지 않는다. 부호 있는 차이는 새 값−기록값이다.',
      '종료 코드 0, Finished!, 모든 summary 항목과 data/tag 조직 파싱, 입력·cell·binary·로그 SHA-256 일치를 요구한다. 비교 스크립트는 미실행/실패/불일치가 있으면 비영 종료한다.',
      '', '## 실행별 결과','', '| Run | Execution | Comparison | Seconds | Raw stdout |','|---|---|---|---:|---|']
    for r in parsed:
        validation.append(f"| {r['run_id']} | {r['status']} | {r['comparison']} | {(r.get('elapsed_seconds') or 0):.2f} | [{r.get('stdout','missing')}](../{r.get('stdout','')}) |")
    validation+=['','## 항목별 비교','', '| Run | Metric | Recorded | New | Difference | Status |','|---|---|---:|---:|---:|---|']
    validation += [f"| {r['run_id']} | {r['metric']} | {r['recorded']} | {r['reexecuted']} | {r['difference']} | {r['status']} |" for r in comparison]
    bad=[r for r in parsed if r['comparison']!='MATCH']
    validation += ['','## 판단 및 불일치 조사','',
      f"{sum(r['status']=='FINISHED' for r in parsed)}/16 실행 완료, {sum(r['comparison']=='MATCH' for r in parsed)}/16 전체 지표 일치.",
      '불일치 실행: '+(', '.join(r['run_id'] for r in bad) or '없음')+'.',
      '현재 입력은 재구성본이다. 수치가 일치해도 historical 원본 입력/로그 복구를 의미하지 않는다. 7nm의 256bit 폭은 다른 공정의 512bit와 다르므로 archive README의 고정 512bit 설명을 그대로 인용하면 안 된다. 숫자를 맞추기 위한 설정 보정은 하지 않았다.',
      '빌드 로그의 기존 compiler warnings는 보존했다. 실패·시간초과 시에도 attempt별 stdout/stderr/metadata를 보존하며, 완료·해시 검증된 실행만 재개 시 생략한다.',
      '', '환경·빌드 명령: [environment.json](../logs/build/environment.json), [stdout](../logs/build/stdout.log), [stderr](../logs/build/stderr.log). 각 실행의 실제 시간과 UTC 시각은 metadata에 기록된다.']
    (directory/'reproducibility_validation.md').write_text('\n'.join(validation)+'\n')
    analysis=['# 공정별 energy scaling 분석','',
      '아래는 새 실행에서 얻은 NS-Cache 모델값이다. NVIDIA GPU 실측값, 검증된 process-only ground truth, Rubin 예측이 아니다.',
      'SF(a→b)=E_b/E_a; 감소율=100×(1−SF). read/write와 L1/L2를 분리했다. 0.001 nJ 단위로 반올림된 출력값을 사용하므로 표시 자릿수 이상의 정확도를 주장하지 않는다. 기초값과 로그 경로: [scaling.csv](../results/scaling.csv).',
      '', '## Scaling matrix','', '| Cache | Objective | Energy | 14→7 | 7→5 | 5→3 |','|---|---|---|---:|---:|---:|']
    for cache in ('L1','L2'):
        for opt in ('ReadLatency','ReadDynamicEnergy'):
            for metric in ('read_pj_per_access','write_pj_per_access'):
                values=[r['scaling_factor'] for r in scales if r['cache']==cache and r['optimization']==opt and r['metric']==metric]
                analysis.append(f"| {cache} | {opt} | {'Read' if metric.startswith('read') else 'Write'} | "+' | '.join(f'{v:.4f}' if v is not None else 'UNTESTED' for v in values)+' |')
    analysis+=['','## 새 실행의 energy / area / latency','', '| Run | Read pJ | Write pJ | Leakage mW | Latency ns | Area mm² | Solutions |','|---|---:|---:|---:|---:|---:|---:|']
    for r in parsed:
        analysis.append('| '+r['run_id']+' | '+' | '.join(str(r.get(k,'UNTESTED')) for k in METRICS)+' |')
    analysis+=['','## 내부 조직','', 'data/tag를 구분하며 상세 활성화·mux·wire/buffer 값은 `parsed_results.json`의 `raw_configuration`과 원본 stdout에 보존한다.', '', '| Run | Data bank / subarray / mat | Tag bank / subarray / mat |','|---|---|---|']
    for r in parsed:
        org=r.get('organization',{})
        analysis.append('| '+r['run_id']+' | '+' | '.join(' / '.join(org.get(k,{}).get(f,'UNTESTED') for f in ('bank','subarray','mat')) for k in ('data','tag'))+' |')
    analysis+=['','## 경향 및 최적화 trade-off','',
      '재현 입력 그대로의 14→7에서는 read/write가 크게 감소하지만, 7→5에서는 네 cache/objective 조합 모두 증가한다. 이는 256→512bit 폭 변화가 포함된 결과이므로 공정 미세화 자체의 역효과로 해석하지 않는다. 5→3에서는 네 조합 모두 read/write energy가 감소한다.',
      '5→3 read SF는 L1 latency/energy 목표에서 0.8125/0.8276, L2에서는 0.9146/0.8816이다. Write SF는 각각 0.7917/0.8571 및 0.9322/0.8704이다. 이 모델·선택 조직에서는 L1의 감소폭이 더 크지만 일반 GPU 법칙으로 확장할 수 없다.',
      'Latency는 공정 미세화에 대해 단조 감소하지 않는다(예: L1 ReadLatency 7→5: 0.325→0.873ns). Leakage도 단조 감소하지 않는다. 실제 값은 위 표를 따른다.',
      '', '| Cache | Node | Read-energy reduction % | Write-energy reduction % | Latency increase % | Area reduction % |',
      '|---|---:|---:|---:|---:|---:|']
    tradeoffs=[]
    for cache in ('L1','L2'):
        for node in (14,7,5,3):
            a=next(r for r in parsed if r['cache']==cache and r['node_nm']==node and r['optimization']=='ReadLatency')
            b=next(r for r in parsed if r['cache']==cache and r['node_nm']==node and r['optimization']=='ReadDynamicEnergy')
            if a['status']!= 'FINISHED' or b['status']!='FINISHED': continue
            row=dict(cache=cache,node_nm=node,
              read_energy_reduction_percent=100*(1-b['read_pj_per_access']/a['read_pj_per_access']),
              write_energy_reduction_percent=100*(1-b['write_pj_per_access']/a['write_pj_per_access']),
              latency_increase_percent=100*(b['hit_latency_ns']/a['hit_latency_ns']-1),
              area_reduction_percent=100*(1-b['area_mm2']/a['area_mm2']))
            tradeoffs.append(row)
            analysis.append(f"| {cache} | {node} | "+' | '.join(f'{v:.2f}' for k,v in row.items() if k not in ('cache','node_nm'))+' |')
    if tradeoffs: write_csv(ROOT/'results/optimization_tradeoffs.csv',tradeoffs)
    analysis+=['', 'ReadDynamicEnergy 목표는 동일 node의 ReadLatency 목표 대비 read/write energy와 area를 줄였지만 hit latency가 증가했다. 최적화 목표만 바뀌어도 선택 조직이 달라지므로 이 trade-off를 공정 효과와 분리해야 한다.']
    diagnostic=ROOT/'results/width_diagnostic.json'
    if diagnostic.exists():
        diag=json.loads(diagnostic.read_text())
        section=['','## 별도 512bit 진단: 재현 실험과 구분','',
          '재현 입력 16개는 수정하지 않았다. 불일치 원인을 분리하기 위해 7nm 4개를 복사하고 WordWidth만 256→512bit로 변경한 별도 실험을 수행했다. 선택한 변경은 사전에 발견한 비교 조건 위반 한 가지이며, 숫자 맞추기 위한 추가 파라미터 조정은 없다.',
          '변경 diff/해시: width_diagnostic_changes.json. 별도 입력: configs/diagnostic_512bit; 로그: logs/diagnostic_512bit; 파싱 결과: width_diagnostic.json/csv. 이 결과를 16개 재현 실행에 대체하거나 historical 원본으로 표시하지 않는다.',
          '', '| Diagnostic | Read pJ | Write pJ | All six recorded metrics exactly equal | Raw stdout |',
          '|---|---:|---:|---|---|']
        for r in diag:
            section.append(f"| {r['run_id']} | {r['read_pj_per_access']} | {r['write_pj_per_access']} | {r['all_six_recorded_exact']} | [log](../{r['stdout']}) |")
        section+=['', '4개 모두 6개 지표가 기록값과 정확히 일치했다. 따라서 제공된 7nm 재구성 설정의 폭 차이가 현재 불일치를 설명한다는 강한 실험적 근거를 확보했다. 원래 설정이 512bit였다는 historical 증명이나 원본 자료 회수로 간주하지 않는다. 소스 버전은 54개 파일의 byte 일치로, 단위 변환은 Decimal 기반 파싱으로 확인했다. 데이터/태그 조직 비교도 각각의 JSON과 로그에서 가능하다.']
        validation+=section
        (directory/'reproducibility_validation.md').write_text('\n'.join(validation)+'\n')
        analysis+=section
    analysis+=['','## 비교 조건과 해석 한계','',
      '- 7nm는 256bit(32-byte line), 14/5/3nm는 512bit(64-byte line)이다. 14→7 및 7→5 비율은 접근 폭/line size 효과가 섞인다. energy를 단순히 bit 수로 정규화해 보정하지 않았다.',
      '- 용량 L1=128KiB/L2=1024KiB, associativity 8/16, normal cache access, LOP roadmap, 300K, H-tree, internal sensing, 4×4 data-bank 설정, 단일 die 및 latency buffer optimization은 유지된다. 전체 명시 옵션은 configuration_audit.csv/json에 있다.',
      '- Port count는 입력 파라미터에서 독립적으로 설정된 항목을 확인하지 못했다. 단일 포트라고 추정하지 않는다. 동일 소스 실행이라는 사실과 실제 GPU 포트 구조 동등성은 별개다.',
      '- 명시 latency/energy/area constraint는 없다. InputParameter 생성자의 clockFreq=3GHz는 기본값이며 고정 hit-latency 제약의 증거가 아니다. ReadDynamicEnergy에서도 BufferDesignOptimization은 latency이다.',
      '- Cell read-voltage 정의는 14/7/5/3nm에서 0.277/0.264/0.253/0.248V이다. 이는 공급전압 Vdd와 다르다. Technology.cpp의 해당 비-HP 분기 Vdd는 0.8/0.7/0.7/0.7V이며, initializeTechnology의 해당 정수 node 보간계수는 0이다. Node별 cell 면적 F²·aspect ratio도 변한다. 전압/셀/소자/배선 모델을 분리한 실험이 아니다.',
      '- 최적화가 선택한 data/tag의 mat, subarray, mux와 배선·buffer 구성이 달라질 수 있다. 5→3은 접근 폭이 같아도 내부 조직과 node별 cell 파라미터를 고정하지 않아 순수 공정 효과를 식별할 수 없다.',
      '- 새 결과의 감소/증가 경향은 아래 후속 해석에 요약한다. Leakage는 전력이며 per-access dynamic energy에 더하지 않는다. 비공개 GPU 실측 또는 historical correction은 포함하거나 검증하지 않았다.',
      '', '## 후속 실험','',
      '1. 별도 이름의 controlled sweep에서 line/access width와 포트 요구·동일 latency 제약을 명시하고 512bit 전 공정을 실행한다. 이번 재현 입력은 보존한다.',
      '2. 고정 조직과 재최적화 조직을 별도 실행하고, data/tag topology 및 wire/buffer를 통제해 architecture 효과를 분리한다.',
      '3. Vdd·cell·technology 모델 감도 분석과 unrounded 출력 검증을 진행한다. 모델값에 대한 GPU 세대 매핑은 별도 하드웨어 검증이 필요하다.',
      '4. 원본 workbook/설정/16개 historical stdout를 회수할 수 있으면 출처를 별도 등록한다. Rubin 최종 예측은 이번 단계 범위 밖이다.']
    (directory/'process_scaling_analysis.md').write_text('\n'.join(analysis)+'\n')

if __name__=='__main__':
    sys.exit(main())
