# Power_Modeling — NS-Cache Phase 1

Generic SRAM/cache energy scaling 후보 모델의 재현성과 기술적 한계를 검증하는 연구 DB입니다. NVIDIA GPU 실측 또는 Rubin 최종 예측 결과가 아닙니다.

- [실행 방법과 DB 구조](NSCache_Experiment_DB/README.md)
- [Phase 1 결과 요약](NSCache_Experiment_DB/reports/phase1_summary.md)
- [재현성 비교](NSCache_Experiment_DB/reports/reproducibility_validation.md)
- [Read/Write scaling 및 조직·trade-off 분석](NSCache_Experiment_DB/reports/process_scaling_analysis.md)
- [출처·라이선스](NSCache_Experiment_DB/provenance/README.md)

16개 재구성 입력 모두 실행 완료. 12개는 기록값과 일치하며 7nm 4개는 접근 폭 차이로 불일치합니다. 별도 512bit 진단 4개는 모든 기록 지표와 일치했지만 원본 재현 실험과 분리해 보존합니다. 기존 ZIP은 수정하지 않았습니다.
