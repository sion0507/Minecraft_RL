# 실행 기록

## 2026-10-10 — 티켓 #2 최종 검토 및 통합 준비

사용자가 #2 완료 확인 후 push·merge를 요청했다. 최신 GitHub #1/#2 본문·댓글(둘 다 댓글 없음), 원격 main `3183b52`, ticket-2 `5c26f95`를 대조했다. 독립 Standards/Spec 검토 모두 중대한 지적 0건이며 #2 수락 기준에서 빠진 구현이나 추가 코드 수정은 없다. 별도 승인된 연구 계획/설치 규칙 문서를 함께 통합한다.

- 전체 pytest 17개 통과(3.51초), strict mypy 9개 파일 통과, diff 공백 검사 통과.
- 공개 smoke CLI의 reset→관측→목표→후보→선택→실행→보상→요약 JSONL을 재확인했다. 모의 목표 완료·1결정·20틱·진단 보상 1.0·확률 null·actor 전이 0·다이아 성공 false다.
- 샌드박스 doctor는 GPU 드라이버 접근 오류(exit 9)를 기록했고, 장비 접근을 허용한 재실행에서 RTX 5070 Ti/driver 595.91.07/16303 MiB 및 실제 GPU 합계 10을 확인했다. Python/Node/Java도 합계 10, Mineflayer 4.39.0 import를 확인했다.
- nvcc 부재는 유지되므로 실제 doctor는 cuda=missing·ready=false·exit 1이다. 진단 기능 검증과 전체 실험 환경 준비를 구분한다. 실제 Minecraft/모델/API/PPO는 후속 티켓이며 미검증 상태다. 기존 인증 의존성 npm audit 경고는 이번에 재검사하거나 해결된 것으로 표시하지 않는다.

검토 상세: `docs/reviews/issue-2.md`. 유료 호출·학습·결제는 수행하지 않는다. 기존 티켓·문서 변경을 포함한 검증된 브랜치를 push하고 main에 통합한 뒤 원격 결과를 확인한다.

## 2026-10-10 — 새 PRD와 기존 구현 티켓 일치화

사용자의 추가 요청으로 기존 구현 이슈 #9, #10, #12, #16, #17, #18, #20, #21, #22, #23, #25의 본문·수락 기준을 GitHub에 갱신했다. #10/#17/#23의 제목을 새 범위에 맞추고 참조 제목도 맞췄다. #18은 #10 의존 링크의 표시 제목만 변경했다. PRD/#1의 기존 '다른 티켓은 변경하지 않는다' 문구도 이번 추가 요청에 맞춰 동기화했다.

- #9/#10: 공통 목표·검증·재계획·복구와 계획기 모델/출처, 고정 7B와 Astra backend·실제 접근/지원 설정/예산 진단. #12: J/F 동일 Jev와 진단·실패/재시도 포함 합산 US$5, 별도 Astra ledger/승인 상한.
- #16/#17: 초기 계획 오류/원인 진단, 지식·입력·검증·재계획 보완, 공통 계획 상태 6건 비교, 여섯 조건의 마지막 학습 제안·명시적 승인 절차. 실제 계획기 학습은 티켓 완료 기준이나 자동 분기가 아니다.
- #20/#21/#22: F 접근·비용·시간/GPU/PC의 본 학습 전 확인, 조건부 학습을 선택한 경우만 승인·PPO 전 완료/재검증, A/B/J 동일 최종 7B 고정. 행동 학습량·알고리즘·checkpoint 선택 규칙은 유지하며 F/계획기 진단 결과로 B checkpoint를 고르지 않는다.
- #23/#25: 핵심 A/B/J/F C4 기본 22회/공통 축소 14회와 필수 G4 6회(총 28/20회), F 미실행 예정 슬롯·질문 미검증, 네 비교의 해석과 비용/실패 보고. B↔F는 전체 시스템 비교다.

검증: 게시 직전 전체 25개 이슈가 초기 조회와 같음을 확인했다. 게시 후 전체를 다시 조회해 수정안 본문·제목 및 PRD 기준 파일 SHA-256의 일치, 미수정 티켓의 원문 보존, 전체 라벨·상태·댓글·의존 ID 및 참조 제목 보존/일치를 확인했다. 새 이슈·댓글·라벨·상태 변경은 없다. `git diff --check` 통과.

현재 추가 티켓은 필요 없다. Astra 연결은 #10, 공통 계획 비교·조건부 학습 검토/제안은 #17에서 담당한다. 향후 실제 계획기 학습을 별도 승인할 경우에만 구체적인 학습 실행 티켓의 필요성을 다시 보고한다. 작업 브랜치는 `ticket-2`이며 이번 변경은 문서/티켓뿐이다. 코드·학습·유료 모델 API·결제·Git commit/push/merge는 실행하지 않았다. Astra/Jev 실제 접근·과금·지연과 180시간 내 수행 가능성은 후속 승인된 진단에서 확인해야 한다.

## 2026-10-10 — 핵심 F 복원 및 조건부 계획기 학습 문서 수정

기준: PLAN v1.7-prd-final, DECISIONS의 기존 결정, GitHub #1 본문·댓글(댓글 없음), 관련 기존 티켓. 작업 브랜치는 `ticket-2`; 기존 #2 구현 commit `19e64cb`와 별도의 미커밋 문서 변경이다. commit/push/merge는 수행하지 않는다.

- PLAN v1.8-core-F, DECISIONS v1.2-core-F, PRD v1.1-core-F와 README/AGENTS/GLOSSARY의 상충 규정을 갱신했다. 과거 결정 본문은 보존하고 현행 결정의 대체 범위를 명시한다.
- F=Astra+J와 동일 Jev를 핵심 비교로 복원한다. 기본 기존 C4 17+F 5+G4 6=28회, 공통 축소 C4 14+G4 6=20회다. 행동 PPO 30,000결정·보상/SMDP/PPO·checkpoint/실패/복구 규칙은 유지한다.
- 계획기 학습은 진단→지식·입력·검증·재계획 보완→공통 Astra 6상태 비교→여섯 조건 검토→별도 제안·분석/비용 보고→명시적 승인 순서의 마지막 대안이다. 실제 학습은 수행하지 않으며 승인한 경우만 PPO 전에 마치고 A/B/J 최종 7B를 동일하게 고정한다.
- 2026-10-10 공개 페이지에서 Jev US$0.042/0, Astra 표준 US$10/50(입력/출력 100만 토큰당)을 조회했다. 실제 접근·응답·사용량·과금·지연은 미검증이다. PLAN §11.1.1의 추가 비용 US$4.17 및 20% 여유 US$5.004는 명시된 토큰/요청 가정의 예시이며 지출 승인이 아니다. Jev 총 US$5는 J/F·진단·실패/재시도 합산, Astra 별도 상한은 미승인이다.
- F 5회 추가 활성 상한 2.5시간, 최초 시도 게임 경과 상한 7.5시간이며 reset/진단/재시도는 별도다. 기본 전체 최초 시도 상한 37.5시간은 기존 최종 평가 배정 27시간을 넘는다. 실측 평균에 따른 재산정 없이 기존 PC 180시간의 충분성을 주장하거나 증액하지 않는다. GPU 연산/PC 점유는 따로 측정해야 한다.
- 구현 영향: 현재 CLI는 doctor/smoke-episode, Goal은 fixed collect, EpisodeSummary는 smoke 전용이고 실제 계획기·A/B/J/F selector·예산/학습/evaluate는 아직 없다. src/tests/configs/fixtures/의 이번 코드 변경은 필요하지 않다. 후속 구현에서 Astra backend·공통 계획기 출처/model ID·J/F 합산 비용·평가 슬롯/lock을 반영해야 한다.

PRD 갱신 단계에서는 기존 티켓을 수정·생성하지 않고 다음 변경 필요성을 보고했다. 이후 사용자의 추가 요청으로 위 기록과 같이 기존 티켓을 갱신했다.

|기존 이슈|변경 필요성|
|---|---|
|#9 / T08|공통 목표·복구 로그에 7B/Astra 모델과 출처를 함께 기록|
|#10 / T09|기본 7B 고정은 유지하고 공통 Astra backend·접근/설정 진단 범위를 반영|
|#12 / T11|J/F 전체 Jev US$5 집계·F 예정 비용 예약·미실행 질문 범위|
|#16 / T15|기존 A/J 진단의 계획 순서/반복/관측 불일치·원인 분류와 공통 6상태 계획 비교|
|#17 / T16|지식 조회 뒤 입력/검증/재계획 보완·Astra 비교·여섯 조건의 마지막 별도 제안. 학습 실행을 필수 수락 기준으로 만들지 않음|
|#20 / T19|F 우선 접근/별도 Astra 예산·시간/GPU/PC·Jev 합산·28/20슬롯·조건부 최종 7B/hash/승인을 lock에 반영|
|#21 / T20|본 PPO 전 조건부 계획기 준비 종료·최종 고정 확인; 학습량/알고리즘은 유지|
|#23 / T22|제목·본문 A/B/J/F, C4 22/14회·F 미실행/Q3/Q4 미검증|
|#25 / T24|J↔F/B↔F와 전체 시스템 해석, 계획기 전후 별도 진단·F 비용/미검증 보고|

GitHub #1 제목·본문을 v1.1-core-F로 갱신하고 재조회해 로컬 PRD와의 일치 및 라벨·댓글 보존을 확인했다. 게시 전 최신 본문과 초기 조회본이 일치하는지도 확인했다.

검증: `git diff --check` 통과. 일회성 문서 검사를 통해 PLAN §6.1–6.2(Choice/PPO), §8(보상/커리큘럼/학습량), §9.2(checkpoint/복구), §9.4(G4)와 PRD §4/§6의 원문 일치, 과거 DECISIONS 본문 보존, 기준 파일 SHA-256, 평가 수/시간 상한/API 가정 산술을 확인했다. 변경 파일은 문서 7개뿐이다. 코드 변경이 없어 pytest/mypy·실제 게임/모델/API 검사는 이번에 재실행하지 않았다. 학습·유료 모델 API·결제·새 티켓·Git commit/push/merge는 이번 작업의 실행 범위에 없다.

## 2026-10-09 — 이슈 #2 / ticket-2

기준: GitHub #1 본문·댓글(댓글 없음), #2 수락 기준·댓글(댓글 없음), PLAN.md §§12–14. 시작 commit `3183b52270b8025144b56d955768ca27332e225e`; 기존 작업 변경 없음.

### 구현

- Python/uv 패키지와 공개 `doctor`, `smoke-episode`, pytest/mypy 설정 및 의존성 lock.
- Observation/Goal/Candidate/SelectionResult/StepResult/EpisodeSummary, episode/attempt/candidate/source-observation ID, 저장 후보·mask, JSONL 출력과 구조화 오류.
- 관리자 FD와 정책 stdin을 구분하는 subprocess RPC. 모의 fixture backend와 같은 실행기를 사용하는 대체 RPC 설정.
- 고정 원목 목표의 reset→관측→후보→선택→step→획득 사건 진단 보상→summary. terminal/유효 절단/무효/backend 오류 구분; 미제공 확률 null; actor 경험 0; 다이아 성공 false.

### 실제 환경 진단

|검사|실제 결과|
|---|---|
|Python|3.12.3; sum(0..4)=10|
|uv|0.12.23; `.tools/uv`에 설치, PATH 영구 변경 없음|
|Node/npm|24.20.0 / 11.19.0; Node sum(0..4)=10|
|Java|OpenJDK 21.0.12.1; 임시 Java 소스 실행 sum(0..4)=10|
|GPU|접근 허용 실행에서 NVIDIA RTX 5070 Ti, driver 595.91.07, 16303 MiB|
|GPU 연산|자체 PTX 커널로 sum(0..4)=10, CPU로 복사한 결과 일치|
|CUDA toolkit|nvcc 없음; doctor의 cuda=missing, ready=false, exit 1|
|Mineflayer|4.39.0 설치/import 및 createBot export 확인. 서버 연결 없음|
|개발 검사|pytest 9.1.1, mypy 1.20.2 설치|

제한된 샌드박스에서는 nvidia-smi가 driver 통신 실패(exit 9)였지만 권한 있는 실제 장비 조회와 GPU 연산은 통과했다. Java 21과 Minecraft 1.16.5의 실제 호환·게임 정지는 검증하지 않았다.
시스템 Python의 pip/ensurepip는 없었으며 uv로 가상환경을 만들었다. 첫 pytest 실행은 시스템 ROS plugin이 lark를 요구해 실패했고 plugin 자동 로드 해제로 해결했다.

### 검증 기록

- 첫 CLI 성공 테스트: 구현 전 exit 1로 RED, 구현 후 PASS.
- doctor 테스트: 명령 미구현으로 RED, 실제/부재/실행 오류 보고 구현 후 PASS.
- backend 실행 불가 요약·정책 채널 EOF 종료·다중 결정 획득 기억: RED 확인 후 수정, 각각 PASS.
- GPU probe: 모듈 부재로 RED, 실제 장비에서 산술 출력 10으로 PASS.
- 마지막 개별 파일 검사: `uv run pytest tests/test_cli.py -q` 16 passed; `uv run mypy .` 통과.
- `npm --prefix bridge ci --ignore-scripts` 설치 통과. npm audit는 uuid 권고에서 전파된 moderate 6건을 보고(exit 1)했으며 무리한 자동 downgrade/override는 적용하지 않았다. 상세 출처는 third_party/README.md 참조.
- 최종 `npm --prefix bridge ci --cache .cache/npm --offline`은 scripts를 포함해 설치 통과했고 이후 Mineflayer 4.39.0 import를 확인했다. offline 설치의 “0 vulnerabilities” 출력은 온라인 보안 권고 검사를 대체하지 않으며 앞서 확인한 6건을 해결한 결과가 아니다.
- 최종 전체 검사: `uv run pytest` 17 passed(3.39초), `uv run mypy .` 9개 파일 통과, `git diff --cached --check` 통과.
- 공개 CLI 수동 실행: 모의 원목 목표 완료, 1결정·20활성 틱·진단 보상 1.0, 실제 다이아 성공 false, actor 전이 0, exit 0.
- Standards 리뷰 0건. Spec 리뷰 P2 2건(잘못된 요청의 유효 ID 상실, 사건 출처 mock 전용)을 재현 테스트 RED→GREEN으로 수정했다. 실제 출처 wire 호환 검사는 외부 scripted RPC이며 게임 검증이 아니다. 상세: docs/reviews/issue-2.md.

### 미실행 및 다음 작업

실제 Minecraft backend/reset/freeze·정보 감사·게임 물리·계획기/NanoJev/Jev·과금·연구 보상/PPO·실험 lock·학습·평가는 미구현/미실행이다. 모델·월드·서버 revision/hash를 임의 고정하지 않았다. API 요청과 비용은 없다.
후속 티켓에서 실제 게임 backend와 자료형을 연결하고 clock/정보 경계를 검증한다. Java 호환성과 인증 의존성의 audit 경고를 실제 연결 전에 해결/평가한다. nvcc 부재를 GPU 계산 불능으로 해석하지 않는다.
