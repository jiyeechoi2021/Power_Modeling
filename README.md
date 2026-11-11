# Power_Modeling — NS-Cache Phase 1

Generic SRAM/cache energy scaling 후보 모델의 재현성과 기술적 한계를 검증하는 연구 DB입니다. NVIDIA GPU 실측 또는 Rubin 최종 예측 결과가 아닙니다.

- [실행 방법과 DB 구조](NSCache_Experiment_DB/README.md)
- [Phase 1 결과 요약](NSCache_Experiment_DB/reports/phase1_summary.md)
- [재현성 비교](NSCache_Experiment_DB/reports/reproducibility_validation.md)
- [Read/Write scaling 및 조직·trade-off 분석](NSCache_Experiment_DB/reports/process_scaling_analysis.md)
- [출처·라이선스](NSCache_Experiment_DB/provenance/README.md)

16개 재구성 입력 모두 실행 완료. 12개는 기록값과 일치하며 7nm 4개는 접근 폭 차이로 불일치합니다. 별도 512bit 진단 4개는 모든 기록 지표와 일치했지만 원본 재현 실험과 분리해 보존합니다. 기존 ZIP은 수정하지 않았습니다.

Phase 1 보완에서는 **As-Reconstructed Input**(7nm=256bit) Matrix를 보존하고, 별도 7nm 진단과 다른 공정의 512bit 실행을 조합한 **Width-Aligned Scaling Matrix**를 추가했습니다. [두 Matrix와 차이](NSCache_Experiment_DB/reports/process_scaling_analysis.md), [SF별 로그·설정·수식](NSCache_Experiment_DB/reports/scaling_matrix_traceability.md)을 확인할 수 있습니다. 폭 정렬 후에도 전압·셀 파라미터·내부 조직이 달라 Pure Process Scaling을 뜻하지 않습니다.

`analyze.py` 재실행으로 두 Matrix와 48개 SF·추적 근거를 raw log에서 자동 복구할 수 있습니다. [최종 반복 실행·무결성 검증](NSCache_Experiment_DB/reports/analysis_regeneration_validation.md)을 참고하세요.
