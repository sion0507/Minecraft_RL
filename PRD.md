# PRD — 고정 환경의 NanoJev 행동 선택 강화학습과 A/B/J 비교

문서 버전: v1.0-final
수정일: 2026-10-08
상태: 사용자 검토의 여섯 보완점 반영 후 확정. 구현·실험은 미검증.

## Problem Statement

학부 수업 프로젝트에서 고정된 작은 계획기 아래 NanoJev 행동 선택 정책의 추가 강화학습 효과를 확인하고, 같은 실행 조건의 기존 Jev에 얼마나 접근하는지 평가하려 한다. 공개 시연의 성공만으로는 행동 선택 학습의 기여, 계획·실행 병목, 실제 시간·API 비용을 구분할 수 없다.

연구 방향과 Q1–Q10은 확정되었다. 현재 저장소에는 계획·결정·용어 문서가 있으며 구현 코드와 테스트는 아직 없다. 필요한 결과는 재현 가능한 공통 실행기, 검증된 학습 연결, 정해진 학습·평가와 실패까지 포함한 보고서다. 성적 상승이나 다이아 성공 자체를 프로젝트 완료의 필수 조건으로 삼지 않는다.

## Solution

Minecraft Java 1.16.5의 자연 월드 하나에서 고정된 7B가 하위 목표를 정하고, 공통 코드가 제한 관측으로 최대 8개 매크로 후보를 생성한다. NanoJev는 후보를 선택하며 공개 Choice 헤드와 독립 local/full 가치 헤드만 PPO로 학습한다.

A는 공개 초기 NanoJev, B는 동일 초기화에서 이번 RL을 수행한 NanoJev, J는 동일 7B 아래 프로젝트 내 추가 학습 없는 기존 Jev다. BC 없이 B 본 학습 한 번, local 15,000결정과 full 15,000결정을 수행한다. 기본 최종 평가는 C4 17회와 필수 G4 독립 진단 6회다. PC 점유 계획 180시간과 전체 Jev 모델 API 사용료 US$5 상한을 유지한다.

파일럿과 실제 환경 진단으로 실행·학습 구조를 확인한 뒤 본 학습 여부를 결정한다. 계획기의 게임 지식 부족이 확인되면 공통 로컬 지식 조회만 조건부로 보완한다. 모든 결과는 고정 환경 적응으로 해석하며, 새로운 연구 범위나 추가 실험을 자동으로 늘리지 않는다.

본 프로젝트는 고정된 작은 계획기와 공통 실행 조건에서 행동 선택 정책만 추가 강화학습하고, 그 전후 변화와 기존 Jev 대비 성능을 평가한다. 계획 오류·규칙 복구·실행 병목·지연·비용을 구분해, 행동 선택 학습이 전체 수행에 기여한 범위를 분석한다. 관련 연구의 세부 사실과 최초성은 별도 출처 확인 없이 추가하지 않으며 이 기여 문구로 새 실험을 요구하지 않는다.

## User Stories

1. As a student researcher, I want a reproducible experiment in one fixed Minecraft world, so that I can study adaptation within the agreed project scope.
2. As a researcher, I want A and B to start from identical public NanoJev weights without BC, so that the A-to-B comparison measures this project's additional RL.
3. As a researcher, I want the same frozen 7B planner for A, B, and J, so that planner changes do not confound the core comparisons.
4. As a researcher, I want J to use the existing Jev without project training, so that I can measure conditional replacement performance honestly.
5. As an experiment operator, I want fixed task snapshots and complete episode resets, so that previous runs do not contaminate later evaluations.
6. As a researcher, I want success to require direct mining and acquisition of a natural diamond drop, so that supplied or unrelated diamonds cannot count as success.
7. As a researcher, I want all policy components to receive only allowed observations, so that hidden resources and hazards cannot influence decisions before exposure.
8. As an experiment operator, I want verified decision-boundary pauses, so that inference latency cannot silently change a paused experiment.
9. As a researcher, I want a validated common realtime fallback when pause repair fails, so that latency-dependent results have a consistent interpretation.
10. As an experiment operator, I want active game time and wall time recorded separately, so that waiting, execution, and operating limits are accounted for correctly.
11. As a researcher, I want shared candidate generation and macro execution across A, B, and J, so that model-specific assistance does not bias comparisons.
12. As a policy trainer, I want meaningful distinct candidates with stable identifiers, so that PPO learns genuine choices from the exact collected action set.
13. As a policy trainer, I want zero-candidate and single-candidate decisions handled explicitly, so that forced actions cannot masquerade as actor training experience.
14. As an experiment operator, I want bounded macros with observable stop reasons, so that the actor retains control over direction and continuation.
15. As a researcher, I want validated goals and bounded regeneration before shared rule recovery, so that invalid planner outputs do not prevent all progress.
16. As a researcher, I want initial goal errors, regeneration errors, and recovery use counted separately, so that planner limitations remain visible.
17. As a researcher, I want progress linked to the adopted goal's source, so that rule recovery achievements are not attributed to the 7B planner.
18. As a researcher, I want planner knowledge problems diagnosed through existing planner and short C4 runs, so that actor or executor failures are not misclassified.
19. As an experiment operator, I want conditional local Minecraft knowledge retrieval, so that confirmed recipe and tool errors can be addressed without planner training.
20. As a researcher, I want identical knowledge material and retrieval rules for A, B, and J, so that B receives no privileged planner information.
21. As a researcher, I want before-and-after knowledge diagnostics and frozen retrieval settings, so that any benefit, lack of benefit, or regression is documented.
22. As a policy trainer, I want the public Choice head preserved and the backbone frozen, so that this experiment trains the agreed policy parameters.
23. As a policy trainer, I want independent local and full critics, so that their different reward scales do not share one value estimate.
24. As a policy trainer, I want discounts and GAE to use actual macro durations, so that long actions and realtime delays receive correct credit.
25. As a policy trainer, I want correct terminal, truncation, and goal-change handling, so that value bootstrapping follows the actual task boundaries.
26. As a researcher, I want event-based rewards and episode reward ledgers, so that provided items and repeated goals cannot inflate training rewards.
27. As a policy trainer, I want full goal rewards deduplicated by normalized kind and target, so that quantity, direction, and goal-ID changes cannot create extra rewards.
28. As an experiment operator, I want repeated unrewarded goals to complete and transition normally, so that reward deduplication does not block execution.
29. As a researcher, I want a bounded wood pilot with two settings and shared evaluation conditions, so that learning connectivity can be checked without open-ended tuning.
30. As a researcher, I want at most one corrective pilot from the public initial actor, so that fixes do not silently expand the experimental budget.
31. As a researcher, I want pretraining G4 and initial A/J diagnostics, so that late-stage execution and external-model connectivity are checked before main training.
32. As a researcher, I want main training to depend on working updates and actual progress rather than short-pilot score improvement, so that a noisy pilot does not impose an unapproved performance gate.
33. As a policy trainer, I want the agreed dynamic local curriculum and G4 minimum allocation, so that later exploration receives its planned experience.
34. As a researcher, I want full training to proceed after functioning local training even when skill connection is weak, so that poor scores do not trigger extra local training automatically.
35. As a policy trainer, I want the first 256 full decisions to train only the full critic, so that the shared actor enters full training with a warmed value estimate.
36. As an experiment operator, I want atomic episode-boundary recovery and separate exact-count selection checkpoints, so that interruptions cannot mix reset game states with mid-episode learning state.
37. As a researcher, I want a fixed checkpoint selection rule and separate development seeds, so that final Jev or G4 results cannot influence model selection.
38. As a researcher, I want Jev's actual probability support and candidate mapping verified, so that native choice is not mislabeled as controlled categorical sampling.
39. As an experiment operator, I want bounded API retries and recorded fallback behavior, so that invalid responses do not silently substitute NanoJev or hide costs.
40. As an experiment operator, I want all charged Jev requests included in the US$5 cap, so that diagnostics, failures, and retries cannot exceed the agreed spending limit.
41. As a researcher, I want primary C4 sampling and auxiliary argmax results kept separate, so that favorable selection modes are not chosen after seeing results.
42. As a researcher, I want the mandatory G4 results reported independently, so that prepared-state exploration ability is not confused with full-task success.
43. As an experiment operator, I want measured complete training cycles and cost forecasts before the experiment is frozen, so that the plan uses actual throughput and billing.
44. As a researcher, I want predetermined reductions applied before performance results, so that budget changes do not become selective reporting.
45. As a researcher, I want one result per planned evaluation slot with bounded server-error retries and preserved attempt logs, so that retries cannot change the denominator or hide operating failures.
46. As a researcher, I want goal, candidate, exploration, learning, and system failures distinguished, so that the report explains where progress was blocked.
47. As an experiment operator, I want secrets excluded from logs and policy actions separated from administrative controls, so that reproduction artifacts do not expose credentials or grant policy privileges.
48. As a maintainer, I want permitted existing libraries reused with source and license records, so that the common executor can be implemented without unauthorized copying or unnecessary infrastructure.
49. As a reviewer, I want one primary public execution test boundary and focused real-environment diagnostics, so that tests verify observable contracts without duplicating each implementation layer.
50. As a student researcher, I want honest results even when every diamond run fails, so that the report still documents learning, progress, cost, and fixed-world limitations.

## Implementation Decisions

### 1. 실험 경계와 비교군

- 기본 게임은 Java 1.16.5, Survival, Peaceful이며 기본 장비는 RTX 5070 Ti 16GB와 RAM 32GB다. 자연 월드 시드 하나를 최초 생성 전에 정해 기록한다. 정책에는 시드를 제공하지 않는다.
- C4는 학습·평가 모두 같은 지상 좌표, 빈 인벤토리, 정상 체력, 다른 플레이어 없는 상태에서 시작한다. G1–G4는 같은 월드의 과제별 고정 좌표·기준 snapshot을 사용한다. reset마다 지형·상태를 복원하고 관측 기억·목표 통계·제어 입력·보상 ledger를 초기화한다.
- 숨은 다이아 위치나 모델별 성적을 보고 시작점을 고르지 않는다. 자연 도달 상태는 연결 분석에만 기록하며 새 학습 reset 풀로 섞지 않는다. 새로운 월드·시작점 이동 평가를 추가하지 않는다.
- 성공은 자연 생성 diamond ore의 적절한 도구 직접 파괴와 해당 드롭 획득을 연결해 판정한다. 초기 지급·관리자 지급·상자·거래·다른 플레이어 다이아는 제외한다. 관리자 사건 로그는 검증용이며 정책 입력에 포함하지 않는다.
- 계획기는 Qwen/Qwen2.5-7B-Instruct, 초기 4비트 추론, 가중치 고정이다. A/B는 C-Tianyu/NanoJev의 공개 unified-games-v1에서 출발한다. 설치 시 immutable revision과 파일 hash를 고정한다. 공개 초기 Choice 헤드를 유지하며 BC는 수행하지 않는다.
- A는 실제 RL 시작 actor이고 B에만 이번 RL을 적용한다. J는 같은 7B와 프로젝트 내 추가 학습 없는 기존 Jev다. J를 ‘미학습 Jev’라고 부르지 않는다. 이번 회차의 F 수행 여부는 제외로 고정한다.
- A/B/J의 목표·관측·기억·후보·매크로·검증·복구·시간 규칙은 공통이다. 서로 다른 궤적이 매 순간 같은 후보 목록을 갖는다고 요구하지 않는다. B의 학습 통계나 경험만 별도로 계획기에 제공하지 않는다.

### 2. 시계·관측·매크로

- C4 상한은 36,000 활성 틱, 실제 경과 90분이다. 20틱/초 기준 30분이다. 선택 wait, 실행, 경계 처리와 실시간 추론 중 실제 전진한 틱을 모두 활성 시간에 포함한다. 즉시 실패도 최소 한 틱을 실제 실행하며 가짜 틱을 더하지 않는다.
- 결정 경계는 매크로 종료/위험 중단 → 잔여 입력 해제 → 클라이언트 물리 중지와 서버 pause → 양쪽 정지 확인 → 관측·후보·추론·선택 검증 → 재개·물리 복원 → 실행 순서다. Mineflayer 물리 플래그나 Carpet freeze 요청만으로 정지를 가정하지 않는다.
- 관측된 안전 지면을 정상 종료 경계로 우선하되 위험을 안정화 대기로 숨기지 않는다. 텔레포트·체력 복구·숨은 안전 이동으로 문제를 감추지 않는다. 가속 실행은 별도 검증 전 도입하지 않는다.
- 정지 실패는 먼저 수정한다. 실패하면 본 학습 전에 실시간 조건과 예산을 검증한 뒤 학습·평가·A/B/J 전체에 동일 적용한다. 검증되지 않으면 보류한다. 실시간 대기 중 사건·틱을 전이·보상·할인에 포함하고 오래된 후보를 공통 규칙으로 재검증한다. 정지 학습과 실시간 평가를 섞거나 기존 결과를 합치지 않는다.
- 선택 후보가 무효화되면 기존 선택을 다른 행동으로 조용히 치환하지 않는다. 대기 중 틱·사건·보상·비용을 보존하고 새 관측·후보에서 다시 선택한다. 취소된 후보 집합·선택·logprob·무효 이유는 진단 기록이며 actor 학습에서 제외한다. 실제 실행한 재선택만 그 선택 당시 관측·후보 집합·logprob와 연결한다. fallback은 원래 선택의 logprob를 사용한 actor 전이가 아니다. 취소/복구 구간은 시간·보상에 정확히 한 번 반영하고 상태·다음 상태·기간이 유효할 때만 critic에 사용하며 actor mask 0과 trace 단절을 기록한다. 재무효화는 같은 규칙·공통 시간 상한을 따른다. 추론 요청 수와 수집 결정 수를 구분하고 취소 기록을 재선택 actor 경험으로 중복 집계하지 않는다.
- 허용 관측은 위치·방향·속도·체력·산소·화염·도구·내구도·인벤토리, 관측 설비, 반경 8블록 내 시야를 통과한 노출 표면, 직접 관측 지도·방문 이력·최근 행동 결과·목표·남은 시간이다. 계획기·후보 생성기·pathfinder·중단·안정 경계 모두 같은 정보 경계를 따른다.
- 숨은 광석·용암, 전체 청크 지도, 관리자 평가 정보, 정답 경로는 금지한다. hidden_hazard_peek는 false다. 미관측 공간을 통행 지도에 넣지 않는다. 실제 노출 또는 공개 피해 이후의 반응은 허용한다.
- 공통 매크로는 관측 이동 최대 16블록, 노출 군집 채굴 최대 8블록, tunnel 최대 8전진 칸, stair_down 최대 4계단, 제작 batch 1–8개, 화로 투입/회수, 설치/장착이다. 각각 최대 400 활성 틱이며 wait는 20/100/200틱이다.
- 기본 조작마다 관측·사건을 갱신한다. 위험·도구 파손·전제조건 실패·시간 소진·사망에서 중단한다. tunnel/stair는 새로 노출된 다이아 또는 현재 목표 관련 광석에서 중단하며 다른 광석은 지도에만 기록한다. 같은 사건으로 반복 중단하지 않는다.
- 자원 발견 뒤 자동 방향 전환이나 전체 제작 사슬 실행을 넣지 않는다. 정책이 방향·대상·계속 수행 여부를 고른다. 정지 이유, 근거 관측/사건 ID, 지도 버전, 안정 경계를 기록한다.
- 후보는 필터·중복 제거 후 최대 8개다. 실행 효과가 같은 설명/ID 변경은 복수 선택이 아니다. 경로·대상·방향·작업량이 다른 의미 있는 선택을 제공하며 억지 대안을 추가하지 않는다.
- 수집 당시 후보 ID·내용·순서·마스크를 저장하고 PPO에서 다시 생성하지 않는다. 단일 후보는 확률 1, actor loss 제외, critic·시간 비용 포함이다. 후보 0개는 실제 wait와 실패 사건을 처리한다.

### 3. 목표·오류 출처·조건부 지식 조회

- Goal은 goal_id, kind, target, quantity, direction, preconditions, active_budget_ticks, completion_rule_id를 가진다. GoalRegistry가 형식·재료·도구·설비·연료 전제조건과 실제 완료를 검사한다.
- collect는 허용 자원 직접 획득과 총 보유량 1–16 충족, craft는 직접 제작 사건과 보유량, smelt는 관측 화로 출력 직접 회수이며 제작·제련 수량은 1–8이다. 제공 아이템으로 충족한 상태에 새 성공 보상을 주지 않는다.
- descend는 철 곡괭이를 보유하고 y=5–12의 관측 안전 지면에서 20 활성 틱 유지한다. explore는 새 공간 16칸 관측 또는 새 목표 자원 발견이다. escape는 관측 위험에서 3블록 이상 이격하고 안전 상태 20틱 유지한다. mine_diamond는 직접 광석 파괴와 드롭 획득이다.
- 7B는 목표 완료, 연속 실패 3회, 목표 활성 3분, 매크로 20회 중 먼저 발생한 사건에서 재계획한다. temperature 0과 고정 프롬프트를 사용한다. 잘못된 JSON/전제조건은 한 번 재생성하고 다시 실패하면 공통 규칙 복구 목표를 사용한다.
- 최초 목표 오류율은 최초 요청, 재생성 오류율은 재생성 요청, 규칙 복구 사용 비율은 전체 목표 결정 수를 각각 분모로 기록한다. 분자·분모를 함께 보존한다. GoalStats는 시도·성공·시간·실패·재시도를 기록하며 평가 시작 통계는 공통 manifest다.
- 채택 목표 출처는 최초 7B·재생성 7B·규칙 복구로 구분한다. 목표 ID로 이후 행동·진행 사건을 연결하고 복구의 성과를 7B 계획 능력으로 해석하지 않는다.
- 기존 계획기 연결 진단, 초기 7B+Jev 진단, 짧은 C4에서 제작·제련·도구 지식 부족에 따른 부적절 목표 반복이 확인될 때만 로컬 지식 조회를 적용한다. 7B를 호출하지 않는 목재 파일럿과 목표 고정 사전 G4로는 판단하지 않는다. 행동 선택·후보/실행 실패와 구분한다.
- Minecraft 1.16.5 제작·제련 레시피, 채굴 도구 조건, 자원 획득 방법을 제공한다. 코드가 현재 허용 관측·목표·최근 실패 관련 정보를 조회해 고정 7B 입력에 넣는다. 계획기 SFT·온라인 RL, 새 검색 서비스나 숨은 좌표·시드·전체 지도·정답 경로는 추가하지 않는다.
- A/B/J는 같은 자료·조회 규칙을 사용한다. 저장된 진단 상태의 보완 전후 목표·전제조건 오류를 비교하고 무효과·악화도 기록한다. 출처·대상 게임 버전·자료 hash·조회 규칙·프롬프트·조회 결과·목표 출력·적용 이유·검증 결과를 본 학습 전에 고정한다. 구현·검증 시간과 실패 이력을 집계한다.
- 보완 후 일부 목표 오류가 남아도 실행 가능한 목표·의미 있는 선택·실제 진행이 있으면 한계를 기록하고 진행한다. 계획·복구 후에도 실행 가능한 목표가 없어 진행이 막히면 보류한다. 조회 추가로 파일럿·본 학습·평가 횟수와 PC 점유 계획 180시간을 자동 확대하지 않는다.

### 4. NanoJev·PPO·보상

- 공개 state/question/candidate-set 의미와 Choice 헤드를 보존한다. 실제 공개 forward·토큰화·pooling을 확인하며 추론용 predict의 역전파를 가정하지 않는다. backbone은 frozen/no_grad, dropout은 0이다. 공개 초기 logits와 adapter 출력을 비교한다.
- actor를 local/full에서 공유한다. 후보 표현 masked mean에 hidden 256, GELU, scalar output의 2층 MLP를 붙여 local/full 독립 critic을 사용한다. 입력에 objective_kind와 시간 예산을 포함한다.
- 제한 관측의 완전한 마르코프성을 주장하지 않는다. 실제 활성 길이 n의 매크로 보상은 틱별 할인합, 전이 할인은 gamma의 n승이다. 목적별 gamma는 2의 (-1/해당 과제 활성 틱 상한)승이다.
- TD는 할인보상 + 전이할인 × bootstrap mask × 다음 가치 − 현재 가치다. GAE는 TD + 전이할인 × lambda × trace mask × 다음 advantage다. PPO 비율은 저장한 동일 상태·목표·후보 집합에서 새 선택확률/old 선택확률을 사용하며 clip 0.2다.
- task terminal은 bootstrap 0이다. full 목표 변경은 bootstrap/trace를 끊지 않는다. rollout 끝은 trace 0이지만 유효 다음 상태에서 bootstrap한다. 목적/에피소드 변경·신뢰 불가 다음 상태는 trace를 연결하지 않는다. 운영 시간 절단은 과제 terminal과 구분하며 유효 다음 상태가 있을 때만 bootstrap한다. 시스템 오류의 불완전 전이는 제외하고 기록한다.
- actor loss와 advantage 정규화는 유효 복수 후보 전이만 사용한다. 해당 전이가 없는 rollout은 actor 업데이트·정규화를 건너뛰고 기록한다. critic은 유효 모든 전이를 사용한다. frozen 특징은 재사용할 수 있으나 trainable Choice/set 처리와 logits는 업데이트마다 계산한다.
- 기본 Choice LR/value LR은 각각 1e-4, lambda 0.95, entropy 0.01, value coefficient 0.5, grad norm 0.5, rollout 128, minibatch 32, epochs 4다. 파일럿에서 선택한 설정을 본 학습 전에 고정한다. 허용된 기존 PPO 구현은 이 계약을 검증해 재사용할 수 있다.
- local 보상은 목표 성공 +1, 사망 -1, 실제 전제조건 실패 -0.01, 시간 상한까지 총 -0.1이다. 성공·사망·local 시간 소진은 terminal이며 full 보상을 중복 지급하지 않는다.
- full 보상은 다이아 직접 채굴·획득 +100, 직접 최초 원목/작업대/나무 곡괭이 각각 +1, 돌 곡괭이/화로 각각 +2, 철광석/철괴 각각 +3, 철 곡괭이 +5다. 진행 보상 상한은 18이다. 사망 -20, 활성 초당 -0.001, 실제 전제조건 실패 -0.05다.
- full 목표 완료는 정규화한 종류·대상으로 식별한 의미 목표의 에피소드 최초 완료에만 +0.5를 지급한다. 최대 8회·총 +4다. 수량·방향·goal_id 변경만으로 새 의미 목표가 되지 않는다. 정규화 규칙을 본 학습 전에 공통 고정한다.
- 이 중복 제한은 full 목표 완료 보상에만 적용한다. 기존 아이템 최초 획득·제작, 다이아, local 보상은 유지한다. 제공 아이템·이미 충족한 목표에 새 보상을 주지 않으며 무보상 반복 목표도 실제 완료·다음 목표 전환은 정상 처리한다.

### 5. 사전 진단·파일럿·진행 판단

- 목재 파일럿은 같은 월드의 관측 원목 4개 직접 수집, 활성 상한 3분, 고정 목표, 7B 미호출이다. 원목 접근·채굴·획득·보상·reset·의미 있는 복수 후보·Choice gradient를 먼저 확인한다.
- 기본 비교는 Choice LR 1e-4/3e-4 두 설정이며 나머지는 같다. 공개 초기 actor·같은 파일럿 난수·fixture에서 설정마다 1,024결정과 완전 rollout+update 8주기를 수행한다. 초기 10회, 설정별 학습 후 10회, 총 30회 평가한다. 성공 수 → 수행 시간 → 학습/수치 오류 순으로 선택하며 동률은 LR 1e-4다. 기존 계획의 다른 단일 변수 두 값 대체는 시작 전 기록할 때만 가능하며 조합 탐색은 없다.
- 수행 시간은 성공한 평가 에피소드의 평균 활성 게임 시간이다. 성공 수가 같고 1회 이상인 설정끼리만 작은 평균을 우선한다. 모두 성공 0회이면 시간 비교를 생략하고 학습/수치 오류 사건 수가 적은 설정, 다시 동률이면 LR 1e-4를 선택한다. 구조·수치 불능 설정은 제외하고 모두 불능이면 선택을 보류한다. 실패 시간·종료 이유·실제 경과 시간은 별도로 보존하며 빠른 실패를 유리하게 평가하지 않는다.
- 원인 수정 추가 파일럿은 최대 한 번, 설정 하나, 최대 1,024결정, 초기/학습 후 목재 평가 각각 10회다. 공개 초기 actor에서 재시작하며 선택된 설정 또는 선택 근거가 없으면 LR 1e-4를 사용한다. LR 자체의 확인된 문제를 수정할 때만 이유·값을 기록해 변경한다. 추가 설정 탐색은 없고 시간·실패를 별도 집계한다.
- 파일럿 actor를 본 학습 초기값으로 사용하지 않는다. 본 학습은 공개 초기 actor를 다시 로드한다. 파일럿 결정과 평가는 공식 30,000결정·최종 평가와 별도다.
- 사전 G4는 고정 기준 snapshot과 철 곡괭이 제공 상태에서 초기 actor로 활성 3분 × 2회, 실제 경과 각 15분 상한이다. 관측 확장·의미 있는 이동/굴착/채굴·중단·도구·reset을 확인하며 다이아 성공을 요구하지 않는다. 노출 시험 광석의 직접 파괴/드롭 fixture는 비노출 탐색 성공과 구분한다.
- 실제 초기 actor를 고정한 후 초기 자원·제작·철 확보·하강·탐색·실패 후 재시도 상태 6건을 출력 확인 전에 정해 같은 관측·목표·후보를 A/J에 입력한다. A/J 각각 C4 단축 실행 한 번, 활성 5분·실제 경과 20분 상한으로 목표·후보·오류·지연·진행을 기록한다. 우열 결론이나 차이가 있어야 한다는 통과 기준은 없다.
- 본 학습 판단은 Choice gradient·파라미터 변화·본체 불변·수치 안정성, 의미 있는 복수 후보·유효 학습 전이, 보상/reset/학습 연결, 원목 직접 획득 및 G4 실제 진행 로그에 따른다. 짧은 파일럿 성적 상승·사전 G4 다이아는 필수가 아니다. 무개선 사실과 진행 근거를 함께 기록하고 수집·업데이트·실행을 막는 문제가 남으면 보류한다.
- 복수 후보 수와 유효 actor 전이를 과제별로 기록하며 합격 비율을 임의로 만들지 않는다. 거의 강제 행동뿐이면 후보/관측을 먼저 진단하고 모든 군에 공통 수정 후 고정한다. 가중치 변화만으로 수행 개선을 주장하지 않는다.
- 기존 규칙 시연을 활용할 경우 최대 3,000결정의 실행 연결 진단이며 BC 데이터로 사용하지 않는다. 제한 관측·공통 후보/매크로로 직접 도달 단계·시간·제공 아이템·관리자 개입·실패를 기록한다. 빈 C4에서 중간 지원 없이 완료했을 때만 공통 실행기의 완료 경로 확인으로 표현하며 정책 성공 보장으로 쓰지 않는다. 새 필수 전체 실행은 추가하지 않는다.

### 6. 본 학습·checkpoint

- 기본 본 학습 난수 11, 환경 하나, B 본 학습 한 번의 총 30,000 수집 결정이다. 단일 후보·critic-only 결정을 전체 actor 경험으로 부르지 않으며 invalid/단일 후보/워밍업을 제외한 유효 actor 전이와 재사용 횟수를 별도 집계한다.
- G1은 빈 인벤토리 원목 4개/3분, G2는 돌 곡괭이 제공 철광석 3개/10분, G3는 철 곡괭이 제공 지상에서 y=5–12 안전 구역/15분, G4는 철 곡괭이 제공 안전 구역에서 자연 다이아 탐색·직접 채굴/15분이다.
- local 15,000 중 첫 4,000은 G1–G4 각 1,000이다. 나머지 11,000은 1,000결정 블록마다 최근 최대 20개 학습 에피소드의 높은 실패율 과제에 배정한다. 미표본 우선, 동률 G1→G4, G4 총 최소 6,000을 보장한다.
- G4 최소량 확보가 실패율 규칙보다 우선한다. 블록 직전 남은 local 결정 R과 G4 부족량 D=max(0, 6,000−현재 G4 결정 수)를 계산하고 다른 과제 1,000 배정 후 R−1,000<D이면 G4에 배정한다. 그 외에는 미표본·실패율·동률 순서다. R=D이면 남은 블록은 G4다. 초기 각 1,000·1,000 단위·총 15,000을 유지한다.
- local 종료 G1–G3 각 5회와 전체 연결 1회로 실패 구간을 기록한다. 성적 개선·자연 기술 연결이 부족해도 정상 구조·의미 있는 선택·실제 진행이면 예정 full을 수행한다. 연결 부족 자체로 중단하거나 local을 자동 연장하지 않는다. 유효 경험 수집/정책 업데이트를 막는 문제는 보류한다.
- full 15,000의 첫 256결정, 2 rollout은 actor/backbone을 고정하고 full critic만 학습한다. hash 불변·critic 변화·가치 오차를 확인한다. 워밍업을 full 예산에 포함하고 이후 actor 경험으로 재사용하지 않는다. 이후 actor 수집은 14,744결정이며 local critic은 보존한다.
- **복구는 에피소드 경계 방식이다.** 초기 reset 및 에피소드 종료 후 다음 과제의 기준 snapshot을 reset한 경계에서 actor·critic·optimizer·RNG·curriculum·확정 결정 수·검증 이력·미업데이트 rollout buffer를 하나의 일관된 묶음으로 원자 저장한다. 복구 때 해당 과제의 기준 월드·플레이어·인벤토리·체력·시간으로 reset하고 관측 기억·제어·현재 목표·에피소드 보상 ledger를 새 에피소드 시작 상태로 함께 초기화한다. 저장된 초기화 RNG에서 local 고정 목표 또는 full 최초 계획기 요청을 다시 시작한다. 진행 중 게임 복구는 지원하지 않으며 reset 게임과 중간 ledger/목표를 섞지 않는다.
- rollout 중간/PPO 업데이트 도중 중단은 마지막 완전 저장 경계 이후 전이·미완성 buffer·파라미터/optimizer/RNG/curriculum 변경을 함께 폐기하고 경계 상태를 복원한다. 경계 전 미업데이트 buffer는 저장본에서 복원하며 새 에피소드와 trace를 연결하지 않는다. 저장 도중 중단된 불완전 checkpoint는 사용하지 않는다. 에피소드 경계와 업데이트 경계가 항상 같다고 가정하지 않는다.
- 공식 30,000결정은 복구 후 유지되는 확정 수집 결정의 누적 수이며 local 15,000/full 15,000을 정확히 지킨다. 폐기 결정은 공식 경험/유효 actor 전이에서 제외하되 실제 폐기 실행량·시간·실패를 별도 집계하고 총 물리 실행량=확정 결정+폐기 결정으로 보고한다. 폐기 업데이트도 rollback하고 새 attempt ID로 중복 경험을 막는다. 실제 비용은 rollback하지 않는다. 복구 overhead는 기존 PC/API 예산에 포함하며 부족하면 미완료로 남기고 계획을 자동 증액하지 않는다.
- **성능 비교 저장과 복구 저장을 구분한다.** 후보는 local 종료, full 누적 7,500, full 누적 15,000이다. 짧은 마지막 rollout으로 정확한 결정 수에서 actor를 저장하며 중간 actor만으로 게임 reset 후 학습 재개를 허용하지 않는다. 7,500 actor 저장 뒤 실제 비교 실행은 나중에 수행해 진행 중 게임을 덮어쓰지 않는다. 단계 예산 종료는 유효 다음 상태의 운영 절단이며 성공으로 세지 않고 bootstrap 후 reset 경계 복구본을 저장한다. rollback으로 폐기된 분기의 성능 후보는 무효 이력을 남기고 같은 결정 지점의 재도달 저장본으로 대체한다. 후보 수를 늘리지 않는다.
- 후보마다 같은 C4 초기 상태에서 sampling 3회, 총 9회/최대 4.5 활성 시간이다. 다이아 성공 수 → 평균 최고 진행 단계 → 더 이른 checkpoint 순으로 선택한다. 개발 난수와 최종 난수를 구분하고 J·최종 G4 결과를 선택에 사용하지 않는다.
- 사전 예산 축소 시 후보를 local/full 종료 2개로 정해 총 6회/최대 3 활성 시간으로 줄인다. 복구 저장은 유지하며 결과를 본 뒤 후보를 임의 제거하지 않는다. 추가 난수 22/33 등 기존 조건부 선택지는 자동 실행하지 않는다.
- 기존 조건부 추가 본 학습은 최대 두 번이며 비용을 먼저 산정하고 최초 실패·모든 반복 결과를 남긴다. 버그/설정 변경은 새 run이다. 더 큰 공개 행동 선택 모델 교체도 본 학습 전 원인 진단에서 표현력/학습 가능 부분의 병목이 확인될 때만 기존 대안으로 검토한다. 실제 확정 시 같은 공개 초기 actor로 A/B를 함께 바꾸고 후보별 확률/logprob·학습 파라미터·사용 조건·메모리·처리량을 검증한 뒤 실제 모델명으로 보고한다. 추가 모델 비교나 두 번째 본 학습을 필수로 만들지 않으며 파일럿 상한·실패 이력·비용을 유지하고 초기 A/J 진단과 lock을 다시 확인한다.

### 7. Jev 계약·오류·지출

- 실제 연결 기준은 OpenRouter의 alpha decisions API와 typesafe/jev-1.13이며 계정 접근·실제 모델 ID·지원 설정·요청/응답·요금 확인 날짜를 기록한다. 문자열 state와 choice 질문·행동 기준·criteria를 공통 Observation/Goal/Candidate 의미로 변환한다.
- 각 요청의 a0 등 전송 키는 저장한 candidate_id와 일대일 대응한다. 반환 선택을 새로운 후보 순서에 적용하지 않는다. A/B/J에는 같은 목표 설명·행동 기준·관측·후보 설명/순서를 제공하고 형식 차이만 변환한다. J 전용 전략·안전 힌트·원본 데모 지침은 넣지 않는다.
- 공개 문서의 전체 확률 지원과 실제 계정의 유효 전체 분포를 구분한다. 모든 유효 후보 확률의 완전성·유한성·비음수·합 1 및 의미를 확인하면 로컬 temperature 1 categorical sampling과 같은 평가 난수 목록을 사용한다.
- 선택 ID만 제공하거나 분포가 불완전·불명확하면 고정 API 설정의 native choice를 사용한다. 선택 confidence를 전체 분포로 만들거나 argmax/sampling과 동등하다고 부르지 않는다. 외부 내부 난수 통제를 가정하지 않으며 결정적 반복 여부를 기록한다.
- SelectionResult는 candidate_id·mode·전체 probabilities 또는 미제공 null·지연·provider/model·usage 또는 null·재시도/오류/fallback을 반환한다. Jev 응답은 PPO·BC·checkpoint 선택에 쓰지 않으며 로컬 logprob로 바꾸지 않는다.
- 잘못된 schema/유효 후보 밖 ID는 동일 입력으로 한 번 재요청하고 다시 실패하면 공통 고정 유효 fallback을 사용해 모델 오류를 기록한다. 후보 0개는 공통 wait 규칙이다. 통신 재시도는 본 학습 전에 고정한 상한을 지키며 원본 로그·대기·모든 과금을 보존한다. 조용히 NanoJev로 대체하지 않는다.
- 모델 API 사용료 총 상한은 US$5다. 연결 확인·A/J 진단·최종 평가·실패 요청의 과금·모든 재시도를 포함한다. 충전 수수료는 별도 기록한다. 실제 과금 요청으로 예정 비용을 본 학습 전에 추정하며 호출 상한과 비용 통제를 고정하고 임의 초과하지 않는다.
- API 키는 비밀 주입으로만 관리하고 문서·Git·로그·lock에서 제외한다. J 접근 불가는 로컬 학습 자체를 금지하지 않지만 J 미실행과 Jev 대체 질문 미검증을 명시한다. mock 연결 검증은 J 성능 결과가 아니다.

### 8. 최종 평가·보고

- A/B C4 주 평가는 temperature 1 categorical sampling 각각 5회, 같은 로컬 평가 난수, 균등 탐색 혼합 없음이다. 각 argmax 1회는 별도 보조 진단이며 동률은 고정 candidate_id 순서다. 성능 결과를 보고 주 선택 모드를 바꾸지 않는다.
- J는 사전 검증·고정한 모드로 5회다. 핵심 C4 합계는 17회/최대 8.5 활성 시간이다. 고정 평가 블록에서 군을 교차 실행하고 매번 reset한다. 외부 모델 버전 변경은 별도 기록하고 결과를 조용히 합치지 않는다.
- 필수 G4는 A와 선택 B의 sampling 각각 3회, 공통 최종 난수, 총 6회다. G4 학습 기준 snapshot·철 곡괭이 제공, 고정 다이아 목표, 7B 미호출, objective_kind local·local 시간 예산이다. 각 18,000 활성 틱/15분, 실제 경과 45분 상한이다.
- G4는 앞단 제작/하강 및 checkpoint 선택과 분리한 진단이며 미사용 맵 시험이 아니다. B의 같은 시작점 학습과 G4 실제 경험량을 밝힌다. 자연 광석 직접 파괴·드롭 획득만 성공이고 0회도 보고한다. C4 성공률과 합치거나 결과로 B checkpoint를 다시 선택하지 않는다.
- 기본 최종 총 23회/최대 10 활성 시간이다. 사전 축소는 A/B/J 주 평가를 모두 3회로 줄이고 argmax 2회와 G4 6회를 유지해 총 17회/7시간이다. J 불가 시 기본 A/B C4 12회와 G4 6회, 총 18회/7.5시간이며 Q2 미검증이다.
- C4 주 지표는 직접 채굴 성공 슬롯 수/예정 슬롯 수다. 예정 평가 1회는 슬롯 하나이며 운영 오류·비용 중단도 예정 분모에 남긴다. 행동 실패·사망·탐색 실패는 재시도하지 않는다. 서버 오류만 같은 snapshot/RNG로 최대 한 번 재시도하고 그 마지막 허용 시도의 성공/실패/오류를 슬롯 결과로 사용한다. 최초 오류는 별도 운영 오류로 기록한다. 재시도도 오류이거나 예산상 재시도 미실행이면 해당 슬롯은 성공 0이고 예정 분모를 유지한다. 두 시도를 독립 평가 두 회로 세지 않는다. 각 attempt ID·원본/재시도·이유·시간·비용을 모두 보존하고 외부 내부 난수 복원은 보장하지 않는다. 파일럿·checkpoint·최종 C4/G4 평가에 공통으로 결과 전에 고정한다.
- 진행 단계는 0 미진행, 1 원목, 2 돌 곡괭이, 3 철 직접 확보, 4 철 곡괭이 직접 제작, 5 안전 채굴 구역, 6 다이아 직접 채굴·획득이다. C4 직접 사건만 세고 제공 상태는 제외한다. 최종 표는 단계별 도달 횟수로 제시하며 단계 평균은 checkpoint 선택에만 쓴다.
- 기록은 성공/실패·최고 단계·종료 이유·활성/실제 시간·결정 수·후보 0–8 분포·복수 선택·유효 actor 전이·목표 오류 분자/분모·복구·출처별 진행·중단 근거·API 비용·GPU 최고 메모리·학습 준비 비용을 포함한다. local/full 학습 곡선, C4 주 평가, argmax, G4를 구분한다. 성공 조건부 시간 평균에는 실패 수와 종료 시간도 제시한다.
- 모든 실패에 계획·후보/실행·탐색 정체·위험·학습·시스템/API/비용 또는 불명확 태그를 남긴다. 로그만으로 원인이 확정되지 않으면 단정하지 않는다. 발표 사례 선정은 군별 첫 실패/최빈 원인 등 사전 기준을 사용한다.
- A↔B는 이번 추가 RL, B↔J는 고정 환경을 연습한 정책의 조건부 대체 비교다. J>A일 때만 J를 향한 초기 격차 축소를 설명한다. 모델 구조·사전학습·서비스 선택 차이와 B의 추가 경험을 밝힌다. 실시간 비교는 지연을 포함한 시스템 결과로 해석한다.
- 다이아 모두 0회여도 주 지표를 바꾸지 않는다. 가중치 변화·부분 과제 개선·형식 검증만으로 전체 수행 개선을 주장하지 않는다. 3/5회 고정 월드 표본으로 동등성·유의성·일반화·보편적 대체·세계 최초를 주장하지 않는다. 맵·광석·경로 암기 가능성을 명시한다.

### 9. 처리량·고정·실행 도구

- PC 점유 180시간은 계획 배정이며 실측 보장이 아니다. 환경/모델/파일럿/사전 진단 20, 시연·부분 기술/연결 진단 20, 본 학습 90, checkpoint 비교 10, 최종 평가 27, 예비 13시간이다. 이번에는 BC가 없다. 사람 개발 시간과 PC 시간·API 금액은 구분한다.
- full critic 워밍업 2주기를 별도 측정하고 이후 최소 3개 완전 rollout+update와 C4 reset 한 번을 포함한다. local도 과제별 완전 업데이트와 reset 비용을 측정한다. 임의 30분 경과만으로 측정을 끝내지 않는다.
- 학습 예상 시간은 15,000/local 처리량 + 14,744/full PPO 처리량 + 워밍업 시간이다. 처리량은 추론·계획·수집·업데이트·reset·일반 저장을 포함한 결정/시간이며 워밍업을 중복 더하지 않는다. 334결정/시간은 대략적 참고치다. 유효 actor 전이/시간과 강제 결정 비율을 함께 보고한다.
- 평가는 군·과제·모드별 실제 평균 시간 × 예정 횟수에 20% 여유를 더한다. API 지연/과금을 포함한다. 예산 부족 시 선택 실험 보류 → checkpoint 2개 → 공통 C4 주 평가 3회 순으로 기존 축소 규칙을 결과 전에 고정한다. 필수 G4는 유지하며 남은 부족은 초과/미완료로 명시한다.
- experiment lock은 모델/공개 초기 hash·코드/출처/허용 근거·프롬프트·관측/목표/후보/매크로/보상·목표 정규화·오류/출처 집계·지식 적용 여부/자료/규칙/진단·월드/고정 snapshot/hash·학습/파일럿/개발/최종 난수·reset·clock 검증/해석·BC 미적용·파일럿 제한/선택/LR 예외·경험 집계·checkpoint/evaluation 수·J 실제 접근/schema/mode/설정/사용량/요율/US$5/호출 상한·미검증 질문을 본 학습 전에 고정한다. 에피소드 경계 복구·확정/폐기 경험 집계·실시간 취소/fallback actor 제외·평가 슬롯/재시도·G4 최소량 우선·파일럿 시간 집계와 기준 문서 hash도 고정한다. F는 제외 상태다. 비밀값은 제거한다.
- 공통 계약은 Environment reset/observe/step, GoalRegistry validate/completed, Planner choose_goal, CandidateGenerator generate, ActionSelector select, NanoJev 후보 encoding/scoring, ActorCritic evaluate_actions, RewardLedger compute, GAE 계산, Curriculum choose_task, BudgetEstimator forecast다. 기존 코드가 생기면 역할을 대응시키며 이름이나 별도 추상 계층을 강제하지 않는다.
- Observation은 episode/obs ID·활성 틱·목적/시간·제한 상태/지도/이력, Candidate는 ID·종류·params·max_ticks·stop rule·source obs·설명, StepResult는 다음 관측·실제 틱/사건·종료/절단/이유·정지 근거/시간을 갖는다. Transition은 저장 상태/목표/후보/mask·선택/old logprob/value·목적/보상/할인·다음 상태·bootstrap/trace/valid를 갖는다. EpisodeSummary는 군/run/checkpoint·시작 상태·과제/목적·모드/난수 통제·clock·단계/성공/실패/시간·후보/actor 경험·목표 오류/출처별 진행·버전을 포함한다.
- Python–게임 bridge는 request_id/method/payload와 같은 ID의 result/error를 가진 JSONL RPC를 사용한다. stdout은 RPC, stderr는 진단이다. 관리자 reset/freeze와 정책 step 권한을 분리하고 정책의 자유 코드/콘솔 명령은 허용하지 않는다.
- 공개 mc-diamond CLI는 환경 확인, 시계/정보 감사, 매크로/계획기/모델/Jev smoke, 목재 파일럿, 초기/G4 진단, benchmark/budget/lock, B 학습, checkpoint 비교, C4/G4 평가와 분석을 연결한다. 현재 명령이 이미 구현되었다고 가정하지 않는다. 기존 도구·표준 라이브러리·허용된 기반 라이브러리를 우선하며 새 테스트 프레임워크나 서비스는 필요 근거 없이 추가하지 않는다.
- 구현 순서는 환경/출처 → schema/selector → 월드/시계 → 제한 관측 → 후보/매크로/성공 판정 → 목표/복구 → 7B/Jev → NanoJev/critic → 보상/PPO → 파일럿/커리큘럼 → 실측/lock → 학습/평가 → 보고서다. 날짜별 마감은 새로 만들지 않는다.
- 참고 공개 시연은 후보→모델 선택→실행 구조의 아이디어로 사용한다. 명시적 허용 전 원본 코드·프롬프트를 복사/번역/변형해 가져오지 않는다. 허용된 기반 라이브러리를 활용한 자체 구현이 기본이며 출처·revision/hash·허용 근거·직접 변경점을 기록한다. 라이선스 문의 메시지 전송은 이 명세의 작업이 아니다.

## Testing Decisions

- **확정한 주 테스트 경계:** 공개 CLI/실험 실행 흐름에서 reset → 관측 → 목표 → 후보 → 선택 → 실행 → 보상 → rollout/update 또는 평가 → 요약/예산 결과를 검증한다. 예정된 게임 RPC·계획기·외부 행동 API 계약에 맞는 최소 모의 backend를 사용하며 모듈별로 동일 시나리오를 반복하는 별도 테스트 계층은 만들지 않는다. 실제 배포 코드와 동일한 공통 실행 흐름을 통과한다.
- **좋은 테스트:** 외부에서 확인할 수 있는 상태·사건·candidate_id·학습/시간 예산·종료 이유·보상·요약·오류/비용을 검증한다. 내부 함수 호출 순서나 구현을 그대로 복제한 기대값, 사전 성적 상승 기준은 피한다. 저장소에는 기존 테스트·fixture·테스트 프레임워크가 없어 재사용할 테스트 선례가 없다. 계획된 doctor/smoke/진단 경로를 재사용한다.
- **모의 연결 시나리오:** 같은 입력/후보 의미의 A/B/J 전달과 ID 매핑, zero/single/multiple 후보, 중단과 reset, 정상/잘못된 목표→재생성→규칙 복구→출처별 진행, 미제공/유효/잘못된 API 분포, 한 번 재요청·fallback·비용 상한·비밀 제거, checkpoint 복구·정확한 결정 수·평가 예정 분모·사전 축소를 대표 시나리오로 확인한다. mock 결과를 실제 J 성능이나 게임 물리 검증으로 표현하지 않는다.
- **이번 보완의 경계 사례:** rollout/업데이트/원자 저장 중단 후 경계 모델·buffer·reset 게임·빈 ledger 일치, 확정/폐기 결정 분리와 정확한 단계 checkpoint, 취소 후보와 실행 재선택의 logprob 분리·대기 사건 한 번 반영, 최초 서버 오류→재시도 성공이 한 성공 슬롯이고 오류 이력은 남는 경우, 재시도 오류/미실행의 고정 분모, G4 부족량 강제 배분, 파일럿 모두 0 성공의 시간 비교 생략을 확인한다. 새로운 성능 실험이나 테스트 계층은 추가하지 않는다.
- **수치 계약의 최소 예외:** 보상·GAE·actor/critic의 이미 계획된 공개 계약에서 손으로 계산 가능한 짧은 전이 예제를 확인한다. 다른 매크로 길이의 할인, terminal/유효 truncation/목표 변경, 단일 후보 actor 제외, actor 전이 없는 rollout, masked 후보 확률과 saved candidate set, local/full 보상 분리, 의미 목표 중복과 8회 상한, 반복 무보상 목표 전환이 대상이다. 전체 CLI에 복잡한 수치 테스트 전용 기능을 추가하지 않는다.
- **실제 시계 진단:** 평지·제련·드롭·용암·낙하·침수·화염에서 결정 지연 0/5/10초를 각각 3회 시험한다. 위치·속도·체력·산소·화염·인벤토리·제련·활성 틱·사건의 지연 불변을 확인한다. 위치 허용 오차는 0.001블록이고 지연 비례 드리프트는 불허다. 실시간 대안도 공통 틱/사건·후보 재검증·학습/평가 일관성과 예산을 별도 검증한다.
- **실제 정보·직접 성공 진단:** 보이는 상태가 같고 벽 뒤 광석/용암만 다른 fixture에서 노출 전 관측·후보·경로·중단이 같아야 한다. 직접 파괴·도구·드롭·획득 연결과 지급/상자 등 제외를 확인한다. 관리자 검증 데이터를 정책으로 보내지 않는다.
- **실제 모델·학습 진단:** 공개 초기 logits의 adapter 일치, Choice gradient·업데이트 후 변화·backbone hash 불변·유한 손실, 독립 critic과 full 워밍업의 actor 불변을 검증한다. 기존 목재 파일럿·사전 G4·A/J·local 연결 진단에서 의미 있는 선택·유효 전이·실제 진행과 본 학습 근거를 기록한다. 하드웨어/모델/과금 확인은 mock으로 대체하지 않는다.
- **조건부 지식 진단:** 저장된 기존 진단 상태로 보완 전후 목표·전제조건 오류와 출처별 결과를 비교한다. 실제 자료·조회·프롬프트 hash와 모든 군의 공통 적용을 확인한다. 무효과/악화와 잔여 오류를 기록하고 추가 학습 파일럿은 늘리지 않는다.
- 진단·테스트는 확정된 사전 검증을 구현하며 새로운 연구 비교군·성능 실험·학습 반복·합격 비율을 추가하지 않는다. 실행 실패는 로그로 남기고 현재 문서 작성만으로 검증 완료 처리하지 않는다.

## Out of Scope

- 이번 회차 F/Astra 구현·진단·평가, 계획기 SFT/온라인 RL, BC, Jev 훈련과 Jev 출력 학습 데이터 사용.
- 추가 비교군·새로운 환경/월드 시드·평가 시작점 이동·미사용 구역·reset 풀·일반화 실험의 자동 추가.
- 추가 난수·추가 모델 비교·J의 G4·L7B/R/S·행동 모델 교체·본 학습 반복을 기본 필수 작업으로 실행하는 것. 기존 계획의 조건부 대안은 유지하되 목적·비용·범위 확정 없이 자동 실행하지 않는다.
- 성적 부족을 이유로 local 학습 연장, 정해진 추가 파일럿 한 번 초과, 반복 설정 탐색, 결과를 본 뒤 checkpoint/평가 모드/예정 분모 변경.
- 숨은 광석/위험/시드/전체 청크 조회, 사전 조사 경로, 모델별 후보/안전 힌트, B만의 계획기 경험, 정책 관리자 명령·자유 코드.
- 전투·네더·포털·엔더드래곤, 매크로 자동 발견, 공개 시연 기록과 시간 우열 비교, 새로운 프런트엔드/웹 서비스/배포, 라이선스 문의 등 제3자 메시지 전송.
- API 키 게시·유료 충전·US$5 초과, PC 계획의 임의 증액, 날짜별 일정표, 추가 통계 검정·동등성/보편적 우월성 주장.

## Further Notes

- 기준은 아래 SHA-256의 실제 작업공간 파일과 2026-10-08 사용자 PRD 검토 보완이다. 이전 첨부 PLAN v1.7-final/2026-10-06과 인터뷰 반영본 v1.7-grill-final/2026-10-07을 구분하며 최종 PLAN은 v1.7-prd-final이다. 첨부되지 않은 문서까지 사용자가 대조했다고 주장하지 않는다. 인터뷰·테스트 경계 검토는 종료했고 사용자가 이번 보완 후 확정·게시·ready-for-agent 부착을 지시했다. 현재 관련 ADR은 없다.

|기준 파일|버전/수정일|SHA-256|
|---|---|---|
|PLAN.md|v1.7-prd-final / 2026-10-08|e3dbf54253a1df0479999eb36ee7c1407bb20c9951ce51e620d5e08b543e7309|
|DECISIONS.md|v1.1-prd-final / 2026-10-08|97fcb8bb74063c2c84db579decfd35fc880173d951e52491a159c49b490f2484|
|GLOSSARY.md|파일 내 버전 표기 없음 / 이번 보완에서 변경 없음|9290318d3e1dea22f88d16990e59a8b3cbd3b876706bc8b66fa0de582809e382|

- 이 hash는 게시 시점 로컬 파일의 정확한 바이트를 식별한다. GitHub 기본 branch와 자동 동기화된다고 가정하지 않는다. 이 Issue 본문은 기준 결정과 이번 보완을 함께 담은 구현 명세이며 별도의 미공개 문서를 읽어야 핵심 규칙을 알 수 있게 작성하지 않는다.
- 설치 시 고정할 revision/hash, 계정의 실제 API 접근·확률·과금·호출 상한, 환경 정지·처리량·학습 효과는 실행 전 확인 사항이다. 임의 값을 확정 사실로 만들지 않는다. 공개 분포 설명은 OpenRouter alpha decisions 응답 명세와 TypeSafe Choice 문서를 근거로 하되 실제 응답 검증이 필요하다.
- 완료 산출물은 재현 가능한 구현·출처·검증 기록·experiment lock·학습/checkpoint/evaluation 이력·local/full 곡선·C4/G4/실패/비용 보고서다. J 불가 시 로컬 결과와 미검증 질문을 남기며 전체 성공 0회도 보고한다. 본 학습을 막는 미해결 문제나 미실행은 완료한 실험처럼 표시하지 않는다.
- 발표는 문제 → 관련 연구와 질문 → 고정 계획기/학습 행동 정책 역할 → A/B/J → G4·실패·비용·한계 순으로 구성할 수 있다. 외부 모델/라이브러리와 직접 설계·검증한 기여를 구분하며 학술 선례와 공개 데모를 구별한다.
