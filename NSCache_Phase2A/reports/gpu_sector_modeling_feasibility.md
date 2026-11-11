# GPU Sector와 NS-Cache Access: 표현 가능성 및 비교 경계

## 배경과 검토 범위

V100/A100 NCU 측정에서 32B sector 및 pJ/bit 계수를 사용한다는 연구 입력에 맞춰 NS-Cache를 256bit로 실행했다. **32B라는 숫자가 같아도 energy boundary나 physical transaction이 같지는 않다.** 이번 검토는 기존 소스의 표현 능력을 조사하며 GPU simulator 구현, NS-Cache 모델 수정, 내부 GPU 계수의 공개 또는 실제 측정값 기반 검증은 하지 않는다.

## 공개 NVIDIA 문서 확인 상태

확인이 필요한 공식 문서:

- [Nsight Compute Profiling Guide — Memory Workload Analysis](https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html#memory-workload-analysis)
- [CUDA C++ Programming Guide — Device Memory Accesses](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#device-memory-accesses)
- [Volta Tuning Guide](https://docs.nvidia.com/cuda/volta-tuning-guide/index.html)
- [Ampere Tuning Guide](https://docs.nvidia.com/cuda/ampere-tuning-guide/index.html)

**이 환경에서는 위 공식 docs host의 HTTPS 요청이 HTTP 403으로 차단돼 본문을 검증하지 못했다.** 따라서 위 링크는 검토 대상이며 읽은 문헌의 증거로 표시하지 않는다. NVIDIA의 공개 [nsight-training 저장소](https://github.com/NVIDIA/nsight-training/tree/b17c40eef23929d08ec42e66667b29ae336ea8ac)는 Git으로 읽어 관련 NCU notebook을 조사했으나, 검토한 자료에서 V100/A100 각각의 cache line/sector 크기와 태그 재사용 정책을 확정할 텍스트 근거를 확보하지 못했다.

그러므로 **V100/A100의 L1/L2가 모두 동일하게 128B line/32B sector를 사용한다고 확정하지 않는다.** 32B sector는 사용자가 제공한 측정 단위로 명시하고, 세대·cache level·operation별 물리 line/sector 및 counter 의미는 미확인 항목으로 남긴다. 128B/32B는 아래 모델 능력을 점검하는 목표 시나리오이지, 검증된 모든 GPU cache의 고정 규격이 아니다. 문헌 확인에는 `docs.nvidia.com` 접근 허용이 필요하다. Nsight 버전별 counter suffix와 access policy도 별도 확인해야 한다.

## 소스에서 확인한 지원 여부

소스는 Phase 1의 검증 upstream revision `2fdcbf093f806bc9a28964aca8402c42738d58e5`를 그대로 사용한다. 아래 위치는 저장소 내 파일·함수·행 번호이며, 이 검토에서 모델 소스를 변경하지 않았다.

| 질문 | 현재 지원 / 확인 사실 | 소스 근거 | 필요한 후속 변경 및 GPU 비교 영향 |
|---|---|---|---|
| Q1. WordWidth=256bit는 32B line 전체 접근인가? | 이 cache 모델에서 그렇다. 입력 wordWidth/8을 Cache Line Size로 출력하고 data blockSize=wordWidth로 설정한다. Normal mode는 모델 line 단위 에너지를 계산한다. 실제 GPU sector와 같다는 뜻은 아니다. | [InputParameter.cpp](../../NSCache_Experiment_DB/source/InputParameter.cpp), ReadInputParameter WordWidth 파싱 330–331, PrintInputParameter 931; [main.cpp](../../NSCache_Experiment_DB/source/main.cpp), nvsim 434–451 및 505–525 | 256bit 결과는 **32B model cache-line access**로 표시해야 한다. |
| Q2. Line Size와 실제 access width를 독립 설정할 수 있나? | 현재 이 cache 경로에서는 없다. wordWidth가 set 수, offset, tag capacity, data block 및 배선 bit 수에 함께 사용된다. 독립 sector-width 입력을 확인하지 못했다. | main.cpp nvsim 434–451, 507; [BankWithHtree.cpp](../../NSCache_Experiment_DB/source/BankWithHtree.cpp), Initialize 164–189 | lineSize/accessWidth/sectorCount를 분리하고 tag indexing과 data activation 전달 경로를 수정해야 한다. WordWidth만 바꾸면 line 수/tag 구성이 바뀌므로 고정 128B line 실험이 아니다. |
| Q3. 128B line 중 32B sector만 활성화할 수 있나? | 전용 sector mask/sector-valid state와 독립 line/access 폭이 없어 현재 설정만으로 충실히 표현할 수 없다. fast/sequential/normal 모드는 sector mode가 아니다. | main.cpp 507–525; InputParameter.h/ReadInputParameter; BankWithHtree Initialize; [SubArray.cpp](../../NSCache_Experiment_DB/source/SubArray.cpp) Initialize/CalculatePower | 1024bit logical line의 tag 계산은 고정하고 data 활성 범위를 256bit로 제한하는 sector mask·mux·wordline/bitline 모델과 회귀 테스트가 필요하다. |
| Q4. Tag lookup과 data activation을 구분할 수 있나? | 별도 tagBank/dataBank를 계산하고 각각의 조직·에너지를 출력한다. Normal mode hit timing은 tag와 data row 병렬 활성 및 column decoder를 조합한다. 통계적 tag hit reuse 상태는 없다. | main.cpp nvsim tag 434–453/data 505–525; [Result.cpp](../../NSCache_Experiment_DB/source/Result.cpp), printAsCache 1596–1645 | 별도 구성요소 값은 얻을 수 있지만 sector 단위로 tag를 생략하는 policy는 구현하지 않는다. Tag-access 횟수와 data-sector 횟수를 독립 입력할 필요가 있다. |
| Q5. Data/Tag, Routing/Peripheral energy를 분리할 수 있나? | Data/Tag bank read/write와 H-tree read/write, per-subarray/per-mat 및 decoder/senseamp/mux/precharge 상세가 stdout에 있다. bank는 routing을 포함하며 계층 값은 서로 겹친다. SRAM cell-only energy는 해당 로그에 독립적으로 완전 분리되지 않는다. | Result.cpp print 833–887 및 write 출력 890 이후; BankWithHtree CalculateArea/CalculateLatencyAndPower 부근 667–735 | 출력된 bank·routing은 비교 가능하지만 중첩 항목을 합쳐 100% partition을 만들면 안 된다. 고정/공유 peripheral 및 cell-only 인과 비중을 얻으려면 별도 instrumented output과 단위/합산 검증이 필요하다. |
| Q6. 같은 line의 여러 sector 접근은 tag/peripheral을 어떻게 계산하나? | 현재 코드는 access마다 cacheHitEnergy=tagRead+dataRead, cacheWriteEnergy=tagWrite+dataWrite를 합산한다. N개의 독립 모델 접근으로 취급하면 N번 반복되며, 동일 line의 4개 sector라는 정보를 저장해 tag/peripheral을 공유하지 않는다. | Result.cpp printAsCache 1611–1644; BankWithHtree 667–735 | N×E_model은 현 모델의 독립 line 접근 가정이며 GPU sector sequence의 tag reuse/coalescing 정책이 아니다. 한 번 tag+선택 sector data+공유/per-sector routing을 구분하는 request/sequence 모델이 필요하다. |

## 모델 에너지 경계에서 추가로 확인할 점

Normal cache hit의 식은 `E_hit = E_tag_read + E_data_read`, write는 `E_write = E_tag_write + E_data_write`다. Normal miss는 tag뿐 아니라 data energy를 더하며 소스에 `TO-DO: not accurate here`라는 주석이 있다(Result.cpp 1619–1620). 따라서 GPU miss/fill/writeback energy에 현재 miss 출력이나 hit coefficient를 무조건 대입하면 안 된다. Cache write 역시 GPU store-hit, write allocation, writeback, ECC/metadata update의 물리 경계가 일치한다는 보장이 없다.

WordWidth를 절반으로 바꿔도 tag+peripheral 에너지가 정확히 절반이 되지 않으며, line 수와 tag capacity 및 최적화 조직이 달라질 수 있다. 이번 결과는 payload width만 다른 동일 GPU-cache sector의 미세 조정이 아니라 모델 line-size/조직 재최적화를 포함한다.

## GPU 실측 비교를 위한 normalization 틀

| 양 | 정의 | 의미 / 조건 |
|---|---|---|
| `E_NS_bit` | `E_NS_access / 256` | 32B **모델 cache-line 접근**의 effective pJ/bit. 물리 cell bit energy 아님. |
| `E_GPU_sector` | `E_GPU_bit × 256` | 사용자의 32B-sector 기준 coefficient를 sector당 단위로 환산. 실제 GPU 값은 이 공개 DB에 저장하지 않음. |
| Energy boundary alignment | tag+data+decoder+routing 범위 및 hit/miss/write 종류별 횟수 매핑 | 단위가 같아도 필수인 별도 검증. 알려지지 않은 항목을 숫자로 채우지 않음. |

절대 energy 비교 전에 확인해야 할 조건:

1. GPU 세대·L1/L2·NCU 버전별 sector/line 규격과 정확한 counter 이름, read/write/atomic, hit/miss/fill/writeback 및 포함 traffic 종류.
2. Coalescing된 warp request와 sector transaction, replay, sector-valid state, 같은 line의 tag lookup 공유/재사용 관계. Sector count를 tag-access count와 같다고 두지 않는다.
3. GPU coefficient의 추정/측정 경계: dynamic/leakage 분리, baseline subtraction, clock/voltage, regression 공선성, 중복 counter, ECC/interconnect/DRAM 포함 범위. 미확인 데이터는 비공개 측정 작업에서 확인한다.
4. Capacity/associativity/ports/banking/latency 제약, voltage/cell/temperature, model tag/data 조직과 GPU 구현 차이.
5. 최적화 목표별 결과 및 반올림 해상도. 단위 환산만으로 absolute accuracy나 process-only causality를 주장하지 않는다.

## 결론과 Phase 2-B 제안

기존 모델에서 256bit 접근은 32B **line** 모델이며 고정 128B line의 32B sector activation과 구조적으로 동일하지 않다. 현재 실험은 effective pJ/bit와 폭 민감도를 비교할 공개 기준을 제공하지만, GPU sector당 절대 energy 검증을 완료하지 않았다.

Phase 2-B에서는 (a) 공식 NVIDIA 문서/정확한 NCU counter 정의 확인, (b) line/access width 분리 및 sector mask를 가진 새 모델 경로 설계, (c) 동일 tag/조직을 고정한 1/2/4-sector 활성 비교와 독립 tag/data 접근 횟수, (d) 공유/per-sector peripheral을 구분한 출력·회귀 테스트, (e) 포트·latency·Vdd 통제 감도 실험을 수행한다. 이는 제안이며 이번 단계에서 실행하거나 모델 수정했다고 표시하지 않는다.
