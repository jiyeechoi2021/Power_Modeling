# 공정별 energy scaling 분석

아래는 새 실행에서 얻은 NS-Cache 모델값이다. NVIDIA GPU 실측값, 검증된 process-only ground truth, Rubin 예측이 아니다.
SF(a→b)=E_b/E_a; 감소율=100×(1−SF). read/write와 L1/L2를 분리했다. 0.001 nJ 단위로 반올림된 출력값을 사용하므로 표시 자릿수 이상의 정확도를 주장하지 않는다. 기초값과 로그 경로: [scaling.csv](../results/scaling.csv).

## Scaling matrix

| Cache | Objective | Energy | 14→7 | 7→5 | 5→3 |
|---|---|---|---:|---:|---:|
| L1 | ReadLatency | Read | 0.2432 | 1.7778 | 0.8125 |
| L1 | ReadLatency | Write | 0.2414 | 1.7143 | 0.7917 |
| L1 | ReadDynamicEnergy | Read | 0.2424 | 1.8125 | 0.8276 |
| L1 | ReadDynamicEnergy | Write | 0.2353 | 1.7500 | 0.8571 |
| L2 | ReadLatency | Read | 0.2312 | 1.7826 | 0.9146 |
| L2 | ReadLatency | Write | 0.2115 | 1.7879 | 0.9322 |
| L2 | ReadDynamicEnergy | Read | 0.2251 | 1.7674 | 0.8816 |
| L2 | ReadDynamicEnergy | Write | 0.2013 | 1.8000 | 0.8704 |

## 새 실행의 energy / area / latency

| Run | Read pJ | Write pJ | Leakage mW | Latency ns | Area mm² | Solutions |
|---|---:|---:|---:|---:|---:|---:|
| L1_14nm | 74.0 | 58.0 | 0.031 | 0.434 | 0.149 | 2.0 |
| L1_7nm | 18.0 | 14.0 | 0.039 | 0.325 | 0.052 | 72.0 |
| L1_5nm | 32.0 | 24.0 | 0.035 | 0.873 | 0.045 | 17.0 |
| L1_3nm | 26.0 | 19.0 | 0.038 | 0.813 | 0.034 | 17.0 |
| L1_14nm_ReadEnergy | 66.0 | 51.0 | 0.027 | 0.447 | 0.129 | 2.0 |
| L1_7nm_ReadEnergy | 16.0 | 12.0 | 0.036 | 0.335 | 0.046 | 72.0 |
| L1_5nm_ReadEnergy | 29.0 | 21.0 | 0.033 | 1.023 | 0.04 | 17.0 |
| L1_3nm_ReadEnergy | 24.0 | 18.0 | 0.034 | 0.978 | 0.029 | 17.0 |
| L2_14nm | 199.0 | 156.0 | 0.191 | 1.104 | 0.895 | 17.0 |
| L2_7nm | 46.0 | 33.0 | 0.258 | 0.77 | 0.317 | 57.0 |
| L2_5nm | 82.0 | 59.0 | 0.235 | 2.141 | 0.269 | 16.0 |
| L2_3nm | 75.0 | 55.0 | 0.249 | 2.072 | 0.214 | 15.0 |
| L2_14nm_ReadEnergy | 191.0 | 149.0 | 0.18 | 1.775 | 0.873 | 17.0 |
| L2_7nm_ReadEnergy | 43.0 | 30.0 | 0.246 | 1.387 | 0.305 | 57.0 |
| L2_5nm_ReadEnergy | 76.0 | 54.0 | 0.219 | 2.911 | 0.238 | 16.0 |
| L2_3nm_ReadEnergy | 67.0 | 47.0 | 0.229 | 2.851 | 0.195 | 15.0 |

## 내부 조직

data/tag를 구분하며 상세 활성화·mux·wire/buffer 값은 `parsed_results.json`의 `raw_configuration`과 원본 stdout에 보존한다.

| Run | Data bank / subarray / mat | Tag bank / subarray / mat |
|---|---|---|
| L1_14nm | 4 x 4 / 2 x 2 / 256 Rows x 64 Columns | 32 x 4 / 2 x 1 / 8 Rows x 40 Columns |
| L1_7nm | 4 x 4 / 2 x 2 / 256 Rows x 64 Columns | 32 x 2 / 2 x 2 / 8 Rows x 72 Columns |
| L1_5nm | 4 x 4 / 2 x 2 / 256 Rows x 64 Columns | 32 x 2 / 2 x 2 / 8 Rows x 40 Columns |
| L1_3nm | 4 x 4 / 2 x 2 / 256 Rows x 64 Columns | 64 x 2 / 2 x 2 / 2 Rows x 72 Columns |
| L1_14nm_ReadEnergy | 4 x 4 / 2 x 1 / 256 Rows x 128 Columns | 2 x 1 / 2 x 2 / 32 Rows x 288 Columns |
| L1_7nm_ReadEnergy | 4 x 4 / 2 x 1 / 256 Rows x 128 Columns | 4 x 1 / 2 x 2 / 32 Rows x 288 Columns |
| L1_5nm_ReadEnergy | 4 x 4 / 2 x 1 / 256 Rows x 128 Columns | 8 x 1 / 2 x 2 / 8 Rows x 288 Columns |
| L1_3nm_ReadEnergy | 4 x 4 / 2 x 1 / 256 Rows x 128 Columns | 8 x 1 / 2 x 2 / 8 Rows x 288 Columns |
| L2_14nm | 4 x 4 / 2 x 2 / 512 Rows x 256 Columns | 16 x 1 / 2 x 2 / 64 Rows x 144 Columns |
| L2_7nm | 4 x 4 / 2 x 2 / 512 Rows x 256 Columns | 16 x 1 / 2 x 2 / 64 Rows x 272 Columns |
| L2_5nm | 4 x 4 / 2 x 2 / 512 Rows x 256 Columns | 64 x 1 / 2 x 2 / 8 Rows x 272 Columns |
| L2_3nm | 4 x 4 / 2 x 2 / 512 Rows x 256 Columns | 64 x 4 / 2 x 2 / 8 Rows x 80 Columns |
| L2_14nm_ReadEnergy | 4 x 4 / 2 x 1 / 512 Rows x 512 Columns | 8 x 1 / 2 x 2 / 32 Rows x 544 Columns |
| L2_7nm_ReadEnergy | 4 x 4 / 2 x 1 / 512 Rows x 512 Columns | 16 x 1 / 2 x 2 / 32 Rows x 544 Columns |
| L2_5nm_ReadEnergy | 4 x 4 / 2 x 1 / 512 Rows x 512 Columns | 8 x 1 / 2 x 2 / 32 Rows x 544 Columns |
| L2_3nm_ReadEnergy | 4 x 4 / 2 x 1 / 512 Rows x 512 Columns | 8 x 1 / 2 x 2 / 32 Rows x 544 Columns |

## 경향 및 최적화 trade-off

재현 입력 그대로의 14→7에서는 read/write가 크게 감소하지만, 7→5에서는 네 cache/objective 조합 모두 증가한다. 이는 256→512bit 폭 변화가 포함된 결과이므로 공정 미세화 자체의 역효과로 해석하지 않는다. 5→3에서는 네 조합 모두 read/write energy가 감소한다.
5→3 read SF는 L1 latency/energy 목표에서 0.8125/0.8276, L2에서는 0.9146/0.8816이다. Write SF는 각각 0.7917/0.8571 및 0.9322/0.8704이다. 이 모델·선택 조직에서는 L1의 감소폭이 더 크지만 일반 GPU 법칙으로 확장할 수 없다.
Latency는 공정 미세화에 대해 단조 감소하지 않는다(예: L1 ReadLatency 7→5: 0.325→0.873ns). Leakage도 단조 감소하지 않는다. 실제 값은 위 표를 따른다.

| Cache | Node | Read-energy reduction % | Write-energy reduction % | Latency increase % | Area reduction % |
|---|---:|---:|---:|---:|---:|
| L1 | 14 | 10.81 | 12.07 | 3.00 | 13.42 |
| L1 | 7 | 11.11 | 14.29 | 3.08 | 11.54 |
| L1 | 5 | 9.38 | 12.50 | 17.18 | 11.11 |
| L1 | 3 | 7.69 | 5.26 | 20.30 | 14.71 |
| L2 | 14 | 4.02 | 4.49 | 60.78 | 2.46 |
| L2 | 7 | 6.52 | 9.09 | 80.13 | 3.79 |
| L2 | 5 | 7.32 | 8.47 | 35.96 | 11.52 |
| L2 | 3 | 10.67 | 14.55 | 37.60 | 8.88 |

ReadDynamicEnergy 목표는 동일 node의 ReadLatency 목표 대비 read/write energy와 area를 줄였지만 hit latency가 증가했다. 최적화 목표만 바뀌어도 선택 조직이 달라지므로 이 trade-off를 공정 효과와 분리해야 한다.

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

## 비교 조건과 해석 한계

- 7nm는 256bit(32-byte line), 14/5/3nm는 512bit(64-byte line)이다. 14→7 및 7→5 비율은 접근 폭/line size 효과가 섞인다. energy를 단순히 bit 수로 정규화해 보정하지 않았다.
- 용량 L1=128KiB/L2=1024KiB, associativity 8/16, normal cache access, LOP roadmap, 300K, H-tree, internal sensing, 4×4 data-bank 설정, 단일 die 및 latency buffer optimization은 유지된다. 전체 명시 옵션은 configuration_audit.csv/json에 있다.
- Port count는 입력 파라미터에서 독립적으로 설정된 항목을 확인하지 못했다. 단일 포트라고 추정하지 않는다. 동일 소스 실행이라는 사실과 실제 GPU 포트 구조 동등성은 별개다.
- 명시 latency/energy/area constraint는 없다. InputParameter 생성자의 clockFreq=3GHz는 기본값이며 고정 hit-latency 제약의 증거가 아니다. ReadDynamicEnergy에서도 BufferDesignOptimization은 latency이다.
- Cell read-voltage 정의는 14/7/5/3nm에서 0.277/0.264/0.253/0.248V이다. 이는 공급전압 Vdd와 다르다. Technology.cpp의 해당 비-HP 분기 Vdd는 0.8/0.7/0.7/0.7V이며, initializeTechnology의 해당 정수 node 보간계수는 0이다. Node별 cell 면적 F²·aspect ratio도 변한다. 전압/셀/소자/배선 모델을 분리한 실험이 아니다.
- 최적화가 선택한 data/tag의 mat, subarray, mux와 배선·buffer 구성이 달라질 수 있다. 5→3은 접근 폭이 같아도 내부 조직과 node별 cell 파라미터를 고정하지 않아 순수 공정 효과를 식별할 수 없다.
- 새 결과의 감소/증가 경향은 아래 후속 해석에 요약한다. Leakage는 전력이며 per-access dynamic energy에 더하지 않는다. 비공개 GPU 실측 또는 historical correction은 포함하거나 검증하지 않았다.

## 후속 실험

1. 별도 이름의 controlled sweep에서 line/access width와 포트 요구·동일 latency 제약을 명시하고 512bit 전 공정을 실행한다. 이번 재현 입력은 보존한다.
2. 고정 조직과 재최적화 조직을 별도 실행하고, data/tag topology 및 wire/buffer를 통제해 architecture 효과를 분리한다.
3. Vdd·cell·technology 모델 감도 분석과 unrounded 출력 검증을 진행한다. 모델값에 대한 GPU 세대 매핑은 별도 하드웨어 검증이 필요하다.
4. 원본 workbook/설정/16개 historical stdout를 회수할 수 있으면 출처를 별도 등록한다. Rubin 최종 예측은 이번 단계 범위 밖이다.
