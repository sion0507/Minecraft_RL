# Minecraft 행동 선택 강화학습

고정된 Minecraft 환경에서 NanoJev 행동 선택 정책의 추가 강화학습 효과와 기존 Jev의 조건부 대체 성능을 비교하는 학부 연구 프로젝트입니다.
고정된 7B 계획기가 하위 목표를 정하고, 공통 코드가 최대 16개 매크로 후보를 생성하면 행동 모델이 하나를 선택합니다.
별도 규칙 기반 행동 선택기 S는 동일 최종 7B 아래 공통 후보를 선택하며 C4 결정적 1회로 진단합니다.
핵심 참조 시스템 F는 계획기를 Astra로 바꾸고 J와 동일한 Jev를 사용해, 작은 로컬 모델과 RL 조합이 강력한 전체 시스템에 얼마나 접근하는지 비교합니다.
목표는 자연 생성 다이아몬드 광석을 적절한 도구로 직접 파괴하고 해당 드롭을 획득하는 것입니다.

## 현재 상태

이슈 #2의 공통 실행 흐름, #3의 실제 Minecraft reset·정지, #4의 제한 관측·보행, #5의 목재 수집에 이어 #6의 개별 제작·설치·화로 투입/회수·철 채굴을 `smoke-macros`에 연결했습니다. 실제 검증 상태와 미달 항목은 [PROGRESS.md](PROGRESS.md)를 따릅니다.

#6은 배치 자원의 제작·제련·노출 철 직접 채굴/획득 연결, 시계63조건·정보26장면·실제 제어 검증을 통과했습니다. 2026-11-06 사용자 승인으로 자연 고정 G2 철광석3개 검증은 **미달 이력을 보존해 #8의 후속 통합 인수 조건으로 이관**했습니다. T05 완료는 자연 G2 성공을 뜻하지 않습니다. 책임·재검증 조건은 [PLAN.md §5.2.1](PLAN.md)를 따릅니다.
현재 실제 backend는 자기 상태, 직접 보인 표면·공기/방문 기억, 노출 원목·돌·철 채굴과 직접 드롭 획득, 개별 제작·제련, wait와 같은 높이의 보행을 제공합니다. 미검증 자연 단차 이동은 보존 후 제외했습니다. 관측 기반 계단 하강(`stair_down`)은 T06(#7)에서 추가했고, 터널·모델/API·PPO는 후속 작업입니다. T05A(#32)는 실제 0.0500초/틱·새 시계 63/63·T05 전체·T04 정보감사와 매크로 회귀를 확인했습니다. 자연 G2는 기존 기준선과 같은 예상 실패이며 철3 통합 인수는 T07(#8)에 남습니다. T06(#7)/T07(#8) 코드 변경 후에는 재인증이 필요합니다. 실제 검사·미실행 기록은 [PROGRESS.md](PROGRESS.md)에 있습니다.

## 실험 범위

| 비교군 | 계획기 | 행동 정책 |
| --- | --- | --- |
| A | 고정 Qwen2.5-7B-Instruct | 공개 초기 NanoJev |
| B | A와 같은 계획기 | A와 동일 초기화에서 PPO로 추가 학습한 NanoJev |
| J | A와 같은 계획기 | 프로젝트 내 추가 학습 없는 기존 Jev |
| F | 고정 Astra | J와 동일한 기존 Jev/설정 |
| S (필수 진단) | A/B/J와 동일 최종 7B | 고정 규칙 기반 행동 선택기 |

월드 시드 하나와 과제별 고정 시작 상태를 사용합니다. B 본 학습은 한 번, local/full 각각 15,000결정입니다.
기본 최종 평가는 기존 C4 17회+F 5회+필수 G4 6회=28회입니다. 사전 축소는 A/B/J/F 주 평가를 모두 각 3회로 조정해 총 20회이며 G4 6회를 유지합니다. 별도 S C4 1회를 포함하면 총 29회/축소 21회이며 핵심/G4/S 결과와 분모를 구분합니다. S 학습이나 G4는 추가하지 않으며 1회로 통계적 우월성·일반적인 신경망 대체 가능성을 주장하지 않습니다. BC는 제외합니다.
A↔B는 행동 PPO 효과, B↔J는 동일 7B에서 모델 비교, J↔F는 동일 Jev에서 계획기 비교, B↔F는 전체 시스템 비교입니다. B↔F를 RL 하나의 인과적 효과로 해석하지 않습니다.
7B 가중치 고정과 로컬 지식 조회 우선을 유지합니다. 진단·지식/입력/검증/재계획 보완·공통 Astra 비교 후에도 중대한 계획 병목이 확인되고 [PLAN.md §5.6](PLAN.md#56-7b-계획기-추가-학습--최후의-조건부-대안)의 여섯 조건을 모두 충족해야만 학습을 별도 제안합니다. 분석·비용 보고와 명시적 사용자 승인 후 PPO 전에 완료·검증하고 A/B/J/S 최종 7B를 동일하게 고정합니다. 자동 학습 단계는 없습니다.
결과는 고정 환경 적응으로 해석하며, 새로운 월드 일반화의 근거로 삼지 않습니다.

## 연구 동기와 한계

실제 로봇에서는 연산량이 큰 상위 목표 계획을 클라우드 등 외부 연산 자원에서 수행하고, 상대적으로 작은 행동 선택 정책을 로봇 내부에서 실행하는 계층적 구조를 고려할 수 있다. 이러한 구조에서는 행동 선택 모델의 크기와 계산 비용이 중요한 설계 요소가 된다. 본 연구는 이와 관련된 동기에서 소형 행동 선택 정책의 추가 강화학습 효과와 규칙 기반 선택기 및 외부 모델과의 수행 차이를 조사한다.

이는 응용 가능성과 후속 연구 방향이며 이번 프로젝트의 실증 결론이 아니다. 실제 로봇이나 온디바이스 배포를 검증하지 않는다. 현재 7B 계획기는 로컬에서 실행하므로 클라우드-로봇 분산 구조를 구현·검증했다고 주장하지 않는다. NanoJev의 CPU 실시간 추론 가능성이나 특정 로봇 하드웨어 성능을 입증하지 않으며, NanoJev는 저수준 모터 제어기가 아닌 매크로 행동 후보를 선택하는 고수준 정책이다. CPU 추론 벤치마크·네트워크 지연 실험·실제 로봇 테스트·클라우드 API로의 계획기 이전·온디바이스 최적화 실험은 추가하지 않는다.

## 예정 스택과 실행

- Minecraft Java Edition 1.16.5, Survival/Peaceful.
- Python + uv: 모델·PPO·평가·`mc-diamond` CLI.
- Node.js + Mineflayer: 게임 연결·제한 관측·매크로 실행.
- `Qwen/Qwen2.5-7B-Instruct` 고정 계획기, `C-Tianyu/NanoJev` Choice 및 local/full 가치 헤드 학습.
- 기본 장비: RTX 5070 Ti 16GB, RAM 32GB.

Python 3.12 이상과 Node 22 이상이 필요합니다. `uv`를 설치하고 아래 명령을 저장소 루트에서 실행합니다.
이번 작업공간에는 `uv`를 `.tools/uv`에 설치했으므로 `export PATH="$PWD/.tools:$PATH"`로 사용할 수 있습니다.

```bash
uv sync
npm --prefix bridge ci
uv run mc-diamond doctor --config configs/pilot.yaml
uv run mc-diamond smoke-episode --config configs/pilot.yaml
uv run mc-diamond smoke-macros --config configs/pilot.yaml
uv run pytest
uv run mypy .
```

`doctor`는 실제 도구·연산 결과를 stdout JSONL로, 부재·오류 설명을 stderr로 내보냅니다. 검사가 모두 사용 가능하면 0, 부재·오류가 있으면 1을 반환합니다.
GPU 검사는 CUDA 드라이버 API로 직접 작은 산술 커널을 실행합니다. `nvcc` 부재와 GPU 연산 실패를 별도로 표시합니다. 제한된 샌드박스에서는 GPU 접근 실패가 실제 장비 상태와 다를 수 있습니다.

`smoke-episode`는 제공된 모의 fixture를 subprocess backend로 실행하고 reset→관측→고정 목표→후보→선택→실행→진단 보상→요약을 출력합니다.
모의 보상은 획득 사건 수이고, 실제 local/full 보상·PPO·다이아 성공 판정의 검증이 아닙니다. 정상 종료/유효 절단은 0, backend 오류/무효 경험은 1, 설정 오류는 2입니다.
실제 backend는 설정의 `backend: rpc`와 `command`로 같은 실행 경로에 연결하고 `fixture`는 제거합니다. 제공하는 설정은 `configs/minecraft.yaml`입니다.

RPC backend는 `--admin-fd <fd>`로 전달받은 파이프에서 reset·snapshot 준비·시계/정보 fixture 진단만, stdin에서 observe/step만 받습니다. 두 채널의 응답은 request_id에 맞춰 stdout JSONL로 반환하고 진단은 stderr에 기록합니다.
요청은 `request_id/method/payload`, 응답은 `request_id`와 정확히 하나의 `result/error`를 가지며 현재 호출은 직렬입니다.
자료형과 허용 필드는 [schema.py](src/mc_diamond/schema.py)에 있습니다. 결과·후보 ID·원본 관측·mask와 episode/attempt ID를 로그에 보존합니다.
알 수 없는 관측 필드와 RPC 결과는 오류로 종료하고 원본 오류 입력을 로그에 출력하지 않습니다.

시계·정보 경계·모델·학습 연결 진단 및 예산 확인 후 실험 설정을 고정합니다.
`smoke-model`은 아래 절을 따릅니다. PPO 본 학습 등 후속 실험 명령의 전체 계약은 [PLAN.md §14](PLAN.md#14-구현-후-사용할-명령), 개발 지침은 [AGENTS.md](AGENTS.md)에 있습니다.

## 공통 계획기 smoke-planner (#10 / T09)

공개 고정 Qwen2.5-7B-Instruct를 실제 CUDA에서 NF4 4비트로 로드하고 기존 목표 검증·한 번 재생성·규칙 복구·매크로 실행을 사용합니다. 직접 작성한 공통 프롬프트와 SHA-256은 `planner_prompt.txt`/`planner_loaded`에, immutable revision과 13개 파일의 SHA-256은 `src/mc_diamond/qwen_files.json`에 있습니다. 모델은 학습하지 않습니다.

```bash
uv sync --extra planner
HF_HOME=.cache/huggingface HF_HUB_DISABLE_XET=1 uv run --extra planner python tools/install_planner.py
uv run --extra planner mc-diamond smoke-planner --config configs/planner_smoke.yaml
# 기존 실제 G1 snapshot과 유효 시계 인증이 필요합니다(최대 8결정·240초).
uv run --extra planner mc-diamond smoke-planner --config configs/planner_minecraft.yaml
uv run --extra planner pytest
uv run --extra planner mypy src tests
```

`planner_smoke.yaml`의 **모델은 실제, 게임은 mock**입니다. `planner_minecraft.yaml`은 실제 모델+자연 G1의 짧은 연결 진단이며 C4/G4 평가가 아닙니다. 문서의 기본 명령 `smoke-planner --config configs/pilot.yaml`도 planner 설정이 없으면 고정 local_7b를 사용합니다. 다른 smoke 명령은 기존 고정 목표를 유지합니다. 설정의 checkpoint는 YAML 기준 상대 경로입니다. 온도 0은 `do_sample=False`의 greedy decoding으로 구현합니다(Transformers는 sampling을 끄면 temperature를 적용하지 않습니다).

7B/Astra는 NanoJev/Jev와 같은 공통 상태(자기 상태·종류별 기억 요약 256칸·최근 방문 32개·결과 8개)와 과제·검증 오류를 받습니다. 후보/관리자 정보는 제공하지 않습니다. 로컬 입력은 생성까지 8192토큰 상한이며 초과 시 조용히 자르지 않고 실패합니다. 지식 조회는 PLAN §5.5의 조건부 후속 작업으로 현재 `knowledge=null`입니다. `planner_call`에 입력 hash·토큰·지연·응답을, 기존 `goal_decision`/`summary`에 검증 오류·각 요청 분모·목표 출처별 직접 진행을 기록합니다. 실제 API 접근 오류는 잘못된 목표와 구분해 종료하며 규칙 복구 성과로 바꾸지 않습니다.

Astra는 HTTPS Chat Completions 계약을 구현했습니다. PLAN의 후보는 OpenRouter `https://openrouter.ai/api/v1/chat/completions` / `openai/gpt-6-astra`이며 실제 계정 접근·버전·지원 추론 옵션·과금은 **미확인**입니다. 사용자는 제공처/model/version/endpoint/실제 지원 설정과 `rates_checked_on`, 입·출력 백만 토큰당 USD 요율을 확인한 뒤 별도 지출 승인을 해야 합니다. 키는 환경변수 `ASTRA_API_KEY`로만 읽습니다. 설정에는 키를 쓰지 않습니다.

`planner.backend: astra`의 유료 실행에는 `approved: true`, `approval_reference`, `max_calls`, `max_usd`, 제공처에서 검증한 **추론·실패 과금까지 포함한 요청당 최악 금액** `request_usd_ceiling`, 지속 `budget_file`이 필요합니다. `supported_settings`는 확인한 temperature/top_p/reasoning_effort만 명시하고 미지원 값을 동일 적용했다고 가정하지 않습니다. 예약 ledger는 재생성·실패·재실행도 호출/금액 상한을 소비하며 자동 환불하지 않습니다. 같은 승인에는 같은 ledger를 사용하고 삭제·새 경로로 한도를 초기화하지 않습니다. 호출 상한은 제공처가 실제로 지키는 요청당 금액 상한을 전제로 합니다. 실제 청구는 별도 확인해야 하며 토큰×기재 요율은 추정치입니다.

실제 Astra 호출은 아직 하지 않았습니다. **2026-11-09 사용자 결정으로 실제 연결·응답·지원 설정·사용량/과금·지연 검증은 추후 비교 단계에 수행하며, 미실행은 #10 종료의 장애가 아닙니다.** 연결 가능성에 대한 기대를 실제 성공으로 표시하지 않습니다. 실제 호출 직전 키/계정·별도 금액/호출 상한 승인과 제공처/버전/지원 설정/청구를 확인하는 계약은 유지합니다. 정상/오류/재생성·공통 복구는 mock 계약 검사이며 실제 Astra 성능이나 F 완료가 아닙니다. F의 Jev 행동 선택은 #12, 6상태 비교는 #17, 본 학습 전 예산/lock은 #20 책임입니다. 실제 `evaluate`의 군별 계획기 연결/lock은 후속 작업이며 현재 실제 계획기 설정으로 평가를 시작하면 거부합니다. 관측 반경32·공통 256칸 요약은 [#44](https://github.com/sion0507/Minecraft_RL/issues/44)에서 구현했습니다. 실제 검증 상태는 PROGRESS를 따릅니다. `mypy .`는 `artifacts/`의 실행 보관 사본과 `checkpoints/`의 외부 다운로드 코드를 제외하고 프로젝트 코드·테스트·진단 도구를 검사합니다. 개발 핵심 범위는 `mypy src tests`로도 확인할 수 있습니다.

## 공개 NanoJev smoke-model (#11 / T10)

실제 공개 모델과 mock Minecraft를 연결하는 최소 진단입니다. CUDA/BF16 GPU와 모델 extra가 필요합니다.
의존성은 공개 bundle의 PyTorch 2.14.0·Transformers 5.17.0·Safetensors 0.8.0에 맞추며 `uv.lock`으로 고정합니다.
기존 게임 CLI는 모델 extra 없이도 사용할 수 있습니다. 모델 수치 테스트·mypy 검사는 extra를 설치한 환경에서 실행합니다.

```bash
uv sync --extra model
HF_HOME=.cache/huggingface HF_HUB_DISABLE_IMPLICIT_TOKEN=1 uv run --extra model python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("C-Tianyu/NanoJev", revision="047b927b30882a1138fc504821b82ac145a4b81a",
    local_dir="checkpoints/nanojev", token=False,
    allow_patterns=["best.safetensors", "config.json", "backbone_config/*", "tokenizer/*", "README.md",
                    "source/LICENSE", "source/scripts/train_toy_decisions.py", "source/scripts/predict_toy_decisions.py"])
PY
uv run --extra model mc-diamond smoke-model --config configs/model_smoke.yaml
uv run --extra model pytest
uv run --extra model mypy src tests
```

`model_smoke.yaml`의 두 관측 원목은 서로 다른 채굴 대상입니다. 후보는 기존 공통 생성기가 만들고 저장한 ID·내용·순서·mask를 사용합니다.
`model.checkpoint`는 YAML 기준 상대 경로, `mode`는 `sampling` 또는 `argmax`, `seed`는 해당 선택기의 난수입니다.
모델 입력은 제한 관측·목표·목적·시간 예산과 후보뿐입니다. 기억한 비공기 칸을 종류별로 묶어 전체 수와 가까운 칸 좌표(현재 시야 now/과거 기억 past)를 모두 256칸까지 공통 요약합니다. 개수가 적은 종류부터 남은 자리의 균등 몫을 받아 광석·위험·설비가 바닥에 밀려 빠지지 않습니다. 최근 방문 32개·결과 8개와 방문 수도 기록합니다. 토큰 경로 상한 8192를 넘으면 실패하고 조용히 잘라내지 않습니다.
전송 키 a0…와 저장 candidate_id를 대응시키고, mask는 Choice attention·정규화·critic 평균·sampling에 적용합니다.
Jev 연결(T11)에서도 같은 의미를 사용해야 하며 외부 API가 mask를 지원하지 않으면 요청에서 비활성 키를 제외해야 합니다.

`model_loaded`는 고정 revision·파일 SHA-256·새 critic 초기화·정밀도를, `model_input`은 정확한 입력/ID/mask를 기록합니다.
첫 복수 후보에서 공개 원본 `DecisionModel.forward`와 FP32/BF16 토큰화·EOS pooling·logits를 대조합니다.
backbone은 frozen/no_grad, dropout 0이며 공개 Choice(norm/scalar/set attention)는 trainable입니다. 후보 표현 masked mean과 목적/시간 4개 수치로 독립 `256/GELU/scalar` local/full critic을 계산합니다.
합성 수치 목표로 Choice/두 critic을 한 번 갱신하고 단일 후보 full critic-only도 검사한 뒤 초기 actor/critic을 복원합니다. `predict()`의 inference_mode를 학습 경로로 사용하지 않습니다.
이 단계는 PPO 성능 검증이 아니며 게임 전이를 학습에 사용하지 않습니다. 에피소드 요약의 actor_transitions는 계속 0입니다.

성공은 `model_summary.model_verified=true`와 exit 0으로 확인합니다. 모델/의존성/파일 부재는 exit 2, 로드 후 진단·에피소드/시계 검증 실패는 exit 1입니다.
기본 `configs/pilot.yaml`은 단일 후보이므로 확률 1·actor 제외는 확인해도 Choice gradient를 검증하지 못해 **exit 1 / model_verified=false**입니다.
실제 Minecraft 설정(`backend: rpc`)에서도 같은 명령을 쓸 수 있으나 별도 runtime/snapshot·시계 인증이 필요합니다. #11에서는 실제 모델+mock 게임만 검증했습니다.
선택 확률은 성능·보정된 신뢰도 주장으로 사용하지 않습니다. 7B/Jev/Astra·유료 API·PPO 본 학습·최종 평가는 실행하지 않습니다.

## 사건 보상과 PPO 연결 진단 (#14)

```bash
uv run --extra model mc-diamond smoke-ppo --config configs/ppo_smoke.yaml
```

공개 NanoJev를 실제로 로드하고 **mock 게임**의 서로 다른 보상을 가진 전이 2개로 짧은 PPO update를 수행합니다.
`smoke-model`의 합성 target 진단과 달리 공통 reset→목표→후보→선택→실행→사건 보상→전이→GAE→PPO를 통과합니다.
Choice와 목적별 critic만 학습하며 backbone은 고정합니다. 진단 actor는 저장하지 않고 본 학습에 이어 쓰지 않습니다.

`reward`는 local/full 목적별 구성·할인보상·task terminal·actor 제외 사유를 기록합니다. 시간 비용은 모든 실제 활성 틱에 부과하고,
사건별 발생 틱이 없는 현재 RPC의 획득/완료 보상은 **반환 경계의 마지막 틱**에 배정합니다. 원시 물리 사건의 발생 시각을 복원한 값은 아닙니다.
full 진행은 직접 최초 사건만 최대 18, 목표 보상은 정규화한 종류·대상별 최초 완료만 최대 8회/총 4입니다.
제공 아이템·이미 충족한 목표는 제외하며, 무보상 반복 목표도 정상 완료·전환합니다.

`transition`에 수집 당시 관측·목표·후보 ID/내용/순서/mask·old logprob/value와 실제 다음 상태를 보존합니다.
full 목표 변경은 trace를 이어 가고, task terminal은 bootstrap 0, 유효한 운영 절단은 bootstrap하며 rollout 끝의 유효 trace mask는 0입니다.
단일/0후보·취소·fallback·critic-only는 actor 제외, 유효한 전이는 critic에 사용합니다. 취소 구간은 trace를 끊고 불완전/무효 전이는 학습하지 않습니다.
후보 0개 상태의 critic은 실제 강제 wait를 값 계산에만 표현하며 제공 후보 집합은 빈 그대로 남깁니다.

`ppo_update`는 유효/actor 전이 수, 수집 정책 대비 최초 ratio, advantage/return/trace mask, 정책 손실·유한 gradient norm과 head 변화를 기록합니다.
`learning_summary.learning_verified=true`와 exit 0은 유효 update와 본체 불변·에피소드/시계 검사를 통과했다는 뜻입니다.
모델 로드 전 실패는 exit 2, 로드 뒤 실패는 exit 1입니다. 실제 게임 학습 성능·파일럿·본 학습·최종 평가 성공을 뜻하지 않습니다.
`ppo` 설정의 기본값은 PLAN §6.2를 따릅니다. 실제 사건 연결 진단은 #15/#16, 커리큘럼·복구는 #18/#19, 예산/lock은 #20입니다.

## 목재 파일럿 (#15 / T14, 신호 보강 #49)

후속 **#51 T14B**는 별도 `pilot-signal` 명령과 `configs/signal_pilot.yaml`을 사용합니다. 현재 구현·7B 결과 보고 뒤 사용자의 게임 파일럿 승인을 받아야 실행합니다.

```bash
PYTHONFAULTHANDLER=1 uv run --extra model mc-diamond pilot-signal --config configs/signal_pilot.yaml --output runs/pilot-signal-51
```

`pilot_signal: true`에서만 원목3 → 나무 곡괭이1 제작 → 조약돌3 사슬과 개당1/N·목표 완료 보상·visible 원천 블록 거리 potential을 켭니다. D=32, k=0.3/32이며 발견 보상은 끕니다. 하위 목표 완료는 return 경계이고 게임을 reset하지 않습니다. 기본 local/full 보상은 그대로입니다.

T14B는 초기10평가의 종류별 좋은/나쁜 선택 MC return 차이가 양수인지 먼저 확인합니다. 비교 표본이 없거나 차이가 양수가 아니면 학습하지 않고 수치를 남깁니다. 통과하면 LR3e-4로4,096결정/32rollout, MC 누적 critic 워밍업(EV≥0.3 또는 최대1,024결정,32epoch) 후 일반 GAE/PPO를 수행하고 후10평가를 보조 보고합니다. 주 판정은 초기평가에서 고정한 상태의 좋은 후보 확률 증가≥0.10/＜0.03/그 사이이며2,048결정 결과는 보조입니다. 같은 위치·인벤토리의 학습 자료는 보조 critic 적합의 학습 분할에서 제외합니다. 고정 상태 평가를 온라인 PPO가 보지 않은 환경에 대한 일반화로 해석하지 않습니다.

산출물은 `--output`의 `signal/`에만 생성하며 초기heads/매updateheads·고정상태·지표·신호gate·분모20·실패·복원 여부를 보존합니다. 파일럿heads와경험은 본 학습 초기화/30,000결정에서 제외합니다. 게임·학습은 #49처럼 완료 이벤트로 확인하며 중간 모델 polling을 하지 않습니다. #18/#20 인계는 [T14B 인계 문서](docs/issue-51-handoff.md)를 참고합니다.

```bash
PYTHONFAULTHANDLER=1 uv run --extra model mc-diamond pilot-wood --config configs/wood_pilot.yaml --output runs/pilot-signal-49
```

자연 G1 snapshot에서 빈 인벤토리로 시작해 나무 곡괭이를 만들고 조약돌 3개를 직접 채굴·획득합니다(2026-11-10 변경, 이전 목표는 원목 4개). 설정당 첫 128결정은 critic만 학습합니다. 실행 코드가 고정 목표를 NanoJev 입력에 전달하며 7B/Jev/Astra를 호출하지 않습니다. #49의 활성 상한은 에피소드당 **1,800틱**이고 실제 경과 상한은 제공 설정에서 15분입니다. 브리지의 `--budget-ticks 1800`은 양의 정수인 예산 축소만 허용하며, 생략한 G1 기본값은 3,600틱입니다. 같은 공개 초기 actor/critic과 난수에서 Choice LR 1e-4/3e-4만 바꿔 각 1,024결정·128결정 rollout 8회로 학습합니다. 짧은 에피소드 경계에서는 rollout을 유지하고, GAE trace와 보상 ledger는 새 에피소드로 연결하지 않습니다.

파일럿 설정의 `discovery_reward: 0.05`는 local 목표 원천 블록(조약돌이면 stone, 곡괭이가 없으면 원목도 포함)이 처음 보일 때 종류당 한 번 지급합니다. reset에 이미 보인 종류와 재발견은 제외합니다. 옵션 기본값은 0이고 PLAN §8.1 기본 local/full 보상은 유지합니다. 이 옵션을 켠 평가는 학습과 같은 ledger로 보상을 계산하며 가중치를 업데이트하지 않습니다. 본 학습 적용은 별도 사용자 결정입니다.

공통 이동 후보는 각 경로의 **마지막 좌표 중심 3차원 거리 16블록 이내**에서 현재 `visible=true`인 비공기 블록을 종류·개수로 설명합니다. 개수가 적은 순, 동률은 이름순으로 최대 8종이며 없으면 `none`입니다. 과거 기억만 남은 블록이나 도착점에서 새로 보일 숨은 블록은 포함하지 않습니다. 모든 그룹에 같은 설명을 제공하고 후보 ID·경로·순서·mask를 유지합니다.

공통 초기 평가 10회와 설정별 학습 후 10회로 예정 분모는 30입니다. 평가 난수 15000–15009는 세 단계에 공통이고 학습 기본 난수 11015와 구분합니다. 서버 오류만 같은 snapshot/평가 난수로 최대 1회 재시도하며, 실패·오류·미실행 슬롯과 모든 attempt 비용을 보존합니다. 실제 초기 성공이 2–8회를 벗어나면 학습 전에 멈춥니다. 성공 수→예정 10슬롯 전체의 평균 완료 틱(실패는 1,800틱)→학습/수치·평가 attempt 오류 수→기본 LR 순으로 선택하며 불능 설정은 제외합니다. 평균 틱 차이가 `2 × sample SD(초기 10슬롯 틱, 실패=1800) × sqrt(2/10)` 미만이면 시간은 동률입니다. 동률 폭을 초기 평가 후, 학습 전에 manifest에 고정합니다. 모두 불능이면 보류합니다. 성적 상승 자체는 완료 조건이 아닙니다.

`--output` 아래 `baseline/manifest.json`, attempt별 `.jsonl.gz`, `summary.json`, 복원용 공개 초기 `initial.safetensors`를 남깁니다. 기존 baseline은 덮어쓰지 않습니다. 전체 관측·후보·선택·사건·보상·전이·PPO 진단은 압축 trace에 있고 stdout은 JSONL 단계 요약입니다. 학습 중 actor는 본 학습 checkpoint로 저장하지 않으며 종료 시 초기 heads를 복원·hash 확인합니다. 파일럿 경험은 본 학습 30,000결정에서 제외됩니다.

#49 실행 자체가 #15의 원인 수정 추가 파일럿 허용량을 소진합니다. **2026-11-11 사용자가 별도로 승인한 예외는 서버 기동 실패로 미완료된 LR1e-4 보완 실행 한 번**입니다. 기존 `--output`에 `--correction-reason "승인된 서버 기동 복구" --correction-lr 0.0001`을 붙이면 기존 `baseline/`을 보존하고 독점 생성한 `correction/`에 LR1e-4만 처음부터1,024결정/8update와 후평가10회를 실행합니다. 원래 초기10회·등록된 시간동률폭과 LR3e-4 후평가는 참조하며 재실행하지 않습니다. 같은 config/snapshot/훈련·평가 seed/입력규칙/모델revision·가중치/초기heads hash를 검사하고, 이미 유효한 LR1e-4·다른 LR·중복 보완 실행은 거부합니다. 이전 실패 LR1e-4 오류도 최종 선택의 오류 수에 포함하고 원래30슬롯과 보완10슬롯을 구분합니다.

`progress.json`은 실행 중 attempt·trace·update 위치를 원자적으로 기록하며 Python faulthandler를 켭니다. native crash는 자동 재실행하지 않고 남은 위치를 사용자에게 보고합니다. 중단 지점의 정확 재개 기능은 없습니다.

설정별 시작 상태의 저장된 특징으로 update 0–8의 후보 확률·정규화 엔트로피를 비교합니다(추가 backbone 호출/표집 없음). 학습 에피소드 앞/뒤 절반 성공·실제/실패 포함 틱과 발견 보상 횟수, 곡괭이 보유·돌 첫 관측/채굴/드롭 획득 틱을 기록합니다. MC critic EV는 끝까지 유효하게 완료된 에피소드의 할인 실제 return과 당시 예측으로 계산합니다. bootstrap이 필요한 운영 절단·무효 궤적은 제외하고, 표본이 없거나 return 분산이 0이면 EV는 null입니다. 학습과 초기/학습 후 평가 지표는 분리합니다.

2026-11-10 후속 사용자 지시로 실제 #49 실행을 승인했습니다. 변경된 브리지의 시계 63조건 재인증·정보 감사·관련 T04/T05 회귀가 모두 통과한 뒤 파일럿을 시작합니다. 백그라운드 실행기는 단계별 종료 코드를 기록하고 실패하면 다음 단계로 가지 않습니다. 종료 시 `codex queue --resume`으로 같은 대화에 완료/실패 이벤트를 보내 결과 보고를 재개합니다. 모델이 중간 로그를 반복 조회하지 않으며, 실제 상태는 실행 폴더의 `background-status.json`을 따릅니다. PC와 로컬 Codex daemon이 계속 실행 중이어야 자동 재개할 수 있습니다.

서버 기동 timeout은45초를 유지합니다. timeout 때 최근 Java stdout/stderr64KiB와 최대5초/1MiB의 jstack 결과(도구 부재/실패 포함)를 관리자 `worlds/server/rpc-errors.log`에 남기고 소유한 Java를 SIGKILL한 뒤 최대5초 안에 회수를 확인합니다. reset의 `Server.restore`에서만 같은 snapshot을 다시 복원해 한 번 재기동하며, 두 번째 timeout·회수 실패·다른 서버 오류는 중단합니다. 중간 에피소드의 경험/ledger를 새 reset에 이어 붙이지 않습니다. 실패/복구 시간은 attempt 전체 실제 경과 시간에 포함하고, 관리자 진단은 정책 입력에 제공하지 않습니다.

`configs/wood_pilot_mock.yaml`은 **공개 NanoJev + scripted mock 게임**입니다. 물리나 학습 성능의 검증이 아닙니다. 모델 파일 없이 개발 검사에서는 기존 tiny model을 다운로드 경계에서 대체하며 공통 CLI/RPC/PPO는 실제 코드를 사용합니다. 실제 실행 근거와 미실행은 PROGRESS.md를 따릅니다.

## 실제 Minecraft 실행

이 작업공간에는 사용자의 EULA 동의 후 Minecraft 1.16.5, Fabric Loader 0.16.14, Carpet 1.4.44를 `worlds/server/`에 설치했습니다. Java 21.0.12.1·Node 24.20.0·Mineflayer 4.39.0에서 실제 연결을 확인했습니다. Linux의 `flock`으로 서버 디렉터리 사용을 잠급니다. 출처와 정확한 해시는 `third_party/README.md` 및 로컬 `worlds/server/installation.json`에 있습니다.

서버는 loopback에서만 열리며 기본 포트는 `25565`입니다. 봇은 해당 서버의 `server.properties`의 `server-port`를 읽습니다. 별도 worktree의 동시 검증은 runtime/snapshot 복사본과 서로 다른 포트를 사용합니다(T05A 검증은 `25566`). 로컬 봇은 `auth: offline`이며 계정 로그인·비밀번호·토큰을 사용하지 않습니다. Microsoft 계정 인증이나 공개 서버 운영을 검증한 결과가 아닙니다.

`worlds/server/server.properties`의 `allow-flight=true`가 필요합니다. 정지된 공중 상태를 서버의 벽시계 기반 비행 추방으로 오인하지 않게 하는 설정이며 Survival 플레이어에게 비행 능력을 지급하지 않습니다. backend는 누락 시 시작을 거부하고, 이 값도 시계 fingerprint에 포함합니다.

Carpet freeze만으로는 침수 중 플레이어 산소가 계속 줄었습니다. 자체 확장 `bridge/pausemod/`는 Carpet의 활성 틱 조건에 맞춰 플레이어 tick·이동을 멈추고, 초기 로그인 상태 패킷은 별도로 보냅니다. 설치된 Fabric 서버 라이브러리로 빌드합니다.

```bash
python3 bridge/pausemod/build.py
```

T05A의 `advance`에는 이 빌드에 포함된 관리자 전용 `mcdiamond_step`이 필요합니다.
이 명령만 서버 실행 큐로 전달하고 Carpet의 정상 20틱/초 step을 요청합니다.
보행 물리를 먼저 완료하고, 관리자 nonce를 같은 클라이언트 연결로 되돌려
선행 이동 패킷이 서버 실행기에서 처리된 뒤 활성 틱을 시작합니다.
입력 확인은 서버의 다음 틱 대기를 끝내므로 두 50ms 타이머의 위상이 만나도 틱을 놓치지 않습니다.
보행 활성 틱의 상한은 클라이언트 물리 타이머라 정상 20틱/초를 넘지 않습니다.
nonce는 지정 봇에만 보내며 플레이어·동결·중복 실행을 검증합니다.
틱 종료 후 남은 블록/metadata/인벤토리 변경과 드롭 위치를 기존 watcher에
전송합니다. 드롭의 상대이동 기준도 갱신하며 tracker 주기나 게임 틱은 추가하지 않습니다.
이 패킷들에 이어 같은 연결로 nonce와 전후 게임 틱을
보냅니다. bridge는 그 수신과 보행의 클라이언트 물리 틱을 기다린 뒤 매 틱 관측하며,
일치하지 않는 틱은 실제 경과량을 보존하고 실패합니다. 결정 경계 pause 검사는 유지합니다.
정책 RPC에는 콘솔 명령이나 이 확인 패킷을 제공하지 않습니다. 이전 확장 jar와
인증서를 재사용하지 말고 새로 빌드한 뒤 63조건을 인증해야 합니다.

시설의 시선은 검증한 공개 표적에 맞춥니다. 각 기본 조작은 틱 상한 안에서
실제1틱과 즉시 관측을 수행한 뒤 정지 상태로 인벤토리 I/O를 기다립니다.
완료 대기는5500ms이고 미완료면 창을 닫은 뒤 다시5500ms까지 기다리며 실제 경과 시간에 기록합니다. 완료 뒤 다시 관측해
중단을 검사하며, 확인되지 않으면 다음 조작을 실행하지 않고 실패 사건을 남깁니다.
제련의200활성틱 대기와 결정 경계 pause는 유지합니다.

고정 관리자 장면(wait20/100/200 각3회)의 처리량은 새 출력 폴더에서 측정합니다.
자연 과제 성공이나 모델/PPO 처리량의 검증은 아닙니다. 최종 로그 회귀는
`--logs <JSONL 경로들>`로 같은 `벽시계=a×결정수+b×틱수` 식을 사용합니다.

```bash
uv run python tools/measure_t05a.py --output artifacts/t05a-timing-new
uv run python tools/verify_tick_sync.py --output artifacts/t05a-sync-new
```

두 번째 명령은 관리자 진단 loader로 침수 첫 틱의 산소, 화로 첫 틱의 점화,
드롭 둘째 틱의 위치를 pause/콘솔 조회 전에 캡처해 서버 실제 상태와 비교합니다.
진단 후 C4를 복원하며 이 검사 자체로 정지 인증서를 발급하지 않습니다.

bridge·mod·설정·snapshot을 바꾼 뒤에는 그 fingerprint로 63조건·정보 감사·관련 회귀를
다시 확인해야 합니다. T06도 T05A 인증을 승계하지 않고 새로 인증했습니다.

snapshot이 없는 새 설치에서만 `uv run mc-diamond prepare-world --config configs/minecraft.yaml --start X Y Z`로 C4/G1–G3를 만들고, 사용자가 G4 시작 칸을 확인한 뒤 `--g4 X Y Z`로 G4만 만듭니다. 기존 snapshot 덮어쓰기는 거부합니다. 이 작업공간은 2026-11-08 사용자가 고른 고정 월드로 준비했습니다(#36). Java 1.16.5, 시드 `-5755571633112603064`, 시작 블록 `-110 65 105`, G4 시작 블록 `-146 12 96`(다이아가 있는 자연 동굴)입니다. 시드·동굴·광석 위치는 운영자 정보라서 정책에 주지 않습니다. 결과는 선정된 고정 환경에서의 성능이며, 다른 월드 일반화는 검증하지 않습니다. 이전 시드 `20261102` 환경은 Git에서 제외한 `archive/seed-20261102/`에 보존합니다. 월드·snapshot·실행 산출물도 Git에서 제외합니다.

자연 G2/G4 가능성 진단(#36)에서는 사용자가 후보 번호만 고르고, 실행과 판정은 코드가 합니다. 결정 대기 중 게임이 정지되므로 실제 경과 상한은 적용하지 않습니다. 이 기록은 학습·성능 결과에 쓰지 않습니다.

```bash
uv run mc-diamond smoke-macros --config configs/g2_natural.yaml --select human > artifacts/issue-36/human/g2.jsonl
uv run mc-diamond smoke-macros --config configs/g4.yaml --select human > artifacts/issue-36/human/g4.jsonl
```

```bash
uv run mc-diamond verify-clock --config configs/minecraft.yaml
uv run mc-diamond smoke-episode --config configs/minecraft.yaml
uv run mc-diamond smoke-movement --config configs/minecraft.yaml
uv run mc-diamond smoke-macros --config configs/macros.yaml
uv run mc-diamond audit-information --config configs/minecraft.yaml
```

각 명령이 서버를 시작하고 종료합니다. `verify-clock`은 평지·제련·드롭·용암·낙하·침수·화염에서 0/5/10초를 각각 3회 검사합니다. 실제 위험 상태가 준비됐는지, 위치 오차 0.001블록과 다른 상태·사건·틱이 보존되는지 판정합니다. 전부 통과한 실행만 검증 기록을 원자 저장하며, 코드·게임 의존성·Java/Node 버전·서버 설정·snapshot hash가 바뀌면 다시 검사합니다. 모의 backend를 실제 정지 근거로 사용하지 않습니다.

인증서와 별개로 reset 및 매 행동의 결정 경계에서 입력을 해제하고 서버·클라이언트 상태와 틱의 불변을 다시 확인합니다. 이동 종료에서는 양쪽 플레이어 위치도 0.001블록 이내로 일치해야 합니다. 정지 중 받은 최신 이동·방향 패킷은 서버 스레드에서 보관하고 다음 활성 틱에 vanilla 검증을 거쳐 적용합니다. 패킷의 순서를 보존하고 텔레포트 전 요청은 비우며, 정지 중에는 위치를 바꾸지 않습니다. 상태가 바뀌거나 서버 위치가 따라오지 못하면 backend 오류로 중단합니다. 인증이 없는 step과 summary는 `clock_mode=unverified`, `pause_verified=false`이며 실제 smoke는 exit 1입니다. 63회 검증과 경계 확인을 통과한 실행만 `paused`로 표시합니다.

`smoke-episode`는 초기 실행 연결 진단입니다. 실제 목재 수집은 `smoke-macros`를 사용합니다. 활성 틱과 실제 경과 시간을 분리하고, 지원하지 않는 행동의 실패도 실제 한 틱을 실행해 기록합니다.

`smoke-macros`는 고정 목재 목표에서 현재 노출 원목의 대상·작업량 후보와 관측 지도 접근 경로를 최대 16개 제공합니다(종류별 자리 배분, PLAN §5.2). 원목을 보지 못하면 관측한 같은 높이의 길에서 탐색하고, 직접 확인한 드롭을 먼저 회수합니다. 보유 도끼 장착, 선택한 노출 군집 최대 8블록/400틱 채굴, wait 20/100/200틱을 지원합니다. 채굴 완료 패킷은 Mineflayer의 벽시계 타이머 대신 실제 활성 틱에 맞춰 보내고, 서버 블록 갱신·드롭 생성·자기 수집·인벤토리 증가를 연결합니다. 매 기본 조작에서 관측을 갱신하고 위험·파손·실패·시간·사망에서 멈춥니다.

첫 후보를 실행하는 진단이며 행동 모델 성능이나 PPO 결과가 아닙니다. 후보 ID·내용·순서·mask와 상한 전 후보 수·종류별 잘린 수, 단일 후보의 확률 1, 모든 결정의 `macro_steps`를 기록하고 actor 전이는 0입니다. 0후보는 실제 wait와 failed 사건을 남깁니다. 선택 무효화는 원 후보·선택·대기 사건/비용과 actor 제외·trace_mask=0을 보존하고 새 관측에서 재선택합니다. 선택 요청 수와 실행 결정 수를 구분하고 중복 사건 ID는 오류로 거부합니다. 목표의 직접 획득과 보유량이 충족돼야 exit 0이며 미인증 정지는 exit 1입니다.

자연 G1과 분리한 실제 매크로 회귀는 `uv run mc-diamond smoke-macros --config configs/macros.yaml --diagnostic-fixture wood`로 실행합니다. `wood_tool`은 도끼 장착, `wood_break`는 마지막 내구도, `wood_hazard`는 채굴 뒤 노출되는 용암, `wood_drop`은 직접 채굴한 드롭의 독립 대기, `empty`는 0후보를 준비합니다. 관리자 준비이며 `diagnostic_fixture` 사건에 `natural_task=false`와 준비 활성 틱을 기록합니다. `wood_drop`의 드롭 이동·초기 속도/획득 지연 설정도 진단 준비에만 적용합니다. 실패/위험 장면의 exit 1은 수집 성공과 구분합니다.

전체 재현 명령은 `uv run python tools/verify_t04.py --output artifacts/t04-new`입니다. 새 폴더에 명령·코드 hash·stdout/stderr·결과를 보존하고, 시계 63조건 → 확장 정보 감사 → 실제 공개 CLI → 실제 상태 진전으로 유도한 취소·재선택을 확인합니다. 취소 검사는 전체 realtime 운용 인증이 아닙니다. 성공·실패 모두 기준 G1 reset을 시도하고 복원 실패도 기록합니다. 개별 검사는 끝에 `clock`, `information`, `macros`를 붙이며, 정보 감사 전에 같은 코드의 시계 인증이 필요합니다. 보고서 작성만을 위해 이 명령을 재실행하지 않습니다.

`smoke-movement`는 같은 실행기에서 관측된 바닥·발/머리 공간만 연결해 최대 8개 경로를 만들고 첫 후보를 실행합니다. 같은 높이에서 최대 16블록/400 활성 틱이며, 위험·공개 경로 변경·진행 정체에서 멈춥니다. 얼음·꽁꽁 언 얼음·살얼음·푸른 얼음은 관측하되 제동 거리 검증 전에는 보행 지면으로 사용하지 않습니다. 후보 경로, 원본 관측 ID, 지도 버전, 중단 근거, 실제 이동 거리/틱/경과 시간과 안정 경계를 출력합니다. 최소 한 번의 안정된 경로 완료가 있어야 exit 0이며, 이는 행동 모델의 성능 검증이 아닙니다.

최종 summary의 `movement_steps`에도 후보 ID·원본 관측 ID·지도 버전·사건·경로·중단 근거·이유·실제 틱·경과 시간·거리·안정 경계를 결정별로 보존합니다. smoke는 후보/결과의 근거 연결과 사건 출처를 검사하며 누락·불일치는 `invalid_step`입니다.

`audit-information`은 관리자 채널에서 벽 뒤 광석/용암의 실제 장면을 준비합니다. 정책은 일반 observe/step으로만 접속하며 노출 전 관측·후보·경로·실행/중단 결과가 같아야 합니다. 벽을 연 양성 대조, 보이는 원목 군집 채굴·드롭 회수, 독립 도끼 장착·20/100/200틱 대기·드롭 대기·0후보를 검사합니다. 드롭의 무작위 흩어짐 좌표/사건 ID를 제외하고 종류·수량·정책 상태·경로·중단 근거를 비교하며, 대기/장착 사건이 없는 응답도 거부합니다. 이 장면의 원목은 관리자 진단용 배치이며 자연 C4 성공이 아닙니다. 원본 snapshot을 보존하고 진단 후 reset으로 기준 월드를 복원합니다. 실제 정지 인증이 없으면 감사가 통과하지 않습니다. 제작·설치·화로·철 채굴 감사도 같은 공개 실행 흐름에서 비교합니다. 하강·터널 감사는 후속 티켓입니다.

지형 관측은 결정 시점에 눈에서 반경 32블록(매크로 중 매 틱 정지 검사는 반경 8)의 셀 중심으로 광선을 보내 처음 만나는 충돌 표면/위험에서 끊습니다. 지나간 공기·비충돌 식물과 첫 표면만 기억하고 미로딩 셀은 막힌 것으로 취급합니다. 유리·부분 충돌 블록을 보수적으로 가리개로 취급하며 숨은 이웃의 모양·청크 전체·시드·관리자 로그를 경로 판단에 쓰지 않습니다. `hidden_hazard_peek=false`를 기록하며 reset은 지도·방문·최근 결과를 초기화합니다.

수동으로 서버만 열 때는 실험 CLI를 종료한 뒤 아래 명령을 사용합니다. 확장 모드는 기동 시 정지 상태로 시작하며, 콘솔의 `stop`으로 저장·종료합니다.

```bash
cd worlds/server
flock -n .mc-diamond-owner java -Xms512M -Xmx3G -jar fabric-server-launch.jar nogui
```

제작 진단은 다음 명령을 사용합니다. `production`은 빈 인벤토리와 관리자 배치 원목·돌·철광석에서 시작합니다. 목표의 관측 가능한 전제조건을 하나씩 후보로 제시하고 매번 선택하며, 전체 사슬을 하나의 매크로로 실행하지 않습니다. 기본 smoke의 결정적 첫 후보 선택이며 S 선택기나 모델 성능 결과가 아닙니다.

```bash
uv run mc-diamond smoke-macros --config configs/production.yaml --diagnostic-fixture production
uv run mc-diamond smoke-macros --config configs/g2.yaml
uv run python tools/verify_t05.py --output artifacts/t05-new clock information production boundaries g2
```

공유 `src/mc_diamond/recipes.json`의 레시피만 사용합니다. 제작 출력은 1–8개이고 레시피 출력 단위의 배수이며, 설치/장착·투입·회수는 별도 후보로 각각 최대 400틱입니다. 현재 보이는 작업대·화로와 재료·도구·연료·지지면을 실행 직전 검사합니다. 화로 상태는 직접 연 창의 기억이며 경과 시간으로 출력을 추측하지 않고 다시 열어 확인합니다. `provided_inventory`, `direct_acquired`, `direct_crafted`, `direct_smelted`로 시작 보유량과 직접 사건을 분리합니다. 직접 제련은 이 에피소드에서 선택한 화로에 넣은 입력과 실제 출력 회수가 연결된 경우만 기록합니다.

`production_no_tool`·`production_no_fuel`·`production_hazard`는 전제조건/위험 진단용이며, 실행기의 `boundaries` 검사가 해당 행동을 명시적으로 선택해 거부·실제 시간·취소/재선택을 검사합니다. `iron`은 제공된 돌 곡괭이와 배치 철광석 진단입니다. fixture 없는 `configs/g2.yaml`만 고정 자연 G2 snapshot에서 시작하고 활성 상한 12,000틱을 유지합니다. 관리자 지원 진단을 자연 G2나 C4 성공으로 합치지 않습니다. 검사기는 G2 직접 철광석 3개 획득이 없으면 실패하며 최종 기준 C4 reset을 시도합니다. 매번 새 출력 경로를 사용합니다.

하강 진단은 다음 명령을 사용합니다. `stair_down`은 선택한 방향으로 최대 4계단·400틱을 내려가며, 위 칸을 파야 아래 칸이 보이므로 숨은 공간을 미리 조회하지 않습니다. G3는 철 곡괭이 보유·y=5–12 관측 안전 지면·20틱 유지(`safe_hold`)로 완료합니다.

```bash
uv run mc-diamond smoke-macros --config configs/g3.yaml
uv run python tools/verify_t06.py --output artifacts/t06-new clock information stairs g3 g2 g2-directions
```

`stairs`는 관리자 장면이며 자연 과제 결과가 아닙니다. `g2`·`g2-directions`는 고정 G2의 접근 가능성·철 노출·실패 구간 진단이고, 자연 철3 직접 획득은 T07 #8의 인수 조건이므로 미달해도 이 검사의 실패로 합치지 않습니다. 시계 인증 전의 실행은 `pause_verified=false`인 사전 검사입니다.

탐색·다이아 진단은 다음 명령을 사용합니다. `tunnel`은 선택한 방향과 단면(1×2 또는 1×3)으로 최대 8칸·400틱을 같은 높이로 파 나가며, 새로 노출된 다이아·목표 광석과 관측 위험에서 멈춥니다. G2(철)와 G4(다이아)는 목표 광석의 생성 상한 위에서는 계단, 그 안에서는 새 보행·tunnel·계단 후보를 받습니다. `configs/g4.yaml`은 고정 G4 snapshot(y=11 준비 공간, 철 곡괭이)에서 18,000 활성 틱·실제 45분 상한입니다.

```bash
uv run mc-diamond smoke-macros --config configs/g4.yaml
uv run mc-diamond smoke-macros --config configs/g4.yaml --diagnostic-fixture diamond
uv run python tools/verify_t07.py --output artifacts/t07-new clock information tunnels diamond g4 g2
```

다이아 성공(`diamond_success`)은 자연 에피소드에서 관리자 검증 로그가 광석 직접 파괴·철 이상 서버 도구·그 광석의 드롭·인벤토리 획득 사건을 모두 잇는 경우만입니다. 관리자 로그는 마지막 결정 뒤에만 읽으며 정책 입력에 들어가지 않습니다. `diamond`·`diamond_given` fixture는 관리자 배치·지급 진단(`natural=false`)이라 성공으로 세지 않습니다. G4 smoke에서 다이아 성공은 필수가 아닙니다. 자연 G2 철 3개(`admin_verified.iron_ore ≥ 3`, `configs/g2_natural.yaml`)는 T07 인수 조건이며 사전 등록한 상한·종료 기준은 DECISIONS 2026-11-08 절에 있습니다.

## 목표 처리와 규칙 선택기 S (T08)

설정에 `planner`가 없으면 `goal`이 고정 목표이고, 재계획 사건(완료·연속 실패 3회·목표 활성 3분·매크로 20회)마다 같은 목표를 새 ID로 다시 채택합니다. `planner: {backend: scripted, outputs: [...]}`를 넣으면 모의 계획기의 JSON 응답을 GoalRegistry가 검사하고, 오류면 한 번 재생성한 뒤 규칙 복구 목표(위험 근처 escape, 아니면 explore)를 씁니다. 결정마다 `goal_decision` 기록과 summary의 계획기 오류·재생성·복구 분자/분모, 출처별 진행(`progress_by_source`), 목표별 결과(`goal_outcomes`)가 남습니다. 실제 7B·Astra 계획기는 T09에서 연결합니다.

`--select rule`은 규칙 기반 선택기 S(`s-rules-v1`)입니다. 결정마다 규칙 version/hash와 후보별 비교 키를 남기며 확률·모델 정보는 null입니다. S 경험은 actor 학습에 쓰지 않습니다.

```bash
uv run mc-diamond smoke-macros --config configs/pilot.yaml --select rule
```

## 평가 슬롯 (T12)

`evaluate`는 예정 슬롯(핵심 C4 22 또는 축소 14, G4 6, 별도 S 1)을 실행하고 슬롯마다 결과 하나를 남깁니다. 서버 오류만 같은 snapshot·난수로 1회 재시도하고, 비용 중단·불가 군도 미실행으로 분모에 남습니다. 지금은 S만 실제 선택기이고 A/B/J/F는 mock backend의 대체 선택기입니다.

```bash
uv run mc-diamond evaluate --config configs/evaluation_mock.yaml --groups A,B,J,F,S --task C4,G4
```

## 문서

| 문서 | 내용 |
| --- | --- |
| [스펙 이슈 #1](https://github.com/sion0507/Minecraft_RL/issues/1) / [PRD.md](PRD.md) | 확정된 구현 스펙과 테스트 경계 |
| reports/ (로컬 전용) | 티켓별 최신 보고서·코드 가이드 PDF 한 쌍, Git 제외 |
| [PLAN.md](PLAN.md) | 상세 실험 규격과 구현 순서 |
| [DECISIONS.md](DECISIONS.md) | 확정한 결정과 근거 |
| [GLOSSARY.md](GLOSSARY.md) | 도메인 용어 |
| [AGENTS.md](AGENTS.md) | 에이전트 작업 규칙과 예정 명령·폴더 구조 |

## 저장소 관리

API 키·로컬 환경값은 Git·문서·로그·실험 lock에 넣지 않습니다. Jev 모델 API 비용 상한은 J/F·진단·실패·재시도 포함 총 US$5입니다.
F 접근·추가 시간·GPU/PC 점유·Astra 별도 비용을 본 학습 전에 우선 확인합니다. S 규칙은 본 학습 전 lock에서 고정하고 B/J/F 결과를 보고 조정하지 않습니다. S 선택 연산·7B 계획 호출·GPU/PC 점유·실행 비용도 사전 예산에 포함합니다. 기존 180시간은 재산정 기준이며 충분성은 미확인입니다. Astra 지출 상한도 아직 미승인입니다. F 불가 시 미실행과 관련 연구 질문 미검증을 남깁니다. 이번 문서 수정은 학습·유료 호출·결제 실행 승인이 아닙니다.
[.gitignore](.gitignore)는 비밀 파일, 가상환경·캐시, 다운로드 모델·게임 바이너리, 월드·체크포인트·실험 산출물을 제외합니다.
설정·실험 lock·의존성 lockfile은 비밀값을 제거한 뒤 버전 관리합니다.
외부 코드·프롬프트는 명시적 허용 범위에서만 재사용하고 출처와 변경점을 기록합니다.
