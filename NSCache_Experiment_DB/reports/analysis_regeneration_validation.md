# Phase 1 최종 분석 자동 재생성 검증

## 변경

`analyze.py`가 기존 16개 재현 실행과 별도 7nm 512bit 진단 4건의 **raw stdout**을 읽어 두 Matrix와 48개 SF, 24개 Matrix 차이, 진단 summary, Traceability 보고서를 자동 생성한다. `scaling.py`는 실행 선택·설정/로그 검증·Decimal 계산·표/추적 근거 렌더링을 담당한다. 기존 scaling CSV나 diagnostic JSON을 energy 입력으로 읽지 않는다.

검증 항목은 latest attempt의 종료 상태/코드, Finished!, configuration/cell/stdout/stderr SHA-256, width/node/objective/capacity/associativity 및 20개 실행 metadata의 동일 binary identity다. 별도 로컬 binary는 필요 없다. 누락·손상·미완료 입력은 결과 쓰기 전에 exit 2로 거부한다. 기존 파일이 남더라도 이 오류 종료를 현재 입력의 성공적 분석으로 간주하면 안 된다.

As-Reconstructed와 Width-Aligned 모두 Decimal로 `E_b/E_a`를 계산한다. 기존 float 문자열과 끝자리 표기가 달라질 수 있지만 입력 energy와 Matrix의 의미는 변하지 않는다. Read/Write, L1/L2, 두 optimization은 각각 분리한다. 512bit 정렬 후에도 Voltage, Cell Parameters, Internal Cache Organization이 다르므로 Pure Process Scaling으로 해석하지 않는다.

## 실행한 검증 명령과 결과

저장소 루트 `/workspace/Power_Modeling`에서 실행했다.

```bash
python3 -m unittest discover -s NSCache_Experiment_DB/tests -v
python3 NSCache_Experiment_DB/scripts/analyze.py
python3 NSCache_Experiment_DB/scripts/analyze.py
git fetch origin main:refs/remotes/origin/main
python3 NSCache_Experiment_DB/scripts/snapshot_manifest.py
python3 NSCache_Experiment_DB/scripts/snapshot_manifest.py --check
cd NSCache_Experiment_DB
sha256sum -c provenance/artifact_SHA256SUMS.txt
```

- 테스트 **13개 통과**. 원래 8개에 더해 캐시 오염/로컬 binary 부재 상태의 raw 재생성·반복 실행, 손상 진단 로그 거부, 변경 설정 거부, 실패한 최신 attempt 거부, manifest 반복성·변조 탐지를 검증한다. 실패 주입은 임시 복사본에서만 수행한다.
- 실제 DB에서 `analyze.py`를 두 번 실행했다. 두 번 모두 재현 실행 **16/16 완료, 12/16 기록 일치**, **24+24 SF 및 20개 검증 raw 실행**을 출력했다. 반환 코드 **1은 기존 7nm 4개 불일치가 검출된 예상 결과**이며 분석 실패나 전체 비교 통과로 표시하지 않았다.
- 아래 **12개 생성 파일 전부**의 첫째/둘째 실행 후 SHA-256이 동일했다. 테스트에서도 48개 SF를 raw energy에서 별도로 계산해 일치함을 확인했다.
- 이전 커밋과 비교해 configuration·모든 실행/build 로그·metadata·ZIP **115개 파일이 byte 단위로 동일**함을 확인했다. 새로운 시뮬레이션은 실행하지 않았다.
- 로컬 origin/main ref가 없어 read-only fetch로 확보한 뒤 manifest와 inventory를 갱신하고 `--check` 및 `sha256sum -c`로 검증했다. manifest 갱신을 두 번 수행해 manifest와 inventory가 byte 단위로 안정적인지도 확인했다.

## 반복 실행 비교 대상

```text
results/parsed_results.json
results/comparison.csv
results/run_summary.csv
results/scaling.csv
results/scaling_width_aligned.csv
results/scaling_matrix_comparison.csv
results/width_diagnostic.json
results/width_diagnostic.csv
results/optimization_tradeoffs.csv
reports/reproducibility_validation.md
reports/process_scaling_analysis.md
reports/scaling_matrix_traceability.md
```

위 12개 경로를 `P`라 할 때 첫 실행 후 `H1={p:sha256(p.read_bytes()) for p in P}`, 둘째 실행 후 `H2`를 계산하여 `H1 == H2`를 assert했다. 변경 전 커밋의 protected 파일들은 `git show HEAD:<path>`의 bytes와 실제 파일 bytes를 비교했다. 최종 commit 이전 검증 기준 HEAD는 `b05fead3037ba73788ce67572b72deeb0e31606b`다.

## Manifest / Inventory 범위

`provenance/artifact_SHA256SUMS.txt`는 Git이 추적하거나 무시하지 않는 현재 저장소 파일의 SHA-256을 DB 상대 경로로 기록한다. 루트 README, AGENTS, .gitignore, 원본 ZIP도 `../` 경로로 포함한다. manifest 자신의 digest는 자기참조 때문에 제외한다. `directory_inventory.txt`는 manifest와 inventory 자신을 포함한 전체 목록이다. `reports/changed_files.txt`는 `origin/main` 대비 현재 변경 파일 목록으로 자동 갱신된다. build/runtime/cache는 Git ignore 규칙으로 제외한다. 생성 시각이나 현재 HEAD SHA를 새로 삽입하지 않아 같은 파일 상태에서 반복 갱신 결과가 동일하다.

수정 후 `snapshot_manifest.py`로 갱신하고, `--check`로 읽기 전용 검증한다. 예전 Phase 1 시점의 목록만 남아 있다는 README 경고는 제거했다. 원본 ZIP·configuration·raw logs는 수정하지 않았으며, 변경은 기존 연구 브랜치에만 추가한다.

## 이번 최종 정리의 변경 파일

총 19개. 이전 Phase 1 전체 변경 목록은 `changed_files.txt`에서 확인한다.

- `NSCache_Experiment_DB/README.md`
- `NSCache_Experiment_DB/provenance/artifact_SHA256SUMS.txt`
- `NSCache_Experiment_DB/provenance/directory_inventory.txt`
- `NSCache_Experiment_DB/reports/analysis_regeneration_validation.md`
- `NSCache_Experiment_DB/reports/changed_files.txt`
- `NSCache_Experiment_DB/reports/process_scaling_analysis.md`
- `NSCache_Experiment_DB/reports/reproducibility_validation.md`
- `NSCache_Experiment_DB/reports/scaling_matrix_traceability.md`
- `NSCache_Experiment_DB/results/comparison.csv`
- `NSCache_Experiment_DB/results/optimization_tradeoffs.csv`
- `NSCache_Experiment_DB/results/run_summary.csv`
- `NSCache_Experiment_DB/results/scaling.csv`
- `NSCache_Experiment_DB/results/scaling_width_aligned.csv`
- `NSCache_Experiment_DB/results/width_diagnostic.csv`
- `NSCache_Experiment_DB/scripts/analyze.py`
- `NSCache_Experiment_DB/scripts/scaling.py`
- `NSCache_Experiment_DB/scripts/snapshot_manifest.py`
- `NSCache_Experiment_DB/tests/test_analysis.py`
- `README.md`
