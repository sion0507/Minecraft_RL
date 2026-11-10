# 확정한 결정

문서 버전: v1.4-core-F-S
수정일: 2026-11-10 (Jev 총 상한 US$10·#12 Jev 연결·sampling 고정·ledger; 이전 2026-11-09: T08 목표 처리·규칙 복구·S 선택기 #9와 실제 검증 사전 등록, #38 병합·종료와 실제 검증의 T08 이관, T07C 후보 상한 16개·종류별 자리 배분 #38, #36·#37·#8 종료, T07B 한 칸 단차 이동·검증 사전 등록; 이전: T07 tunnel·다이아 판정·자연 G2 사전 등록, G2 1차 결함 수정·2차 사전 등록, 연구용 고정 월드 교체 결정)

현행 결정은 2026-10-10 기록이다. 같은 날의 S 필수 진단 보완이 과거 선택 S=규칙 계획/규칙 행동 정의를 대체하며 핵심 F/조건부 7B 학습 결정은 유지한다. 아래 과거 F 제외·계획기 학습 미허용·최종 23회/축소 17회 문구는 당시 결정의 이력이며 해당 부분은 현행 결정으로 대체한다. 과거 기록은 삭제하지 않는다.

## 2026-11-10 — #15 실제 파일럿 사용자 중단

사용자가 실제 실행을 여기까지 멈추고 의미를 설명하라고 요청했다. 619결정·4update에서 중단하고 재실행하지 않는다. 학습 연결 확인과 성능 개선/설정 선택 미검증을 구분한다. 공개 원본은 고정hash가 유지되지만 중단 시 메모리의 초기 heads 복원 hash는 미확인이고 중간 학습 checkpoint는 없다. #15의 전체 실제 수락 검증/이슈 종료는 완료로 표시하지 않는다. 재개·추가 실행 범위는 사용자의 명시적 요청 후 다시 정하며 자동으로 새 campaign이나 추가 파일럿을 시작하지 않는다.

## 2026-11-10 — #15 T14 목재 파일럿 구현·실제 실행 사전 고정

- 사용자 `이슈 15 $implement` 요청으로 현재 main `f48ccf1`에서 구현하고 로컬 커밋한다. #13/#14 Closed를 확인했고 #15/#1 본문·댓글, PLAN §§6.1–6.2/7.1/10/11.3과 GLOSSARY를 읽었다. 문서에 이미 확정된 실험을 구현하며 새 연구 설계/설정 탐색을 추가하지 않는다. push/PR/merge/이슈 종료는 승인 범위에 없다.
- 기존 run_episode·후보·NanoJevSelector·EpisodeLearner·자연 G1 reset을 재사용한다. 고정 목표는 collect/oak_log/4/source=fixed이며 계획기/API를 호출하지 않는다. 실제 config는 configs/wood_pilot.yaml(자연 G1, 빈 인벤토리, 3,600틱, 실제 경과 에피소드 상한900초)이다. 기존 configs/pilot.yaml의 1개 smoke 목표는 바꾸지 않는다.
- 두 설정은 Choice LR 1e-4/3e-4뿐이고 나머지 PPO 기본값은 동일하다. 공개 초기 actor/critic을 저장·복원하고 각 설정에서 optimizer/RNG를 새로 시작한다. 제공 설정의 학습 난수11015, 평가 공통15000–15009는 실행 전에 manifest에 기록한다. 본 학습 난수11과 파일럿 평가를 구분한다.
- 1,024 수집 결정은 실제 selection 요청 수로 제한한다. 취소 요청도 이미 선택·시간을 소비한 수집 결정으로 세고 executed_decisions와 별도 보고한다. 유효 actor/critic·무효 전이는 별도다. flush_on_finish=False에서 에피소드 경계의 보상 ledger/trace는 끊되 rollout은 유지해128결정 완전 update8회를 수행한다. smoke-ppo의 기본 finish 부분 update는 유지한다. PPO 보고에 Choice 자체의 gradient norm을 추가해 critic gradient와 구분한다.
- 초기10+설정별후10=30슬롯, 서버 오류만 같은 snapshot/seed로 최대1회 재시도한다. 평가 중 학습하지 않는다. 성공 수→성공이 있는 동률 설정의 성공 평균 활성 틱→학습/수치 오류 수→1e-4로 선택한다. 불능 설정은 제외하고 모두 불능이면 선택을 보류한다. 성적 상승/성공률 기준을 추가하지 않는다.
- 공유 learner를 사용하는 파일럿의 EpisodeSummary.actor_transitions는 reset 이후 누적값과 종료값의 차이로 에피소드별 수를 보고한다. 설정 전체 누적값은 유지한다. 실제 진행 중인 이전 버전의 원시 episode 요약은 누적값이므로 합산하지 않고 개별 transition.actor_valid와 설정 합계를 대조한다. 이 보고 수정은 정책·보상·학습에 영향을 주지 않는다.
- baseline/correction 디렉터리를 배타적으로 만들어 기존 실행을 덮어쓰지 않는다. 원인 수정은 명시적인 correction-reason과 기존 baseline 근거가 있을 때 같은 campaign에서 최대1회, 선택/default LR하나·최대1,024결정·초기/후10회다. LR 자체 문제를 수정한 override의 이유도 같은 필드에 기록한다. 자동 추가 파일럿/본 학습은 없다. 운영 중단의 정확 복구는 #19 범위이며 자동 재개를 넣지 않는다.
- 각 attempt의 전체 JSONL을 표준 gzip(level1)으로 보존해 반복 관측 로그의 공간을 줄인다. 요약에는 학습/수치·실행 오류, 무효·미업데이트 경험, 활성/실제 시간, 직접 원목, 선택/계획 호출, API비용0을 기록한다. 실패·미실행 슬롯도 분모에 남긴다. 정상/실패 종료 후 공개 초기 heads를 다시 로드해 hash로 복원을 검증하며 파일럿 actor/경험은 공식30,000결정에서 제외한다.
- bridge/runtime/mod/정보 관측/기준 snapshot은 바꾸지 않는다. 실제 파일럿의 각 step에서 기존 정지 인증을 확인하며 이전 시계 결과를 새 bridge 인증으로 표현하지 않는다. 실제 실행은 artifacts/issue-15/real의 자연 G1만 사용한다. 실제 학습·평가 결과는 PROGRESS에 기록한다. 진단 실패나 결과 때문에 snapshot/시드/후보 규칙을 조정하지 않는다.

## 2026-11-10 — #14 게시·PR 병합·이슈 종료 승인과 #12 통합

- 사용자가 #14의 push·merge·이슈 종료 후 마무리를 명시적으로 요청했다. 아래 최초 구현 시점의 로컬 전용/Open 상태는 당시 이력이다. 최종 상태는 GitHub PR/#14 조회, `artifacts/issue-14/publication.json`과 최신 로컬 PDF를 따른다.
- 원격 main에 먼저 병합된 #12(PR #47, `a48253a`)를 보존한다. feat/issue-14-ppo에서 원격을 merge하고 CLI의 smoke-ppo/smoke-jev 및 EpisodeConfig의 PPO/Jev 설정을 모두 유지한다. DECISIONS/PROGRESS 양쪽의 기록도 모두 보존한다. #12의 최신 사용자 결정(US$10·모드·ledger)을 되돌리지 않는다. 유료 호출은 이번 게시 범위에 없다.
- 통합 코드로 전체 pytest·mypy를 확인한 뒤 PR로 게시한다. bridge/runtime/모델/실제 게임은 변경하거나 재실행하지 않는다. reports는 PDF2개만 최신 상태로 교체하고 Git에서 제외한다.

## 2026-11-10 — #14 T13 사건 보상·저장 전이·GAE·PPO 연결

- 사용자 `$implement 이슈 14 먼저` 요청으로 현재 main(`b0d239a`)에서 구현·로컬 커밋한다. 선행 #9/#11 Closed와 #14/#1 본문·댓글, PLAN §§6.2/8.1/12를 확인했다. 기존 공개 CLI 흐름 및 짧은 공개 보상/GAE/actor-critic 수치 예제가 합의된 검사 경계다. 새 브랜치·push·PR·병합·이슈 종료는 요청 범위에 없다.
- 기존 run_episode에 선택적인 LearningObserver를 연결한다. 기본 smoke/evaluate는 진단 보상을 유지한다. 연구 보상 ledger는 목적별로 분리하고 reset에서 초기화한다. full 진행 원목은 여섯 log 종류를 한 보상으로 묶고, 제공 재고는 최초 진행 집합에 포함한다. 의미 목표는 정규화 kind/target이며 수량·방향·ID를 제외한다. 보상 ledger가 GoalRegistry의 완료/전환을 막지 않는다.
- **보상 시각:** 현재 RPC는 사건별 발생 틱을 보내지 않는다. 시간 비용은 실제 n틱 각각, 직접 사건/완료 보상은 반환되어 확인된 경계의 마지막 틱에 배정한다. 이 규칙으로 틱별 할인합과 gamma^n을 계산하고 sparse_reward_timing을 기록한다. 원시 물리 사건 발생 시각을 복원했다는 주장이 아니다. bridge/runtime/관측 규칙은 바꾸지 않으며 새 시계 인증을 주장하지 않는다. 향후 발생 시각을 직접 할인하려면 bridge의 사건별 시각 계약과 실제 재검증을 별도로 추가해야 한다.
- 다이아 보상은 적절한 관측 도구로 파괴한 광석 사건과 bridge가 귀속한 직접 드롭 획득을 연결한다. acquired.position은 블록 좌표가 아닌 드롭 생성 위치이므로 bridge와 같은 블록 중심 반경2를 사용한다. 실제 acquired에는 entity_id가 필요하다. 자연 광석의 최종 성공은 기존 관리자 검증을 유지한다. 관리자 데이터는 정책/가치 입력에 넣지 않는다.
- 저장 State는 관측·목표·후보 ID/내용/순서/mask와 frozen 특징/context를 복사한다. PPO는 후보를 재생성하지 않고 trainable Choice logits를 다시 계산한다. full 목표 변경은 다음 채택 목표/후보로 bootstrap하고 trace를 유지한다. 운영 절단도 유효 다음 상태로 bootstrap하며 rollout 마지막 유효 trace는0이다. 취소/fallback은 actor 제외·trace 단절, 단일/0후보·critic-only는 actor 제외, 유효 critic 전이는 유지한다. 0후보의 실제 강제 wait는 값 계산에만 쓰고 제공 후보 기록은 빈 집합을 유지한다.
- PLAN 기본 PPO 설정을 사용한다. actor advantage 정규화는 유효 복수 선택만 대상으로 하며 단일 유효 actor의 정규화 값은0이다. actor 전이가 없으면 Choice gradient/Adam 갱신을 생략한다. 독립 local/full critic 중 해당 목적만 gradient를 받는다.
- `smoke-ppo --config configs/ppo_smoke.yaml`은 공개 NanoJev+mock 게임의 2결정 연결 진단이다. 실제 model을 쓰며 결과 actor를 저장하거나 본 학습에 이어 쓰지 않는다. Astra/Jev 유료 호출을 쓰지 않는다. 본 학습/커리큘럼/원자 복구/lock/최종 평가는 #18–#24의 범위다.
- 최초 전체 회귀248개 통과 뒤 연결 코드 점검에서 드롭 좌표 오해를 발견했다. 실제 생성 좌표 사례로 RED를 재현해 위 반경2 규칙으로 수정했고, 기존 실제 로그5개를 새 ledger로 재생했다. 최종 수정본의 검사·독립 리뷰·후속 수정은 PROGRESS에 별도 기록한다. 실제 게임의 사건→보상→학습 전체 연결은 #15/#16에서 확인한다.
- 독립 리뷰의 사망 전이 P1을 재현했다. 실제 bridge는 death에서 danger=true라 stable_boundary=false다. 안전 지면은 비종료 bootstrap의 조건이며 신뢰 가능한 task terminal까지 제외하는 조건이 아니다. invalid·검증된 clock을 유지하고 `(stable_boundary or task_terminal)`로 유효 전이를 구분한다. local/full 공개 CLI 사망2검사 RED→GREEN, 같은 Spec 에이전트의 수정 재검토에서 해결을 확인했다.

## 2026-11-10 — Jev 총 상한 US$10과 #12(T11) 실행 승인 (사용자 결정)

- 사용자가 OpenRouter 키를 `~/.config/mc-diamond/jev.env`(`JEV_API_KEY`, 권한 600)에 저장하고, Jev 모델 API 총 상한을 US$5에서 **US$10**으로 올렸다. 연결·진단·A/J·J/F 최종 평가·실패/재시도를 모두 합친 총액이며, 이 안에서 테스트와 실제 구현을 마치라고 #12 구현과 실제 호출을 승인했다("10달러 이내에 테스트 및 실제 구현까지 완료"). 계정 키 한도도 US$10으로 확인했다(`/api/v1/key` limit 10).
- 이전 US$5 문구는 이 결정으로 대체한다. Astra 지출은 여전히 별도 ledger·별도 승인이며 이 결정에 포함되지 않는다. 충전은 하지 않는다.

## 2026-11-10 — #12(T11) Jev 실제 연결·선택 모드·비용 ledger (구현 선택)

main `b0d239a`에서 worktree 브랜치 `issue-12-t11`. 원래 checkout의 미커밋 #14 변경은 건드리지 않았다. #12/#1 본문·PLAN §6.3·§7.3·§9.3·§11.1.1을 확인했다. 관련 ADR은 없다.

- **요청(`jev.request_body`):** `POST https://openrouter.ai/api/alpha/decisions`, `model=typesafe/jev-1.13`, `state`=공통 `public_state`+목표 JSON 문자열, `questions.action={type:choice, instructions:공통 INSTRUCTIONS, criteria}`. NanoJev와 같은 `choice_input`을 쓰고 바깥 형식만 바꾼다. Jev 전용 전략·안전 힌트 없음. API에 외부 mask가 없어 masked 후보 key는 빼고, 남은 key는 저장 index(`a0`, `a2`…)를 그대로 써서 저장 candidate_id에 일대일 대응한다. 유효 후보가 1개면 유료 요청을 보내지 않는다.
- **응답 검증:** `answers.action.type=="choice"`이고 `choice`가 보낸 key 안이어야 한다. 아니면(schema 오류·refusal·후보 밖 ID) 같은 body로 1회만 재요청하고, 다시 실패하면 공통 고정 fallback(첫 유효 후보, `selector_mode=fallback`, `error=model_response_invalid`)을 쓴다. 통신 오류(HTTP 0/408/429/5xx/524/529)는 1·2초 backoff로 최대 3회 시도한 뒤 에피소드를 `jev_error`로 멈춘다. NanoJev로 조용히 대체하지 않는다. 401/402/403/404는 `jev_unavailable`(외부 원인 기록용), 그 밖의 4xx는 `jev_error`(요청/설정 버그)로 구분한다.
- **분포와 선택 모드:** `probabilities`가 보낸 key 전부를 정확히 덮고, 유한·비음수·합 1(반올림 허용오차 1e-3)일 때만 전체 분포로 인정한다. 그 외는 native choice로 기록하고 probabilities=null이다. `confidence`는 분포로 쓰지 않는다. TypeSafe Choice 문서(2026-11-10 재확인)는 `probabilities`=모든 선택지의 전체 분포·합1, `choice`=최고 확률 선택지, `confidence`=분포의 퍼짐에서 계산한 값으로 정의한다. 실제 응답 6건(2·3후보)이 모두 완전·합1이고 choice=argmax였다. 그래서 PLAN §9.3 표의 첫 줄을 적용해 **J/F 주 모드를 로컬 temperature 1 categorical sampling으로 고정**한다(`EvaluationConfig.jev_mode` 기본 `sampling`, 시드 목록은 A/B와 공유). 성능 결과를 보기 전의 고정이다. 실제 J/F 슬롯에 Jev 선택기와 슬롯 시드를 연결하는 것은 T19/T22다.
- **비용 ledger(`jev.Ledger`):** 모든 요청(실패·재시도·진단 포함)을 `~/.local/share/mc-diamond/jev_ledger.jsonl`에 append한다. 모든 checkout·worktree가 같은 파일을 쓰고 Git 밖이다. `usage.cost`(HTTP 200)가 있으면 확인 비용, 없으면 미확인으로 남기고 상한 계산에는 요청당 `max_call_usd`(US$0.001)를 청구한 것으로 친다. 요청 전마다 `청구합 + max_call_usd ≤ cap_usd − reserve_usd`를 확인하고 넘으면 `budget_exceeded`로 보내지 않는다. `reserve_usd`는 이 명령이 돌리지 않는 예정 슬롯(F 포함) 예약분이다. 값은 T19가 실측 결정당 비용으로 정한다. F 전용 상한은 만들지 않는다. `evaluate`는 `jev_ledger`를 주면 그 청구합에서 이어서 상한을 센다. 계정 측 사용량은 무료 `GET /api/v1/key`로 smoke 전후에 대조한다.
- **비밀:** 키는 `JEV_API_KEY` 환경변수 또는 위 파일에서만 읽는다. ledger·오류 메시지·로그에 남는 원본 오류에서 키 문자열을 `<redacted>`로 바꾼다. 요청 header는 기록하지 않는다.
- **`smoke-jev`:** `configs/jev_smoke.yaml`(mock Minecraft·후보 2개 fixture·Jev sampling) reset→관측→목표→후보→실제 Jev 선택→실행→요약 뒤 `jev_summary`에 확인일·endpoint·요청/응답 모델·제공처·응답·분포 판정·argmax 일치·fallback·ledger·계정 사용량 전후를 남긴다. exit 0=검증, 1=접근 불가(미검증 항목·Q2/Q3/Q4 기록)·오류·fallback, 2=키 없음(요청 없음).
- **범위 밖:** A/J 6상태 진단과 A/J 5분 실행(§7.3)은 실제 초기 actor 고정 후 Task 9(T13/T14)다. Astra는 별도 승인 전이라 호출하지 않았다. 실제 Minecraft 위 Jev 실행은 하지 않았다(mock Minecraft만).

## 2026-11-09 — #44 게시·병합·종료와 #1·#20 인계 댓글 (사용자 결정)

- 사용자가 #44 결과 확인 뒤 push → PR 병합 → #44 종료와 #1·#20 결과 댓글을 명시적으로 요청했다("1,2 하고 마무리해"). 원격 main(`e9e84ae`)이 작업 시작점과 같음을 확인했다. 게시 직전 pytest·mypy를 다시 확인한다. 게임·모델은 게시 때문에 다시 실행하지 않는다.
- 수정 뒤 독립 재리뷰는 하지 않는다(사용자가 선택 항목 3을 고르지 않음). 리뷰 보류 2건은 다음 bridge 변경 때 다룬다.
- 커밋·PR 본문에는 이슈 자동 종료 키워드를 쓰지 않고, #44는 `gh issue close`에 근거 댓글을 달아 닫는다.

## 2026-11-09 — #44 관측 반경32·공통 256칸 요약 (구현 선택)

사용자 `/implement 이슈 44` 요청으로 main `e9e84ae`에서 브랜치 `feat/issue-44-observation`을 만들었다. #44/#1 본문·PLAN §4.2를 확인했다. 관련 ADR은 없다. push·PR·병합·이슈 종료는 요청 범위가 아니다.

- **스캐너(`bridge/terrain.js`):** 눈에서 반경 안 모든 칸 중심으로 광선을 보내고, 어떤 광선이든 도달한 칸이 visible이라는 기존 의미를 유지한다. 바꾼 것은 구현뿐이다. 칸 캐시를 문자열 Map에서 정수 배열로, 광선 상태를 배열에서 스칼라로 바꿨다. 반복 상한 32를 없애고, 목표 칸에 맨해튼 거리 안에 도달하지 못하면 예외로 멈춘다(조용한 누락 금지). 같은 가림(supercover) 규칙이다. 합성 평지·무작위 동굴·터널 각 2위치에서 반경8 결과가 이전 코드와 칸·순서까지 같았다. 합성 평지 반경32는 이전 방식(상한128) 1,062ms → 약115ms다(CPU 합성 측정, 실제 서버 아님).
- **갱신 시점과 의미:** 결정 관측(reset·observe·각 step의 시작 재검증과 끝)은 반경32 전체 스캔이다. 매크로 안의 매 틱 정지 검사는 반경8 근거리 스캔이다(이전 반경8과 같은 정지 판단). `visible`은 언제나 마지막 스캔의 집합이다. 매크로 중에는 먼 칸이 기억에 남고 visible이 아니다. 근거리 상태는 정책에 가지 않는다(관측에 `observed_map`이 없어 보내면 검증 실패). 관측 시각은 visible=이 관측의 활성 틱, 기억=그 이전 스캔이다. 실행 전 재검증은 기존대로 step 시작의 전체 스캔과 `map_version` 비교다. 매크로 안에서 부르는 보행(드롭 줍기)은 그 매크로의 근거리 스캔을 이어 쓴다. 모든 군이 같은 bridge 규칙을 쓴다.
- **정책 지도(`observed_map`):** 기억한 비공기 칸은 전부, 공기(`air`·`cave_air`·`void_air`)는 봇 칸에서 Chebyshev 18 안만 보낸다. Python 경로는 최대16걸음(머리·점프 칸 포함 18 안)이므로 후보 생성에 필요한 정보는 같다. 실행기는 전체 기억을 계속 쓴다. 이유: 반경32 지표면 한 번에 공기 약7.4만 칸이고, RPC 상한 16MB·로그·검증 시간이 감당하지 못한다. 정렬은 좌표 숫자순으로 바꿨다(이전 locale 문자열 순).
- **탐색 완료:** 공기 창 때문에 "목표 시작 관측에 없던 칸" 비교가 창을 다시 들어온 칸을 새 칸으로 센다. 그래서 bridge가 `discovered_open`(이 에피소드에서 처음 관측했을 때 통과 가능했던 위치 수)을 보내고 explore는 그 증가 16 이상으로 판정한다. 목표 자원 새 관측은 기존대로 위치 비교다(비공기라 창에 잘리지 않음). 같은 규칙의 의미 보존이며 반경32에서 탐색 완료가 더 쉬워지는 것은 반경 변경의 결과다.
- **공통 모델 입력(`model_input.public_state`):** Qwen/Astra 계획기와 NanoJev/Jev가 같은 상태를 받는다. 이전에는 계획기=현재 visible만 dict 64개, NanoJev=기억 포함 배열 64개로 달랐다. 새 `memory`는 비공기 기억을 (block, passable, support, hazard) 종류로 묶고 종류별 `total`과 가까운 칸 좌표를 `now`(현재 visible)/`past`(기억)로 나눈다. 전체 256칸이다. 종류는 개수 작은 순으로 남은 자리의 균등 몫을 받는다. 그래서 몇 개뿐인 광석·위험·설비는 바닥이 많아도 모두 들어가고, 바닥은 남은 자리에서 가까운 순이다. 목표·모델별 힌트는 없다. 관측하지 않은 칸을 채우지 않는다. 계획기 JSON도 공백 없는 구분자로 바꿨다. 프롬프트에 `memory` 의미 한 줄을 더했다(PROMPT_HASH 변경). 규칙 hash는 `model_input.py` 파일 sha256(`INPUT_HASH`)이고 `planner_loaded`에 남긴다. lock 고정은 #20이다. 8192 상한 초과는 기존대로 실패이며 자르지 않는다.
- **테스트 경계:** 반경32 대각/상하 도달·벽 뒤 미조회·근거리 재스캔·공기 창·reset(JS), 바닥 1,600칸 속 광석·용암·작업대 보존과 계획기/NanoJev 동일 상태(Python), explore 카운터. 이동 물리 fixture는 장면 기억을 근거리(8) 스캔으로 만든다(물리 판정은 반경과 무관하고, 무한 평지 하늘 7.5만 칸 스캔이 장면마다 반복되어 64초가 걸렸다).

### 실제 검증 범위 사전 등록 (#44, 실행 전 기록)

변경 코드를 커밋한 뒤 같은 커밋으로 각 1회 한다. 고정 선택기·계획기 없음(측정 5만 실제 Qwen/NanoJev). bridge가 바뀌어 fingerprint가 달라지므로 63조건을 새로 인증한다. 서버 오류만 같은 명령 1회 재실행하고 모든 시도를 남긴다. 실행기 결함이면 멈추고 수정·보고한다. 자연 G2/G4 성공은 기록만 한다. 반경8 결과와 합치지 않는다. 출력은 `artifacts/issue-44/real-1/`.

|순서|명령|내용·판정|
|---|---|---|
|1|`tools/measure_observation.py game`|C4·G1·G2·G3·G4 snapshot reset→observe 3→wait20. 칸 수·프레임·RPC 지연, G4 시작 다이아 visible 여부(난이도 변화 기록, snapshot 불변), 정지 반복 관측 동일. 시계 미인증 상태의 진단|
|2|`verify_t07.py ... clock information tunnels steps diamond g4 g2`|63조건 인증 → 정보 감사 → tunnel·계단 장면·다이아 fixture → 자연 G4·G2|
|3|`verify_t06.py ... stairs g3`|계단 장면·자연 G3|
|4|`verify_t05.py ... production boundaries`|생산·경계(도구/연료/위험/취소/reset)|
|5|`verify_t04.py ... macros`|자연 G1 원목과 관리자 매크로 장면|
|6|`tools/measure_observation.py models`|1의 관측으로 실제 Qwen 토큰(새/이전 64칸)·1회 호출 지연·GPU, NanoJev 경로 토큰·forward 지연·GPU, 두 모델 동시 적재 메모리|

- **실행 중 변경 기록(2026-11-09 22:15):** 2번 `verify_t07`은 63/63 인증과 정보 감사를 통과한 뒤 `tunnel_long-8x2` 장면이 `tunnel_completed`(8칸·16블록)로 정상 종료했다. 그러나 검사기 단언 "정책 지도 칸 수가 늘어야 한다"에서 멈췄다(15,232 → 9,230). 원인은 #44의 공기 창이다. 봇이 8칸 이동하면 보내는 공기 칸 수가 줄 수 있다. 비공기 표면은 382 → 425로 늘었다. 실행기 결함·서버 오류가 아니라 이전 전체 기억 전송을 가정한 검사기 결함이다. 단언을 "파낸 칸이 모두 열린 칸으로 관측된다"로 바꾸고 저장 결과에서 통과를 확인했다. bridge는 바뀌지 않아 인증서가 그대로 유효하다. 같은 커밋으로 남은 `tunnels steps diamond g4 g2`만 `t07-rest`에 1회 실행하고, 통과한 시계·정보 감사는 다시 하지 않는다. 계획기 기록용 Python 수정(`bf19d8a`)은 고정 선택기 실행의 동작을 바꾸지 않는다.
- **실행 중 변경 기록(2026-11-09 23:05) — 원목 후보 결함:** 측정 6(모델)에서 C4/G1 시작 후보가 0개임을 발견했다. 반경32에서 원목 12개가 보이지만 모두 16걸음 경로 밖이고, `generate_resource_candidates`는 광석만 탐색 보행으로 넘기고 원목은 빈 후보(강제 대기)를 냈다. 반경8에서는 원목이 안 보여 탐색 보행 8개였다. 보이지만 다가갈 수 없으면 모든 자원에서 탐색 보행으로 넘기도록 고쳤다(Python만, fingerprint 불변). 이 규칙은 이전부터 있던 "보이지만 접근 불가" 경우(T04 wood_hazard: 이전 강제 대기 10회 → 보행 후보 5개)에도 적용된다. 그래서 같은 커밋으로 `verify_t04.py macros`를 `t04-after-wood-fix`에, 자연 G1 고정 선택기(`smoke-macros --config configs/macros.yaml`, 12결정)를 1회 실행한다. 다른 이미 끝난 실행은 후보 0개가 원목 목표에서만 나왔으므로(저장 관측 재계산: T07/T06/T05 영향 없음, diamond_given 0→0) 다시 하지 않는다. 측정 도구의 Qwen 토큰 계산 결함(dict 키 수를 셈)을 고치고 측정 6을 다시 한다.

## 2026-11-09 — #44 관측 확대 등록·Astra 비교 시 실연결·#10 게시/종료 승인 (사용자 결정)

- 사용자가 관측 확대 검토안을 새 이슈로 등록하고 해당 구현 때 실제 검증하도록 요청했다. [#44](https://github.com/sion0507/Minecraft_RL/issues/44)에 반경32/입력 최소256개 수준·정보 보존·스캐너/표현 개선·공통 입력·토큰/처리량·실제63조건/정보 감사/회귀·G4 시작 노출 변화 확인을 기록했다. 지금은 등록만 하며 구현/게임 검사를 시작하지 않는다. 현재 반경8/64개는 그대로다.
- 사용자가 현재 #10 작업의 push·PR 병합·이슈 종료를 명시적으로 승인했다. 기존 로컬 e887f4a를 보존해 feat/issue-10-planner에서 게시한다. GitHub 작업은 사용자 후속 지시로 gh CLI만 사용한다. 원격 main을 확인하고 전체 pytest/mypy·diff를 검증한 뒤 PR 병합·상태 확인을 수행한다.
- Astra 실제 연결·응답·지원 설정·사용량/과금·지연 검증은 사용자의 결정대로 **추후 비교 단계**로 이연한다. 단순 접근 확인을 위한 유료 호출은 지금 하지 않고 미실행을 #10 종료 장애로 삼지 않는다. 사용자의 연결 가능성 예상은 실제 성공 증거가 아니다. 호출0/실제 미검증과 mock backend 검증을 구분한다.
- 실제 비교 호출 직전에 제공처/endpoint/모델·버전/지원 설정/응답/요율·확인일/호출·금액 상한을 확인·기록한다. 키·계정·별도 Astra 지출 승인은 유지하며 이번 게시/종료가 유료 호출·결제 승인은 아니다. F 핵심 비교와 Jev합산US$5·PC 예산·학습량·평가 분모는 유지한다. #1/#10/#17/#20 및 PLAN/PRD에 같은 결정을 기록하고 #10 초기 실접근 미완료를 실제 완료로 체크하지 않는다.
- 최종 commit/push/PR/merge/이슈 종료는 원격 조회와 artifacts/issue-10/publication.json 및 최신 로컬 PDF에서 구분한다. 보고서 상태 갱신 때문에 게임/모델을 재실행하지 않는다. 최종 게시 검사는 개발 pytest/mypy만 수행한다.

## 2026-11-09 — #10 T09 공통 고정 계획기 연결 (구현 선택)

- 선행 #9의 Closed/completed와 #10/#1 본문·댓글, PLAN §5.1·5.5·5.6·7.4·14를 확인했다. 관련 ADR은 없다. 사용자가 `$implement`로 구현·검증·두 축 리뷰·현재 브랜치 커밋을 요청했다. 현재 main에서 작업하며 push/merge/이슈 종료는 범위에 넣지 않는다.
- 기존 Planning/GoalRegistry와 run_episode를 재사용한다. local_7b/Astra는 같은 고정 자체 프롬프트·제한 관측 요약·task·검증 오류를 받으며 목표 JSON만 반환한다. 메모리는 거리순 관측 비공기 표면64·최근 방문32·결과8이다. 후보·관리자 정보·시드·숨은 광석/위험을 추가하지 않는다. knowledge=null이며 조건부 지식 조회·계획기 학습은 후속 진단/승인 없이 실행하지 않는다.
- Qwen 공식 Apache-2.0 배포 revision a09a35458c702b33eeacc393d103063234e8bc28을 고정했다. 13개 파일의 SHA-256을 설치·로드 때 확인한다. 기존 Torch/Transformers extra에 accelerate1.15.0/bitsandbytes0.50.2를 더한 planner extra는 model extra를 포함한다. 실제 CUDA NF4/double quant/BF16·frozen/eval, greedy(실효 온도0)·max_new_tokens256·입출력 합8192 상한이다. CPU/임의 가중치로 대체하지 않는다.
- 공개 smoke-planner는 mock/실제 게임을 구분하고 기존 고정 선택기로 목표→후보→실행→출처별 요약을 확인한다. 실제 G1 연결 진단을 8결정/240초로 제한했다. 게임 bridge/runtime/snapshot/fingerprint 입력을 바꾸지 않으므로 기존 인증을 확인하며63조건을 불필요하게 반복하지 않는다. 검증 후 G1 reset/observe와 서버 종료를 확인한다.
- 문서의 `smoke-planner --config configs/pilot.yaml`은 planner 설정이 없으면 고정 local_7b를 사용한다. 다른 명령의 고정 목표 동작은 유지한다. 이 기본값 경로도 공개 CLI에서 실패 재현 후 통과를 확인했다.
- Astra는 표준 라이브러리 HTTPS Chat Completions adapter를 제공하고 redirect를 차단한다. PLAN 후보의 공개 페이지를2026-11-09 재확인했지만 계정 접근·실제 버전/지원 설정/청구는 미확인이다. 유료 호출은 명시적 별도 승인/금액·호출 한도/제공처 검증 요청당 최악 금액과 ASTRA_API_KEY 없이는 실행하지 않는다. 영속 잠금·원자 ledger는 실패/재생성/재시작도 보수적으로 예약하고 자동 환불하지 않는다. 실제 상한 준수는 제공처의 검증된 요청당 비용 상한을 전제로 하며, 토큰 요율 추정을 실제 청구 확인으로 표시하지 않는다.
- 잘못된 목표는 한 번 재생성/공통 복구하지만 제공처 접속 실패·응답 계약 오류·승인/예산 부족은 별도로 중단한다. 실제 평가의 군별 backend와 Jev 연결/lock은 후속 티켓이다. 한 episode 설정의 Astra를 A/B/J/S에도 잘못 적용하지 않도록 실제 planner를 evaluate에 넣으면 거부한다. mock 평가/기존 scripted 설정은 보존한다.
- 테스트 경계는 #1에 승인된 공개 CLI 흐름·공통 Planner 계약이다. 실제 공개 모델과 게임 물리는 별도 실제 실행으로 확인한다. dict/list 목표 값이 set membership에서 TypeError를 일으키던 신뢰 경계 결함을 재현 후 수정했다.

## 2026-11-09 — #11 T10 커밋·푸시·원격 main 병합·이슈 종료 승인 (사용자 결정)

- 사용자가 두 축 code-review(Standards0/Spec0) 결과를 확인하고 "푸쉬하고 머지하고 이슈 클로스"를 명시적으로 요청했다. 앞 T10의 미승인/미수행 Git 상태는 당시 이력이며 이 요청으로 commit/push/PR/원격 main 병합/#11 완료 종료를 진행한다.
- 작업·커밋은 이 전용 worktree 브랜치에서만 한다. GitHub PR 병합을 사용하고 기존 main checkout의 파일·로컬 main ref·다른 세션은 변경하지 않는다. reports/와 모델·실행 산출물은 계속 Git 제외다.
- 병합 전 최신 origin/main·전체 pytest·mypy·diff 검사를 확인한다. 코드 충돌/실패가 있으면 먼저 해결하고 새 성공 근거를 확인한다. 게임/모델은 코드 변경 없이 보고서 상태 갱신 때문에 재실행하지 않는다. 실제 최종 commit/push/merge/issue 상태는 원격 조회와 #11 완료 기록/PDF로 구분해 남긴다.

## 2026-11-09 — 공개 NanoJev Choice/critic 연결 (#11 T10)

- 사용자 요청 범위는 이 독립 worktree의 구현·실행 검증이며 공개 모델/추가 Python·Node 의존성 다운로드가 승인됐다. main·다른 세션 파일, sudo·새 라이선스 동의·계정·키·유료 호출·본 학습·push/merge/이슈 종료는 범위에 넣지 않았다. 선행 #5의 실제 Closed와 #11/#1 본문·댓글을 확인했다. 관련 ADR은 없다.
- 공개 루트 step-400 `unified-games-v1`을 A/B의 초기 actor로 사용한다. immutable revision `047b927b30882a1138fc504821b82ac145a4b81a`, 초기 weights SHA-256 `f68c47d66998231b86b7e91b4ed5e82ae23acf104c8b7cd6d165c3ac7b7ffe1b`. 설치 때 사용한 설정/tokenizer/source/weights 9개를 고정 hash로 검사하고 strict loading하며 임의 초기 actor로 진행하지 않는다. MIT source 허용문은 third_party에 보존, 모델카드·Qwen Apache-2.0는 출처 문서를 따른다.
- `predict`는 inference_mode이므로 역전파 경로로 쓰지 않는다. 공개 원본의 segmented tokenization과 EOS pooling, norm/scalar/set attention Choice 구조를 필요한 Choice 경로에 적용했다. backbone만 frozen/no_grad, Choice와 새 독립 local/full critic만 trainable이다. `train()` 뒤에도 dropout 0·backbone eval을 유지한다. 저장 raw EOS 특징을 재사용해도 trainable Choice/logits는 매번 계산한다.
- critic은 mask가 true인 raw 후보 표현의 평균에 목적 one-hot 2개와 `log1p(남은 활성틱)/log1p(36000)`, `log1p(목표 활성 예산)/log1p(36000)`를 붙여 각자 hidden256/GELU/scalar로 계산한다. critic이 Choice의 norm을 공유하지 않아 critic-only는 actor에 gradient를 주지 않는다. 두 critic은 새 난수 초기화임을 로그에 명시하며 공개 actor와 혼동하지 않는다.
- 공통 입력은 검증된 Observation/Goal/CandidateSet만 받는다. 비공기 관측 표면 거리순64, 최근 방문32/결과8과 전체 표면·방문 수, 자기 상태/목적/예산/목표를 요약한다. 후보 params/내용/순서/max_ticks/stop_rule을 보존하고 a0…를 저장 ID에 매핑한다. masked 후보는 attention key·softmax·평균·sampling에서 제외한다. 예산/요약은 NanoJev/Jev 공통 의미이며 Jev가 외부 mask를 지원하지 않으면 비활성 key를 요청에서 빼야 한다. 후보 생성/경로/bridge는 변경하지 않았다.
- 입력 과장은 하지 않는다. 토큰 경로8192 초과는 실패하며 조용히 자르지 않는다. backbone 인코딩만 padded token32768 이내 chunk로 나눌 수 있고, 전체 후보 Choice는 함께 재계산한다. 이는 처리량/7B 동시 VRAM 보장이 아니다.
- 공개 `smoke-model`은 첫 저장 복수 후보로 실제 FP32/BF16 public forward/tokenization/EOS/logits를 비교하고 명시적인 수치 목표로 gradient·한 번의 head 업데이트·backbone 불변·단일 후보 full critic-only를 검사한 뒤 finally에서 초기 actor/critic을 복원한다. 이 optimizer step은 PPO/게임 보상 학습이 아니며 에피소드 actor_transitions는0이다. 새 `SelectionResult.actor_eligible`도 선택 자격일 뿐 실제 학습 전이를 뜻하지 않는다.
- model extra는 공개 코드와 같은 PyTorch2.14.0/Transformers5.17.0/Safetensors0.8.0, 전이는 uv.lock이다. 기본 모델은 CUDA/BF16이며 CPU/mock 모델로 조용히 대체하지 않는다. 게임 backend가 mock인 경우는 명시한다. 기본 pilot의 단일 후보만으로는 전체 gradient 진단을 완료하지 않고 exit1로 남긴다. 복수 후보용 `configs/model_smoke.yaml`은 서로 다른 관측 원목 대상 두 개의 mock 게임이며 실제 공개 모델을 사용한다.
- T10 범위의 head 저장/복원은 Safetensors와 revision·초기 weight hash를 쓰고 모든 key/shape/dtype/유한값을 검사한 뒤 교체한다. PPO/optimizer/RNG rollout 경계 복구·본 학습/checkpoint·실제 A/B evaluate 연결은 후속 티켓이다.

## 2026-11-09 — Pathfinder 이동 보류, 기존 이동으로 진행 (사용자 결정)

- **결정:** mineflayer-pathfinder는 지금 채택하지 않는다. 다음 이슈는 기존 T08 이동·매크로(`navigation.py`·`terrain.js`·`moveObserved`·`stair_down`/`tunnel`)로 진행한다. 위 #13 절의 "#10은 pathfinder 비교 확정까지 대기"는 이 결정으로 해소된다.
- **이유(검토 `artifacts/claude-pathfinder-review-2026-11-09/report.md`, Codex `artifacts/pathfinder-*-2026-11-09/`):**
  - 투시 센서: 시험 센서가 반경 8의 가려진 블록까지 `observed_map`에 넣었다. 자연 G2에서 보이지 않은 철 80칸이 정책 입력에 들어갔다. 엔티티·`blockUpdate` 통로도 남아 있다.
  - 위험 반경 미반영: PF 경로 계산은 반경 1.5를 모른다. 용암 옆 장면에서 7틱 만에 `observed_hazard`로 멈췄다(기존 방식은 우회해서 도착).
  - 목적지 미끄러짐: 블록에 들어서는 순간 완료되고 입력만 해제한다. 연속 단차에서 0.72블록 넘어갔다.
  - 저장 후보와 실행 불일치: 후보 `path`의 끝점만 쓰고 실행 때 다시 계산한다.
  - 달리기를 똑같이 끄면 공통 4장면 이득은 약 14%다(달리기 포함 24%, Codex 8장면 36.8%).
- **보존:**
  - 로컬 브랜치 `test/pathfinder-spike`(`4f436d7`)·`test/pathfinder-t08-compare`(`6b9e781`), 로컬 태그 `pathfinder-deferred-2026-11-09`(`6b9e781`). push하지 않았다.
  - Git 제외 `archive/pathfinder-2026-11-09/`: 두 브랜치 bundle, Codex worktree의 산출물, 검토용 수정 런타임. 무엇을 뺐는지는 `archive/pathfinder-2026-11-09/README.md`에 있다.
  - `artifacts/pathfinder-*-2026-11-09/`, `artifacts/claude-pathfinder-review-2026-11-09/`.
- **다시 꺼낼 조건:** 실험(자연 G2/G4·평가 슬롯 등)이 기존 이동의 한계 때문에 실패할 때. 예: 2칸 이상 낙하·틈·막힌 길에서 반복 무진행. 그때 교체를 다시 검토한다.
- **채택 전 필요한 작업:**
  1. PF 입력을 시야 전용 센서(`terrain.visible`+관측 기억)로 제한한다. 엔티티 비용을 끄고, 블록·청크 이벤트의 재계산은 관측 변화로만 일으킨다. 그 뒤 숨은 블록 변형 정보 감사를 실제로 통과한다.
  2. 위험 반경 1.5를 PF 경로 비용/금지로 넣는다. 실행 중단에도 서 있음/지지 확인을 쓴다.
  3. 목적지에서 정확히 멈추게 하고(중심 0.15·감속), `maxDropDown=3`으로 둔다. 달리기 사용 여부를 두 방식에 같게 맞춰 사전 등록한다.
  4. 실행이 저장된 후보 경로를 그대로 따르게 하고 브리지에서 재검증한다. 굴착은 기존 `dig()`(검증 기록·`ore_exposed`·`hazardNear`)를 쓰고, 설치·장착은 `operation()` 틱 회계를 쓴다. 실패 사유도 바로잡는다.
  5. 새 63조건 인증, 굴착·설치·파쿠르 중 정지 검사, 장면당 3회 이상 반복, 자연 G2/G4 동일 목적지 대조를 실행한다. 틱 이득은 원인별(달리기/경로/능력)로 나눠 보고한다.
  - 더 싼 대안부터 검토한다: 기존 이동에 달리기를 켜거나 2~3칸 낙하 단계를 추가한다.

## 2026-11-09 — #13 병합, #9·#13 종료 (사용자 결정)

- 사용자 지시로 `issue-13-t12`를 push하고 PR로 main에 병합한다. #13(수락 기준 mock 충족)과 #9(남은 S 슬롯 연결을 #13에서 해결)를 근거 댓글과 함께 닫는다.
- #10 T09(7B 계획기)는 pathfinder 이동 비교가 확정될 때까지 대기한다(사용자 결정).

## 2026-11-09 — T12 공통 평가 슬롯과 서버 오류 재시도 (#13)

구현 위치: `src/mc_diamond/evaluation.py`, CLI `evaluate --config <평가 설정> --groups <군> --task <C4,G4>`. 사용자 지시로 pathfinder 비교 결정을 기다리지 않고 진행했다. 슬롯 코드는 후보 형식을 읽지 않는다.

- **예정 슬롯(§9.3–9.5):** 핵심 C4는 A·B sampling 5(축소 3)+argmax 1, J·F 주 모드 5(축소 3)로 22/14개. G4는 A·B sampling 각 3으로 6개. S는 C4 결정적 1개를 별도 표(`s`)로 둔다. 합계 29/21이다. 규모(`scale`)·난수·예산은 평가 설정에서 결과 전에 고정하고, 본 실험 값은 T19 lock이 정한다. `--groups`·`--task`는 실행할 슬롯만 고르고, 각 슬롯의 ID·난수는 전체 일정에서 정해진 그대로다.
- **난수:** A·B sampling은 같은 5개(축소 시 앞 3개)를 공유하고, G4는 3개를 공유한다. J·F도 같은 목록을 기록한다(native choice면 외부 API 내부 난수는 통제하지 않는다). argmax와 S는 `fixed_seed`. 재시도는 같은 난수·snapshot이다. 지금 mock 선택기는 난수를 쓰지 않는다. sampling 선택기는 T10/T11에서 이 난수를 받는다.
- **시도:** 슬롯마다 attempt ID `<slot_id>:<n>`, 시도마다 새 bridge 세션과 reset, snapshot은 과제 snapshot 파일(mock은 fixture) sha256으로 기록한다.
- **서버 오류만 재시도(최대 1회):** `backend_error`·`timeout`·`protocol_error`. 행동 실패·사망·탐색 실패·계약 오류(`invalid_step` 등)는 재시도하지 않는다. 슬롯 결과는 마지막 허용 시도의 결과다. 최초 오류(`first_error`)와 모든 시도의 시간·비용을 보존한다. 재시도도 서버 오류면 `error`, 성공 0.
- **비용 중단:** 유료 군(J·F)은 시도 시작 전에 누적 비용이 `budget_usd` 이상이면 실행하지 않는다. 최초 시도면 `not_run`(`budget_stopped`), 재시도면 `retry=not_run_budget`이다. 둘 다 예정 분모에 남는다. 진행 중 에피소드의 비용 상한 중단은 Jev 비용 통제(T11 #12)가 맡는다.
- **불가 군:** Jev 불가면 J·F, Astra 불가면 F 슬롯을 `not_run`(사유 `jev_unavailable`/`astra_unavailable`)으로 남긴다. 분모에서 빼지 않는다.
- **성공:** 과제 목표가 `mine_diamond`면 `diamond_success`(관리자 검증)만 성공이다. 그 밖의 목표는 mock·smoke 설정에서만 쓰며 `goal_completed`를 쓴다. mock 실행이 하나라도 있으면 요약에 `mock: true`.
- **최고 진행 단계(§10):** 그 에피소드의 직접 사건으로 1 원목·2 돌 곡괭이·3 철 광석·4 철 곡괭이·5 y=5–12에서 20틱 safe_hold·6 다이아.
- **요약:** 표(`core_c4`·`g4`·`s`)마다 예정·성공·실패·오류·미실행·시도·재시도 사용/미실행·활성 틱·실제 시간·비용. S 진단은 따로 성공 x/1·최고 단계·시간·선택 수·7B 계획 호출 수·실패 사유·비용.
- **선택기 연결:** S는 T08의 규칙 선택기(`rule_select`)를 그대로 쓴다. A/B/J/F는 mock backend에서만 첫 후보 mock 선택기로 대신하고(J/F는 설정한 mock 결정당 비용), 실제 backend에서는 연결 전이라 설정 오류(exit 2)로 거부한다. T10/T11이 실제 선택기를 붙인다.
- **mock 서버 오류:** mock fixture의 `server_error_attempts`에 적은 attempt ID는 첫 step에서 `backend_error`를 낸다(검사용).
- **리뷰 반영(같은 날):**
  - **실행 순서:** 평가 블록 i마다 A·B·J·F를 i번째 난수로 교차 실행한다(§9.3). 그 뒤 A/B argmax, G4(난수마다 A·B), S 순서다. 슬롯 ID는 그대로다.
  - **예산:** `budget_usd`는 Jev 총상한(연결·진단·J/F·실패 포함)이다. 이번 실행 전 사용액은 `jev_spent_usd`로 넣어 같은 상한에 합친다. 그래서 군을 나눠 실행해도 상한이 다시 생기지 않는다. 사용액 ledger 자체는 T11이 만든다.
  - **S 비용:** S의 API 비용은 0이지만 7B 계획·GPU/PC 비용은 아직 측정하지 않았다. 그래서 S 진단에는 `api_cost_usd`만 숫자로 두고 `cost_usd`는 null로 둔다(§11.1.2, 0으로 표시하지 않는다).
  - **reset 상태:** 실제 backend는 저장소의 `worlds/snapshots/<과제>/snapshot.json` 해시를, mock은 fixture 해시를 기록한다. 파일이 없으면 어떤 시도도 시작하지 않고 설정 오류로 끝낸다.
  - **시작 실패 시간:** backend가 시작하지 못한 시도도 그 시간까지 실제 경과로 남긴다.
  - **입력 검증:** `--groups`·`--task`의 알 수 없는 값은 설정 오류(exit 2)다.
  - **잠정 CLI:** AGENTS의 최종 명령은 `--lock experiment_lock.json`이다. lock은 T19에서 생기므로 그 전까지 `--config <평가 설정>`을 쓰고, T19에서 lock 입력으로 바꾼다.
  - **범위 밖으로 남긴 것:** 파일럿(T14)·checkpoint 비교(T21)는 같은 `run_attempt`·슬롯 규칙을 쓰도록 그 티켓에서 연결한다. S의 36,000 활성 틱·실제 90분 상한은 C4 설정·lock(T19/T22)이 정한다. S는 유료 군이 아니고 불가 사유도 없어서, 지금 규칙으로는 미실행이 생기지 않는다. 오류·재시도에도 분모 1을 유지하는 것은 검사로 확인했다. 시드는 기록·재시도 일치까지만 한다. 선택기가 실제로 시드를 쓰는 것은 T10/T11이다.

## 2026-11-09 — #9 병합, 이슈는 Open 유지 (사용자 결정)

- 사용자 지시로 `issue-9-t08`을 push하고 PR로 main에 병합한다. #9는 #13 S 슬롯 연결이 남아 있으므로 닫지 않는다.

## 2026-11-09 — T08 목표 처리·재계획·규칙 복구와 S 선택기 (#9)

구현 위치: `src/mc_diamond/goals.py`(GoalRegistry·Planning·ActiveGoal), `selectors.py`(공통 ActionSelector), `rule_selector.py`(S), `episode.py`(연결). A/B/J/F/S가 같은 코드를 쓰고 계획기 제공처만 바뀐다. 실제 7B·Astra 연결은 T09(#10)다.

- **규칙 복구 목표(사용자 선택 "escape/explore"):** 관측 위험이 3블록 안이면 `escape`, 아니면 `explore`(target `space`). 제작 사슬의 단계를 고르지 않는다. 그래서 복구 출처의 진행을 계획 능력으로 볼 근거가 없다.
- **전제조건(사용자 선택 "즉시 전제조건"):** 지금 관측·인벤토리로 확인되는 것만 본다.
  - collect: cobblestone은 곡괭이, iron_ore는 돌 이상, 원목은 없음. mine_diamond: 철 이상 곡괭이. descend: 철 곡괭이 보유.
  - craft: 한 레시피의 재료×반복 수가 지금 인벤토리에 있고, 작업대가 필요하면 보유하거나 관측돼야 한다.
  - smelt(iron_ingot만): 보유·화로 투입·화로 출력의 철 합이 필요량 이상, 필요한 연료 보유(화로에 이미 투입했으면 면제), 화로 보유 또는 관측.
  - escape: 관측 위험이 3블록 안에 있어야 한다. explore: 없음.
  - 이미 보유량을 채운 collect/craft/smelt(제공 아이템 포함)는 `already_satisfied` 오류다. 제공 상태로 새 성공을 만들지 않는다.
- **`direction`:** explore에서만 받아 기록한다. 지금 후보 생성은 읽지 않는다(새 후보 규칙을 만들지 않기 위해서다). 쓰려면 모든 군 공통으로 따로 정한다.
- **형식:** JSON 객체 하나, 키는 `kind`·`target`(필수)과 `quantity`·`direction`(선택)만. 대상 목록은 `goals.TARGETS`. 수량은 collect 1–16, craft/smelt 1–8, 나머지 1. `direction`은 explore만(north/south/east/west). 오류 코드는 `invalid_json`·`invalid_format`·`already_satisfied`·`precondition`이고 메시지를 재생성 요청의 feedback으로 넘긴다.
- **재계획 사건(PLAN §5.1, 처음 일어난 것 하나):** 목표 완료 → 연속 실패 3회 → 목표 활성 3,600틱(3분) → 목표 매크로 20회. 실패는 그 스텝에 `failed` 사건이 있는 것(bridge의 실패 사건, 후보 0개 강제 대기)이다. 취소된 선택은 매크로·실패로 세지 않고 시간에는 포함한다.
- **한 번 재생성과 집계:** 최초 요청 오류 → 같은 결정에서 재생성 1회 → 다시 오류면 복구 목표. 분자/분모는 최초 오류/최초 요청, 재생성 오류/재생성 요청, 복구 사용/전체 목표 결정으로 각각 summary에 남는다. 결정마다 `goal_decision` 기록에 계기·근거 관측 ID·출처·계획기 모델/버전·원문 응답·오류를 남긴다.
- **출처 연결:** 목표 출처는 `fixed`·`planner`·`regenerated`·`rule_recovery`다. 각 매크로 증거·보상 기록에 `goal_id`·`goal_source`를 넣고, 직접 획득·제작·제련은 `progress_by_source`로 출처별로 센다. 목표별 시도·완료·시간·매크로·실패 수와 실패 사유별 수(`failure_reasons`)·채택 전 재생성 수(`planner_retries`)·종료 사유는 `goal_outcomes`(GoalStats)다.
- **완료 규칙:** collect·mine_diamond·craft·smelt는 목표 시작 뒤 그 목표의 직접 사건이 있고 보유량을 채웠을 때다(이전 단일 목표 규칙과 같다). descend는 기존 규칙. escape는 끝난 위치가 관측 위험에서 3블록 이상이고 중단 없는 20틱 `safe_hold`. explore는 목표 시작 때 관측에 없던 통과 가능 칸 16개, 또는 target 자원의 새 관측 칸이다.
- **후보:** escape는 보행(위험에서 3블록 이상이고 안전 지면이면 hold 20틱을 앞에), explore는 새 땅 보행(target이 철·다이아 광석이면 기존 광석 탐색 후보). 새 후보 종류·매크로는 없다. hold는 descend와 같은 후보(`navigation.hold_candidate`)다.
- **고정 설정 목표(계획기 없음):** `configs/*.yaml`의 `goal`은 과제 정의다. 계획기 출력이 아니므로 GoalRegistry 검사·재생성·복구를 거치지 않고, 재계획 사건마다 같은 목표를 새 ID(`<goal_id>:<n>`)로 다시 채택한다. 후보는 목표 ID를 쓰지 않으므로 T04–T07 궤적은 그대로일 것으로 예상한다(실제 실행으로는 아래 검증에서 확인). 계획기를 설정하면 `config.goal`은 에피소드 종료를 정하는 과제이고 계획기 목표가 후보를 정한다.
- **계획기 모의 backend:** `planner: {backend: scripted, outputs: [...]}`가 응답을 순서대로 내고, 다 쓰면 빈 응답(오류)이다. 모델·과금 주장 없음.
- **S 규칙(사용자 승인 순서, `s-rules-v1`):** 후보별 사전식 키 ① 최근 실패한 같은 행동(종류+경로 끝/대상/방향, 에피소드의 최근 실패 3개) ② 도달·절삭 지점이 관측 위험 3블록 안 ③ 목표 관련성(직접 수행 0: 목표 블록 채굴·제작·화로·hold, 준비·접근 1: 다른 채굴·장착/설치·관측 목표 자원/드롭/설비에 가까워지는 보행·descend의 계단·escape에서 위험에서 멀어지는 보행, 탐색 2, 일반 대기 3) ④ 작업량 큰 쪽 ⑤ 동률이면 저장 순서. 모든 후보가 최근 실패면 ①은 동률이 되어 무시된다. 공개 전제조건은 생성기와 마스크가 이미 적용하므로 S가 보는 후보는 모두 전제조건을 만족한다. 결정마다 `rule_version`·`rule_hash`(`rule_selector.py`만의 sha256)·후보별 키를 SelectionResult에 남기고 mode는 `rule_deterministic`, 확률·provider·model·usage는 null이다. 후보 1개는 공통 계약대로 확률 1이다. S 보상 기록의 actor 제외 사유는 `rule_selector`다.
- **공통 selector 계약:** selector는 `(observation, goal, saved, failures) → SelectionResult`이고, episode가 제시·마스크된 후보인지 검사한다(`invalid_selection`). 고정·사람·S가 같은 경로를 쓴다.
- **#13 슬롯 연결:** #13이 아직 구현되지 않아 이 티켓에서는 연결하지 않았다. #13 구현 때 `--select rule` 실행을 S 슬롯에 연결하고 #20 lock 전에 확인한다. 규칙 hash는 #20에서 고정한다.

### 실제 검증 범위 사전 등록 (#38에서 이관; 2026-11-09 사용자 승인으로 `1f081e3`에서 실행, 결과는 PROGRESS)

T08 코드를 커밋한 뒤 같은 코드로 각 1회 한다. 고정 선택기(첫 후보)·계획기 없음이다. bridge·fingerprint 입력이 바뀌지 않았으므로 4차 63조건 인증서를 쓴다. 실행 시 fingerprint가 인증서와 다르면 멈추고 보고한다(63조건 재인증은 따로 승인).

|순서|명령(`uv run python tools/...`, 출력 `artifacts/issue-9/real-1/<tool>`)|내용·판정|
|---|---|---|
|1|`verify_t07.py ... information g4 g2`|정보 감사(ore/lava 쌍의 정책 입력·후보·선택 동일; 입력 해시가 이전 기록과 다른 것은 `generated`·`truncated` 때문이며 실패 아님) → 자연 G4(다이아 성공은 기록만) → 자연 G2(철3 성공은 기록만)|
|2|`verify_t06.py ... g3`|자연 G3 하강|
|3|`verify_t05.py ... production boundaries`|관리자 생산 장면·도구/연료/위험/취소/reset 경계(생산 후보가 목표를 받으므로 포함)|
|4|`verify_t04.py ... macros`|자연 G1 원목과 관리자 매크로 장면|

- 자연 실행은 공개 CLI에 새 기록(`goal_decision`·목표 출처)이 들어간 것 외에 결정 궤적이 이전 고정 선택기 기록과 같은지 비교한다(#38 이후 첫 실제 실행이라 16개 후보 배분 영향도 함께 본다). 다르면 실패가 아니라 차이로 기록하고 원인을 조사한다.
- 실행기 결함(무한 반복·후보 0개 교착·정지 실패·사건/시간 누락), 정보 누출, 시계·reset 실패만 실패다. 실패한 검사는 승인 없이 다시 돌리지 않는다.
- 시계 검사(`clock`)는 넣지 않는다(인증서 유효). 서버 오류만 같은 snapshot으로 1회 재시도하고 두 시도를 모두 기록한다.

## 2026-11-09 — #38 병합·종료와 실제 검증의 T08 이관 (사용자 결정)

- #38에서 미룬 실제 정보 감사와 T04–T07 자연 실행 회귀는 T08(#9)을 구현한 뒤 함께 한다. #9 수락 기준에 이 항목을 옮긴다. 그때 범위를 이 문서에 먼저 등록한다.
- 사용자 지시로 `issue-38-candidate-cap`을 push하고 PR로 main에 병합한 뒤 #38을 닫는다. 실제 검증 항목은 #38에서 완료로 표시하지 않고 #9로 넘긴 것으로 기록한다.
- 사용자 지시로 스펙 이슈 #1과 #9·#23·#25 본문의 "최대 8개"·"0/1/8"·"0–8 분포"를 16개 기준으로 고치고, 각 이슈에 근거 댓글을 단다.

## 2026-11-09 — 후보 상한 16개와 종류별 자리 배분 (#38, 연구 명세 변경, 사용자 결정)

PLAN §2 기본 규격의 "후보 상한 8개"를 바꾸는 연구 명세 변경이다. PLAN v1.11·PRD v1.4·AGENTS.md·GLOSSARY("후보 자리 배분")를 갱신했다.

- **상한:** 16개(`schema.MAX_CANDIDATES`). A/B/J/F/S 모두 같은 생성·실행 규칙이다.
- **공통 함수:** 모든 후보 생성(보행·하강·광석 탐색·자원·생산·탈출, mock smoke 포함)은 `schema.allocate`를 거친다. 생성기 안의 `[:8]` 자르기와 자원 생성의 8개 중단은 없앴다. 생성기는 상한 없이 우선순위 순서로 만든다.
- **자리(사용자 선택 6/5/4/1):** 걷기(`move_observed`) 6, tunnel 5, 계단(`stair_down`) 4, 기타 종류 합쳐 1. 기타는 채굴·장착/설치·대기/hold·제작/제련/화로다.
- **빈 자리(사용자 선택 "생성 순서"):** 어떤 종류가 자리보다 적으면 잘린 후보를 생성 순서대로 넣는다. 남긴 후보는 생성 순서 그대로다. 그래서 첫 후보는 바뀌지 않고, 고정 선택기 궤적도 그대로일 것으로 예상한다(실제 실행으로는 아직 확인하지 않았다).
- **근거(구현 전 수치 선택):** 고정 월드 기록(#36·#37 자연 G2/G4, 사람 선택 실행 595결정)을 새 생성기로 다시 만들어 셌다. 상한 없는 종류별 최대는 걷기 8·tunnel 5·계단 8(4계단 4 + 1계단 4)이다. 595결정 전체에서 잘리는 수는 6/5/4/1이 걷기 24·계단 329, 5/5/5/1이 걷기 71·계단 282, 4/5/6/1이 걷기 163·계단 190이다. tunnel은 어느 경우에도 잘리지 않는다. 6/5/4/1은 서로 다른 걷기 방향을 거의 다 남기고, 이미 4계단으로 제시된 같은 방향의 1계단 작업량을 주로 자른다. 결과(성공률 등)는 보지 않았다.
- **상황별 결과(사용자 질문 "상황별로 종류가 다르지 않나"):** 표는 하나이고 상황에 없는 종류의 자리는 빈 자리가 된다. 고정 월드 730결정(T04–T07 기록 포함) 재생성 기준으로 16개를 넘는 것은 광석 탐색(242결정 중 126)과 노출 자원 채굴(44결정 중 3, 모두 T05 생산 실행의 돌 채굴)뿐이다. 노출 자원 3결정은 매번 채굴 10·접근 걷기 6으로 남았다. 하강(최대 16)·탈출(최대 5)·생산(최대 2)·걷기만(최대 12)은 잘리지 않는다. 채굴의 보장 자리는 1개뿐이다. **상황별 보장은 상황별 기록이 더 쌓이면 다시 정한다(사용자 결정).** 후보 생성 규칙은 본 학습 lock(T19) 전에 고정한다.
- **기록:** 저장 후보 집합(`candidates` 사건)에 `generated`(상한 전 후보 수)와 `truncated`(종류별 잘린 수)를 함께 저장한다. `generated == 남긴 수 + 잘린 수`를 schema가 검사한다. 후보 ID·내용·순서·마스크 규칙은 그대로다. `verify_t07.py`의 접근 보고에 0–16 분포·잘린 결정 수·종류별 잘린 수를 넣었다.
- **바꾸지 않은 것:** 매크로 상한(채굴 군집 8블록, tunnel 8칸, 제작 1–8개), bridge, 시계 fingerprint 입력. 후보 생성은 fingerprint 밖이라 4차 63조건 인증서가 유효하다.
- **실제 검증(사용자 선택 "구현만 하고 나중에"):** 정보 감사와 T04–T07 자연 실행 회귀는 이번에 실행하지 않는다. 다음 작업에서 범위를 사전 등록한 뒤 한다. 그 전까지 #38 수락 기준의 실제 검증 항목은 미완료다.
- **해소된 남은 결정:** #36 사람 선택 진단 시점은 #36 종료(같은 날, 8개 상한 진단 통과)로 해소됐다.
- **기록 형식:** `generated`는 기본값 없는 필수 필드다. 결정마다 기록을 schema가 강제한다. 그래서 #38 이전 로그의 저장 집합은 `CandidateSet`으로 읽히지 않는다. 이전 로그는 원시 JSON으로 읽는다(`measure_t07c.py`가 그렇게 한다).
- **측정 전용 의존성:** 토큰 측정에만 `tokenizers` 0.21.1을 `uv run --with`로 쓴다. 프로젝트 의존성(pyproject)에는 넣지 않았다. 토크나이저 파일은 NanoJev `unified-games-v1`(`047b927b…`)의 `tokenizer/tokenizer.json`이고, 도구가 sha256 `be756060…`을 확인한다.
- **남은 일:** 스펙 이슈 #1 본문과 #9(T08) 수락 기준의 "최대 8개"를 16개로 고쳐야 한다. GitHub 이슈 수정은 승인 후 한다.

## 2026-11-09 — #36·#37·#8 종료 (사용자 결정)

- 사람 선택 진단(G2 철3·G4 다이아 직접 채굴·획득)을 #36 통과 조건 충족으로 받아들인다. 두 성공 시도는 포트만 다른 복사본 설치(`worlds/human-copy/`, 25566)에서 했고, 그 설치에는 63조건 인증서가 없어 `pause_verified=false`였다. 이 사실은 그대로 기록에 남긴다. 본 설치에서 다시 하지 않는다.
- 사용자 지시로 PR #39를 main에 병합하고 #36·#37·#8을 닫는다. #8의 자연 G2 철3·G4 판정은 #36 기준(가능성 진단 + 사람 선택 진단)을 따른다. 고정 선택기 결과(G4 다이아 성공, G2 철 미달)는 기록만 한다.
- 남은 미실행: 최종 bridge(`a9a046a`) 기준 과제별 reset·tunnel·구성 fixture·T04–T06 회귀(2차 `d3268bf` 통과로 갈음). 후보 상한 16개·종류별 배분은 #38에서 한다.

## 2026-11-09 — T07B 한 칸 단차 이동과 검증 사전 등록 (#37)

T05 때 제외해 보존한 패치(`artifacts/issue-6/excluded-natural-steps-2026-11-06/`)는 붙이지 않았다. 규칙만 가져와 현재 코드에 다시 구현했다. 변경 전 코드(`c1338a7`)로 한 #36 검증은 참고 기록이다.

- **경로 규칙(Python `observed_routes`와 bridge `terrain.canStep`이 같다):**
  - 한 칸 옆으로, 높이는 −1·0·+1만 허용한다.
  - 도착 칸은 관측된 지지·비위험 바닥 위에 있어야 하고, 발·머리 칸이 관측된 통과 가능 칸이어야 한다(`terrain.safe`).
  - 높이가 바뀌면 출발 칸도 같은 조건을 만족해야 한다.
  - 내리기: 출발 높이의 앞쪽 머리 칸(`nx, y+1`)이 비어 있어야 한다.
  - 오르기: 출발 칸 위 칸(`x, y+2`)이 비어 있어야 한다. 그 위(`y+3`)는 막혀 있어도 된다. 천장이 점프를 발 높이 y+1.2에서 멈춰도 단을 넘는다. 설치된 prismarine 물리에서 3칸 높이 오르기가 21틱에 끝났다. 보존 패치는 y+3 두 칸도 요구했지만, 동굴의 3칸 높이 단차를 막아 #37의 목적과 어긋나서 뺐다.
  - 최대 16칸·400틱은 그대로다.
- **슬라임:** 출발 바닥이나 도착 바닥이 `slime_block`이면 높이 변화를 내지 않고 bridge도 거부한다(사용자 선택). 보존 패치의 "scripted 슬라임 거리 상한 결함"을 이렇게 고쳤다. 이 거부를 빼면 슬라임 하강이 400틱 동안 안정되지 않는다. 같은 높이의 슬라임 보행은 바꾸지 않았다(119틱/15.8764블록 그대로).
- **실행(bridge `moveObserved`):**
  - 오르기는 점프, 내리기는 한 칸 떨어지기다. 단차 점은 그 높이에 착지해야 도달로 친다. 같은 높이 점의 도달 판정은 그대로다.
  - 단차 중에는 지나는 빈 칸 하나만 서 있지 않아도 된다. 오를 때는 출발 칸 위, 내릴 때는 도착 칸 위다. 기존 `terrain.danger(state, transit)`를 쓴다.
  - 다른 칸에서 서 있지 못하면(예상 밖 낙하·경로 이탈) 그대로 `observed_hazard`로 멈춘다. 근처 위험·체력 판정도 그대로다.
  - 12블록을 넘기면 새 단차를 시작하지 않는다. 점프나 낙하와 착지가 16블록 상한 안에 들어가게 하려는 것이다. 이미 시작한 단차는 끝낸다(출발 칸 열을 벗어났거나 출발 바닥을 떠났으면 시작한 것이다). 가장자리에서 멈추면 안정 상태가 되지 않아 틱 상한까지 걸리기 때문이다. 리뷰에서 찾은 이 두 경우를 고쳤다. 단차 위치 9–16블록 × 시작 오프셋 6개 × 오르기·내리기 sweep을 물리 fixture에 넣었다.
  - 정지 경계 규칙(`terrain.stable`)은 바꾸지 않았다.
- **두 칸 이상 낙하·오르기**는 범위 밖이다.
- **공유 경로:** `observed_routes`를 쓰는 원목/드롭 접근(T04)·시설 접근(T05)·G2/G3/G4 탐색 보행에도 단차 경로가 들어간다. 이 영향은 아래 T04–T07 회귀로 확인한다.
- **실제 장면(관리자, 자연 과제 아님):** `information_fixture` scope `steps`.
  - y=100 장면 북쪽에 한 칸 높은 발판(x−1..x+1, z−8..z−2)을 둔다.
  - 동쪽 열의 점프 칸(`x+1, y+2, z−1`)에 돌을 두어 막는다.
  - 서쪽 열에는 한 칸 위 천장을 두어 3칸 높이 오르기를 만든다.
  - 정보 감사의 숨은 광석/용암은 이 장면에서만 오르기 착지 바닥 바로 아래(`x, y−1, z−2`)에 둔다. 돌로 둘러싸 보이지 않는다.
  - `verify_t07.py steps` 순서: 막힌 오르기 거부(1틱) → 오르기 → 내리기 → 3칸 높이 오르기. 정책 쪽 경로가 막힌 열을 내지 않고 3칸 높이 오르기를 내는지도 확인한다.
  - `audit-information`은 같은 장면의 ore/lava 쌍에서 오르기·내리기 두 결정의 관측·후보·선택·스텝을 비교한다. 선택은 생성된 걷기 후보를 첫 해당 단차 직후에서 자른 것이다. 계단 감사가 생성 후보의 작업량을 바꾸는 것과 같은 방식이다.
- **위험 반경 갇힘 수정(2026-11-09 사용자 결정 "양쪽 수정"):**
  - #36 자연 G2/G4가 `repeated_stall`로 끝난 원인이다. 봇이 관측 위험 1.5블록 안(`terrain.danger`)에 들어가면 모든 매크로가 시작 시 1틱 만에 멈춘다. #37 이전 코드에서 나왔다.
  - 규칙(Python `observed_routes`와 bridge `validPath`가 같다): 위험 반경 안의 경로 점은 바로 앞 점보다 가장 가까운 관측 위험에서 멀 때만 쓴다. 그래서 보행은 반경에 들어가지 않고, 반경 안에서 시작한 보행은 멀어지기만 한다.
  - 실행: 반경 안에서 시작한 보행은 시작 거리보다 0.05블록 넘게 가까워지지 않는 동안 계속한다. 반경 밖에서 시작한 보행은 이전처럼 1.5에서 멈춘다.
  - 후보: 봇이 반경 안에 있으면 매크로 목표와 상관없이 탈출 보행만 낸다(`escape_candidates`, 방문한 칸으로 가는 보행 포함). G2 2,224틱 갇힘에서는 방문 칸 제외 때문에 걷기 후보가 없고 bridge가 항상 거부하는 `stair_down`만 있었다.
  - 계단·tunnel·채굴·대기는 이전처럼 반경 안에서 시작하면 거부한다.
  - 갈 곳이 없으면 후보 0개 대기가 되고, 그대로 `repeated_stall`로 기록한다.
  - 실제 장면 `escape`(관리자): 봇 시작 칸 옆에 흐르지 않는 위험(magma_block, 1.0블록)을 두고 탈출 후보를 실행한다. `verify_t07.py steps` 끝에서 한다.
  - descent 단위 검사의 "lava-in-corridor" 용암을 한 칸 동쪽으로 옮겼다. 원래 위치(봇에서 1.41블록)는 실제 bridge에서 모든 계단이 거부되는 상태였다. 동쪽 방향 거부라는 검사 의도는 그대로다.
- **시계 재시도(사용자 결정):** 1차의 fall 장면 준비 실패(62/63)는 장면 준비 경합으로 보고 두 시도를 모두 기록한다. bridge가 다시 바뀌었으므로 아래 순서를 새 커밋으로 한 번 더 실행한다. fall이 또 실패하면 멈추고 장면 준비(순간이동 반영 확인)를 고친다.
- **가장자리 걸침(3차 자연 G2 결함):**
  - 몸이 관측 안전 칸에 걸쳐 땅 위에 있으면 중심 칸에 바닥이 없어도 서 있는 것으로 본다(`terrain.supported`). 중심 칸의 발·머리는 관측된 빈칸이어야 한다.
  - 계단 관성으로 생긴 0.53블록 넘침 같은 상태에서 모든 매크로가 1틱 만에 멈추는 갇힘을 없앤다.
  - 계단 매크로의 관성 넘침 자체는 고치지 않았다. 원인을 고치려면 T06 계단 동작을 바꿔야 하는데, 이번 결함의 갇힘은 서 있음 판정으로 풀린다.
  - 바닥 미관측·공중·액체·불은 이전처럼 위험이다.
- **RPC 프레임 상한(4차 자연 G2 결함, 사용자 결정 "16MiB"):**
  - 관측은 관측 기억 전체(칸당 약 125바이트)를 담는다. 그래서 4차 G2에서 9,611칸이 1.20MB가 되어 Python RPC 상한 1MiB를 넘었다.
  - `MAX_FRAME_BYTES`를 16MiB(약 13만 칸)로 올렸다. 관측 내용·정책 입력·제한 관측 규칙은 그대로다. `rpc.py`는 fingerprint 밖이라 63조건 인증은 유지된다.
  - Python→bridge 요청 상한(bridge 1MiB)은 바꾸지 않았다. 요청은 후보 하나 크기다.
  - 모델 입력용 상태 요약은 T10/T11·#38이 맡는다.
  - 실제 에피소드가 이 상한에 가까워지면 그때 기억 범위 제한(제한 관측 명세 변경)을 검토한다.
- **5차 범위(사용자 결정, 실행 전 등록, `84b6df3` 이후 기록 커밋 기준):** `verify_t07.py g2` 1회. bridge가 같아 4차 63조건 인증서를 쓴다. 고정 선택기 성공은 기록만 하고 실행기 결함만 실패다. 그 밖의 생략 항목은 4차와 같다.
- **4차 범위(사용자 결정, 실행 전 등록, `a9a046a` 기준):**
  - `verify_t07.py clock information steps g2`를 각 1회 실행한다(63조건 → 정보 감사 → 단차·탈출 장면 → 자연 G2).
  - bridge가 바뀌었으므로 63조건을 다시 받는다.
  - 생략: 자연 G4(3차 성공), tunnel·구성 fixture, T04–T06 회귀. 따라서 이 bridge 변경(`terrain.supported`)에 대한 그 장면들의 실제 회귀 근거는 없다.
  - 자연 G2의 고정 선택기 성공은 기록만 한다. 실행기 결함만 실패다.
- **3차 범위(사용자 결정, 실행 전 등록, `f8019d5` 기준):**
  - 2차 자연 G4의 `protocol_error`(시작 칸 열 끝점이 아홉 번째 후보)를 고친 뒤 `verify_t07.py information g4 g2`만 각 1회 실행한다.
  - 63조건은 생략한다. 바뀐 것은 fingerprint 밖의 Python 후보 생성뿐이라 2차 인증서가 유효하다.
  - T04–T06 회귀는 생략한다. 2차(`d3268bf`) 통과로 갈음한다는 사용자 결정이다. 따라서 이 수정에 대한 T04–T06 실제 회귀 근거는 없다.
  - 자연 G4/G2의 고정 선택기 성공은 기록만 한다. 실행기 결함만 실패다.
- **검증 순서(실행 전 등록, 탈출 수정 커밋 기준. 1차 `463c3a3`에도 같은 순서를 썼다):**
  1. 과제별 reset(C4/G1–G4)
  2. `verify_t07.py`: 63조건 → 정보 감사 → tunnel 장면 → 단차 장면 → 구성 fixture → 자연 G4 → 자연 G2, 각 1회
  3. 인증서가 새 fingerprint와 맞으면 회귀: T06(stairs, g3) → T05(production, boundaries) → T04(macros)

  서버 오류만 같은 snapshot으로 1회 재시도한다. 그 밖의 실패는 그대로 기록하고 사용자에게 보고한다. 자연 G2/G4의 고정 선택기 성공은 기록만 한다(가능성 진단). 실행기 결함만 실패다. 사람 선택 진단(`smoke-macros --select human`, G2·G4)은 이 검증 뒤 사용자가 새 후보로 다시 한다. #36의 통과 조건이다.

## 2026-11-08 — 새 고정 월드 기준과 검증 사전 등록 (#36)

- **입력(사용자):** Java 1.16.5, 시드 `-5755571633112603064`, 시작 블록 `-110 65 105`, 동굴 입구 `-117 65 74`(운영자 정보). 평원 시작, 동굴에 철이 있음. 물·용암·모래·자갈과 다이아 접근성은 추가 확인 대상이었다.
- **백업:** 기존 `worlds/`는 `archive/seed-20261102/worlds/`로 옮겼다. `artifacts/`는 그 자리에 두고 `archive/seed-20261102/artifacts/`에 사본을 만들었다. 두 SHA-256 목록(317·1,082 파일)이 있고, 사본은 원본 목록과 일치한다. `archive/`는 Git·mypy에서 제외한다.
- **생성:** 같은 런타임을 새 `worlds/server/`로 복사했다(`runtimeHash` `93838888…7dc7` 일치). `level-seed`만 바꿨고, 사람이 손대지 않은 새 월드를 생성했다. 시드는 JS 정밀도(2^53)를 넘어 문자열로 기록한다. level.dat의 시드가 입력과 같다.
- **시작점 해석:** 정수 좌표는 발 칸 블록이다. 봇은 그 칸 중앙 `[-109.5, 65, 105.5]`에 선다. `prepare_world`는 이 칸에 `setworldspawn`(반경 0)을 하고 서버를 다시 켠 뒤 접속한다. 위치가 정확히 같고, 바닥이 단단한 비낙하 블록이고, 발·머리 칸이 마른 빈칸일 때만 snapshot을 만든다. 실제로는 grass_block 위에 공기·공기였다.
- **G4 (사용자 규칙):** 입구 동굴은 y=50까지만 내려간다. 사용자 지시는 "근처의 다이아 있는 자연 동굴, 없으면 그 동굴에 붙인 관리자 방"이었다. C4 시작 기둥에서 가장 가까운, 노출 다이아가 있는 자연 동굴(y 7–40, 노출 다이아 9)을 골랐다. 안전 구역 칸 중에서 8칸 안에 물·용암이 없고, 4칸 안에 낙하 블록이 없고, 8칸 안에 다이아가 없는 가장 가까운 칸 `-146 12 96`을 사용자가 확인했다. 노출 다이아까지 직선 28.8, 동굴 경로 116칸이다. 더 가까운 `-114 11 96`(용암 호수 3.3칸)은 사용자가 고르지 않았다. 운영자 다이아 정보에 기댄 선택이므로 G4 결과는 "다이아가 있는 동굴에서의 탐색·채굴"로 해석한다. PLAN §4.3·§7.2·§9.4와 PRD의 "숨은 다이아·광석 위치로 고르지 않는다"를 대체한다. 시작 시야에 다이아가 보이지 않는다는 조건은 유지한다.
- **사전 조사(운영자 전용, region 파일 읽기만):** 시작 반경 32·y≥55에서 물·용암·모래 0, 자갈 63. 입구 동굴(1,648칸)에 노출된 물·용암·모래는 0이고 철 12면, 자갈 45면이다. 원시 자료와 스크립트는 `artifacts/issue-36/survey/`에 있다.
- **snapshot (새 기준):**

|과제|시작 위치|인벤토리|tree sha256|준비 출처|
|---|---|---|---|---|
|C4|`[-109.5, 65, 105.5]`|`{}`|`2b5023c9cdcd…`|user-provided start block (#36); natural surface; no ore search|
|G1|`[-109.5, 65, 105.5]`|`{}`|`2b5023c9cdcd…`|user-provided start block (#36); natural surface; no ore search|
|G2|`[-109.5, 65, 105.5]`|`{'stone_pickaxe': 1}`|`d3381fbe65c7…`|user-provided start block (#36); provided tool; no ore search|
|G3|`[-109.5, 65, 105.5]`|`{'iron_pickaxe': 1}`|`36f5afb60d12…`|user-provided start block (#36); provided tool; no ore search|
|G4|`[-145.5, 12, 96.5]`|`{'iron_pickaxe': 1}`|`9561e53bd4c3…`|user-confirmed natural diamond-cave cell (#36); provided tool; operator-only survey, never in observations|

  C4–G3는 첫 판 `prepare_world`로 만들었다. 그 뒤 서 있음 검사를 G4와 함께 쓰는 함수로 옮겼을 뿐 동작은 같다. 두 판의 patch는 `artifacts/issue-36/prepare*/uncommitted.patch`에 있다.
- **코드:** `prepare-world --start`/`--g4`, 검사기 시작 좌표를 manifest에서 읽기, 자연 G2/G4는 `repeated_stall`만 실패로 처리(`verify_t07`)하고 T05 G2 assert는 기록만 하게 변경, 사람 선택 진단 `smoke-macros --select human`(실제 경과 상한 없음, `selector_mode=human`), `configs/minecraft.yaml` RPC 시간 60→180초(서버 재시작 여러 번). 과제 도구·시간 상한·성공 판정은 그대로다.
- **검증 순서(실행 전 등록):** 과제별 reset(C4/G1–G4) → `verify_t07.py`(63조건 → 정보 감사 → tunnel 장면 → 구성 fixture → 자연 G4 → 자연 G2, 각 1회) → 인증서가 새 fingerprint와 맞으면 T06(stairs, g3)·T05(production, boundaries)·T04(macros) 회귀. 서버 오류만 같은 snapshot으로 1회 재시도한다. 그 밖의 실패는 그대로 기록하고 사용자에게 보고한다. 자연 G2/G4의 고정 선택기 성공은 필수가 아니다. 사람 선택 진단은 사용자가 직접 실행한다.

## 2026-11-08 — 자연 G2/G4 수락 기준을 가능성 진단으로 변경 (사용자 결정, #36·#8)

- **변경:** 자연 G2 철3·G4 다이아는 학습 전 단계에서 "성공 필수"가 아니다. 지금 테스트하는 고정 선택기(첫 후보)는 가장 단순한 행동이므로 성공 여부는 기록만 한다. 성공 판정은 학습 뒤 평가에 맡긴다.
- **통과 조건:** (1) 실행기 결함(무한 반복·후보 0개 교착·정지 실패·사건/시간 누락)·정보 누출·시계 인증/reset 실패가 없다. (2) 같은 snapshot·시작 상태·활성 틱 상한에서 코드가 만든 매크로 후보(최대 8개) 중 하나를 사용자가 매 결정마다 직접 골라 실행한다(사람 선택 진단). 이렇게 철3(G2)·다이아(G4)를 직접 채굴·획득할 수 있으면 통과다.
- **사람 선택 진단:** 후보·실행기·성공 판정은 정책과 같고 선택만 사람이 한다. 정지된 결정 대기 덕분에 생각 시간은 활성 시간에 들어가지 않는다. 실제 경과 상한은 적용하지 않는다. 궤적은 학습·성능·checkpoint 선택에 쓰지 않고(BC 제외), 모든 시도를 기록한다. 사용자는 월드를 알고 고르므로 이 결과는 "후보 집합에 성공 경로가 있다"는 증거이지 정책이 그 경로를 찾는다는 뜻이 아니다. 구현(대화형 선택 모드)은 #36에서 입력을 받은 뒤 한다.
- **대체:** 2026-11-06 재배치의 T07 "철3 실제 충족, 미달이면 #8 미완료"를 대체한다. 사전 등록 1회·종료 사유 기록·관리자 지급 제외·승인 없는 반복 금지는 그대로다. PLAN §5.2.1·PRD·#8·#36 본문에 반영했다.

## 2026-11-08 — 연구용 고정 월드 교체 (사용자 결정, 입력 대기, #36)

- **범위:** 다양한 자연 월드 일반화가 아니라, 자원 접근성을 확인한 고정 시드 1개에서 학습·평가한다. 물·용암·낙하 블록 대응이 연구의 중심이 되지 않게 환경을 고른다. 결과는 선정된 고정 환경에서의 성능이며 다른 월드 일반화는 검증하지 않는다(PLAN §4.4, GLOSSARY "선정 고정 월드").
- **이유와 한계:** 기존 시드 `20261102`에서 자연 G2 철3이 모래 재충전(1차)과 침수(2차)로 미달했다. 지형 대응이 과제의 병목이 되는 것을 피하려는 교체다. 결과를 본 뒤의 교체이므로 보고서에 밝힌다. 새 월드에서는 결과를 보고 시드·시작점을 다시 고르지 않는다.
- **입력:** 버전·시드·시작 좌표·동굴 입구 좌표는 사용자가 직접 찾아 제공한다. 에이전트는 시드를 찾지 않는다. 1.16.5가 아니면 업그레이드하지 않고 영향을 먼저 보고한다. 양식은 #36에 있다.
- **기존 환경:** 서버·world·snapshot·원시 로그는 백업만 한다. 추가 분석·문서 정리·보고서·재검증은 하지 않는다. 이전 인증과 결과를 새 환경에 승계하거나 섞지 않는다. #8의 G2 1·2차 미달은 이전 환경 이력이다.
- **새 기준:** 손대지 않은 새 월드를 생성한다. C4/G1/G2/G3는 제공 시작 좌표를 쓴다. G4 지하 시작점·준비 공간은 따로 제안해 확인받는다. 제공 도구·시간 상한·성공 조건은 그대로다. 새 fingerprint로 63조건·reset·정보 감사·T04–T07 회귀·pytest/mypy·자연 G2 철3·G4 판정을 다시 확인한다.
- **이번에 바꾼 것:** PLAN v1.10(§2·§3.5·§4.3·§4.4·§5.2.1), PRD v1.3, GLOSSARY, 이 기록, #36 생성. 코드·설정·월드·snapshot은 바꾸지 않았다.

## 2026-11-08 — T07 G2 1차 미달 결함 수정·2차 시도 사전 등록 (사용자 승인)

1차 시도(`ee76c2c`, `artifacts/issue-8/final/`)는 미달로 그대로 남긴다. 사용자가 결함 두 개를 고친 뒤 같은 조건으로 새 시도 1회를 하도록 승인했다. 이 수정은 1차 결과를 본 뒤의 변경이다. 그래서 관찰된 결함만 고치고 탐색 전략은 바꾸지 않는다.

- **자기 칸 재충전(bridge):**
  - `terrain.buried`는 봇의 머리/발 칸이 낙하 블록(sand, red_sand, gravel)과 통과 가능 칸으로만 이루어지고, 그중 적어도 하나가 낙하 블록이며, 관측된 바닥이 지지·비위험일 때만 그 칸들을 위에서부터 돌려준다.
  - 그 경우 `stair_down`/`tunnel`만 시작할 수 있다. 시작 전에 그 칸을 보이는 것만 파내고, 판 뒤에는 원래의 서 있음 검사를 다시 쓴다.
  - 다른 블록에 묻혔거나 바닥을 관측하지 못했으면 이전처럼 `observed_hazard`다. 숨은 칸을 읽지 않고 기억과 보이는 칸만 쓴다.
  - 머리 칸 질식 피해는 체력 감소 정지로 그대로 둔다. 실제 1차 결함은 발 칸이었다.
- **반복 정지 종료(Python `run_episode`):**
  - 1틱 이하이고 위치·지도 버전·인벤토리·내구도가 그대로인 스텝이 연속 20회(`STALL_LIMIT`)면 `repeated_stall`로 truncated 종료한다.
  - 1차의 2,107회 반복처럼 같은 선택이 예산 끝까지 반복되는 것을 막는다. 이것은 실패이며 성공으로 세지 않는다.
- **실제 장면 `tunnel_sand`(관리자, 자연 과제 아님):** 고정 상태에서 머리 위 두 칸에 모래를 놓는다. 첫 tunnel 중 모래가 발 칸으로 떨어지고, 다음 tunnel이 그 칸부터 파고 진행해야 한다. 미인증 사전 확인(`preflight-3`)에서 이 경로가 실제 물리로 동작했다.
- **바꾸지 않은 것:** 후보 순서·내구도 예약·tunnel/계단 매개변수·고정 선택기(첫 후보), `configs/g2_natural.yaml`(sha256 `2c31e865…972d`), G2 snapshot(sha256 `3a11c163…6a5c`)·시작점·돌 곡괭이1·12,000 활성 틱·2,700초, 성공 판정(`goal_completed` + `pause_verified` + `admin_verified.iron_ore ≥ 3`), G4 snapshot.
- **2차 시도(실행 전 기록):**
  - 이 수정 커밋에서 새 63조건 인증 → 정보 감사 → tunnel 장면(`tunnel_sand` 포함) → 구성 fixture → G4 smoke → 자연 G2 2차 1회 순서로 `verify_t07.py`를 실행하고, 이어서 T06(stairs, g3)/T05(production, boundaries)/T04(macros) 회귀를 한다.
  - 종료 사유는 `goal_completed`, `active_tick_limit`, `wall_time_limit`, `repeated_stall`, 오류 중 하나다. 앞의 것 외에는 모두 미달이다.
  - 서버 오류만 같은 snapshot으로 1회 재시도한다. 미달이면 결과를 그대로 보고하고 #8은 Open으로 둔다. 추가 수정·재시도는 다시 사용자 승인이 필요하다.

## 2026-11-08 — T07 #8 tunnel·다이아 판정·자연 G2 사전 등록

- **tunnel:** `stair_down`과 같은 절단·보행·정지 루프를 쓴다. 차이는 한 칸씩 내려가지 않는다는 것과 단면뿐이다. 단면은 `height` 2(1×2, 보행 가능한 최소)와 3(1×3)이다. 최대 8칸·400틱이고, 새로 노출된 정지 목록 광석(다이아 + 현재 목표 광석)과 관측 위험에서 멈춘다. 발견 뒤 방향 전환·채굴 사슬은 없다. 다른 광석은 지도에만 남는다.
- **광석 탐색 후보(`ore_search_choices`):** 목표 광석의 1.16.5 생성 상한(철 y≤63, 다이아 y≤15) 위에서는 계단을 먼저, 그 안에서는 새 보행 4개 → tunnel → 계단 순으로 낸다(최대 8개). 이 순서는 관측과 일반 게임 지식만 쓴다. T06 G2 방향별 결과로 방향이나 순서를 고르지 않았다. 고정 선택기는 기존대로 첫 후보다.
  - 절단 후보는 `(내구도 − 남은 목표 수) // 단면 칸 수`로 길이를 줄인다. 찾은 광석을 캘 내구도를 탐색에 쓰지 않기 위해서다. G3 `descent_choices`는 바꾸지 않았다.
  - 지나온(visited) 칸으로 되돌아가는 tunnel은 내지 않는다. 같은 효과는 보행 후보가 맡는다.
- **드롭 대응:** `diamond_ore`→diamond, `coal_ore`→coal, `grass_block`→dirt, stone→cobblestone. 다이아는 철 이상 곡괭이만 `mine_visible_cluster`로 캔다. tunnel/계단은 정지 광석을 절대 캐지 않는다.
- **병합 귀속:** 추적 드롭이 줍지 않은 채 사라지는 순간, 1.5블록 안에 있던 같은 품목의 다른 추적 드롭을 흡수 후보로 적는다. 나중에 그 후보 B를 주울 때 실제 수량이 기록보다 크면 그만큼만 B에 더한다. 용암·소멸·비추적 엔티티로의 병합은 후보가 없어 끝내 세지 않고, 비추적 엔티티가 B에 합쳐진 분량도 세지 않는다. 인벤토리 증가 확인은 그대로다(리뷰 반영: 시각·위치 없이 아무 사라진 드롭이나 흡수하던 초안을 고쳤다).
- **관리자 검증 로그:** `verifiedOres`(다이아·철)를 캘 때 서버 명령으로 직전 블록·서버 손 도구·직후 air를 기록하고, 드롭 엔티티와 그 `acquired` 사건 ID를 잇는다. 관리자 채널 `verification_log`로만 읽고, `smoke-macros`가 마지막 결정 뒤에 한 번 읽는다. 관측·후보에는 들어가지 않는다.
  - `admin_verified`는 자연 에피소드(`natural=true`, fixture/시계 장면이 아님)의 기록 중 모든 연결이 맞고, `acquired` 사건 수량과 기록 수가 같은 것만 센다. mock 사건은 세지 않는다.
  - `diamond_success`는 `mine_diamond` 목표 완료와 `admin_verified.diamond ≥ 1`일 때만 참이다. 지급·상자·거래·타 플레이어 다이아는 채굴 기록이 없어 셀 수 없다.
- **G4 상한:** `configs/g4.yaml`은 18,000 활성 틱(bridge 예산)과 실제 2,700초(45분, `wall_limit_seconds` → `wall_time_limit`)다. 결정 상한 18,000은 매 결정이 최소 1틱이라 활성 상한보다 먼저 걸리지 않는다.
- **자연 G2 인수 실행 사전 등록(실행 전 기록):**
  - 조건: 같은 G2 snapshot·시작점·제공 돌 곡괭이1·12,000 활성 틱, 고정 선택기(첫 후보), 이 커밋의 최종 코드와 새 시계 인증.
  - 설정: `configs/g2_natural.yaml`. `configs/g2.yaml`은 T05/T06 기준선과 비교하는 64결정 진단으로 그대로 둔다.
  - 운영 상한: 결정 12,000(활성 상한보다 먼저 걸리지 않음), 실제 2,700초. 실제 상한에 걸리면 `wall_time_limit` 실패로 적고 10분 소진으로 쓰지 않는다.
  - 성공: `goal_completed` + `pause_verified` + `admin_verified.iron_ore ≥ 3`. 종료 사유는 `goal_completed`, `active_tick_limit`(10분 소진), `wall_time_limit`, 오류 중 하나다.
  - 시도: 1회(`verify_t07.py g2`; 미달이면 모든 산출물·reset 뒤 실패 종료). 서버 오류만 같은 snapshot으로 1회 재시도한다. 실패해도 snapshot·시작점·시드·상한·선택기를 바꾸지 않고, 결과를 보고 후보 순서를 조정해 다시 돌리지 않는다. 코드 결함으로 실행이 무효가 되면 그 시도도 기록에 남긴다.

## 2026-11-07 — T06 독립 리뷰 반영 (`882d5e8`)

- **자갈 재판정 틱:** 자갈이 막은 칸을 다시 판정할 때 쓰던 1틱은 상한 안에서만 쓴다. 마지막 틱에 막힘이 보이면 그 자리에서 `macro_tick_limit`, 또는 활성 예산이 다 찼으면 `active_tick_limit`로 멈춘다. 상한을 넘겨 1틱을 더 쓰면 `max_ticks`와 활성 예산이 모두 깨진다. 판정을 다시 해도 쓸 틱이 없으므로 멈춘다.
- **`dig()` 굴착 시간 경계:** T05의 `required < 1` 거부를 되살리고, T06의 `required > 400` 거부는 함께 둔다.
  - 시간 0 굴착 거부는 T05가 검증한 동작이다. 공통화하면서 빠진 것은 의도한 변경이 아니었다.
  - 후보 `max_ticks`는 400 이하(`schema.Candidate`)라서, 400틱이 넘는 굴착은 어떤 매크로 안에서도 끝나지 않는다. 그래서 틱을 쓰기 전에 거부한다.
  - T05 대상(원목·돌·철광석)은 땅 위의 건조한 곳에서 맨손이어도 300틱 이하다. 실제 T05·T05A·T06 기록 어디에도 `dig_failed`는 없다.
  - 공중이나 물속처럼 시간이 5배로 늘어 400틱을 넘기면, 예전에는 상한까지 틱을 쓴 뒤 `macro_tick_limit`로 멈췄다. 지금은 1틱 만에 `dig_failed`로 멈춘다.
- **철 정지 경로의 정보 감사:** 정보 감사에 실제 숨은 철/용암 쌍을 넣었다. G2가 철을 찾을 때는 `descent_choices(observation, ["iron_ore"])`로 정지 목록에 철을 더한다. 기존 쌍은 다이아/용암뿐이었고, 실제 실행에서는 철이 한 번도 노출되지 않아 이 경로를 실제 Minecraft에서 비교한 적이 없었다. 같은 bridge 코드이지만 감사 근거는 실제 실행으로 남긴다.
- **드롭 병합 진단:** stderr 진단만 추가했다. 추적 중인 드롭이 줍지 않은 채 사라지면 `drop_gone_uncollected`, 주운 양이 기록과 다르면 `drop_count_mismatch`를 남긴다. 사건·관측·판정은 바꾸지 않는다. 병합분을 `acquired`로 다시 귀속하는 일은 출처 검증과 함께 #8 판정 설계에 속한다.
- **Python/JS 안전 판정 중복:** 그대로 둔다. Python `safe_ground`와 `descent_choices`는 저장된 관측만으로 후보를 거르는 사전 필터다. 실제 중단과 `safe_hold`는 bridge의 `terrain.stable`·`danger`·`hazardNear`가 매 틱 다시 판정한다. 두 판정이 어긋나도 손해는 후보 하나가 헛도는 것이고, 안전 판정이 느슨해지지는 않는다.
- **`stop_rule_id`:** 계단용 장착 후보의 `stair_ore_or_hazard`는 그대로 둔다. 모듈마다 정지 규칙 ID 하나를 장착 후보와 함께 쓰는 기존 관례를 따른다. 나무 장착은 `wood_or_hazard`, 생산은 `production_or_hazard`를 쓴다.

## 2026-11-07 — T06을 #32 위로 통합

rebase 대신 merge로 올렸다. `c4caf44` 커밋을 다시 쓰지 않아 이전 검증과 코드 기준의 연결이 유지되고, 충돌을 한 번만 해소한다.
stair 경로는 바꾸지 않았다. 실제 12장면과 G3가 #32 전후 틱·위치까지 같아 조정할 근거가 없다.
`server-port`는 fingerprint 입력이라 T06 설치도 25565를 유지한다. 포트를 나누면 코드와 런타임이 같아도 main과 fingerprint가 달라진다. 동시 실행이 필요할 때만 분리하고 그때의 인증은 그 설치에 한정한다.
`acquired` 과소 집계는 고치지 않았다. #32 이전부터 있던 동작이고 T06 인수 조건에는 쓰이지 않는다. 그 결과를 판정에 쓰는 #8에서 다룬다. 리뷰 반영 때 원인 확인용 진단만 추가했고, 내용은 위 절에 있다.

## 2026-11-07 — 입력 확인이 서버 틱 대기를 끝낸다

클라이언트 물리와 서버 틱의 두 50ms 타이머가 만나면 입력 fence가 틱을 놓쳐 100ms가 된다.
벤더 물리를 다시 구현해 클라이언트를 잠그는 대신, 입력 확인 시 서버의 대기 시각만 현재로
맞춘다. 변경이 mod 한 곳에 머물고 mineflayer 물리 경로와 그 회귀 근거가 그대로 유지되기 때문이다.
보행 advance는 물리 타이머가 상한이라 20틱/초를 넘지 않는다. 대기를 끝내도 틱 수는 그대로다.

fall 시계 장면은 물리1틱을 보장하는 advance(1,true)를 쓴다. prepared 기준은 바꾸지 않는다.
wood_break 보상은 드롭 난수에 좌우되므로 실제 획득량과 일치만 검사한다.
최종 수치는 PROGRESS 같은 날 절. 아래 “b0.059591389 완료 근거”와 “T04/G2 미실행”을 대체한다.

## 2026-11-07 — 사용자 승인으로 T05 전체 통과를 완료 근거로 채택

사용자가 추가 테스트 중단 뒤 T05 전체 통과를 근거로 이전 티켓 재검증을
생략하고 #32를 완료·커밋·푸시하도록 명시 승인했다. 이 세션의 완료 판단에는
이 최신 지시를 적용한다. 기존 인수 절차의 실제 실행 이력을 바꾸지는 않는다.
최종b0.059591389초/틱·새63/63/drift0·T05감사26/제작/경계/취소/reset·pytest80/
mypy22를 확인했다. 최종T04는사용자중단/reset통과, 자연G2는미실행으로 기록한다.
이전 티켓을 이번 코드로 새로 통과했다는 주장과 자연G2 성공 주장은 하지 않는다.
main/T06 수정·merge·#7완료는 하지 않는다. T06 통합 후 fingerprint 재인증은
별도로 필요하다. 이후 오류가 생기면 사용자의 지시에 따라 관련 검사를 재개한다.

## 2026-11-07 — 철광석 정보 감사의 공개 수집 경로

T04 정보감사에서 iron 기둥 높이3의 맨아래 채굴 후 머리 공간이 막혀
공개 terrain.validPath가 수집 위치로의 보행을 거부했다. 무작위 드롭이 정지
봇의 수집 반경 밖에 남으면 엄격한 직접획득 검사가 실패했다.
한 개 획득을 감사하는 iron 관리자 장면만 높이1로 바꿔 기존 채굴→공개 보행→
자연 픽업 경로를 검사한다. production_no_tool 장면 높이3은 유지한다.
자연 snapshot/RNG·정책·관측 필터·단일 step·획득1·전체 signature 비교는 바꾸지
않는다. 실패를 재시도로 지우거나 공개 drop 위치를 비교에서 빼지 않는다.
이 변경도 bridge fingerprint를 바꾸므로 기존63조건 인증을 승계하지 않는다.

## 2026-11-07 — 클라이언트 입력과 서버 틱의 인과 순서

재개 독립 Spec 검토에서 서버 receipt 뒤 늦은 physicsTick이 동결 서버의 다음
활성 틱으로 보류될 수 있음을 확인했다. 공개 dispatch 회귀에 서버 입력/위치
반영을 모델링해 `late movement left queued on frozen server`로 RED를 재현했다.
클라이언트 물리는 서버 step 전에 완료하고, console에서 승인한 nonce를 같은
Minecraft 연결로 되돌려 선행 이동 핸들러와 같은 서버 실행기에서 확인한다.
지정 ResearchBot의 플레이어 객체·nonce·동결·armed 상태를 검증한 뒤에만
TickSpeed를 진행한다. receipt도 지정 봇에만 보내며 정책 RPC에는 노출하지 않는다.
이 확인은 추가 게임 틱을 실행하거나 정지/물리 검사를 줄이는 방식이 아니다.

모의 지연 물리·nonce 계약·쓰기 실패 정리는 GREEN이며, 실제 물리 시작에
0/5/20/45/75ms 지연을 순환 주입한 보행 두 경로47틱/6.379블록에서 위치 허용
오차 검사와 마지막 C4 reset을 통과했다. 새 인증 전 진단이므로 exit1/미인증을
보존한다. mod27fe07bcbbbc100dbcbc4114d08426a66a50007ed1e243d5b722c81bebaa71a6으로
전체pytest79(24.46초)/mypy22와 두 축 재검토 지적0을 확인했다. 이전 final-t05는
SIGINT(-2)·reset통과로 보존하며 이 fingerprint의 인증으로 사용하지 않는다.

## 2026-11-07 — T05A 재개·시설 I/O와 활성 틱 분리

재개 시 기존 /tmp worktree와 로컬 원시가 없어졌음을 확인했다. 보존된787712f에서
영속 worktree `/home/sion/.codex/worktrees/327b/Minecraft_learning`와 새 전용 branch
`issue-32-t05a-resume`을 생성했다. main/T06은 읽기 전용이며 기존 브랜치·누락된
worktree의 Git 등록도 건드리지 않는다. 미커밋 I/O 수정·회귀는 대화에 남은 패치로
복원한다. 사라진 원시나 이전 인증을 현재 완료 증거로 사용하지 않고 새로 검증한다.

이전 정보 감사는 같은 설치 상태에서22/23틱 차이로 실패했다. 시설 API의
wall-clock 시선 회전과 I/O polling이 네트워크 지연을 활성 틱에 섞던 원인이다.
감사 비교는 완화하지 않는다. 기존 보행/채굴처럼 같은 공개 시설 표적에 시선을
맞추고, 기본 조작은 상한 확인→실제1틱/즉시 관측→정지 상태의 bounded I/O 대기→
재관측/중단 검사로 실행한다. 기존5500ms 한도와 wall_seconds 기록을 유지한다.
제련200활성틱·매 틱 중단·최종 pause·과제/매크로 상한은 바꾸지 않는다.

확인되지 않은 연료 뒤 추가 투입이 진행될 수 있던 timeout 경로는
operation_unconfirmed로 막고 failed 사건을 보존한다. 영구 회귀는 연료 미확인 시
철3 보존·성공 사건 부재·실패 사건과 지연 I/O의 불필요한 활성 틱 소진 방지를
검사한다. 실제 지연을 모사하는 fixture는 도착을 네트워크 이벤트로 표현한다.

복구 후 T05 변경 전 고정 장면9결정960틱은 a=1.193834879,b=0.199745351이다.
기존 유효 T05/T04 최종 로그10개의 재계산은 a=1.225208660,b=0.199272347로 일치했다.
원시·소스·hash는 새 worktree의 artifacts/issue-32/recovery에 보존한다. 최종 코드의
측정·즉시 동기화·63조건·T04/T05/G2·개발 검사 결과는 새 PROGRESS를 따른다.

## 2026-11-07 — T05A receipt 직전의 실제 상태 동기화

독립 Spec 검토에서 vanilla의 전송 단계 뒤 시뮬레이션이 metadata/블록/드롭
상태를 바꾸는 문제가 확인됐다. FIFO만으로 아직 보내지 않은 갱신을 보장하지
못했다. `tools/verify_tick_sync.py`의 관리자 loader는 pause/조회 전에 클라이언트
상태를 캡처하며 실제 RED는 산소300/서버299, 화로lit false/서버true,
drop y101/서버100.8808이었다. 이는 기존 pause 뒤 sample 비교로 가려졌다.

receipt 전에 기존 vanilla dirty block·metadata/attributes·현재 screen handler를
전송한다. drop은 기존 watcher에 현재 위치를 보내고 상대이동 기준 좌표를
갱신한다. tracker tick·수신 대상 재계산·추가 게임 틱은 실행하지 않는다.
이는 허용 관측 필터를 바꾸지 않으며 새로운 숨은 정보를 정책에 제공하지 않는다.
같은 실제 진단 GREEN: 산소299=299, lit true=true, drop100.8808=100.8808,
finally C4 reset 통과. 새 mod hash는c0ff66d5a455075e98ae3fea92ea94d520eaa9909c577b36878626486bbee3fe.
실제 RED/GREEN은 artifacts/issue-32/sync-{red,green}/에 보존한다.

앞선 final-t05 시계 실행은57/63 통과 때 SIGINT(-2)로 중단했고 새 인증이 아니다.
검사기의 assert/exit1을 보존했으며 finally C4 reset은 통과했다. 변경된 mod의
최종 속도를 다시 측정하고 새 폴더에서63조건 전체와 모든 관련 회귀를 실행한다.
Standards/Spec은 보완 코드에서 확정 지적0/P1해결을 확인했지만 최종 인증을
독립 재실행한 검토로 표현하지 않는다.

## 2026-11-06 — T05A 실제 틱 처리량과 동시 작업 격리

사용자가 #32 즉시 구현과 T06 동시 작업의 격리를 명시적으로 지시했다.
아래의 과거 “T05A 착수 금지”는 이번 지시로 해제된다. main 4694d54를 기준으로
새 branch `issue-32-t05a`와 별도 worktree `/tmp/Minecraft_learning-t05a-32`를 만들었다.
main 및 Claude의 `Minecraft_learning-t06`/`issue-7-t06`은 읽기 전용으로 취급한다.
서버·snapshot·Node/Python 환경도 복사하고 서버/봇은 전용 포트25566을 사용한다.
기존 기본 포트25565는 유지하며 봇이 설치의 server-port를 읽도록 했다.
#7을 수정·완료하지 않는다. 이후 T06에 최종 #32 코드 통합과 새 fingerprint의
63조건 인증·정보 감사·관련 회귀가 필요하며 #32 인증을 승계하지 않는다.

기존 `advance`의 1틱 콘솔 왕복4회와 대기를 실제 계측했다. 960샘플 평균은
사전 gameTime47.75ms/step49.96ms/대기50.24ms/완료확인1.56ms/최종조회48.03ms다.
서버 콘솔의 틱 말미 큐가 추가 지연을 만든다. 새 관리자 전용 `mcdiamond_step`
명령만 서버 executor에 전달해 다음 정상 활성 틱 전에 처리한다. TickSpeed의
20틱/초 step을 쓰며 가속하지 않는다. 틱 말미의 world/network/player 업데이트 뒤
같은 클라이언트 연결로 nonce·전후 실제 게임 틱을 보낸다. FIFO 수신을 기다려
그 틱 상태 갱신 뒤 관측하고 매크로는 계속 `advance(1,true)`로 중단을 검사한다.
보행의 물리 틱 제한·예상 밖 경과량 보존 후 실패·기존 pause/위치 검사는 유지한다.
관리자 응답/명령은 정책 관측·RPC에 넣지 않으며 stdout JSONL도 유지한다.
추가 외부 코드·의존성·연구 조건/예산 변경은 없다.

최종 T05/T04 로그 회귀는 a=1.225208660초/결정,b=0.199272347초/틱이다.
동일 고정 관리자 장면 wait20/100/200 각3회·960틱의 전후 비교는
변경 전 a=1.174859334,b=0.199932601 → a=1.195367608,b=0.050001196이다(fence 전 4f22bdf 값, 최종 아님).
중간 receipt만 적용한 b=0.100186100은 필수0.10 미달 시도로 보존하며 최종으로
세지 않는다. 목표0.06 충족은 이 고정 장면의 실제 측정에 한정한다.
모델 추론/PPO/reset을 포함한 본 학습 예산 충족의 증거로 확대하지 않는다.

구현 커밋3284ba0의 최종63조건과 정보/T04/T05/G2 회귀는 새 출력 폴더에서
진행한다. 결과·미달·인증/시도/제공량/사건/종료 이유/reset은 PROGRESS와 원시를
기준으로 보고한다. 사전 장착/채굴·보행은 인증 전 exit1/정지 미인증이다.
자연 G2 철3은 여전히 기존 실패 기준선이며 성공 전환이나 assert 우회는 금지한다.

## 2026-11-06 — T06 stair_down·G3 하강 구현 선택 (격리 브랜치 `issue-7-t06`)

사용자가 #32 미완료 상태에서도 격리 브랜치 구현을 멈추지 말라고 지시했다. 의존성 #5→#6→#32→#7→#8은 유지한다. 아래 선택은 #32 통합 뒤에도 그대로이며 재인증 결과는 PROGRESS 2026-11-07 첫 절을 따른다.

- stair_down 한 칸은 진행 열의 머리+1·발·발-1 세 칸을 **위에서 아래로** 판다. 위 칸을 파야 아래 칸이 보이므로 판단이 항상 방금 노출된 관측을 따른다. 칸마다 `terrain.memory`/`visible`만 쓰고, 바닥(발-2)이 관측되고 full support일 때만 내려선다.
- 가장자리가 바닥을 가리면 맹목적으로 내려서지 않고 1틱씩 조금씩 전진해 관측한다. 관성이 약 0.2블록이라(prismarine-physics 실측) 연속 전진은 절벽을 넘을 수 있다. 중심 이동 0.45 이상에서도 안 보이면 `floor_unobserved`로 멈춘다.
- 내려서는 중 발밑이 빈 것은 위험이 아니다. 바닥을 확인한 뒤의 단일 통과 칸만 `terrain.danger(state, transit)`로 허용하고, 불·액체·체력·근접 위험 판정은 그대로 둔다. 전체 공중 허용(제외된 단차 패치의 `allowUnsupported`)은 쓰지 않는다.
- 위험은 예정 칸(열+바닥)의 26-이웃에 관측된 hazard가 있으면 중단한다. 광석은 매크로 시작 시 기억에 없던 `stop_blocks` 칸이 생길 때만 `ore_exposed`로 멈춰 같은 노출로 반복 중단하지 않는다. 다이아는 항상 포함하고, 그 외는 후보가 목표에서 넘긴 광석이다(G3 다이아, G2 다이아+철). 다른 광석은 지도에만 남고 통로에 있으면 그냥 판다. 정지 대상 광석은 자동으로 캐지 않고 `ore_in_path`로 멈춘다.
- 후보는 열린 방향별 최대 계단 → 미방문 관측 이동 → 방향별 1계단 순으로 8개 이내다. 첫 후보는 현재 시선 방향이라 고정 선택기로 계속 수행을 재현한다. **관측된 칸만** 방향을 거부할 수 있고, 미관측 칸은 노출 시 매크로가 판단한다. 안전 대역 아래로 파지 않게 계단 수를 y=5까지로 제한한다.
- G3 완료는 `descent_completed`: 철 곡괭이 보유, y=5–12, 안정 경계, 선택한 wait의 모든 틱이 관측 안전 지면에서 안정 상태였다는 `safe_hold`(20틱 이상) 사건. 취소 복구 wait는 `safe_hold`를 만들지 않는다. 중단되면 사건이 없어 대기로 위험을 가릴 수 없다.
- G2는 철이 보이지 않거나 보이지만 같은 높이에서 닿을 수 없을 때만 stair_down을 먼저 제시한다. 저장된 T05 제작 51결정의 후보 ID·내용·순서·마스크는 순수 재생에서 동일하고 G2만 의도대로 달라진다.
- 채굴 절차는 `mine_visible_cluster`와 복제하지 않고 `dig` 클로저로 공유한다. T04/T05의 확인 조건(`block === 'air'`)을 유지한다.
- 자갈이 파낸 칸을 다시 메우거나 가리면 `block_changed`로 끝내지 않고 1틱 진행 후 위에서부터 다시 판단한다(실제 fixture에서 발견). 틱을 소모하므로 시간 상한 안에서 끝난다.
- 정보 감사의 stair 쌍은 드롭 산포·줍기 시점만 비교에서 제외한다(서버 난수이며 숨은 지형과 무관). 경로·중단·지도·틱은 그대로 비교한다.
- `run_episode`의 `select`는 기본이 첫 후보이며, `verify_t06.py`의 `g2-directions`만 저장된 후보 안에서 동·서·북을 고르는 데 쓴다. 시작 방향을 바꾸려고 관리자 이동이나 snapshot/시작점 변경을 쓰지 않는다. 후보에 없는 행동은 선택할 수 없다.
- `safe_hold`가 위험을 가리지 않는지는 실제 물 장면(`stair_hold`)으로 확인한다. 10틱에 `observed_hazard`로 끊기고 사건이 없어 완료되지 않는다.
- 침수·용암 뒤 탈출은 stair_down 책임이 아니다. 매크로는 관측 즉시 멈추고, 그 뒤 후보가 없으면 기존 T04 0후보 실패 경로를 탄다. 자연 G2 동쪽의 침수 사례(y=45)는 복구 필요 근거로 T08에 넘긴다.

## 2026-11-06 — 사용자 승인: 자연 G2 인수 이관과 T05 범위 확정

사용자가 T05의 제작·제련·노출 철 직접 채굴/획득 연결을 완료 범위로 정리하고, 미달인 자연 고정 G2 철3 검증을 후속 통합 단계로 이관하도록 명시적으로 승인했다. 이는 성공 판정 변경이나 실패 면제가 아니라 티켓 인수 책임과 실행 순서의 변경이다. 이 절과 PLAN §5.2.1이 아래 과거의 “G2 미달이면 #6 Open 유지” 지시를 대체한다. 실제 실패 기록은 보존한다.

- T05 #6은 개정된 기능·실제 fixture/시계/정보 감사/중단·취소/reset 기준을 모두 충족한 경우만 커밋·푸시·완료 처리한다. 코드 기준은 기존 검증본 ff75f36이며 자연 G2 성공은 주장하지 않는다.
- T05A #32는 #6 완료 뒤, #7 전에 진행한다. 기존 G2 실패(64결정/1778틱/철0/decision_limit/정지 인증true)를 회귀 기준선으로 사용한다. assert/exit1을 성공으로 바꾸지 않으며 새 오류·정지 실패·사건/시간 누락은 회귀 결함이다. 최종 T05 로그로 처리량 기준선을 고정하는 작업은 T05A 착수 뒤 수행한다. 이번에는 T05A 구현·계측을 하지 않는다.
- T06 #7은 기존 G3 하강과 별도 고정 G2 접근 가능성·철 노출/실패 구간 확인을 담당한다. G3 제공 철 곡괭이와 G2 제공 돌 곡괭이 상태를 분리한다. T07 #8은 같은 G2 snapshot/hash·시작점·돌 곡괭이1·10분/12000틱에서 자연 철 발견→적절한 도구 직접 파괴→해당 드롭 직접 획득3의 최종 통합 인수를 책임진다. 미달/장애면 #8을 닫지 않는다.
- 의존 그래프는 #5→#6→#32→#7→#8과 #7의 기존 #5 선행을 유지한다. #6/#32를 후속 G2 성공에 역의존시키지 않는다. bridge/runtime/mod/설정/snapshot fingerprint 변경 시 각 최종 코드로63조건 재인증·정보 감사·관련 T04/T05 회귀와 개발 검사를 수행한다. 연구 조건·예산은 바꾸지 않는다.
- 미커밋 자연 단차 이동 7개 소스는 패치·원본 사본·hash를 로컬 `artifacts/issue-6/excluded-natural-steps-2026-11-06/`에 보존하고 ff75f36으로 복원한다. 단차 상하행 실제 사전 검사는24/17틱이었으나 새 시계/정보 감사가 미완료이고 scripted 슬라임 하강에서 거리 상한 초과도 확인됐다. 이 실험을 T05 완료나 향후 사용 가능한 구현으로 표시하지 않는다. 자연 G2 사전 실행도64결정/150틱/철0·정지 미인증으로 별도 보존한다.

## 2026-11-06 — T05 개별 제작·제련 (이하 당시 결정 이력)

- G2 사전 실패의 공개 상태에 미방문 경로55개가 남아 있는데 후보0이 생성되는 결함을 보완한다. 방향별 후보를 고를 때 미방문 끝점을 먼저 보존해, 방문한 대표 끝점을 나중에 거르는 과정에서 다른 새 경로를 잃지 않게 한다. 후보8개/같은 높이/관측 지도/16블록·400틱과 G2 설정은 유지한다. 수정 후에도 실제 고정G2 철0이면 인수 미달로 남기며 시작점·숨은 광석·새 매크로·예산 변경으로 성공을 만들지 않는다. T05A의 advance/틱 최적화는 이 작업에 포함하지 않는다.

- 기존 공개 smoke-macros/episode/RPC/관측 지도/보행/활성 틱 실행을 재사용한다. 공통 자료 recipes.json에서 레시피와 재료를 읽고 목표의 전제조건 하나만 후보로 내며 매번 다시 선택한다. 나무/돌 곡괭이·화로·철 직접 확보·철괴 회수·철 곡괭이를 전체 사슬 매크로로 묶지 않는다. 새 계획기·S 선택기·학습은 추가하지 않는다.
- 제작 출력 1–8개/레시피 배수, 개별 제작·설치·화로 투입/회수·장착 ≤400틱을 실행 경계에서 검증한다. 재료·현재 보이는 설비·연료량·채굴 도구·설치 지지면을 확인하고 기본 조작마다 제한 관측과 위험/사망/시간을 검사한다. 재료 수집 중에는 가려진 작업대에 먼저 돌아가지 않으며, 다시 제작할 때 기억한 설비로 접근한다. 기억한 설비를 벽 너머에서 직접 사용하지 않는다.
- Mineflayer 비동기 완료와 인벤토리 수신은 별개다. 작업 상한 안에서 실제 갱신을 확인하고 사건을 기록한다. 도중 중단된 배치의 완료분과 이미 투입한 연료/입력은 보존한다. 미완료 transaction은 다음 선택으로 넘기지 않는다.
- 화로 창이 열렸을 때 재고는 현재 창의 플레이어 영역(items)을 읽는다. 설비 입력/출력을 플레이어 보유량으로 합치지 않고 닫힌 기본 창의 오래된 재고를 기다리지 않는다. 실제 한 틱마다 관측하는 실행은 벽시계에서 느리므로 새 production/G2 설정의 RPC 한도는 180초다. 매크로 활성400틱·G2 활성12,000틱 한도는 늘리지 않는다.
- 직접 획득 기준은 제작/투입 소비를 반영한다. 같은 틱의 자기 직접 채굴 드롭 수집과 재료 소비가 상쇄돼도, 확인된 파괴·자기 수집·재고 변화를 연결한다. 목표는 새 직접 사건이 있고 총 보유량을 충족해야 완료하며 제공량만으로 새 달성을 만들지 않는다.
- 화로 창에서 직접 읽은 상태만 기억하고, 이 에피소드에 직접 투입한 입력을 화로 좌표별로 회수와 연결한다. 지급된 화로 출력은 furnace_collected만 기록하고 smelted로 세지 않는다. reset은 화로/출처 기억도 비운다. 이미 다른 내용물이 들어 있는 화로의 추가 투입은 현재 거부한다.
- 고정 자연 G2와 빈 인벤토리/배치 자원의 production 진단을 구분한다. 준비 틱·제공 상태·직접 사건·시계 인증·숨은 정보 쌍·예상 실패·취소·최종 reset을 원시로 보존한다. 자연 G2가 미달이면 T05 전체 인수 조건 미완료로 보고하고 관리자 철광석 진단으로 대체하지 않는다. 하강/터널·자연 snapshot 변경·모델/API/학습·연구 예산 증액은 하지 않는다.

## 2026-11-05 — T04 리뷰 보완

- 채굴 완료 틱의 실제 블록 제거 확인과 중단 판단을 분리한다. 위험·도구 파손·사망을 그대로 보고하면서 확인된 파괴와 뒤이은 정당한 획득 근거는 보존한다.
- 정책이 보내는 stop_rule_id는 메타데이터다. 임의 문자열로 내부 취소 특례나 실패 사건을 만들지 않는다. 일반 wait는 20/100/200 또는 잔여 20틱 미만의 절단만 허용한다. 취소의 짧은 대기는 내부 인자로만 허용하고, 0후보 failed는 저장 후보 집합과 실제 wait 증거를 확인한 공통 episode에서 만든다.
- Python 공통 근거 검사는 한 번 수행하되 이동 고유의 경로·사건 검사를 유지한다. MacroEvidence·executeMacro로 이름을 맞추고 Node 결과 구성을 공유한다. Python 후보 생성과 Node 실행 사이의 도달/도구 검증은 서로 다른 신뢰 경계이므로 유지한다.
- 자연 G1의 고정 첫 후보 탐색과 매크로 실제 회귀를 구분한다. 공개 CLI의 명시적 --diagnostic-fixture만 관리자 장면을 사용하고 natural_task=false와 준비 틱을 출력한다. 독립 드롭 대기는 실제 채굴한 드롭을 관리자 준비 단계에서 옮기고 초기 속도·획득 지연을 설정한다. 준비 활성 틱(채굴 포함)과 에피소드 활성 틱을 구분하고 자연 snapshot은 저장하지 않는다.
- 기존 정보 감사에 독립 장착·20/100/200 wait·드롭 대기·0후보의 숨은 광석/용암 쌍을 추가한다. 실제 취소는 같은 게임 서버를 20틱 진전시킨 뒤 원 선택을 취소하고 20틱 대기·재선택하는 공통 흐름으로 별도 검증한다. 이것을 전체 realtime 운용이나 숨은 두 경우의 취소 쌍 감사로 표시하지 않는다.
- tools/verify_t04.py를 재현 실행기로 Git 추적한다. 시도별 새 출력 폴더에 명령·코드 hash·stdout/stderr·결과를 보존하고 일부 검사만 실행하거나 중간에 실패해도 마지막 기준 reset을 시도한다. 보고서 생성 때문에 게임 검사를 재실행하지 않는다. 모델·API·학습·연구 예산·Java 정지 확장·공통 allow-flight 설정은 이번 보완에서 변경하지 않는다.

## 2026-11-04 — T04 관측 원목 수집

- 기존 공개 CLI/RPC/episode와 제한 관측 BFS·보행·정지를 재사용한다. `smoke-macros`는 고정 목재 목표에서 직접 관측한 대상·경로·1블록/최대 8블록 작업량을 중복 제거해 최대 8후보로 저장한다. 새 모델·계획기·선택기 S·학습은 추가하지 않는다.
- 지형 기억과 현재 시야를 구분한다. 현재 보이는 원목만 채굴 대상으로 쓰고, 접근·드롭 회수 경로는 직접 관측한 같은 높이의 바닥·발/머리 공간으로 제한한다. 무작위 흩어짐은 관측한 자기 파괴 드롭으로만 보완하며 전체 entity/청크 탐색을 하지 않는다.
- Mineflayer 기본 dig는 벽시계 타이머와 낙관적 클라이언트 블록 제거를 사용하므로 그대로 쓰지 않는다. 설치된 프로토콜의 시작/완료/취소 패킷을 실제 digTime/50 활성 틱으로 진행하고 서버가 보낸 블록 갱신으로 파괴를 확인한다. 파괴 요청 직후 2 활성 틱 내 한 드롭 생성·확인된 파괴·자기 수집·인벤토리 증가를 연결하며 오래된/실패한 파괴는 획득에 기여하지 않는다.
- 장착·채굴·대기는 매 틱 제한 관측으로 위험·피해·산소·도구 파손·시간·사망을 확인하고 즉시 중단한다. 드롭 회수도 같은 보행을 사용하며 총 매크로 상한 안에 둔다. 새로운 광석/자원을 보고 선택 밖의 군집으로 확장하지 않는다.
- 단일 후보는 확률 1, 0후보는 실제 wait와 failed 사건이다. smoke의 actor 전이는 항상 0이다. 무효 선택은 취소 대기와 원 후보/선택을 보존하며 actor 제외·trace 단절을 명시하고 재선택한다. 취소 대기 시간과 미실행 원 매크로 상한을 구분하고 에피소드 남은 틱/연속성은 검증한다. 사건 ID를 중복 집계하지 않는다.
- 정보 감사에 동일 공개 원목 군집·숨은 광석/용암 두 장면의 채굴/드롭 접근/중단·안정 경계를 추가한다. 드롭 무작위 흩어짐 좌표·사건/entity ID만 비교에서 정규화하며 정책 상태·대상/수량·경로·중단 근거는 유지한다. 실제 진단용 배치와 자연 task snapshot을 구분한다.
- 실제 회수 실패를 추적해 기존 정지 확장이 클라이언트 이동 패킷을 버려 서버 플레이어가 출발점에 남는 문제를 확인했다. 최신 위치/방향을 vanilla의 서버 스레드 인계 뒤에 보관하고 활성 틱의 vanilla handler에 전달한다. 오래된 look이 새 position/look을 덮거나 frozen 위치가 새 active 위치를 덮지 않도록 순서를 유지하고, 텔레포트 전 pending을 비우며 확인 전 이동은 보관하지 않는다. 차량은 기존처럼 정지 중 차단한다. 이동 종료는 정지뿐 아니라 서버/클라이언트 위치 오차 0.001블록도 검사한다. 관리자 위치는 실행 검증에만 쓰며 경로 선택에 추가하지 않는다. 확장 변경 후 시계 63회를 새 fingerprint로 재검증한다.
- 낙하 장면 재검증에서 vanilla의 벽시계 기반 floating 추방을 재현했다. Java에 추가 타이머 우회 코드를 넣지 않고 서버 표준 allow-flight=true를 사용한다. Survival abilities/게임 물리·행동 입력은 바꾸지 않으며 모든 군의 공통 환경 설정으로 fingerprint와 향후 lock에 고정한다. backend는 잘못된 설정을 fail-fast로 거부한다.

## 2026-11-04 — T01–T03 리뷰 후속 수정

- `clock_mode=paused`는 63회 인증과 실행 중 경계 확인이 모두 유효할 때만 사용한다. StepResult는 paused/검증 플래그의 불일치를 거부하고 EpisodeSummary에도 pause_verified를 남긴다. 미인증 실제 smoke는 unverified/exit 1이며 다중 결정 중 미검증/오류를 마지막 정상 step으로 덮지 않는다.
- 인증서는 환경 검증 근거이며 매 결정의 정지 확인을 대신하지 않는다. reset 및 wait/이동 매크로 종료에서 입력 해제·클라이언트 물리 중지 후 서버/클라이언트 두 표본의 완전 상태·실제 틱 불변을 확인한다. freeze 명령을 보낸 경우 응답도 확인하며 실패하면 인증 플래그를 해제하고 중단한다. 150ms는 표본 사이 확인 구간이며 장기 0/5/10초 검증을 대체하지 않는다. 관리자 player 상태는 시계 검사에만 쓰고 관측/후보/이동 근거에 추가하지 않는다.
- 이동 summary는 기존 StepResult의 공개 사건·근거·시간을 movement_steps로 결정별 보존한다. 후보 source obs/path, 결과 map/stop evidence, 사건 출처·이동 여부를 검증한다. mock도 동일 근거 계약을 만족해야 하며 실제 정지를 인증하지 않는다.
- Mineflayer 자체 stdout 오류 로깅을 끄고 연결 오류는 민감한 원문 없이 stderr로 알린다. vec3는 설치된 0.1.10을 직접 의존성으로 선언한다. 물리 fixture는 bridge 전체를 로드해 함수 순서에 의존하는 소스 자르기를 제거한다.
- 중복 틱 검사·Python/JS 안전 검증·과제/장면/권한 상수·private RPC 호출은 현 시점 기능 결함으로 확인되지 않아 구조를 유지한다. 언어/신뢰 경계별 검증을 제거하지 않는다. README의 로컬 uv PATH 설정은 이미 있으므로 설치 방식은 바꾸지 않는다.

## 2026-11-03 — T03 제한 관측과 보행

- 기존 RPC·공개 episode 실행기를 확장하며 새 경로 탐색 의존성을 추가하지 않는다. 눈 위치에서 반경 8의 셀 중심으로 자체 voxel ray를 보내 최초 충돌 표면/위험과 통과한 공기·비충돌 식물만 기억한다. 충돌 블록/유리·부분 블록은 보수적으로 광선을 가리고 미로딩 셀은 조회를 중단한다. 모서리에서는 앞선 접촉 셀이 막히면 이후 대각 셀을 읽지 않는다. map/visited/history는 reset마다 비운다.
- Python 후보는 공개 지도에서 확인한 동일 높이의 바닥·발/머리 공간만 BFS로 연결한다. 최대 8방향·경로 16블록·400틱이며 Node도 공개 셀·원본 obs/map 버전과 경로 연속성을 재검증한다. 실행 중 매 기본 이동 뒤 관측을 갱신하며 공개 위험·길 변경·피해·정체에서 중단한다. 정상 완료는 입력 해제 후 공개 지면과 수평 정지를 확인한다. 접지 중 남는 prismarine의 vy=-0.0784는 수직 이동으로 오인하지 않는다.
- 보행에서는 실제 서버 틱 수만큼 클라이언트 physicsTick도 제한해 관리 명령/통신 대기 중 별도 물리 진행을 막는다. 즉시 실패의 최소 1틱 규칙은 유지하고 죽은 플레이어의 발생하지 않는 physicsTick을 기다리지 않는다. 실제 틱·경과 시간·거리·경로·근거 obs/map·종료 이유를 로그에 보존한다. smoke-movement는 안정된 경로 완료가 없으면 실패한다.
- PR #29 검토에서 기본 15블록 후 정지 여유가 얼음 위 관성에 부족함을 설치된 물리 코드로 재현했다. ice/packed_ice/frosted_ice/blue_ice는 관측을 유지하되 support=false로 공통 후보/경로/안정 판정에서 제외한다. 얼음 보행을 추가하려면 공개 지면/속도에 따른 제동 거리를 실제 교정해야 한다. 필수 실패 1틱도 동일하게 실제 이동 거리와 moved 사건에 반영한다. 돌/슬라임의 현재 거리 상한은 scripted 물리 검사로 확인하며 실제 서버 근거와 구분한다.
- 정보 감사는 관리자 전용 준비와 정책 observe/step을 분리한다. 같은 벽 뒤에 광석/용암을 두는 실제 두 장면에서 run ID/벽시계만 제외하고 관측·후보/경로·실행/중단 근거가 같아야 한다. 벽을 연 양성 대조에서 노출을 확인한다. 준비된 자연 snapshot을 수정하지 않고 진단 후 다음 reset에서 복원한다. 실제 정지 인증도 요구하며 제작·계단·터널 감사는 해당 후속 티켓과 최종 lock 전에 수행한다.
- 일반 높이 차·점프·부분 블록 보행·모델 선택·원목 채굴은 이번 티켓에 추가하지 않는다. 같은 제한 정보 아래 선택지를 제공하는 기반이며 A/B/J/F/S·보상·학습/평가 예산을 바꾸지 않는다.

## 2026-11-02 — T02 실제 월드와 정지

- 기존 관리자 FD/정책 stdin·Python 공개 episode 실행기를 유지하고 Node Mineflayer backend를 추가한다. 현재 T02는 자기 상태·wait와 실제 시계 검증을 제공하며 지형 관측/다른 매크로는 후속 티켓에서 구현한다.
- 사용자 EULA 승인 후 단일 자연 월드를 생성한다. 시드는 생성 전에, 지상 시작점은 최초 자연 spawn으로 정한다. G2/G3 도구와 G4의 고정 지하 공간/철 곡괭이는 관리자 준비로 기록하고 광석/성적을 조사해 위치를 고르지 않는다. 과제별 immutable snapshot/hash를 reset마다 검증한다.
- Carpet freeze만으로 플레이어 산소가 줄어드는 실패를 재현했으므로 자체 최소 Fabric/Carpet 확장으로 플레이어 simulation/이동도 멈춘다. 입력 해제·클라이언트 물리 정지·서버 활성 tick 종료 후 관측하고, 실제 tick step으로 재개한다. 서버 기동 시에도 정지하며 초기 로그인 상태만 실제 저장 상태에서 전송한다.
- 7장면×0/5/10초×3회의 실제 상태 불변과 위험 장면 준비를 모두 확인한 결과만 검증 근거로 원자 저장한다. 코드·게임/의존성·Java/Node·설정·snapshot fingerprint가 다르면 정지를 다시 검증한다. 모델 없는 모의/transport 검사는 물리 근거로 쓰지 않는다. 정지 결과로 실시간 전환이나 본 학습을 자동 승인하지 않는다.
- `flock`으로 단일 서버 소유권을 보장하고 hash/symlink 검사를 swap 전에 수행한다. timeout 시 진행 작업을 중단하고 Java 저장·종료에 필요한 유예를 준다. 연결 종료 후 cached 관측과 이전 reset의 후보를 거부한다. 이 선택은 실제 실패와 검토 결과에 따른 실행 기반 보완이며 A/B/J/F/S·예산·학습·평가 계획은 유지한다.
- 현재 서버/봇은 loopback offline 인증이다. 계정 비밀번호/토큰을 받지 않는다. Microsoft 로그인·공개 서버·유료 API·모델 학습은 이번 구현에서 검증하거나 실행하지 않았다.

## 2026-10-07 — 계획 검토 1차

- **초기화:** BC 없이 동일한 공개 NanoJev 가중치에서 A/B를 시작한다. A는 실제 RL 시작 actor이며 B에만 이번 RL을 적용한다. 공개 가중치의 revision/hash는 설치 시 고정한다.
- **실험 범위:** 이번 회차는 F를 제외하고 A/B/J와 필수 G4에 집중한다. 본 학습 30,000결정·기본 핵심 최종 평가 23회·PC 점유 계획 180시간은 유지한다.
- **시계:** 정지 수정을 먼저 시도한다. 실패하면 본 학습 전에 실시간 조건과 예산을 검증한 뒤 모든 군에 적용한다. 검증되지 않으면 보류하며, 정지 학습 결과와 실시간 평가 결과를 섞지 않는다. 실시간 B↔J는 지연을 포함한 시스템 비교로 해석한다.
- **파일럿:** 기본 파일럿 이후 원인 수정에 따른 추가 파일럿은 최대 1회다. 짧은 파일럿의 성적 상승을 필수 조건으로 삼지 않고 학습 구조의 정상 작동과 실제 진행 근거로 본 학습 여부를 판단한다.

이 기록은 구현·실험이 검증되었다는 뜻이 아니다.

## 2026-10-07 — 계획 검토 2차

- **본 학습 진행 근거:** 파일럿 성적 상승은 필수 조건이 아니다. Choice gradient와 파라미터 변화, 본체 고정, 수치 안정성, 의미 있는 복수 후보와 유효 학습 전이, 보상·reset·학습 연결의 정상 작동을 확인한다. 원목 직접 획득과 G4의 관측 확장·이동·굴착 등 실제 진행도 로그로 확인한다. 성적이 오르지 않은 사실과 진행 판단 근거를 기록하고, 학습 연결이나 실행을 막는 문제가 남으면 보류한다. 사전 G4의 다이아 획득은 요구하지 않는다.
- **추가 파일럿 범위:** 원인 수정 후 공개 초기 actor에서 설정 하나로 최대 1,024결정을 학습하고 초기·학습 후 목재 평가를 각각 10회 수행한다. 기존에 선택한 설정을 사용하고 선택 근거가 없으면 기본 LR 1e-4를 사용한다. 학습률 자체가 확인된 문제여서 수정하면 이유와 값을 기록한다. 추가 설정 탐색은 하지 않으며 시간과 실패 이력을 별도 집계한다.
- **Jev 비용 상한:** 연결 확인·A/J 진단·최종 평가·실패 요청에서 발생한 과금·재시도를 포함한 모델 API 사용료 상한은 총 US$5다. 충전 수수료는 별도로 기록한다. 본 학습 전에 실제 요청 과금량으로 예정 평가 비용을 추정하고 필요하면 기존 사전 축소 규칙을 적용한다. 상한을 임의로 초과하지 않는다.
- **조건부 계획기 지식 조회:** 기존 계획기 연결 진단과 7B+Jev 초기 진단·짧은 C4 실행의 목표 출력·전제조건 오류·실패 원인에서 게임 지식 부족에 따른 목표 오류 반복이 확인되면 적용한다. 7B를 호출하지 않는 목재 파일럿과 목표 고정 사전 G4만으로 판단하지 않으며, 행동 선택·후보/실행 실패와 구분한다.
- **보완 방식과 정보 경계:** Minecraft 1.16.5 제작·제련 레시피, 채굴 도구 조건, 자원 획득 방법을 로컬 자료로 제공한다. 코드가 현재 관측·목표·최근 실패에 관련된 정보를 조회해 계획기 입력에 넣고, 가중치가 고정된 7B가 다음 목표를 결정한다. 계획기 SFT나 온라인 RL은 추가하지 않는다. 숨은 광석 좌표·월드 시드·전체 청크 지도·사전 조사 정답 경로를 제공하지 않는다. A/B/J가 같은 자료·조회 규칙을 사용하며 B의 학습 경험이나 통계만 별도로 제공하지 않는다.
- **검증·고정·범위:** 보완 전후의 저장된 진단 상태 등으로 목표 오류 감소 여부를 확인하고 효과가 없거나 악화된 결과도 기록한다. 자료의 출처·게임 버전·버전/hash, 조회 규칙·프롬프트와 적용 이유·검증 결과를 본 학습 전에 고정한다. 도구 추가로 추가 학습 파일럿 상한을 늘리지 않으며 구현·검증 시간과 실패 이력을 기록한다. NanoJev 행동 선택 강화학습, BC 미적용, F 제외, A/B/J와 필수 G4, 본 학습 30,000결정·기본 핵심 최종 평가 23회·PC 점유 계획 180시간과 나머지 확정 사항을 유지한다.

## 2026-10-07 — 계획 검토 3차 및 인터뷰 종료

- **local에서 full로 진입:** local 15,000결정 후 성적 향상이나 기술 간 자연 연결이 부족해도 학습·실행 구조가 정상이고 의미 있는 선택과 실제 진행이 확인되면 예정 full 15,000결정을 진행한다. 연결 부족 자체를 중단 사유로 삼지 않고 실패 구간과 진행 근거를 기록한다. 유효한 경험 수집이나 정책 업데이트를 막는 문제가 발견되면 보류하며, 성적 부족으로 local 학습량을 자동으로 늘리지 않는다.
- **지식 보완 후 잔여 목표 오류:** 오류가 일부 반복되어도 실행 가능한 목표·의미 있는 선택·실제 진행이 발생하면 한계를 기록하고 본 학습을 진행한다. 최초 목표 오류, 재생성 후 오류, 규칙 복구 사용 비율은 각각의 분자·분모를 구분한다. 실제 진행을 최초 7B·재생성 7B·규칙 복구 목표 출처에 연결하며 복구의 성과를 7B 자체의 계획 능력으로 해석하지 않는다. 계획·복구를 거쳐도 실행 가능한 목표가 없어 진행이 막히면 보류한다. 보완 여부와 설정은 본 학습 전에 확정하고 A/B/J에 공통 적용한다.
- **의미 목표와 완료 보상:** 정규화한 목표 종류와 대상을 기준으로 동일 의미 목표를 식별한다. 수량·방향·목표 ID 변경은 새 의미 목표가 아니며 에피소드당 최초 완료에만 +0.5를 지급하고 최대 8회·총 +4를 유지한다. 이 제한은 full 목표 완료 보상에만 적용한다. 기존 아이템 최초 획득·제작, 다이아 성공, local 성공 보상과 반복 목표의 실제 완료 판정·다음 목표 전환은 유지한다. 정규화 규칙은 본 학습 전에 공통으로 고정한다.

Q1–Q10과 조건부 게임 지식 조회 보완을 사용자 답변대로 확정하고 인터뷰를 마무리한다. 기존 연구 방향과 확정 사항을 유지하며 새로운 연구 범위·추가 실험을 자동으로 늘리지 않는다. 실제 환경·모델·과금·처리량·효과는 이후 진단에서 확인한다.

## 2026-10-08 — PRD 검토 보완 및 게시 확정

사용자가 여섯 보완점 반영 후 PRD 확정·GitHub Issue 게시·ready-for-agent 부착을 지시했다. 연구 인터뷰와 테스트 경계 확인을 다시 요구하지 않는다.

- **기준 문서:** 작업공간의 인터뷰 반영본은 PLAN v1.7-grill-final/2026-10-07이며, 이전 제공본 v1.7-final/2026-10-06과 구분한다. 이번 보완본은 PLAN v1.7-prd-final/2026-10-08, 이 결정 기록 v1.1-prd-final, 기존 GLOSSARY다. 정확한 파일 SHA-256을 PRD에 기록하며, GitHub 기본 branch의 문서가 동일 파일이라고 가정하지 않는다.
- **에피소드 경계 복구:** 초기/에피소드 종료 후 reset 경계의 모델·critic·optimizer·RNG·curriculum·확정 결정 수·검증 이력·미업데이트 rollout buffer를 원자 저장한다. 해당 과제의 기준 월드/플레이어/인벤토리/체력/시간으로 복원하고 기억·목표·제어·에피소드 ledger를 함께 초기화한다. 게임 reset과 중간 ledger 복원을 섞지 않는다. 중간 중단은 마지막 경계 이후 경험·업데이트 전체를 rollback하며 원자 저장 미완료본은 사용하지 않는다. 공식 30,000은 유지되는 확정 수집 결정이고 폐기 결정·시간·비용은 별도 보고해 총 실제 실행량을 숨기지 않는다. 복구 overhead로 기존 예산을 자동 증액하지 않는다. 정확한 15,000/7,500/15,000 성능 actor 저장은 복구본과 구분하며 rollback 분기의 후보는 무효 이력 후 재도달 저장본으로 대체한다. 단계 예산 종료는 성공이 아닌 유효 절단으로 마감한다.
- **실시간 재선택:** 무효 후보를 조용히 다른 행동으로 치환하지 않는다. 대기 중 틱/사건/보상/비용을 보존하고 새 관측/후보로 선택한다. 취소 선택과 fallback에는 원래 선택 logprob의 actor 학습을 적용하지 않는다. 실제 실행한 재선택의 관측/후보/logprob만 연결한다. 취소/복구 구간은 보상·시간을 한 번 반영하고 유효 상태 전이만 critic에 사용하며 actor 제외와 trace 단절을 기록한다.
- **평가 슬롯:** 예정 평가 1회는 슬롯 하나다. 서버 오류만 같은 snapshot/RNG로 최대 한 번 재시도하고 마지막 허용 시도의 결과를 슬롯 결과로 사용한다. 최초 오류·각 attempt 시간/비용은 모두 기록한다. 재시도도 오류이거나 예산상 미실행이면 슬롯 성공 0, 예정 분모 유지다. 행동 실패·사망·탐색 실패는 재시도하지 않는다. 파일럿/checkpoint/최종 C4/G4 평가에 공통 적용하며 재시도 두 건을 독립 평가로 세지 않는다.
- **G4 최소량 우선:** 남은 local 결정 R, G4 부족량 D=max(0, 6,000−G4 누적 결정)에서 다른 과제 1,000 배정 뒤 R−1,000<D이면 G4를 우선한다. 그 외에 미표본·실패율·동률 순서를 적용한다. 총 15,000과 초기 각 1,000, G4 최소 6,000을 유지한다.
- **파일럿 시간 집계:** 동일 성공 수가 1 이상인 설정끼리 성공 에피소드 평균 활성 시간을 비교한다. 모두 0이면 시간 비교를 생략하고 학습/수치 오류 사건 수, 다시 동률이면 LR 1e-4 순으로 선택한다. 구조/수치 불능 설정은 제외하고 전부 불능이면 보류한다. 실패 시간·종료 이유·실제 경과는 별도로 보존한다.
- **연구 기여:** 고정된 작은 계획기와 공통 실행 조건에서 행동 선택 정책만 추가 RL하고 학습 전후 및 기존 Jev를 비교한다. 계획 오류·규칙 복구·실행 병목·지연·비용을 구분해 전체 수행에 기여한 범위를 분석한다. 새 관련 연구 사실이나 실험을 추가하지 않는다.

기존 Q1–Q10, 지식 조회 조건, F 제외·BC 미실시, 30,000결정·최종 23회/축소 17회·PC 계획 180시간·Jev 모델 API 총 US$5를 유지한다. 문서 검증과 GitHub 게시를 구현·실험 검증 완료로 해석하지 않는다.

## 2026-10-07 — 공개 문서로 확인한 사실

- [OpenRouter 응답 명세](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request)와 [TypeSafe Choice 문서](https://docs.typesafe.ai/primitives/choice)에 모든 후보의 확률 분포가 명시되어 있다. 실제 계정·프로젝트 입력의 응답 검증은 미실행이며, 9.3절의 분포 검증과 평가 모드 고정 규칙을 유지한다.
- [Jev 1.13 모델 페이지](https://openrouter.ai/typesafe/jev-1.13/)의 확인일 기준 요율은 입력 100만 토큰당 $0.042, 출력 $0이다. 이는 모델 사용료이며 충전·플랫폼 수수료와 구분한다. 허용 모델 API 사용료 상한은 2차 검토에서 총 US$5로 확정했으며 실제 계정 접근·사용량·과금 검증은 미실행이다.

## 2026-10-09 — 이슈 #2 실행 기반

- Python 패키지는 `src/mc_diamond`에 둔다. argparse·subprocess·selectors·ctypes를 사용하고 Pydantic은 RPC 자료형 검증, PyYAML은 확정 YAML 설정 계약, pytest/mypy는 개발 검사에 사용한다. 배포 의존성은 uv.lock과 bridge/package-lock.json에 고정한다.
- 모의 backend도 subprocess JSONL RPC와 공통 에피소드 실행기를 통과한다. 관리자는 별도 상속 FD로 reset하고 정책 stdin은 observe/step만 허용한다. 향후 Node backend도 같은 계약과 공개 실행 경로를 사용한다.
- 리뷰 보완: JSON 형식으로 전달된 유효 request_id는 나머지 요청 schema가 잘못돼도 같은 ID로 오류를 반환한다. 실제 사건 출처 minecraft를 공통 wire에 허용하고, 제공 mock backend는 mock 출처와 mock 시계만 허용한다.
- 고정 collect 목표와 노출 원목 후보만 진단용으로 연결한다. 진단 보상은 획득 사건 수이며 local/full 보상·모델 선택·actor 경험·다이아 성공을 구현했다고 표시하지 않는다. 후속 티켓에서 연구 계약을 확장한다.
- CUDA toolkit 없이도 실제 GPU 연산을 확인하도록 자체 PTX 산술 커널과 드라이버 API를 사용한다. nvcc 도구 부재·NVIDIA 접근 오류·GPU 연산 결과를 구분한다. 샌드박스 결과와 장비 접근이 허용된 실행 결과를 구분해 기록한다.
- 시스템 ROS PYTHONPATH가 외부 pytest plugin을 자동 로드해 lark 부재로 실행을 막았다. 프로젝트 pytest는 자동 plugin 로드를 끄며 잠금된 검사 도구만 사용한다.
- npm audit의 여섯 moderate 경고는 uuid 버퍼 검사 권고에서 전파됐다. 현재 확인한 로그인 의존성은 v4를 호출하지만 실제 인증 경로는 미검증이다. Mineflayer를 1.4.0으로 낮추라는 자동 수정이나 미검증 major override는 적용하지 않고 후속 실제 연결 작업의 위험으로 기록한다.

## 2026-10-10 — 핵심 F 복원과 계획기 학습의 마지막 조건부 대안

- **변경 이유:** 행동 선택 RL을 핵심으로 유지하면서 작은 로컬 7B+RL NanoJev가 강력한 Astra+기존 Jev에 어느 정도 접근하는지 답하도록 사용자가 F 복원을 요청했다. 이전 F 제외 결정과 선택 F 명세의 적용 제한을 대체하며 새 알고리즘이나 학습량 확대는 하지 않는다.
- **비교 구조:** A=최종 7B+공개 초기 NanoJev, B=동일 7B+PPO 후 NanoJev, J=동일 7B+기존 Jev, F=고정 Astra+J와 동일 Jev/설정이다. A↔B는 행동 선택 RL, B↔J는 동일 계획기 모델 대체, J↔F는 동일 Jev 계획기 차이, B↔F는 전체 시스템 비교다. B↔F를 RL 하나의 인과적 효과로 설명하지 않는다. 모든 군의 관측·지식 조회/프롬프트 의미·목표·후보·매크로·시간·검증·복구는 공통이다.
- **평가:** F는 핵심 참조 시스템이며 C4 5회를 기본 포함한다. 기존 C4 17+F 5+필수 G4 6=28회/최대 12.5 활성 시간이다. 사전 축소는 A/B/J/F 주 평가 모두 각 3회, A/B argmax 각 1회, G4 6회로 총 20회/8.5시간이다. F 접근·예산을 우선 확인하며 외부 불가/비용 문제이면 예정 슬롯 미실행과 Q3/Q4 미검증을 남긴다. 선택 비교로 낮추지 않는다.
- **시간·비용:** 기존 PC 계획 180시간과 Jev 총 모델 API US$5는 유지하되 충분성을 미리 주장하지 않는다. F의 실제 시간·GPU/PC 점유·Astra 비용·추가 Jev 비용을 분리해 산정한다. J/F Jev와 모든 연결·진단·실패/재시도를 합쳐 US$5 이내여야 한다. Astra 별도 금액/호출 상한은 미승인이다. PLAN §11.1.1의 공개 요율·가정 예시는 실측이나 지출 승인이 아니다. 예산 부족은 선택 추가 실험 보류→checkpoint 2개→A/B/J/F 주 평가 각 3회 순으로 사전 검토한다. 남은 부족은 미완료로 남기며 임의 증액하지 않는다.
- **계획기 기본 방침과 변경 이유:** 기존 공개 7B 가중치 고정·로컬 지식 조회 우선은 유지한다. 보완으로 해결되지 않는 중대한 계획 병목에도 대응할 마지막 제안 경로를 마련하도록 사용자가 요청했으므로 과거 SFT/온라인 RL 전면 제외 문구를 PLAN §5.6의 제한적 검토 절차로 대체한다. 계획기 학습은 필수 구현·자동 분기·필수 본 학습 단계가 아니다. 단순 저성능이나 Astra 대비 열세로 시작하지 않는다.
- **정확한 검토 조건:** (1) 지식 조회 및 입력·검증·재계획 보완 시도, (2) 보완 후 목표 순서·실패 복구·장기 계획 오류 반복, (3) 실제 게임 진행의 중대한 병목 확인, (4) 공통 6상태 Astra 비교 등을 통한 충분한 원인 분석, (5) 학습 필요 이유·예상 개선 가능성 설명, (6) 데이터·학습 시간·GPU 메모리·추가 평가 비용의 현실적 감당 가능성 검토를 모두 충족해야 한다. Astra 우수성이 없거나 형식/지식/실행 문제이면 그대로 기록하고 원인을 혼동하지 않는다. 일부 오류에도 목표 실행과 진행이 가능하면 한계를 기록하고 행동 RL을 우선한다.
- **제안·승인:** 조건 충족 후에도 경량 LoRA/SFT 방법·허용 계획 데이터 확보/분할·학습 목표/손실·기존/학습 후 동일 상태 평가·과적합/오류 악화·RTX 5070 Ti 16GB 메모리/시간 근거·본 학습/평가/예산 충돌·학습 없이 마치는 대안을 별도 제안한다. 분석과 예상 비용 보고 뒤 사용자 명시적 승인 후에만 실제 훈련한다. 이번 요청은 훈련·유료 API 호출·결제 승인이 아니며 Jev/Astra 출력 학습 데이터 사용도 허용하지 않는다.
- **공정성:** 승인된 계획기 학습은 행동 모델의 정식 PPO 전에 완료·검증하고 최종 7B 가중치/hash·설정을 A/B/J 공통으로 고정한다. 전후 계획 성능은 별도 진단으로 분리하며 A↔B RL 효과와 섞지 않는다. F의 외부 Astra는 고정한다.
- **유지 조건:** Java 1.16.5·시드 하나/고정 시작 상태·제한 관측/정보 차단·공통 후보/매크로·NanoJev Choice PPO·독립 local/full critic·local/full 각 15,000결정·기존 보상/SMDP/PPO 수식·checkpoint/실패/복구/슬롯 규칙·A/B 동일 초기 NanoJev·BC 미적용·Jev 추가 학습 없음·추가 실행 별도 승인을 유지한다.

실제 F 접근·과금·처리량·계획 병목과 7B 경량 학습 메모리/시간은 아직 미검증이다. 문서와 PRD 갱신을 구현·학습·실험 완료로 표현하지 않는다.


## 2026-10-10 — S 필수 진단과 로봇 응용 동기 보완

- **검토·범위:** 원격 main d809cd9bbbe2deda0ed193a9120c4964911a9185(PR #26 머지), Closed T01(#2)와 Open T02(#3), Issue #1과 24개 티켓을 확인했다. T01 코드·기존 의존/테스트 경계를 보존하며 새 티켓·구현·학습·유료 호출은 추가하지 않는다.
- **S 정의:** A/B/J와 동일 최종 7B + 별도 규칙 기반 행동 선택기다. GoalRegistry 규칙 복구/Mineflayer 실행기와 구분한다. 같은 Observation/Goal/최대 8개 Candidate/mask에서 ID를 반환하고 목표 관련성·공개 전제조건·관측 위험·최근 실패·예상 진행의 일반 규칙만 사용한다. 새 매크로·숨은 정보·사전 조사 경로·특별 도움·신경망/PPO/별도 API를 추가하지 않는다. 규칙/동률/실패 처리/hash를 T19 lock에서 고정하고 B/J/F 결과를 보고 최적화하지 않는다.
- **담당:** T08(#9) selector 구현 → T12(#13) 슬롯/reset/오류 연결 확인 → T19(#20) 사전 비용/규칙/lock → T22(#23) 최종 S C4 1회 → T24(#25) 별도 진단 보고다. T12 슬롯 기반은 기존 선행대로 먼저 구현할 수 있고 S 연결은 T08 이후 lock 전에 확인한다. 기존 blocking 그래프를 바꾸지 않는다.
- **횟수·비용:** 핵심 A/B/J/F C4 22+G4 6=28회/축소 14+6=20회를 유지한다. 별도 예정 분모 S1을 더해 총 29/21회, 최대 활성 13/9시간, 최초 시도 게임 경과 상한 39/27시간이다. S 추가분은 활성 0.5/경과 1.5시간이며 reset/검증/서버 재시도는 별도다. 선택 연산·7B 계획 호출·GPU/PC/실행 비용과 20% 계획 여유를 사전 산정한다. 180시간을 자동 증액하거나 핵심군/S를 임의 삭제하지 않으며 부족하면 측정 근거와 필요한 결정을 보고한다. S는 학습/G4를 추가하지 않고 서버 오류 최대 1회 재시도·모든 비용·예정 분모 규칙을 공유한다.
- **해석:** 다이아 성공·최고 단계·활성/실제 시간·선택/계획 호출 수·실패·비용을 별도 표로 보고한다. 규칙 기준선과 RL 정책의 실제 수행 차이에 관한 탐색적 진단이며 1회로 통계적 우월성·일반적인 신경망 대체 가능성을 주장하지 않는다. S 결과는 B checkpoint 선택에 쓰지 않는다.
- **연구 동기:** 큰 상위 계획을 외부 연산 자원에서, 작은 행동 선택을 로봇 내부에서 수행할 수 있다는 응용 방향에서 정책 크기/계산 비용과 추가 RL·규칙/외부 모델 차이를 조사한다. 현재 7B는 로컬이며 로봇·온디바이스·클라우드-로봇 분산 구조·CPU 실시간 추론·특정 로봇 하드웨어 성능을 검증하지 않는다. NanoJev는 매크로 선택 고수준 정책이다. 이는 후속 방향이며 CPU/네트워크/로봇/클라우드 이전/온디바이스 최적화 실험을 추가하지 않는다.
- **보존:** F 핵심 지위·A/B/J/F 정의·B local/full 각 15,000·보상/PPO/curriculum/checkpoint/G4·BC 제외·고정 월드/시작 상태·최후 7B 학습 여섯 조건/별도 승인·Jev US$5·Astra 별도 비용 승인·슬롯/복구/정보 경계를 유지한다. S 구현과 실제 수행·180시간 충분성은 후속 검증 대상이다.
