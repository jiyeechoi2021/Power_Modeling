# 재현성 검증

새 실행만 비교에 사용한다. 원본 historical 로그/설정은 복구되지 않았으며, bundled 로그는 새 실행으로 집계하지 않는다.
원본 ZIP과 추출 파일은 `provenance/archive_manifest.csv`의 SHA-256으로 추적한다. 복구된 소스 54개는 보고된 upstream commit의 대응 파일과 모두 byte-identical이며, 소스 변경 없이 빌드했다.

## 비교 방법

stdout의 cache summary에서 read/write nJ를 ×1000 하여 pJ/access로 변환한다. leakage=mW, latency=ns, area=mm². 0.001 nJ 출력 간격에 대해 에너지는 ±0.5 pJ, 나머지 세 연속 지표는 ±0.0005, solution count는 정확히 비교한다. 이는 출력 해상도 기준이며 내부 계산 정밀도의 동등성을 증명하지 않는다. 부호 있는 차이는 새 값−기록값이다.
종료 코드 0, Finished!, 모든 summary 항목과 data/tag 조직 파싱, 입력·cell·binary·로그 SHA-256 일치를 요구한다. 비교 스크립트는 미실행/실패/불일치가 있으면 비영 종료한다.

## 실행별 결과

| Run | Execution | Comparison | Seconds | Raw stdout |
|---|---|---|---:|---|
| L1_14nm | FINISHED | MATCH | 10.92 | [logs/new/L1_14nm/20261111T021209.801549Z/stdout.log](../logs/new/L1_14nm/20261111T021209.801549Z/stdout.log) |
| L1_7nm | FINISHED | DIFFERENT | 17.37 | [logs/new/L1_7nm/20261111T021312.264165Z/stdout.log](../logs/new/L1_7nm/20261111T021312.264165Z/stdout.log) |
| L1_5nm | FINISHED | MATCH | 12.82 | [logs/new/L1_5nm/20261111T021259.442309Z/stdout.log](../logs/new/L1_5nm/20261111T021259.442309Z/stdout.log) |
| L1_3nm | FINISHED | MATCH | 12.55 | [logs/new/L1_3nm/20261111T021246.385146Z/stdout.log](../logs/new/L1_3nm/20261111T021246.385146Z/stdout.log) |
| L1_14nm_ReadEnergy | FINISHED | MATCH | 13.06 | [logs/new/L1_14nm_ReadEnergy/20261111T021246.382768Z/stdout.log](../logs/new/L1_14nm_ReadEnergy/20261111T021246.382768Z/stdout.log) |
| L1_7nm_ReadEnergy | FINISHED | DIFFERENT | 17.82 | [logs/new/L1_7nm_ReadEnergy/20261111T021324.523014Z/stdout.log](../logs/new/L1_7nm_ReadEnergy/20261111T021324.523014Z/stdout.log) |
| L1_5nm_ReadEnergy | FINISHED | MATCH | 13.21 | [logs/new/L1_5nm_ReadEnergy/20261111T021311.306906Z/stdout.log](../logs/new/L1_5nm_ReadEnergy/20261111T021311.306906Z/stdout.log) |
| L1_3nm_ReadEnergy | FINISHED | MATCH | 12.36 | [logs/new/L1_3nm_ReadEnergy/20261111T021258.940138Z/stdout.log](../logs/new/L1_3nm_ReadEnergy/20261111T021258.940138Z/stdout.log) |
| L2_14nm | FINISHED | MATCH | 31.06 | [logs/new/L2_14nm/20261111T021329.639043Z/stdout.log](../logs/new/L2_14nm/20261111T021329.639043Z/stdout.log) |
| L2_7nm | FINISHED | DIFFERENT | 41.39 | [logs/new/L2_7nm/20261111T021505.430977Z/stdout.log](../logs/new/L2_7nm/20261111T021505.430977Z/stdout.log) |
| L2_5nm | FINISHED | MATCH | 35.18 | [logs/new/L2_5nm/20261111T021430.245271Z/stdout.log](../logs/new/L2_5nm/20261111T021430.245271Z/stdout.log) |
| L2_3nm | FINISHED | MATCH | 29.54 | [logs/new/L2_3nm/20261111T021400.697064Z/stdout.log](../logs/new/L2_3nm/20261111T021400.697064Z/stdout.log) |
| L2_14nm_ReadEnergy | FINISHED | MATCH | 29.74 | [logs/new/L2_14nm_ReadEnergy/20261111T021342.346075Z/stdout.log](../logs/new/L2_14nm_ReadEnergy/20261111T021342.346075Z/stdout.log) |
| L2_7nm_ReadEnergy | FINISHED | DIFFERENT | 40.28 | [logs/new/L2_7nm_ReadEnergy/20261111T021517.121198Z/stdout.log](../logs/new/L2_7nm_ReadEnergy/20261111T021517.121198Z/stdout.log) |
| L2_5nm_ReadEnergy | FINISHED | MATCH | 34.62 | [logs/new/L2_5nm_ReadEnergy/20261111T021442.501285Z/stdout.log](../logs/new/L2_5nm_ReadEnergy/20261111T021442.501285Z/stdout.log) |
| L2_3nm_ReadEnergy | FINISHED | MATCH | 30.41 | [logs/new/L2_3nm_ReadEnergy/20261111T021412.092928Z/stdout.log](../logs/new/L2_3nm_ReadEnergy/20261111T021412.092928Z/stdout.log) |

## 항목별 비교

| Run | Metric | Recorded | New | Difference | Status |
|---|---|---:|---:|---:|---|
| L1_14nm | read_pj_per_access | 74 | 74.000 | 0.000 | MATCH |
| L1_14nm | write_pj_per_access | 58 | 58.000 | 0.000 | MATCH |
| L1_14nm | leakage_mw | 0.031 | 0.031 | 0.000 | MATCH |
| L1_14nm | hit_latency_ns | 0.434 | 0.434 | 0.000 | MATCH |
| L1_14nm | area_mm2 | 0.149 | 0.149 | 0.000 | MATCH |
| L1_14nm | feasible_solutions | 2 | 2 | 0 | MATCH |
| L1_7nm | read_pj_per_access | 34 | 18.000 | -16.000 | DIFFERENT |
| L1_7nm | write_pj_per_access | 25 | 14.000 | -11.000 | DIFFERENT |
| L1_7nm | leakage_mw | 0.037 | 0.039 | 0.002 | DIFFERENT |
| L1_7nm | hit_latency_ns | 0.325 | 0.325 | 0.000 | MATCH |
| L1_7nm | area_mm2 | 0.05 | 0.052 | 0.002 | DIFFERENT |
| L1_7nm | feasible_solutions | 17 | 72 | 55 | DIFFERENT |
| L1_5nm | read_pj_per_access | 32 | 32.000 | 0.000 | MATCH |
| L1_5nm | write_pj_per_access | 24 | 24.000 | 0.000 | MATCH |
| L1_5nm | leakage_mw | 0.035 | 0.035 | 0.000 | MATCH |
| L1_5nm | hit_latency_ns | 0.873 | 0.873 | 0.000 | MATCH |
| L1_5nm | area_mm2 | 0.045 | 0.045 | 0.000 | MATCH |
| L1_5nm | feasible_solutions | 17 | 17 | 0 | MATCH |
| L1_3nm | read_pj_per_access | 26 | 26.000 | 0.000 | MATCH |
| L1_3nm | write_pj_per_access | 19 | 19.000 | 0.000 | MATCH |
| L1_3nm | leakage_mw | 0.038 | 0.038 | 0.000 | MATCH |
| L1_3nm | hit_latency_ns | 0.813 | 0.813 | 0.000 | MATCH |
| L1_3nm | area_mm2 | 0.034 | 0.034 | 0.000 | MATCH |
| L1_3nm | feasible_solutions | 17 | 17 | 0 | MATCH |
| L1_14nm_ReadEnergy | read_pj_per_access | 66 | 66.000 | 0.000 | MATCH |
| L1_14nm_ReadEnergy | write_pj_per_access | 51 | 51.000 | 0.000 | MATCH |
| L1_14nm_ReadEnergy | leakage_mw | 0.027 | 0.027 | 0.000 | MATCH |
| L1_14nm_ReadEnergy | hit_latency_ns | 0.447 | 0.447 | 0.000 | MATCH |
| L1_14nm_ReadEnergy | area_mm2 | 0.129 | 0.129 | 0.000 | MATCH |
| L1_14nm_ReadEnergy | feasible_solutions | 2 | 2 | 0 | MATCH |
| L1_7nm_ReadEnergy | read_pj_per_access | 31 | 16.000 | -15.000 | DIFFERENT |
| L1_7nm_ReadEnergy | write_pj_per_access | 23 | 12.000 | -11.000 | DIFFERENT |
| L1_7nm_ReadEnergy | leakage_mw | 0.034 | 0.036 | 0.002 | DIFFERENT |
| L1_7nm_ReadEnergy | hit_latency_ns | 0.335 | 0.335 | 0.000 | MATCH |
| L1_7nm_ReadEnergy | area_mm2 | 0.045 | 0.046 | 0.001 | DIFFERENT |
| L1_7nm_ReadEnergy | feasible_solutions | 17 | 72 | 55 | DIFFERENT |
| L1_5nm_ReadEnergy | read_pj_per_access | 29 | 29.000 | 0.000 | MATCH |
| L1_5nm_ReadEnergy | write_pj_per_access | 21 | 21.000 | 0.000 | MATCH |
| L1_5nm_ReadEnergy | leakage_mw | 0.033 | 0.033 | 0.000 | MATCH |
| L1_5nm_ReadEnergy | hit_latency_ns | 1.023 | 1.023 | 0.000 | MATCH |
| L1_5nm_ReadEnergy | area_mm2 | 0.04 | 0.040 | 0.000 | MATCH |
| L1_5nm_ReadEnergy | feasible_solutions | 17 | 17 | 0 | MATCH |
| L1_3nm_ReadEnergy | read_pj_per_access | 24 | 24.000 | 0.000 | MATCH |
| L1_3nm_ReadEnergy | write_pj_per_access | 18 | 18.000 | 0.000 | MATCH |
| L1_3nm_ReadEnergy | leakage_mw | 0.034 | 0.034 | 0.000 | MATCH |
| L1_3nm_ReadEnergy | hit_latency_ns | 0.978 | 0.978 | 0.000 | MATCH |
| L1_3nm_ReadEnergy | area_mm2 | 0.029 | 0.029 | 0.000 | MATCH |
| L1_3nm_ReadEnergy | feasible_solutions | 17 | 17 | 0 | MATCH |
| L2_14nm | read_pj_per_access | 199 | 199.000 | 0.000 | MATCH |
| L2_14nm | write_pj_per_access | 156 | 156.000 | 0.000 | MATCH |
| L2_14nm | leakage_mw | 0.191 | 0.191 | 0.000 | MATCH |
| L2_14nm | hit_latency_ns | 1.104 | 1.104 | 0.000 | MATCH |
| L2_14nm | area_mm2 | 0.895 | 0.895 | 0.000 | MATCH |
| L2_14nm | feasible_solutions | 17 | 17 | 0 | MATCH |
| L2_7nm | read_pj_per_access | 87 | 46.000 | -41.000 | DIFFERENT |
| L2_7nm | write_pj_per_access | 63 | 33.000 | -30.000 | DIFFERENT |
| L2_7nm | leakage_mw | 0.243 | 0.258 | 0.015 | DIFFERENT |
| L2_7nm | hit_latency_ns | 0.771 | 0.770 | -0.001 | DIFFERENT |
| L2_7nm | area_mm2 | 0.3 | 0.317 | 0.017 | DIFFERENT |
| L2_7nm | feasible_solutions | 15 | 57 | 42 | DIFFERENT |
| L2_5nm | read_pj_per_access | 82 | 82.000 | 0.000 | MATCH |
| L2_5nm | write_pj_per_access | 59 | 59.000 | 0.000 | MATCH |
| L2_5nm | leakage_mw | 0.235 | 0.235 | 0.000 | MATCH |
| L2_5nm | hit_latency_ns | 2.141 | 2.141 | 0.000 | MATCH |
| L2_5nm | area_mm2 | 0.269 | 0.269 | 0.000 | MATCH |
| L2_5nm | feasible_solutions | 16 | 16 | 0 | MATCH |
| L2_3nm | read_pj_per_access | 75 | 75.000 | 0.000 | MATCH |
| L2_3nm | write_pj_per_access | 55 | 55.000 | 0.000 | MATCH |
| L2_3nm | leakage_mw | 0.249 | 0.249 | 0.000 | MATCH |
| L2_3nm | hit_latency_ns | 2.072 | 2.072 | 0.000 | MATCH |
| L2_3nm | area_mm2 | 0.214 | 0.214 | 0.000 | MATCH |
| L2_3nm | feasible_solutions | 15 | 15 | 0 | MATCH |
| L2_14nm_ReadEnergy | read_pj_per_access | 191 | 191.000 | 0.000 | MATCH |
| L2_14nm_ReadEnergy | write_pj_per_access | 149 | 149.000 | 0.000 | MATCH |
| L2_14nm_ReadEnergy | leakage_mw | 0.18 | 0.180 | 0.000 | MATCH |
| L2_14nm_ReadEnergy | hit_latency_ns | 1.775 | 1.775 | 0.000 | MATCH |
| L2_14nm_ReadEnergy | area_mm2 | 0.873 | 0.873 | 0.000 | MATCH |
| L2_14nm_ReadEnergy | feasible_solutions | 17 | 17 | 0 | MATCH |
| L2_7nm_ReadEnergy | read_pj_per_access | 83 | 43.000 | -40.000 | DIFFERENT |
| L2_7nm_ReadEnergy | write_pj_per_access | 59 | 30.000 | -29.000 | DIFFERENT |
| L2_7nm_ReadEnergy | leakage_mw | 0.231 | 0.246 | 0.015 | DIFFERENT |
| L2_7nm_ReadEnergy | hit_latency_ns | 0.961 | 1.387 | 0.426 | DIFFERENT |
| L2_7nm_ReadEnergy | area_mm2 | 0.284 | 0.305 | 0.021 | DIFFERENT |
| L2_7nm_ReadEnergy | feasible_solutions | 15 | 57 | 42 | DIFFERENT |
| L2_5nm_ReadEnergy | read_pj_per_access | 76 | 76.000 | 0.000 | MATCH |
| L2_5nm_ReadEnergy | write_pj_per_access | 54 | 54.000 | 0.000 | MATCH |
| L2_5nm_ReadEnergy | leakage_mw | 0.219 | 0.219 | 0.000 | MATCH |
| L2_5nm_ReadEnergy | hit_latency_ns | 2.911 | 2.911 | 0.000 | MATCH |
| L2_5nm_ReadEnergy | area_mm2 | 0.238 | 0.238 | 0.000 | MATCH |
| L2_5nm_ReadEnergy | feasible_solutions | 16 | 16 | 0 | MATCH |
| L2_3nm_ReadEnergy | read_pj_per_access | 67 | 67.000 | 0.000 | MATCH |
| L2_3nm_ReadEnergy | write_pj_per_access | 47 | 47.000 | 0.000 | MATCH |
| L2_3nm_ReadEnergy | leakage_mw | 0.229 | 0.229 | 0.000 | MATCH |
| L2_3nm_ReadEnergy | hit_latency_ns | 2.851 | 2.851 | 0.000 | MATCH |
| L2_3nm_ReadEnergy | area_mm2 | 0.195 | 0.195 | 0.000 | MATCH |
| L2_3nm_ReadEnergy | feasible_solutions | 15 | 15 | 0 | MATCH |

## 판단 및 불일치 조사

16/16 실행 완료, 12/16 전체 지표 일치.
불일치 실행: L1_7nm, L1_7nm_ReadEnergy, L2_7nm, L2_7nm_ReadEnergy.
현재 입력은 재구성본이다. 수치가 일치해도 historical 원본 입력/로그 복구를 의미하지 않는다. 7nm의 256bit 폭은 다른 공정의 512bit와 다르므로 archive README의 고정 512bit 설명을 그대로 인용하면 안 된다. 숫자를 맞추기 위한 설정 보정은 하지 않았다.
빌드 로그의 기존 compiler warnings는 보존했다. 실패·시간초과 시에도 attempt별 stdout/stderr/metadata를 보존하며, 완료·해시 검증된 실행만 재개 시 생략한다.

환경·빌드 명령: [environment.json](../logs/build/environment.json), [stdout](../logs/build/stdout.log), [stderr](../logs/build/stderr.log). 각 실행의 실제 시간과 UTC 시각은 metadata에 기록된다.

## 별도 512bit 진단: 재현 실험과 구분

재현 입력 16개는 수정하지 않았다. 불일치 원인을 분리하기 위해 7nm 4개를 복사하고 WordWidth만 256→512bit로 변경한 별도 실험을 수행했다. 선택한 변경은 사전에 발견한 비교 조건 위반 한 가지이며, 숫자 맞추기 위한 추가 파라미터 조정은 없다.
변경 diff/해시: width_diagnostic_changes.json. 별도 입력: configs/diagnostic_512bit; 로그: logs/diagnostic_512bit; 파싱 결과: width_diagnostic.json/csv. 이 결과를 16개 재현 실행에 대체하거나 historical 원본으로 표시하지 않는다.

| Diagnostic | Read pJ | Write pJ | All six recorded metrics exactly equal | Raw stdout |
|---|---:|---:|---|---|
| L1_7nm | 34.0 | 25.0 | True | [log](../logs/diagnostic_512bit/L1_7nm/20261111T021548.654557Z/stdout.log) |
| L1_7nm_ReadEnergy | 31.0 | 23.0 | True | [log](../logs/diagnostic_512bit/L1_7nm_ReadEnergy/20261111T021548.654632Z/stdout.log) |
| L2_7nm | 87.0 | 63.0 | True | [log](../logs/diagnostic_512bit/L2_7nm/20261111T021559.405221Z/stdout.log) |
| L2_7nm_ReadEnergy | 83.0 | 59.0 | True | [log](../logs/diagnostic_512bit/L2_7nm_ReadEnergy/20261111T021559.763894Z/stdout.log) |

4개 모두 6개 지표가 기록값과 정확히 일치했다. 따라서 제공된 7nm 재구성 설정의 폭 차이가 현재 불일치를 설명한다는 강한 실험적 근거를 확보했다. 원래 설정이 512bit였다는 historical 증명이나 원본 자료 회수로 간주하지 않는다. 소스 버전은 54개 파일의 byte 일치로, 단위 변환은 Decimal 기반 파싱으로 확인했다. 데이터/태그 조직 비교도 각각의 JSON과 로그에서 가능하다.
