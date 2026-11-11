# Scaling Matrix 계산 근거

두 Matrix의 각 24개 SF를 raw stdout과 configuration에 연결한다. 새로운 실험이나 추정값을 생성하지 않았다. As-Reconstructed Input은 기존 16개 재현 실행만 사용한다. Width-Aligned는 7nm만 별도 512bit 진단으로 선택하며 나머지는 같은 재현 실행을 재사용한다. 원래의 16개 실행을 별도 진단으로 대체하지 않는다.

## 수식과 정밀도

`E_pJ/access = stdout의 nJ/access × 1000`; `SF(a→b)=E_b/E_a`; `감소율(%)=100×(1−SF)`. Read/Write, L1/L2, 두 optimization을 각각 독립 계산했다. SF는 무차원이다. CSV는 반올림된 출력의 Decimal 비율을 보관하고 본문 Matrix는 소수점 넷째 자리로 표시한다. 두 CSV 모두 raw log의 Decimal 값에서 자동 재계산한다. 이전 float 표현과 끝자리 표현 차이가 있을 수 있지만 기초 energy와 SF의 의미는 같다. 출력 간격 0.001nJ=1pJ에 따른 정밀도 한계가 있으며 SF의 유효 정확도가 소수점 넷째 자리라는 뜻은 아니다.
`ΔSF = Width-Aligned − As-Reconstructed`; `상대변화(%)=100×(Width-Aligned/As-Reconstructed−1)`.

## 선택한 실행과 Configuration

S-는 원래 재현 실행, D-는 별도 512bit 진단 실행이다. 각 실행의 종료 코드·Finished!·configuration/cell/stdout/stderr SHA-256을 기존 metadata와 대조했다. CSV에는 SF 양 끝의 config/log/metadata 경로와 config/log 해시도 기록했다.

| Source ID | Width bit | Read pJ/access | Write pJ/access | Configuration | Raw stdout | Metadata |
|---|---:|---:|---:|---|---|---|
| <a id='d-l1_7nm'></a>D-L1_7nm | 512 | 34.000 | 25.000 | [cfg](../configs/diagnostic_512bit/L1_7nm.cfg) | [stdout](../logs/diagnostic_512bit/L1_7nm/20261111T021548.654557Z/stdout.log) | [metadata](../logs/diagnostic_512bit/L1_7nm/20261111T021548.654557Z/metadata.json) |
| <a id='d-l1_7nm_readenergy'></a>D-L1_7nm_ReadEnergy | 512 | 31.000 | 23.000 | [cfg](../configs/diagnostic_512bit/L1_7nm_ReadEnergy.cfg) | [stdout](../logs/diagnostic_512bit/L1_7nm_ReadEnergy/20261111T021548.654632Z/stdout.log) | [metadata](../logs/diagnostic_512bit/L1_7nm_ReadEnergy/20261111T021548.654632Z/metadata.json) |
| <a id='d-l2_7nm'></a>D-L2_7nm | 512 | 87.000 | 63.000 | [cfg](../configs/diagnostic_512bit/L2_7nm.cfg) | [stdout](../logs/diagnostic_512bit/L2_7nm/20261111T021559.405221Z/stdout.log) | [metadata](../logs/diagnostic_512bit/L2_7nm/20261111T021559.405221Z/metadata.json) |
| <a id='d-l2_7nm_readenergy'></a>D-L2_7nm_ReadEnergy | 512 | 83.000 | 59.000 | [cfg](../configs/diagnostic_512bit/L2_7nm_ReadEnergy.cfg) | [stdout](../logs/diagnostic_512bit/L2_7nm_ReadEnergy/20261111T021559.763894Z/stdout.log) | [metadata](../logs/diagnostic_512bit/L2_7nm_ReadEnergy/20261111T021559.763894Z/metadata.json) |
| <a id='s-l1_14nm'></a>S-L1_14nm | 512 | 74.000 | 58.000 | [cfg](../configs/study_reconstructed/L1_14nm.cfg) | [stdout](../logs/new/L1_14nm/20261111T021209.801549Z/stdout.log) | [metadata](../logs/new/L1_14nm/20261111T021209.801549Z/metadata.json) |
| <a id='s-l1_14nm_readenergy'></a>S-L1_14nm_ReadEnergy | 512 | 66.000 | 51.000 | [cfg](../configs/study_reconstructed/L1_14nm_ReadEnergy.cfg) | [stdout](../logs/new/L1_14nm_ReadEnergy/20261111T021246.382768Z/stdout.log) | [metadata](../logs/new/L1_14nm_ReadEnergy/20261111T021246.382768Z/metadata.json) |
| <a id='s-l1_3nm'></a>S-L1_3nm | 512 | 26.000 | 19.000 | [cfg](../configs/study_reconstructed/L1_3nm.cfg) | [stdout](../logs/new/L1_3nm/20261111T021246.385146Z/stdout.log) | [metadata](../logs/new/L1_3nm/20261111T021246.385146Z/metadata.json) |
| <a id='s-l1_3nm_readenergy'></a>S-L1_3nm_ReadEnergy | 512 | 24.000 | 18.000 | [cfg](../configs/study_reconstructed/L1_3nm_ReadEnergy.cfg) | [stdout](../logs/new/L1_3nm_ReadEnergy/20261111T021258.940138Z/stdout.log) | [metadata](../logs/new/L1_3nm_ReadEnergy/20261111T021258.940138Z/metadata.json) |
| <a id='s-l1_5nm'></a>S-L1_5nm | 512 | 32.000 | 24.000 | [cfg](../configs/study_reconstructed/L1_5nm.cfg) | [stdout](../logs/new/L1_5nm/20261111T021259.442309Z/stdout.log) | [metadata](../logs/new/L1_5nm/20261111T021259.442309Z/metadata.json) |
| <a id='s-l1_5nm_readenergy'></a>S-L1_5nm_ReadEnergy | 512 | 29.000 | 21.000 | [cfg](../configs/study_reconstructed/L1_5nm_ReadEnergy.cfg) | [stdout](../logs/new/L1_5nm_ReadEnergy/20261111T021311.306906Z/stdout.log) | [metadata](../logs/new/L1_5nm_ReadEnergy/20261111T021311.306906Z/metadata.json) |
| <a id='s-l1_7nm'></a>S-L1_7nm | 256 | 18.000 | 14.000 | [cfg](../configs/study_reconstructed/L1_7nm.cfg) | [stdout](../logs/new/L1_7nm/20261111T021312.264165Z/stdout.log) | [metadata](../logs/new/L1_7nm/20261111T021312.264165Z/metadata.json) |
| <a id='s-l1_7nm_readenergy'></a>S-L1_7nm_ReadEnergy | 256 | 16.000 | 12.000 | [cfg](../configs/study_reconstructed/L1_7nm_ReadEnergy.cfg) | [stdout](../logs/new/L1_7nm_ReadEnergy/20261111T021324.523014Z/stdout.log) | [metadata](../logs/new/L1_7nm_ReadEnergy/20261111T021324.523014Z/metadata.json) |
| <a id='s-l2_14nm'></a>S-L2_14nm | 512 | 199.000 | 156.000 | [cfg](../configs/study_reconstructed/L2_14nm.cfg) | [stdout](../logs/new/L2_14nm/20261111T021329.639043Z/stdout.log) | [metadata](../logs/new/L2_14nm/20261111T021329.639043Z/metadata.json) |
| <a id='s-l2_14nm_readenergy'></a>S-L2_14nm_ReadEnergy | 512 | 191.000 | 149.000 | [cfg](../configs/study_reconstructed/L2_14nm_ReadEnergy.cfg) | [stdout](../logs/new/L2_14nm_ReadEnergy/20261111T021342.346075Z/stdout.log) | [metadata](../logs/new/L2_14nm_ReadEnergy/20261111T021342.346075Z/metadata.json) |
| <a id='s-l2_3nm'></a>S-L2_3nm | 512 | 75.000 | 55.000 | [cfg](../configs/study_reconstructed/L2_3nm.cfg) | [stdout](../logs/new/L2_3nm/20261111T021400.697064Z/stdout.log) | [metadata](../logs/new/L2_3nm/20261111T021400.697064Z/metadata.json) |
| <a id='s-l2_3nm_readenergy'></a>S-L2_3nm_ReadEnergy | 512 | 67.000 | 47.000 | [cfg](../configs/study_reconstructed/L2_3nm_ReadEnergy.cfg) | [stdout](../logs/new/L2_3nm_ReadEnergy/20261111T021412.092928Z/stdout.log) | [metadata](../logs/new/L2_3nm_ReadEnergy/20261111T021412.092928Z/metadata.json) |
| <a id='s-l2_5nm'></a>S-L2_5nm | 512 | 82.000 | 59.000 | [cfg](../configs/study_reconstructed/L2_5nm.cfg) | [stdout](../logs/new/L2_5nm/20261111T021430.245271Z/stdout.log) | [metadata](../logs/new/L2_5nm/20261111T021430.245271Z/metadata.json) |
| <a id='s-l2_5nm_readenergy'></a>S-L2_5nm_ReadEnergy | 512 | 76.000 | 54.000 | [cfg](../configs/study_reconstructed/L2_5nm_ReadEnergy.cfg) | [stdout](../logs/new/L2_5nm_ReadEnergy/20261111T021442.501285Z/stdout.log) | [metadata](../logs/new/L2_5nm_ReadEnergy/20261111T021442.501285Z/metadata.json) |
| <a id='s-l2_7nm'></a>S-L2_7nm | 256 | 46.000 | 33.000 | [cfg](../configs/study_reconstructed/L2_7nm.cfg) | [stdout](../logs/new/L2_7nm/20261111T021505.430977Z/stdout.log) | [metadata](../logs/new/L2_7nm/20261111T021505.430977Z/metadata.json) |
| <a id='s-l2_7nm_readenergy'></a>S-L2_7nm_ReadEnergy | 256 | 43.000 | 30.000 | [cfg](../configs/study_reconstructed/L2_7nm_ReadEnergy.cfg) | [stdout](../logs/new/L2_7nm_ReadEnergy/20261111T021517.121198Z/stdout.log) | [metadata](../logs/new/L2_7nm_ReadEnergy/20261111T021517.121198Z/metadata.json) |

## As-Reconstructed Input — SF 계산 24개

| Cache | Objective | Energy | Transition | Formula (pJ/access ÷ pJ/access) | From source | To source |
|---|---|---|---|---|---|---|
| <a id='as-l1-lat-read-14-7'></a>L1 | ReadLatency | Read | 14→7 | 18.000 / 74.000 = 0.24324324 | [S-L1_14nm](#s-l1_14nm) | [S-L1_7nm](#s-l1_7nm) |
| <a id='as-l1-lat-read-7-5'></a>L1 | ReadLatency | Read | 7→5 | 32.000 / 18.000 = 1.77777778 | [S-L1_7nm](#s-l1_7nm) | [S-L1_5nm](#s-l1_5nm) |
| <a id='as-l1-lat-read-5-3'></a>L1 | ReadLatency | Read | 5→3 | 26.000 / 32.000 = 0.81250000 | [S-L1_5nm](#s-l1_5nm) | [S-L1_3nm](#s-l1_3nm) |
| <a id='as-l1-lat-write-14-7'></a>L1 | ReadLatency | Write | 14→7 | 14.000 / 58.000 = 0.24137931 | [S-L1_14nm](#s-l1_14nm) | [S-L1_7nm](#s-l1_7nm) |
| <a id='as-l1-lat-write-7-5'></a>L1 | ReadLatency | Write | 7→5 | 24.000 / 14.000 = 1.71428571 | [S-L1_7nm](#s-l1_7nm) | [S-L1_5nm](#s-l1_5nm) |
| <a id='as-l1-lat-write-5-3'></a>L1 | ReadLatency | Write | 5→3 | 19.000 / 24.000 = 0.79166667 | [S-L1_5nm](#s-l1_5nm) | [S-L1_3nm](#s-l1_3nm) |
| <a id='as-l1-energy-read-14-7'></a>L1 | ReadDynamicEnergy | Read | 14→7 | 16.000 / 66.000 = 0.24242424 | [S-L1_14nm_ReadEnergy](#s-l1_14nm_readenergy) | [S-L1_7nm_ReadEnergy](#s-l1_7nm_readenergy) |
| <a id='as-l1-energy-read-7-5'></a>L1 | ReadDynamicEnergy | Read | 7→5 | 29.000 / 16.000 = 1.81250000 | [S-L1_7nm_ReadEnergy](#s-l1_7nm_readenergy) | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) |
| <a id='as-l1-energy-read-5-3'></a>L1 | ReadDynamicEnergy | Read | 5→3 | 24.000 / 29.000 = 0.82758621 | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) | [S-L1_3nm_ReadEnergy](#s-l1_3nm_readenergy) |
| <a id='as-l1-energy-write-14-7'></a>L1 | ReadDynamicEnergy | Write | 14→7 | 12.000 / 51.000 = 0.23529412 | [S-L1_14nm_ReadEnergy](#s-l1_14nm_readenergy) | [S-L1_7nm_ReadEnergy](#s-l1_7nm_readenergy) |
| <a id='as-l1-energy-write-7-5'></a>L1 | ReadDynamicEnergy | Write | 7→5 | 21.000 / 12.000 = 1.75000000 | [S-L1_7nm_ReadEnergy](#s-l1_7nm_readenergy) | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) |
| <a id='as-l1-energy-write-5-3'></a>L1 | ReadDynamicEnergy | Write | 5→3 | 18.000 / 21.000 = 0.85714286 | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) | [S-L1_3nm_ReadEnergy](#s-l1_3nm_readenergy) |
| <a id='as-l2-lat-read-14-7'></a>L2 | ReadLatency | Read | 14→7 | 46.000 / 199.000 = 0.23115578 | [S-L2_14nm](#s-l2_14nm) | [S-L2_7nm](#s-l2_7nm) |
| <a id='as-l2-lat-read-7-5'></a>L2 | ReadLatency | Read | 7→5 | 82.000 / 46.000 = 1.78260870 | [S-L2_7nm](#s-l2_7nm) | [S-L2_5nm](#s-l2_5nm) |
| <a id='as-l2-lat-read-5-3'></a>L2 | ReadLatency | Read | 5→3 | 75.000 / 82.000 = 0.91463415 | [S-L2_5nm](#s-l2_5nm) | [S-L2_3nm](#s-l2_3nm) |
| <a id='as-l2-lat-write-14-7'></a>L2 | ReadLatency | Write | 14→7 | 33.000 / 156.000 = 0.21153846 | [S-L2_14nm](#s-l2_14nm) | [S-L2_7nm](#s-l2_7nm) |
| <a id='as-l2-lat-write-7-5'></a>L2 | ReadLatency | Write | 7→5 | 59.000 / 33.000 = 1.78787879 | [S-L2_7nm](#s-l2_7nm) | [S-L2_5nm](#s-l2_5nm) |
| <a id='as-l2-lat-write-5-3'></a>L2 | ReadLatency | Write | 5→3 | 55.000 / 59.000 = 0.93220339 | [S-L2_5nm](#s-l2_5nm) | [S-L2_3nm](#s-l2_3nm) |
| <a id='as-l2-energy-read-14-7'></a>L2 | ReadDynamicEnergy | Read | 14→7 | 43.000 / 191.000 = 0.22513089 | [S-L2_14nm_ReadEnergy](#s-l2_14nm_readenergy) | [S-L2_7nm_ReadEnergy](#s-l2_7nm_readenergy) |
| <a id='as-l2-energy-read-7-5'></a>L2 | ReadDynamicEnergy | Read | 7→5 | 76.000 / 43.000 = 1.76744186 | [S-L2_7nm_ReadEnergy](#s-l2_7nm_readenergy) | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) |
| <a id='as-l2-energy-read-5-3'></a>L2 | ReadDynamicEnergy | Read | 5→3 | 67.000 / 76.000 = 0.88157895 | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) | [S-L2_3nm_ReadEnergy](#s-l2_3nm_readenergy) |
| <a id='as-l2-energy-write-14-7'></a>L2 | ReadDynamicEnergy | Write | 14→7 | 30.000 / 149.000 = 0.20134228 | [S-L2_14nm_ReadEnergy](#s-l2_14nm_readenergy) | [S-L2_7nm_ReadEnergy](#s-l2_7nm_readenergy) |
| <a id='as-l2-energy-write-7-5'></a>L2 | ReadDynamicEnergy | Write | 7→5 | 54.000 / 30.000 = 1.80000000 | [S-L2_7nm_ReadEnergy](#s-l2_7nm_readenergy) | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) |
| <a id='as-l2-energy-write-5-3'></a>L2 | ReadDynamicEnergy | Write | 5→3 | 47.000 / 54.000 = 0.87037037 | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) | [S-L2_3nm_ReadEnergy](#s-l2_3nm_readenergy) |

## Width-Aligned — SF 계산 24개

| Cache | Objective | Energy | Transition | Formula (pJ/access ÷ pJ/access) | From source | To source |
|---|---|---|---|---|---|---|
| <a id='wa-l1-lat-read-14-7'></a>L1 | ReadLatency | Read | 14→7 | 34.000 / 74.000 = 0.45945946 | [S-L1_14nm](#s-l1_14nm) | [D-L1_7nm](#d-l1_7nm) |
| <a id='wa-l1-lat-read-7-5'></a>L1 | ReadLatency | Read | 7→5 | 32.000 / 34.000 = 0.94117647 | [D-L1_7nm](#d-l1_7nm) | [S-L1_5nm](#s-l1_5nm) |
| <a id='wa-l1-lat-read-5-3'></a>L1 | ReadLatency | Read | 5→3 | 26.000 / 32.000 = 0.81250000 | [S-L1_5nm](#s-l1_5nm) | [S-L1_3nm](#s-l1_3nm) |
| <a id='wa-l1-lat-write-14-7'></a>L1 | ReadLatency | Write | 14→7 | 25.000 / 58.000 = 0.43103448 | [S-L1_14nm](#s-l1_14nm) | [D-L1_7nm](#d-l1_7nm) |
| <a id='wa-l1-lat-write-7-5'></a>L1 | ReadLatency | Write | 7→5 | 24.000 / 25.000 = 0.96000000 | [D-L1_7nm](#d-l1_7nm) | [S-L1_5nm](#s-l1_5nm) |
| <a id='wa-l1-lat-write-5-3'></a>L1 | ReadLatency | Write | 5→3 | 19.000 / 24.000 = 0.79166667 | [S-L1_5nm](#s-l1_5nm) | [S-L1_3nm](#s-l1_3nm) |
| <a id='wa-l1-energy-read-14-7'></a>L1 | ReadDynamicEnergy | Read | 14→7 | 31.000 / 66.000 = 0.46969697 | [S-L1_14nm_ReadEnergy](#s-l1_14nm_readenergy) | [D-L1_7nm_ReadEnergy](#d-l1_7nm_readenergy) |
| <a id='wa-l1-energy-read-7-5'></a>L1 | ReadDynamicEnergy | Read | 7→5 | 29.000 / 31.000 = 0.93548387 | [D-L1_7nm_ReadEnergy](#d-l1_7nm_readenergy) | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) |
| <a id='wa-l1-energy-read-5-3'></a>L1 | ReadDynamicEnergy | Read | 5→3 | 24.000 / 29.000 = 0.82758621 | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) | [S-L1_3nm_ReadEnergy](#s-l1_3nm_readenergy) |
| <a id='wa-l1-energy-write-14-7'></a>L1 | ReadDynamicEnergy | Write | 14→7 | 23.000 / 51.000 = 0.45098039 | [S-L1_14nm_ReadEnergy](#s-l1_14nm_readenergy) | [D-L1_7nm_ReadEnergy](#d-l1_7nm_readenergy) |
| <a id='wa-l1-energy-write-7-5'></a>L1 | ReadDynamicEnergy | Write | 7→5 | 21.000 / 23.000 = 0.91304348 | [D-L1_7nm_ReadEnergy](#d-l1_7nm_readenergy) | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) |
| <a id='wa-l1-energy-write-5-3'></a>L1 | ReadDynamicEnergy | Write | 5→3 | 18.000 / 21.000 = 0.85714286 | [S-L1_5nm_ReadEnergy](#s-l1_5nm_readenergy) | [S-L1_3nm_ReadEnergy](#s-l1_3nm_readenergy) |
| <a id='wa-l2-lat-read-14-7'></a>L2 | ReadLatency | Read | 14→7 | 87.000 / 199.000 = 0.43718593 | [S-L2_14nm](#s-l2_14nm) | [D-L2_7nm](#d-l2_7nm) |
| <a id='wa-l2-lat-read-7-5'></a>L2 | ReadLatency | Read | 7→5 | 82.000 / 87.000 = 0.94252874 | [D-L2_7nm](#d-l2_7nm) | [S-L2_5nm](#s-l2_5nm) |
| <a id='wa-l2-lat-read-5-3'></a>L2 | ReadLatency | Read | 5→3 | 75.000 / 82.000 = 0.91463415 | [S-L2_5nm](#s-l2_5nm) | [S-L2_3nm](#s-l2_3nm) |
| <a id='wa-l2-lat-write-14-7'></a>L2 | ReadLatency | Write | 14→7 | 63.000 / 156.000 = 0.40384615 | [S-L2_14nm](#s-l2_14nm) | [D-L2_7nm](#d-l2_7nm) |
| <a id='wa-l2-lat-write-7-5'></a>L2 | ReadLatency | Write | 7→5 | 59.000 / 63.000 = 0.93650794 | [D-L2_7nm](#d-l2_7nm) | [S-L2_5nm](#s-l2_5nm) |
| <a id='wa-l2-lat-write-5-3'></a>L2 | ReadLatency | Write | 5→3 | 55.000 / 59.000 = 0.93220339 | [S-L2_5nm](#s-l2_5nm) | [S-L2_3nm](#s-l2_3nm) |
| <a id='wa-l2-energy-read-14-7'></a>L2 | ReadDynamicEnergy | Read | 14→7 | 83.000 / 191.000 = 0.43455497 | [S-L2_14nm_ReadEnergy](#s-l2_14nm_readenergy) | [D-L2_7nm_ReadEnergy](#d-l2_7nm_readenergy) |
| <a id='wa-l2-energy-read-7-5'></a>L2 | ReadDynamicEnergy | Read | 7→5 | 76.000 / 83.000 = 0.91566265 | [D-L2_7nm_ReadEnergy](#d-l2_7nm_readenergy) | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) |
| <a id='wa-l2-energy-read-5-3'></a>L2 | ReadDynamicEnergy | Read | 5→3 | 67.000 / 76.000 = 0.88157895 | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) | [S-L2_3nm_ReadEnergy](#s-l2_3nm_readenergy) |
| <a id='wa-l2-energy-write-14-7'></a>L2 | ReadDynamicEnergy | Write | 14→7 | 59.000 / 149.000 = 0.39597315 | [S-L2_14nm_ReadEnergy](#s-l2_14nm_readenergy) | [D-L2_7nm_ReadEnergy](#d-l2_7nm_readenergy) |
| <a id='wa-l2-energy-write-7-5'></a>L2 | ReadDynamicEnergy | Write | 7→5 | 54.000 / 59.000 = 0.91525424 | [D-L2_7nm_ReadEnergy](#d-l2_7nm_readenergy) | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) |
| <a id='wa-l2-energy-write-5-3'></a>L2 | ReadDynamicEnergy | Write | 5→3 | 47.000 / 54.000 = 0.87037037 | [S-L2_5nm_ReadEnergy](#s-l2_5nm_readenergy) | [S-L2_3nm_ReadEnergy](#s-l2_3nm_readenergy) |

## CSV만으로 재계산 / 검증

각 CSV 행의 from_log/to_log에서 해당 cache summary의 Read 또는 Write Dynamic Energy를 추출해 ×1000하고, to/from을 계산하면 scaling_factor가 된다. from_config/to_config의 WordWidth 및 metadata 해시와 함께 확인할 수 있다. 첫 Matrix는 7nm만 256bit이며, 두 번째는 양 끝 모두 512bit다. scaling_matrix_comparison.csv는 두 CSV의 (cache, optimization, metric, from_nm, to_nm) 키를 대응시킨 차이다.

## 해석 제한

**Width-Aligned Scaling은 Pure Process Scaling이 아니다.** 폭만 정렬했으며 node별 Voltage, Cell Parameters 및 재최적화된 Internal Cache Organization은 동일하지 않다. 이것은 기존 실행을 조합한 모델 내 비교이고 historical 원본 설정 복구나 NVIDIA GPU 측정 검증이 아니다.
