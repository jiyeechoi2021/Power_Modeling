# Phase 2-A: 256bit L1/L2 energy scaling

## 배경과 실험 조건

GPU 32B sector 단위와 비교할 모델 기준을 만들기 위해 Phase 1의 512bit 설정에서 WordWidth만 256bit로 바꿨다. L1=128KiB/8-way, L2=1MiB/16-way; 14/7/5/3nm; ReadLatency/ReadDynamicEnergy; 300K/LOP/Normal/H-tree/단일 die 및 나머지 옵션은 유지했다. 7nm도 새 실행이며 기존 로그를 재사용하지 않았다. 원본 Phase 1 자료와 모델 소스는 수정하지 않았다.
설정 diff·원본·SHA-256: [derivation](../provenance/configuration_derivation.json). 실행 환경/실제 빌드: [environment](../logs/build/environment.json), [build stdout](../logs/build/stdout.log). 각 로그 옆 metadata에 종료 코드/시간/해시가 있다.

## 실행 상태 및 256bit 절대 Energy Matrix

| Run | Status | Read pJ/access | Write pJ/access | Leakage mW | Hit ns | Area mm² | Solutions | Raw log |
|---|---|---:|---:|---:|---:|---:|---:|---|
| L1_14nm | FINISHED | 38.000 | 30.000 | 0.032 | 0.433 | 0.161 | 15 | [stdout](../logs/phase2_256bit/L1_14nm/20261111T095654.943244Z/stdout.log) |
| L1_7nm | FINISHED | 18.000 | 14.000 | 0.039 | 0.325 | 0.052 | 72 | [stdout](../logs/phase2_256bit/L1_7nm/20261111T095741.466300Z/stdout.log) |
| L1_5nm | FINISHED | 17.000 | 13.000 | 0.037 | 0.873 | 0.048 | 72 | [stdout](../logs/phase2_256bit/L1_5nm/20261111T095726.059550Z/stdout.log) |
| L1_3nm | FINISHED | 15.000 | 12.000 | 0.040 | 0.813 | 0.034 | 72 | [stdout](../logs/phase2_256bit/L1_3nm/20261111T095710.681814Z/stdout.log) |
| L1_14nm_ReadEnergy | FINISHED | 35.000 | 27.000 | 0.028 | 0.447 | 0.137 | 15 | [stdout](../logs/phase2_256bit/L1_14nm_ReadEnergy/20261111T095654.943326Z/stdout.log) |
| L1_7nm_ReadEnergy | FINISHED | 16.000 | 12.000 | 0.036 | 0.335 | 0.046 | 72 | [stdout](../logs/phase2_256bit/L1_7nm_ReadEnergy/20261111T095743.422810Z/stdout.log) |
| L1_5nm_ReadEnergy | FINISHED | 15.000 | 11.000 | 0.034 | 1.041 | 0.041 | 72 | [stdout](../logs/phase2_256bit/L1_5nm_ReadEnergy/20261111T095728.011090Z/stdout.log) |
| L1_3nm_ReadEnergy | FINISHED | 13.000 | 9.000 | 0.035 | 0.982 | 0.030 | 72 | [stdout](../logs/phase2_256bit/L1_3nm_ReadEnergy/20261111T095712.085479Z/stdout.log) |
| L2_14nm | FINISHED | 103.000 | 81.000 | 0.201 | 1.103 | 0.947 | 72 | [stdout](../logs/phase2_256bit/L2_14nm/20261111T095755.830625Z/stdout.log) |
| L2_7nm | FINISHED | 46.000 | 33.000 | 0.258 | 0.770 | 0.317 | 57 | [stdout](../logs/phase2_256bit/L2_7nm/20261111T095955.392894Z/stdout.log) |
| L2_5nm | FINISHED | 44.000 | 32.000 | 0.246 | 2.140 | 0.276 | 65 | [stdout](../logs/phase2_256bit/L2_5nm/20261111T095916.559895Z/stdout.log) |
| L2_3nm | FINISHED | 37.000 | 27.000 | 0.257 | 2.072 | 0.217 | 57 | [stdout](../logs/phase2_256bit/L2_3nm/20261111T095836.172778Z/stdout.log) |
| L2_14nm_ReadEnergy | FINISHED | 98.000 | 76.000 | 0.191 | 1.850 | 0.922 | 72 | [stdout](../logs/phase2_256bit/L2_14nm_ReadEnergy/20261111T095757.832618Z/stdout.log) |
| L2_7nm_ReadEnergy | FINISHED | 43.000 | 30.000 | 0.246 | 1.387 | 0.305 | 57 | [stdout](../logs/phase2_256bit/L2_7nm_ReadEnergy/20261111T095958.504262Z/stdout.log) |
| L2_5nm_ReadEnergy | FINISHED | 39.000 | 28.000 | 0.234 | 3.598 | 0.255 | 65 | [stdout](../logs/phase2_256bit/L2_5nm_ReadEnergy/20261111T095916.961744Z/stdout.log) |
| L2_3nm_ReadEnergy | FINISHED | 35.000 | 24.000 | 0.244 | 3.387 | 0.209 | 57 | [stdout](../logs/phase2_256bit/L2_3nm_ReadEnergy/20261111T095837.427048Z/stdout.log) |

## 256bit SF Matrix

`SF(a→b)=E_b/E_a`; `Reduction%=100×(1−SF)`. Read/Write는 별도이며 SF는 무차원이다. CSV의 각 행에 raw log/configuration/대입식을 기록했다. [256bit SF](../results/phase2_256bit_scaling.csv).

| Cache | Optimization | Energy | 14→7 | 7→5 | 5→3 |
|---|---|---|---:|---:|---:|
| L1 | ReadLatency | Read | 0.473684 | 0.944444 | 0.882353 |
| L1 | ReadLatency | Write | 0.466667 | 0.928571 | 0.923077 |
| L1 | ReadDynamicEnergy | Read | 0.457143 | 0.937500 | 0.866667 |
| L1 | ReadDynamicEnergy | Write | 0.444444 | 0.916667 | 0.818182 |
| L2 | ReadLatency | Read | 0.446602 | 0.956522 | 0.840909 |
| L2 | ReadLatency | Write | 0.407407 | 0.969697 | 0.843750 |
| L2 | ReadDynamicEnergy | Read | 0.438776 | 0.906977 | 0.897436 |
| L2 | ReadDynamicEnergy | Write | 0.394737 | 0.933333 | 0.857143 |

## Table A: 256bit/512bit Absolute Energy Comparison

E256/E512와 E512/E256을 구분해 CSV에 기록했다. 아래 비율은 E256/E512다. Effective pJ/bit=Eaccess/WordWidth이며 물리적 단일 SRAM cell bit energy가 아니다.
[전체 energy·pJ/bit·latency/leakage/area 차이 CSV](../results/width_256_vs_512_comparison.csv).

| Run | Read256 / 512 pJ | Read ratio | Read256 / 512 pJ/bit | Write256 / 512 pJ | Write ratio | Write256 / 512 pJ/bit |
|---|---:|---:|---:|---:|---:|---:|
| L1_14nm | 38.000 / 74.000 | 0.5135 | 0.148438 / 0.144531 | 30.000 / 58.000 | 0.5172 | 0.117188 / 0.113281 |
| L1_7nm | 18.000 / 34.000 | 0.5294 | 0.070312 / 0.066406 | 14.000 / 25.000 | 0.5600 | 0.054688 / 0.048828 |
| L1_5nm | 17.000 / 32.000 | 0.5312 | 0.066406 / 0.062500 | 13.000 / 24.000 | 0.5417 | 0.050781 / 0.046875 |
| L1_3nm | 15.000 / 26.000 | 0.5769 | 0.058594 / 0.050781 | 12.000 / 19.000 | 0.6316 | 0.046875 / 0.037109 |
| L1_14nm_ReadEnergy | 35.000 / 66.000 | 0.5303 | 0.136719 / 0.128906 | 27.000 / 51.000 | 0.5294 | 0.105469 / 0.099609 |
| L1_7nm_ReadEnergy | 16.000 / 31.000 | 0.5161 | 0.062500 / 0.060547 | 12.000 / 23.000 | 0.5217 | 0.046875 / 0.044922 |
| L1_5nm_ReadEnergy | 15.000 / 29.000 | 0.5172 | 0.058594 / 0.056641 | 11.000 / 21.000 | 0.5238 | 0.042969 / 0.041016 |
| L1_3nm_ReadEnergy | 13.000 / 24.000 | 0.5417 | 0.050781 / 0.046875 | 9.000 / 18.000 | 0.5000 | 0.035156 / 0.035156 |
| L2_14nm | 103.000 / 199.000 | 0.5176 | 0.402344 / 0.388672 | 81.000 / 156.000 | 0.5192 | 0.316406 / 0.304688 |
| L2_7nm | 46.000 / 87.000 | 0.5287 | 0.179688 / 0.169922 | 33.000 / 63.000 | 0.5238 | 0.128906 / 0.123047 |
| L2_5nm | 44.000 / 82.000 | 0.5366 | 0.171875 / 0.160156 | 32.000 / 59.000 | 0.5424 | 0.125000 / 0.115234 |
| L2_3nm | 37.000 / 75.000 | 0.4933 | 0.144531 / 0.146484 | 27.000 / 55.000 | 0.4909 | 0.105469 / 0.107422 |
| L2_14nm_ReadEnergy | 98.000 / 191.000 | 0.5131 | 0.382812 / 0.373047 | 76.000 / 149.000 | 0.5101 | 0.296875 / 0.291016 |
| L2_7nm_ReadEnergy | 43.000 / 83.000 | 0.5181 | 0.167969 / 0.162109 | 30.000 / 59.000 | 0.5085 | 0.117188 / 0.115234 |
| L2_5nm_ReadEnergy | 39.000 / 76.000 | 0.5132 | 0.152344 / 0.148438 | 28.000 / 54.000 | 0.5185 | 0.109375 / 0.105469 |
| L2_3nm_ReadEnergy | 35.000 / 67.000 | 0.5224 | 0.136719 / 0.130859 | 24.000 / 47.000 | 0.5106 | 0.093750 / 0.091797 |

## Table B: 256bit/512bit Read/Write SF Comparison

[24개 SF 비교: 양 폭의 모든 log/configuration/수식](../results/width_256_vs_512_scaling.csv). ΔSF=SF256−SF512.

| Cache | Optimization | Energy | Transition | SF256 | SF512 | ΔSF |
|---|---|---|---|---:|---:|---:|
| L1 | ReadLatency | Read | 14→7 | 0.473684 | 0.459459 | 0.014225 |
| L1 | ReadLatency | Read | 7→5 | 0.944444 | 0.941176 | 0.003268 |
| L1 | ReadLatency | Read | 5→3 | 0.882353 | 0.812500 | 0.069853 |
| L1 | ReadLatency | Write | 14→7 | 0.466667 | 0.431034 | 0.035632 |
| L1 | ReadLatency | Write | 7→5 | 0.928571 | 0.960000 | -0.031429 |
| L1 | ReadLatency | Write | 5→3 | 0.923077 | 0.791667 | 0.131410 |
| L1 | ReadDynamicEnergy | Read | 14→7 | 0.457143 | 0.469697 | -0.012554 |
| L1 | ReadDynamicEnergy | Read | 7→5 | 0.937500 | 0.935484 | 0.002016 |
| L1 | ReadDynamicEnergy | Read | 5→3 | 0.866667 | 0.827586 | 0.039080 |
| L1 | ReadDynamicEnergy | Write | 14→7 | 0.444444 | 0.450980 | -0.006536 |
| L1 | ReadDynamicEnergy | Write | 7→5 | 0.916667 | 0.913043 | 0.003623 |
| L1 | ReadDynamicEnergy | Write | 5→3 | 0.818182 | 0.857143 | -0.038961 |
| L2 | ReadLatency | Read | 14→7 | 0.446602 | 0.437186 | 0.009416 |
| L2 | ReadLatency | Read | 7→5 | 0.956522 | 0.942529 | 0.013993 |
| L2 | ReadLatency | Read | 5→3 | 0.840909 | 0.914634 | -0.073725 |
| L2 | ReadLatency | Write | 14→7 | 0.407407 | 0.403846 | 0.003561 |
| L2 | ReadLatency | Write | 7→5 | 0.969697 | 0.936508 | 0.033189 |
| L2 | ReadLatency | Write | 5→3 | 0.843750 | 0.932203 | -0.088453 |
| L2 | ReadDynamicEnergy | Read | 14→7 | 0.438776 | 0.434555 | 0.004221 |
| L2 | ReadDynamicEnergy | Read | 7→5 | 0.906977 | 0.915663 | -0.008686 |
| L2 | ReadDynamicEnergy | Read | 5→3 | 0.897436 | 0.881579 | 0.015857 |
| L2 | ReadDynamicEnergy | Write | 14→7 | 0.394737 | 0.395973 | -0.001236 |
| L2 | ReadDynamicEnergy | Write | 7→5 | 0.933333 | 0.915254 | 0.018079 |
| L2 | ReadDynamicEnergy | Write | 5→3 | 0.857143 | 0.870370 | -0.013228 |

### Latency / Leakage / Area 비교

| Run | Hit ns 256 / 512 | Leakage mW 256 / 512 | Area mm² 256 / 512 |
|---|---:|---:|---:|
| L1_14nm | 0.433 / 0.434 | 0.032 / 0.031 | 0.161 / 0.149 |
| L1_7nm | 0.325 / 0.325 | 0.039 / 0.037 | 0.052 / 0.050 |
| L1_5nm | 0.873 / 0.873 | 0.037 / 0.035 | 0.048 / 0.045 |
| L1_3nm | 0.813 / 0.813 | 0.040 / 0.038 | 0.034 / 0.034 |
| L1_14nm_ReadEnergy | 0.447 / 0.447 | 0.028 / 0.027 | 0.137 / 0.129 |
| L1_7nm_ReadEnergy | 0.335 / 0.335 | 0.036 / 0.034 | 0.046 / 0.045 |
| L1_5nm_ReadEnergy | 1.041 / 1.023 | 0.034 / 0.033 | 0.041 / 0.040 |
| L1_3nm_ReadEnergy | 0.982 / 0.978 | 0.035 / 0.034 | 0.030 / 0.029 |
| L2_14nm | 1.103 / 1.104 | 0.201 / 0.191 | 0.947 / 0.895 |
| L2_7nm | 0.770 / 0.771 | 0.258 / 0.243 | 0.317 / 0.300 |
| L2_5nm | 2.140 / 2.141 | 0.246 / 0.235 | 0.276 / 0.269 |
| L2_3nm | 2.072 / 2.072 | 0.257 / 0.249 | 0.217 / 0.214 |
| L2_14nm_ReadEnergy | 1.850 / 1.775 | 0.191 / 0.180 | 0.922 / 0.873 |
| L2_7nm_ReadEnergy | 1.387 / 0.961 | 0.246 / 0.231 | 0.305 / 0.284 |
| L2_5nm_ReadEnergy | 3.598 / 2.911 | 0.234 / 0.219 | 0.255 / 0.238 |
| L2_3nm_ReadEnergy | 3.387 / 2.851 | 0.244 / 0.229 | 0.209 / 0.195 |

가장 큰 |ΔSF|는 L1/ReadLatency/write_pj_per_access 5→3의 0.131410이다. 폭에 따라 SF 자체도 달라진다.
Cache summary energy는 0.001nJ=1pJ 간격으로 출력된다. 작은 pJ/bit·SF 차이의 통계적 유의성이나 내부 계산 정밀도를 이 표만으로 주장하지 않는다.

## Width 영향: 관측과 원인 분석

- 관측: L1 read energy 감소율(512→256)은 42.31–48.65%; effective pJ/bit의 256/512 비는 1.0270–1.1538. 정확한 선형 반감이라면 각각 50%, 1이어야 한다.
- 관측: L1 write energy 감소율(512→256)은 36.84–50.00%; effective pJ/bit의 256/512 비는 1.0000–1.2632. 정확한 선형 반감이라면 각각 50%, 1이어야 한다.
- 관측: L2 read energy 감소율(512→256)은 46.34–50.67%; effective pJ/bit의 256/512 비는 0.9867–1.0732. 정확한 선형 반감이라면 각각 50%, 1이어야 한다.
- 관측: L2 write energy 감소율(512→256)은 45.76–50.91%; effective pJ/bit의 256/512 비는 0.9818–1.0847. 정확한 선형 반감이라면 각각 50%, 1이어야 한다.

### 선택된 조직과 printed breakdown

[data/tag별 전체 조직·mux·wire/buffer와 breakdown JSON](../results/organization_breakdown_comparison.json). 아래 bank read energy는 cache summary보다 높은 출력 정밀도지만 여전히 반올림된 값이다. Routing은 bank energy에 포함된 하위 항목이며 다시 더하면 안 된다. Per-subarray와 per-mat 값은 전체 접근 에너지가 아니므로 단순 합산하지 않는다.

| Run | Data subarray/mat 256→512 | Tag bank/mat 256→512 | Data bank read pJ 256→512 | Tag bank read pJ 256→512 | Data H-tree read pJ 256→512 |
|---|---|---|---:|---:|---:|
| L1_14nm | 2 x 2/256 Rows x 64 Columns → 2 x 2/256 Rows x 64 Columns | 32 x 1/8 Rows x 144 Columns → 32 x 4/8 Rows x 40 Columns | 35.615 → 68.252 | 2.318 → 5.394 | 25.547 → 48.115 |
| L1_7nm | 2 x 2/256 Rows x 64 Columns → 2 x 2/256 Rows x 64 Columns | 32 x 2/8 Rows x 72 Columns → 32 x 4/8 Rows x 40 Columns | 16.536 → 31.724 | 1.690 → 2.498 | 10.791 → 20.236 |
| L1_5nm | 2 x 2/256 Rows x 64 Columns → 2 x 2/256 Rows x 64 Columns | 32 x 2/8 Rows x 72 Columns → 32 x 2/8 Rows x 40 Columns | 15.635 → 29.970 | 1.488 → 1.701 | 10.551 → 19.801 |
| L1_3nm | 2 x 2/256 Rows x 64 Columns → 2 x 2/256 Rows x 64 Columns | 32 x 4/8 Rows x 40 Columns → 64 x 2/2 Rows x 72 Columns | 12.843 → 24.615 | 2.270 → 1.310 | 8.419 → 15.767 |
| L1_14nm_ReadEnergy | 2 x 1/256 Rows x 128 Columns → 2 x 1/256 Rows x 128 Columns | 4 x 1/32 Rows x 288 Columns → 2 x 1/32 Rows x 288 Columns | 33.452 → 65.026 | 1.413 → 1.326 | 23.637 → 45.396 |
| L1_7nm_ReadEnergy | 2 x 1/256 Rows x 128 Columns → 2 x 1/256 Rows x 128 Columns | 4 x 1/32 Rows x 288 Columns → 8 x 1/8 Rows x 288 Columns | 15.651 → 30.547 | 0.831 → 0.782 | 10.059 → 19.364 |
| L1_5nm_ReadEnergy | 2 x 1/256 Rows x 128 Columns → 2 x 1/256 Rows x 128 Columns | 4 x 1/32 Rows x 288 Columns → 8 x 1/8 Rows x 288 Columns | 14.554 → 28.367 | 0.715 → 0.670 | 9.600 → 18.458 |
| L1_3nm_ReadEnergy | 2 x 1/256 Rows x 128 Columns → 2 x 1/256 Rows x 128 Columns | 4 x 1/32 Rows x 288 Columns → 8 x 1/8 Rows x 288 Columns | 12.242 → 23.883 | 0.620 → 0.576 | 7.929 → 15.257 |
| L2_14nm | 2 x 2/512 Rows x 256 Columns → 2 x 2/512 Rows x 256 Columns | 16 x 1/64 Rows x 272 Columns → 16 x 1/64 Rows x 144 Columns | 98.371 → 193.429 | 4.849 → 5.951 | 73.272 → 143.231 |
| L2_7nm | 2 x 2/512 Rows x 256 Columns → 2 x 2/512 Rows x 256 Columns | 16 x 1/64 Rows x 272 Columns → 16 x 1/32 Rows x 272 Columns | 43.178 → 84.977 | 2.804 → 2.155 | 28.689 → 55.997 |
| L2_5nm | 2 x 2/512 Rows x 256 Columns → 2 x 2/512 Rows x 256 Columns | 32 x 1/32 Rows x 272 Columns → 64 x 1/8 Rows x 272 Columns | 40.056 → 78.814 | 3.455 → 2.924 | 27.056 → 52.815 |
| L2_3nm | 2 x 2/512 Rows x 256 Columns → 2 x 2/512 Rows x 256 Columns | 32 x 1/32 Rows x 272 Columns → 64 x 4/8 Rows x 80 Columns | 34.476 → 67.833 | 3.001 → 7.113 | 22.994 → 44.868 |
| L2_14nm_ReadEnergy | 2 x 1/512 Rows x 512 Columns → 2 x 1/512 Rows x 512 Columns | 8 x 1/64 Rows x 544 Columns → 8 x 1/32 Rows x 544 Columns | 95.382 → 188.584 | 2.946 → 2.696 | 70.651 → 139.122 |
| L2_7nm_ReadEnergy | 2 x 1/512 Rows x 512 Columns → 2 x 1/512 Rows x 512 Columns | 16 x 1/32 Rows x 544 Columns → 8 x 1/32 Rows x 544 Columns | 41.287 → 81.845 | 1.771 → 1.611 | 27.059 → 53.390 |
| L2_5nm_ReadEnergy | 2 x 1/512 Rows x 512 Columns → 2 x 1/512 Rows x 512 Columns | 16 x 1/32 Rows x 544 Columns → 8 x 1/32 Rows x 544 Columns | 37.820 → 74.954 | 1.536 → 1.386 | 25.035 → 49.385 |
| L2_3nm_ReadEnergy | 2 x 1/512 Rows x 512 Columns → 2 x 1/512 Rows x 512 Columns | 16 x 1/32 Rows x 544 Columns → 8 x 1/32 Rows x 544 Columns | 33.189 → 65.791 | 1.329 → 1.204 | 21.898 → 43.209 |

### Tag / routing 비중: 중복 없는 bank 기준

[Read/Write 32개 component 비교 CSV](../results/breakdown_width_comparison.csv). `bank_total=data_bank+tag_bank`, `tag_share=tag_bank/bank_total`, `routing_share=(data_Htree+tag_Htree)/bank_total`, `nonrouting_residual=bank_total−routing`. Routing share와 tag share는 서로 겹치므로 더하지 않는다. Residual은 cell-only가 아니다.
- 관측: 256bit read에서 tag bank 비중 3.00–15.02%, routing 비중 61.45–73.18%. 분모는 출력된 두 bank의 합이다.
- 관측: 512bit read에서 tag bank 비중 1.41–9.49%, routing 비중 62.01–73.47%. 분모는 출력된 두 bank의 합이다.
- 관측: 256bit write에서 tag bank 비중 2.00–16.98%, routing 비중 84.59–93.30%. 분모는 출력된 두 bank의 합이다.
- 관측: 512bit write에서 tag bank 비중 0.93–11.77%, routing 비중 85.48–93.87%. 분모는 출력된 두 bank의 합이다.

구체적 사례: L1/14nm/ReadLatency의 data subarray/mat 형태는 두 폭에서 같지만 tag bank와 mat는 달라진다. Data bank read는 68.252→35.615pJ(512→256), tag는 5.394→2.318pJ, data H-tree는 48.115→25.547pJ다. 같은 data 조직 표기에서도 활성 bit 수·wire load가 달라지므로 energy가 정확히 반감되지 않는다. 이 수치는 관측이며, 개별 transistor/셀 기여의 인과 분해를 완료한 것은 아니다.

- 확인된 모델 구조: WordWidth 변경은 출력 데이터 폭만 줄이지 않고 cache line/line 수/tag array capacity와 wire broadcast/distribute bit 수에도 영향을 준다. 태그와 주변 회로의 overhead는 payload bit 수에 비례하지 않는다.
- 관측: 위 표와 JSON에서 선택 조직 및 라우팅·bank energy의 변화 여부를 직접 비교할 수 있다. Optimizer가 독립적으로 재선택한 tag bank/mat/mux/buffer 변화와 고정/공유 overhead가 비선형성을 설명할 수 있다.
- 가설과 한계: 개별 회로의 인과 기여율은 고정 조직 대조 실험 없이 확정하지 않는다. tag+data는 cache-hit 식에서 합산되지만 summary는 1pJ 간격이라 세부 pJ 합과 미세하게 다를 수 있다. Routing/peripheral/cell 분해는 겹치는 계층이며 전체를 서로 배타적인 기여도로 제시하지 않는다.
- Width별 SF 차이는 상대 overhead와 재최적화 조직 변화가 node마다 달라 생길 수 있다. 전압·cell 모델 차이도 남아 있으므로 어느 폭의 SF도 Pure Process Scaling이 아니다.

## 재현성·정규화·결론

새 7nm 실행 4개의 6개 지표는 기존 Phase 1 256bit 실행과 4/4 일치했다. [기존 로그와의 비교](../results/phase1_7nm_replay_comparison.csv).
`E_NS_bit=E_NS_access/256`, `E_GPU_sector=E_GPU_bit×256`은 단위 정렬이다. 동일한 물리 경계라는 뜻이 아니다. GPU read/write·hit/miss counter, multi-sector tag 재사용, coalescing/replay, miss fill/writeback 및 energy coefficient의 측정/회귀 경계를 먼저 확인해야 한다.
내부 GPU 계수·실측 에너지·회사 자료·비공개 검증 결과는 사용하거나 저장하지 않았다. GPU sector 구조의 근거/미확인 사항과 Phase 2-B 제안은 [feasibility 보고서](gpu_sector_modeling_feasibility.md)를 따른다.
