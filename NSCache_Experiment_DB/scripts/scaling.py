"""Recalculate both scaling matrices from verified raw attempts, never cached CSV/JSON."""
from decimal import Decimal
import hashlib
import json
import re

D = Decimal
TRANSITIONS = ((14, 7), (7, 5), (5, 3))
METRIC_NAMES = ('read_pj_per_access', 'write_pj_per_access')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def case_name(cache, opt, node):
    return f'{cache}_{node}nm' + ('_ReadEnergy' if opt == 'ReadDynamicEnergy' else '')


def anchor(matrix, row):
    return '-'.join([matrix.lower(), row['cache'].lower(),
                     'lat' if row['optimization'] == 'ReadLatency' else 'energy',
                     'read' if row['metric'].startswith('read') else 'write',
                     str(row['from_nm']), str(row['to_nm'])])


def load_sources(root, parse):
    sources = {}
    for cache in ('L1', 'L2'):
        for opt in ('ReadLatency', 'ReadDynamicEnergy'):
            for node in (14, 7, 5, 3):
                for group, prefix, suite in [('new', 'S', 'study_reconstructed')] + (
                        [('diagnostic_512bit', 'D', 'diagnostic_512bit')] if node == 7 else []):
                    name = case_name(cache, opt, node)
                    attempts = sorted((root / 'logs' / group / name).glob('*/metadata.json'))
                    require(bool(attempts), f'{group}/{name}: no raw attempt')
                    metadata = attempts[-1]
                    meta = json.loads(metadata.read_text())
                    require(meta['status'] == 'FINISHED' and meta['returncode'] == 0,
                            f'{metadata}: latest attempt did not finish')
                    config = root / 'configs' / suite / f'{name}.cfg'
                    require(meta['config'] == str(config.relative_to(root)), 'wrong configuration path')
                    options = {}
                    for line in config.read_text().splitlines():
                        if line.startswith('-') and ':' in line:
                            key, value = line[1:].split(':', 1)
                            require(key not in options, f'duplicate option {key}')
                            options[key] = value.strip()
                    width = int(options['WordWidth (bit)'])
                    require(int(options['ProcessNode']) == node and options['OptimizationTarget'] == opt,
                            f'{config}: node/objective mismatch')
                    capacity_kib = (int(options['Capacity (KB)']) if 'Capacity (KB)' in options
                                    else int(options['Capacity (MB)']) * 1024)
                    require(capacity_kib == (128 if cache == 'L1' else 1024)
                            and int(options['Associativity (for cache only)']) == (8 if cache == 'L1' else 16),
                            f'{config}: capacity/associativity mismatch')
                    require(width == (256 if node == 7 and prefix == 'S' else 512),
                            f'{config}: unexpected access width')
                    cell = (root / 'configs' / options['MemoryCellInputFile'].removeprefix('config/')).resolve()
                    require(cell.is_relative_to((root / 'configs').resolve()), 'cell escapes configs')
                    out, err = metadata.parent / 'stdout.log', metadata.parent / 'stderr.log'
                    for path, field in [(config, 'config_sha256'), (cell, 'cell_sha256'),
                                        (out, 'stdout_sha256'), (err, 'stderr_sha256')]:
                        require(digest(path) == meta[field], f'{path}: {field} mismatch')
                    require(bool(re.fullmatch(r'[0-9a-f]{64}', meta['binary_sha256'])), 'missing binary identity')
                    # Historical attempts retain their binary identity; a local build is not required.
                    raw = out.read_text()
                    require('Finished!' in raw, f'{out}: missing Finished!')
                    values, organization = parse(raw)
                    sid = prefix + '-' + name
                    sources[sid] = dict(sid=sid, group=group, run_id=name, width=width,
                        values=values, organization=organization, meta=meta,
                        log=str(out.relative_to(root)), config=meta['config'],
                        metadata=str(metadata.relative_to(root)),
                        config_sha256=meta['config_sha256'], log_sha256=meta['stdout_sha256'])
    require(len({s['meta']['binary_sha256'] for s in sources.values()}) == 1,
            'matrix attempts used different binary identities')
    return sources


def scaling_rows(sources, aligned=False):
    rows = []
    for cache in ('L1', 'L2'):
        for opt in ('ReadLatency', 'ReadDynamicEnergy'):
            for metric in METRIC_NAMES:
                for a, b in TRANSITIONS:
                    endpoints = [sources[('D' if aligned and n == 7 else 'S') + '-' + case_name(cache, opt, n)]
                                 for n in (a, b)]
                    before, after = endpoints
                    first, second = before['values'][metric], after['values'][metric]
                    require(first > 0 and second > 0, 'energy must be positive')
                    sf = second / first
                    row = dict(cache=cache, optimization=opt, metric=metric, from_nm=a, to_nm=b,
                        energy_from=first, energy_to=second, scaling_factor=sf,
                        reduction_percent=100 * (1 - sf), width_from_bits=before['width'], width_to_bits=after['width'],
                        interpretation=('width-aligned descriptive ratio; voltage/cell/organization not controlled; not pure process scaling'
                                        if aligned else 'descriptive reconstructed-input ratio; not process-only'),
                        from_log=before['log'], to_log=after['log'],
                        matrix='Width-Aligned' if aligned else 'As-Reconstructed Input', energy_unit='pJ/access',
                        formula='SF(a->b) = E_b / E_a', substitution=f'{second} / {first}')
                    for direction, source in zip(('from', 'to'), endpoints):
                        for suffix, key in [('source_id', 'sid'), ('config', 'config'), ('metadata', 'metadata'),
                                            ('config_sha256', 'config_sha256'), ('log_sha256', 'log_sha256')]:
                            row[direction + '_' + suffix] = source[key]
                    rows.append(row)
    return rows


def compare_matrices(rows, aligned):
    result = []
    for a, b in zip(rows, aligned):
        x, y = a['scaling_factor'], b['scaling_factor']
        result.append({k:a[k] for k in ('cache','optimization','metric','from_nm','to_nm')} | dict(
            as_reconstructed_sf=x, width_aligned_sf=y, delta_sf_aligned_minus_reconstructed=y-x,
            relative_change_percent=100*(y/x-1), as_reconstructed_csv='results/scaling.csv',
            width_aligned_csv='results/scaling_width_aligned.csv',
            formula='delta = aligned - reconstructed; relative_change_percent = 100 * (aligned / reconstructed - 1)'))
    return result


def render_traceability(sources, rows, aligned):
    trace=['# Scaling Matrix 계산 근거','',
     '두 Matrix의 각 24개 SF를 raw stdout과 configuration에 연결한다. 새로운 실험이나 추정값을 생성하지 않았다. As-Reconstructed Input은 기존 16개 재현 실행만 사용한다. Width-Aligned는 7nm만 별도 512bit 진단으로 선택하며 나머지는 같은 재현 실행을 재사용한다. 원래의 16개 실행을 별도 진단으로 대체하지 않는다.',
     '', '## 수식과 정밀도','',
     '`E_pJ/access = stdout의 nJ/access × 1000`; `SF(a→b)=E_b/E_a`; `감소율(%)=100×(1−SF)`. Read/Write, L1/L2, 두 optimization을 각각 독립 계산했다. SF는 무차원이다. CSV는 반올림된 출력의 Decimal 비율을 보관하고 본문 Matrix는 소수점 넷째 자리로 표시한다. 두 CSV 모두 raw log의 Decimal 값에서 자동 재계산한다. 이전 float 표현과 끝자리 표현 차이가 있을 수 있지만 기초 energy와 SF의 의미는 같다. 출력 간격 0.001nJ=1pJ에 따른 정밀도 한계가 있으며 SF의 유효 정확도가 소수점 넷째 자리라는 뜻은 아니다.',
     '`ΔSF = Width-Aligned − As-Reconstructed`; `상대변화(%)=100×(Width-Aligned/As-Reconstructed−1)`.',
     '', '## 선택한 실행과 Configuration','',
     'S-는 원래 재현 실행, D-는 별도 512bit 진단 실행이다. 각 실행의 종료 코드·Finished!·configuration/cell/stdout/stderr SHA-256을 기존 metadata와 대조했다. CSV에는 SF 양 끝의 config/log/metadata 경로와 config/log 해시도 기록했다.',
     '', '| Source ID | Width bit | Read pJ/access | Write pJ/access | Configuration | Raw stdout | Metadata |','|---|---:|---:|---:|---|---|---|']
    for sid,s in sorted(sources.items()):
     trace.append(f"| <a id='{sid.lower()}'></a>{sid} | {s['width']} | {s['values']['read_pj_per_access']} | {s['values']['write_pj_per_access']} | [cfg](../{s['config']}) | [stdout](../{s['log']}) | [metadata](../{s['metadata']}) |")
    for label,data,slug in [('As-Reconstructed Input',rows,'as'),('Width-Aligned',aligned,'wa')]:
     trace += ['',f'## {label} — SF 계산 24개','', '| Cache | Objective | Energy | Transition | Formula (pJ/access ÷ pJ/access) | From source | To source |','|---|---|---|---|---|---|---|']
     for r in data:
      energy='Read' if r['metric'].startswith('read') else 'Write';sf=D(r['scaling_factor'])
      trace.append(f"| <a id='{anchor(slug,r)}'></a>{r['cache']} | {r['optimization']} | {energy} | {r['from_nm']}→{r['to_nm']} | {r['substitution']} = {sf:.8f} | [{r['from_source_id']}](#{r['from_source_id'].lower()}) | [{r['to_source_id']}](#{r['to_source_id'].lower()}) |")
    trace += ['', '## CSV만으로 재계산 / 검증','',
     '각 CSV 행의 from_log/to_log에서 해당 cache summary의 Read 또는 Write Dynamic Energy를 추출해 ×1000하고, to/from을 계산하면 scaling_factor가 된다. from_config/to_config의 WordWidth 및 metadata 해시와 함께 확인할 수 있다. 첫 Matrix는 7nm만 256bit이며, 두 번째는 양 끝 모두 512bit다. scaling_matrix_comparison.csv는 두 CSV의 (cache, optimization, metric, from_nm, to_nm) 키를 대응시킨 차이다.',
     '', '## 해석 제한','',
     '**Width-Aligned Scaling은 Pure Process Scaling이 아니다.** 폭만 정렬했으며 node별 Voltage, Cell Parameters 및 재최적화된 Internal Cache Organization은 동일하지 않다. 이것은 기존 실행을 조합한 모델 내 비교이고 historical 원본 설정 복구나 NVIDIA GPU 측정 검증이 아니다.']
    trace_text='\n'.join(trace)+'\n'
    return trace_text

def table(data,slug):
 lines=['| Cache | Objective | Energy | 14→7 | 7→5 | 5→3 |','|---|---|---|---:|---:|---:|']
 for cache in ('L1','L2'):
  for opt in ('ReadLatency','ReadDynamicEnergy'):
   for metric in ('read_pj_per_access','write_pj_per_access'):
    group=[r for r in data if r['cache']==cache and r['optimization']==opt and r['metric']==metric]
    lines.append(f"| {cache} | {opt} | {'Read' if metric.startswith('read') else 'Write'} | "+' | '.join(f"[{D(r['scaling_factor']):.4f}](scaling_matrix_traceability.md#{anchor(slug,r)})" for r in group)+' |')
 return '\n'.join(lines)


def matrix_report(rows, aligned):
    increased = sum(a['scaling_factor'] > 1 for a in rows if a['from_nm'] == 7)
    decreased = sum(a['scaling_factor'] < 1 for a in aligned if a['from_nm'] == 7)
    unchanged = sum(a['scaling_factor'] == b['scaling_factor']
                    for a, b in zip(rows, aligned) if a['from_nm'] == 5)
    return '\n\n'.join([
        '## As-Reconstructed Input Scaling Matrix',
        '기존 16개 재현 입력·로그를 그대로 사용한다. 7nm는 256bit, 14/5/3nm는 512bit다. 각 SF 링크는 해당 수식과 raw log/configuration 근거로 이어진다. [24개 SF CSV](../results/scaling.csv).',
        table(rows, 'as'),
        '## Width-Aligned Scaling Matrix',
        '모든 공정의 WordWidth=512bit로 정렬한다. **7nm만 별도 512bit 진단 4건**을 선택하고 14/5/3nm는 기존 512bit 실행을 재사용한다. 기록된 energy를 입력으로 사용하거나 256bit energy를 두 배로 환산하지 않는다. 기존 16개 재현 결과와 재현성 판정을 대체하지 않는다. [24개 SF CSV](../results/scaling_width_aligned.csv).',
        table(aligned, 'wa'),
        '## 두 Matrix의 차이와 폭 혼재 영향',
        '[24개 SF 차이 CSV](../results/scaling_matrix_comparison.csv), [48개 계산식과 20개 실행 근거](scaling_matrix_traceability.md).',
        '- As-Reconstructed의 14→7은 512→256bit로 폭이 줄어 감소가 과장될 수 있다. 512bit 진단을 사용하면 14→7 SF가 커져 에너지 감소율이 작아진다.\n'
        f'- 7→5에서 SF>1인 As-Reconstructed 항목은 {increased}/8개이고, Width-Aligned에서 SF<1인 항목은 {decreased}/8개다. 256→512bit 폭이 섞인 증가를 공정 미세화의 역효과로 해석하면 안 된다.\n'
        f'- 5→3은 동일한 512bit 실행 두 개를 사용하므로 {unchanged}/8개 SF가 정확히 같고 ΔSF=0이다.',
        '**512bit 정렬 후에도 Pure Process Scaling으로 해석하지 않는다.** Voltage(Vdd 및 cell read-voltage), node별 Cell Parameters(면적·aspect ratio 등), Internal Cache Organization(data/tag bank·mat·subarray·mux·wire·buffer 선택)이 달라진다. 폭 효과 한 가지를 제거한 비교이며, 전압·셀·조직을 통제한 공정 단독 인과효과가 아니다.',
    ])
