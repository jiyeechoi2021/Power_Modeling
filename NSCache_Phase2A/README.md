# NS-Cache Phase 2-A — 256bit sweep / GPU sector alignment

Phase 1의 512bit 설정에서 WordWidth만 256bit로 바꾼 16개 입력을 **모두 새로 실행**했다. 소스, 원본 ZIP, Phase 1 configuration/log/result/report는 보존한다. 데이터는 NS-Cache 모델값이며 실제 NVIDIA GPU 실측, 물리 cell bit energy 또는 Pure Process Scaling이 아니다.

- [실행 결과·256bit Energy/SF Matrix·Table A/B·조직 분석](reports/phase2_256bit_energy_analysis.md)
- [GPU sector 표현 가능성, Q1–Q6, normalization와 Phase 2-B](reports/gpu_sector_modeling_feasibility.md)
- [설정 원본·diff·해시](provenance/configuration_derivation.json)
- [검증 및 보존 결과](reports/validation.md)

L1=128KiB/8-way, L2=1MiB/16-way, node=14/7/5/3nm, optimization=ReadLatency/ReadDynamicEnergy. 7nm의 새 입력도 Phase 1의 256bit 입력과 byte 동일하지만 이번 로그는 새로운 실행이다. Phase 1 Width-Aligned 비교 기준은 7nm만 별도 512bit 진단, 나머지 공정은 기존 512bit 재현 실행이다. GPU 비공개 계수/측정값은 포함하지 않았다.

## 경로

`configs/phase2_256bit/`: 16개 신규 입력. `logs/phase2_256bit/`: 실행별 attempt 디렉터리와 stdout/stderr/metadata/environment. `results/`: energy·SF·width 비교 CSV, data/tag 조직·printed energy breakdown JSON. `scripts/`: 준비·빌드·실행·raw 재분석·manifest. `provenance/`: 변환/보존/빌드/해시. `build/`, `runtime/`, `__pycache__/`는 ignored.

소스·cell·기본 parser는 `../NSCache_Experiment_DB/`를 읽기 전용으로 재사용한다. GNU g++ 14.2.0 / make 4.4.1 / Python 3.12.14, C++17 `-O3 -mtune=native -Wall`로 검증했다. 외부 Python 패키지나 GPU는 필요 없다. 두 실험군 binary SHA-256도 동일했다. upstream 및 inherited 비상업적 사용·저작권 고지는 [Phase 1 source/LICENSE](../NSCache_Experiment_DB/source/LICENSE)와 나머지 LICENSE_*를 그대로 따른다.

## 재실행

저장소 루트에서:

```bash
python3 NSCache_Phase2A/scripts/prepare.py
bash NSCache_Phase2A/scripts/build.sh
python3 NSCache_Phase2A/scripts/run.py --jobs 2
python3 NSCache_Phase2A/scripts/analyze.py
python3 -m unittest discover -s NSCache_Phase2A/tests -v
python3 NSCache_Phase2A/scripts/manifest.py
python3 NSCache_Phase2A/scripts/manifest.py --check
```

Raw log 재분석에는 build/binary가 필요 없다. 재개는 Phase 2 최신 attempt의 완료 상태와 config/cell/binary/stdout/stderr 해시가 같을 때만 허용한다. 과거 Phase 1 로그를 Phase 2 성공으로 대신 사용하지 않는다. `--timeout 1800` 기본값, `--case L1_14nm` 등으로 일부 실행도 가능하다. 실패/timeout도 attempt별로 보존한다. 빌드 로그를 갱신하더라도 기존 실행 디렉터리의 environment snapshot은 유지된다.

두 번 연속 분석한 생성 결과는 byte 동일하다. 원본 입력·로그는 변경하지 않으며 실패한/누락된 입력은 분석 전에 거부한다. `prepare.py`는 예상 외 기존 설정 파일을 덮어쓰지 않는다. 초기 빌드 environment의 generic build_command 필드에 대한 설명과 실제 명령은 [build_recipe.json](provenance/build_recipe.json)을 따른다.

## 식과 해석

`E_effective_bit=E_access/WordWidth`; `SF(a→b)=E_b/E_a`; `Reduction%=100×(1−SF)`. 비교 CSV에는 방향이 명확한 `E256/E512`와 역비를 모두 기록했다. 256bit 접근의 pJ/bit는 모델의 tag+data+peripheral 접근을 payload width로 나눈 effective 양이다.

NS-Cache WordWidth는 line 크기와 tag/data 조직에도 연결돼 있다. 따라서 32B model line access를 실제 GPU 128B line 내 32B sector transaction과 동등하다고 보지 않는다. Voltage, cell parameters, 선택 조직, hit/miss/write energy boundary도 별도 확인해야 한다. 공식 NVIDIA docs와 GitHub API는 이 환경에서 403으로 차단됐다. GPU 세대별 미확인 규격은 확정하지 않았으며, 새 PR 생성과 문헌 확인의 잔여 작업으로 기록한다.

## 브랜치 / 보존

`research/nscache-phase2a-256bit`는 Phase 1 `26ba752`에서 분기했다. 확인한 main에는 Phase 1 코드가 없어, 검토 PR base는 `research/nscache-phase1-reproduction`으로 지정한다. main/PR #1에 직접 병합하지 않는다.

Phase 1 전체 226개 파일의 baseline bytes를 `provenance/phase1_preservation.json`에 기록했다. `manifest.py`는 이를 먼저 검사하고 Phase 2 내부만 갱신한다. SHA manifest는 자기 digest를 제외하며 inventory는 자기 자신과 manifest를 포함한다. 부모 Phase 1의 snapshot 도구는 실행하지 않아 기존 manifest/inventory도 보존한다.
