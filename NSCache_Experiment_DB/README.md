# NS-Cache Phase 1 — reproduction and validation

NVIDIA GPU 세대 간 에너지 연구를 위한 후보 모델 검토 단계다. 여기의 결과는 generic SRAM/cache 모델값이며 실제 GPU 측정값 또는 검증된 process-only scaling이 아니다. Rubin 최종 예측은 수행하지 않는다.

**현재 결론:** 재구성 입력 16개를 모두 새로 실행했고 12개는 기록값의 6개 지표와 일치했다. 7nm 4개는 불일치한다. 이 입력들만 폭이 256bit이고 다른 공정은 512bit다. 원본을 유지한 별도 512bit 진단 4건은 모두 6개 기록 지표와 정확히 일치했다. 이는 불일치 원인을 설명하지만 historical 원본 복구를 의미하지 않는다.

## 두 Scaling Matrix

- **[As-Reconstructed Input Scaling Matrix](reports/process_scaling_analysis.md#as-reconstructed-input-scaling-matrix)**: 기존 16개 재현 실행을 보존한다. 7nm=256bit, 나머지=512bit. [24개 SF CSV](results/scaling.csv).
- **[Width-Aligned Scaling Matrix](reports/process_scaling_analysis.md#width-aligned-scaling-matrix)**: 7nm만 별도 512bit 진단으로 선택하고, 다른 공정의 기존 512bit 실행과 조합한다. [24개 SF CSV](results/scaling_width_aligned.csv).
- [Matrix 차이 24개](results/scaling_matrix_comparison.csv)와 [각 SF의 raw log·configuration·수식 근거](reports/scaling_matrix_traceability.md)를 제공한다. L1/L2, ReadLatency/ReadDynamicEnergy, Read/Write를 분리했다. `SF(a→b)=E_b/E_a`, energy 단위는 pJ/access다.

혼합 폭에서는 7→5 SF가 모두 1보다 크지만, 512bit 정렬 후에는 모두 1보다 작다. 5→3은 두 Matrix에서 동일하다. 정렬하더라도 **Voltage, Cell Parameters, Internal Cache Organization이 달라 Pure Process Scaling이 아니다.** 새로운 재현성 성공 판정, historical 원본 복구 또는 GPU 실측 검증으로 간주하지 않는다.

`scripts/analyze.py`는 두 Matrix, 차이 CSV, Traceability, 진단 summary를 모두 **20개 raw log에서 자동 재생성**한다. 기존 분석 CSV/JSON을 입력값으로 읽지 않는다. 설정·cell·stdout/stderr 해시, 종료 상태, width/node/objective, 실행 metadata의 공통 binary identity를 검증한 후 결과를 쓴다. 로컬 binary나 새 빌드는 재분석에 필요 없다. 두 번 연속 실행한 12개 생성 파일이 byte 단위로 같음을 검증했다.

Exit code: `0`은 모든 재현 비교 일치, `1`은 현재 데이터의 7nm 4개 기록 불일치, `2`는 누락·손상·미완료 raw 입력이다. Exit 2에서는 기존 생성 결과를 덮어쓰지 않는다. 새 Matrix가 추가돼도 원래 12/16 재현성 판정은 유지된다.

파일을 변경한 뒤 `python3 scripts/snapshot_manifest.py`로 manifest·전체 inventory·변경 파일 목록을 갱신하고 `python3 scripts/snapshot_manifest.py --check`로 검증한다(DB 디렉터리 기준). 경로는 DB 기준이며 저장소 루트 README·AGENTS·.gitignore·원본 ZIP은 `../` 경로로 포함한다. SHA manifest 자신은 해시 대상에서 제외하고, inventory에는 manifest와 inventory 자신을 포함한다. 무시된 build/runtime/cache는 제외한다. `--base origin/main`은 변경 파일 목록의 기준이다. 해당 remote ref가 없는 checkout에서는 먼저 `git fetch origin main:refs/remotes/origin/main`을 실행하거나 `--base <검증한 base SHA>`를 지정한다.

## 구조 및 출처

| Directory | Content / origin |
|---|---|
| `source/` | 복구 C++/Makefile 54개, 별도 확보한 upstream 라이선스 4개 |
| `configs/New_Configs/` | 복구 기본 config/cell |
| `configs/study_reconstructed/` | 재구성 입력 16개, ZIP과 byte 동일 |
| `configs/diagnostic_512bit/` | 새 one-factor 진단 입력 4개, 원본과 분리 |
| `logs/bundled/` | 기존 패키지 재실행 로그 5개, historical 원본 아님 |
| `logs/new/` | 이번 16개 실행의 stdout/stderr/metadata |
| `logs/diagnostic_512bit/` | 별도 진단 4개 실행 |
| `logs/build/` | 환경, 빌드 stdout/stderr, binary 해시 |
| `results/recorded/` | 기존 workbook 전사 CSV/JSON, raw 측정 아님 |
| `results/` | 새 파싱, 비교, scaling, 설정 감사, trade-off |
| `scripts/` | 새 빌드·재개·감사·검증 코드 |
| `scripts/bundled/` | ZIP의 기존 스크립트 byte 보존본; 이전 경로용, 새 워크플로에 사용하지 않음 |
| `reports/` | 재현성/공정 scaling 보고서 |
| `provenance/` | ZIP mapping/SHA-256, upstream 비교, 출처와 변경 이력 |
| `build/`, `runtime/` | 무시되는 로컬 binary/object 및 실행 작업 공간 |

원본 ZIP은 저장소 루트에서 수정 없이 유지한다. `provenance/archive_manifest.csv`는 ZIP의 108개 모든 멤버를 새 경로와 연결한다. ZIP에 포함된 SHA256SUMS는 107개 항목이며 checksum 목록 파일 자체를 제외한다. historical 설정/16개 원본 로그와 원래 workbook 자체는 이 저장소에 없다. 기존 README의 고정 512bit 설명과 부분 실행 상태는 당시 문서로 보존했으며 현재 사실과 구분한다.

## 실행

GNU g++ 14.2.0, GNU make 4.4.1, Python 3.12.14, Linux x86-64에서 검증했다. Python 외부 패키지, 서버, 비밀키는 필요 없다. C++17 `-O3 -mtune=native -Wall`로 빌드한다. 소스/설정 변경 없이 경로만 Makefile의 target/OUTDIR override와 runtime symlink로 연결한다. CPU 동시 실행 기본값은 2개다.

저장소 루트에서:

```bash
python3 NSCache_Experiment_DB/scripts/audit_inputs.py
bash NSCache_Experiment_DB/scripts/build.sh
python3 NSCache_Experiment_DB/scripts/run_experiments.py --case L1_14nm
python3 NSCache_Experiment_DB/scripts/run_experiments.py --jobs 2
python3 NSCache_Experiment_DB/scripts/analyze.py
```

**현재 입력 기준 마지막 명령의 exit code는 1이다.** 실행 실패가 아니라 7nm 4개 기록 불일치가 검출되기 때문이다. 16개 실행은 각각 exit 0 및 Finished!를 확인했다. `results/comparison.csv`는 96개 지표 비교의 recorded/new/difference/tolerance/status를 제공한다. analyzer는 bundled 로그를 새 실행으로 대신 사용하지 않는다.

선택적 진단 및 코드 검증:

```bash
python3 NSCache_Experiment_DB/scripts/diagnose_width.py
python3 NSCache_Experiment_DB/scripts/analyze.py
python3 -m unittest discover -s NSCache_Experiment_DB/tests -v
```

재개 시 latest 완료 attempt의 config/cell/binary/stdout/stderr 해시가 일치하는 경우에만 실행을 생략한다. 실패/timeout은 attempt별로 보존하고 다음 호출에서 재시도한다. 기본 timeout=1800초이며 `--timeout`으로 바꿀 수 있다. 빌드 산출물은 Git에서 제외하므로 새 checkout에서는 먼저 build한다. `-mtune=native`로 빌드된 binary의 해시는 호스트/컴파일러에 따라 다를 수 있다. 각 실행 로그의 정밀도는 내부 계산 정밀도보다 낮다.

## 읽을 결과

- [재현성 검증 및 96개 지표 비교](reports/reproducibility_validation.md)
- [두 Read/Write Scaling Matrix, 조직 및 trade-off](reports/process_scaling_analysis.md)
- [SF별 raw log·configuration·수식 추적](reports/scaling_matrix_traceability.md)
- [최종 자동 재생성 검증](reports/analysis_regeneration_validation.md)
- [출처, 라이선스 및 누락 자료](provenance/README.md)
- [후속 연구 원칙](../AGENTS.md)

## 저작권 / 비상업적 사용

NeuroSim (NS)-Cache: Georgia Institute of Technology, Prof. Shimeng Yu's group. Upstream: https://github.com/neurosim/NS-Cache ; 검증 revision `2fdcbf093f806bc9a28964aca8402c42738d58e5`. `source/LICENSE`의 CC Attribution–NonCommercial 4.0 및 copyright/disclaimer와 `LICENSE_CACTI3DD`, `LICENSE_DESTINY`, `LICENSE_NVSim`을 보존한다. 모델 소스는 상업적 사용을 허가하는 라이선스로 재지정하지 않는다. 연구/출판 인용은 `provenance/upstream_README.md`의 저자·논문·DOI를 따른다. 본 작업은 소스 모델을 수정하지 않고 데이터 정리·실행·분석 코드를 추가했다.
