# #14 T13 — 보상·시간 할인 PPO 구현, 독립 리뷰와 최종 기록 진행

사용자 implement 요청으로 현재 main `b0d239a`에서 구현한다. 새 브랜치/push/PR/merge/이슈 종료는 요청하지 않았다. 결정은 DECISIONS 2026-11-10 #14, 검증은 PROGRESS 같은 절이다.
- local/full RewardLedger, 저장 후보/특징/old logprob·GAE·PPO, 공통 실행기의 학습 연결, 공개 smoke-ppo를 구현했다. 현재 새 learning14검사·mypy34파일 통과, 첫 전체248통과 후 다이아 드롭 좌표 수정/실제 로그 재생을 완료했다. 최종 회귀·두 축 리뷰·보고서·커밋은 진행 중이다.
- 실제 공개 NanoJev+mock 게임2결정/PPO1회 통과: 보상0.96, ratio1, Choice/critic 변화·본체불변. #44 실제 로그5개 offline 재생을 별도로 했다. 실제 게임 PPO/본 학습/유료 API는 실행하지 않았다.
- sparse 사건은 RPC에 개별 시각이 없어 반환 경계 마지막 틱 보상이다. 자연 다이아 최종 성공은 기존 관리자 검증을 유지한다. bridge/runtime/관측은 불변이다.
- 다음 파일럿 #15와 커리큘럼 #18의 학습 기반이며 실제 연결/처리량/복구/lock을 완료했다고 표시하지 않는다.

# #44 관측 반경32·공통 256칸 요약 — 구현·실제 검증 완료, 게시 대기 (이전 기록)

브랜치 `feat/issue-44-observation`(로컬 커밋, push 안 함). 결정·사전 등록은 DECISIONS 최신 #44 절, 결과는 PROGRESS 같은 제목 절, 원시 `artifacts/issue-44/real-1/`.
- 결정 관측 반경32·매크로 틱 정지 검사 반경8, 정책 지도는 비공기 전부+공기 Chebyshev 18, explore는 `discovered_open`, 계획기/NanoJev 공통 `public_state` 256칸 종류별 균등 요약.
- 실제: 63/63 새 인증(`bc7a012d…`), 정보 감사, T04–T07 회귀, 자연 G4 다이아 성공, G4 시작 다이아 비노출, 실제 Qwen/NanoJev 토큰·지연·GPU 측정.
- 다음: push·PR·병합·#44 종료는 사용자 결정. lock 고정은 #20.

# #10 게시·병합·종료 승인 / 관측 확대는 #44 후속

2026-11-09 사용자가 현재 #10의 push·PR 병합·이슈 종료를 요청했다. 구현 e887f4a를 보존해 feat/issue-10-planner에서 사용자 결정 기록과 함께 게시한다. 최종 실제 Git/원격/이슈 상태는 artifacts/issue-10/publication.json과 최신 PDF를 따른다. 이전 아래 미푸시/Open 표기는 당시 이력이다.
- GitHub 작업은 사용자가 요청한 gh CLI만 사용한다. 관측 확대 [#44](https://github.com/sion0507/Minecraft_RL/issues/44)는 CLI로 생성했다. 반경32·모델 정보 최소256개 수준과 정보 보존/처리량·실제63조건/정보 감사/회귀·G4 시작 노출 변화는 **#44 구현 시** 확인한다. 지금은 새 이슈에 기록만 하며 구현/게임 검사를 시작하지 않는다. 현재8/64 규칙은 그대로다.
- **Astra 실제 연결·응답·설정·사용량/과금·지연 검증은 추후 비교 단계로 이연**한다. 호출0/실제 미검증이며 #10 종료를 막지 않는다. 단순 접근 확인을 위한 유료 호출은 지금 하지 않는다. 사용자 예상은 검증 성공이 아니다. 실제 비교 직전 키/계정·별도 Astra 금액/호출 상한 승인과 metadata/실제 청구 확인은 유지한다. F핵심/연구량/분모/예산은 바꾸지 않는다.
- #1/#10/#17/#20·PLAN/PRD/DECISIONS에 동일 결정을 남긴다. 개발 pytest/mypy·diff만 게시 전 수행하고 실제 모델/게임은 보고서 상태 갱신 때문에 재실행하지 않는다. PDF2개는 reports에서 최신 교체하고 Git에서 제외한다.

# #10 T09 — 공통 계획기 구현·실제 Qwen/G1 검증, Astra 승인 대기 (이전 기록)

사용자 `$implement 다음 이슈10` 요청으로 main의 작업시작 HEAD `7a7f8c8`부터 구현했다. 선행 #9 Closed/completed, #10/#1 본문·댓글과 관련 PLAN을 확인했다. 현재 브랜치 로컬 커밋 범위이며 push/merge/#10종료는 요청되지 않아 실행하지 않는다. 최종 커밋은 git log/evidence를 따른다.
- 공통 프롬프트·제한 입력, 고정 Qwen NF4 4비트CUDA와 Astra HTTPS adapter, 공개 smoke-planner를 기존 목표 검증/한 번 재생성/복구·출처별 실행에 연결했다. revision/hash/설정은 소스manifest와로그에고정했다. DECISIONS/PROGRESS 최신 #10절을 따른다.
- 실제 Qwen+mock 게임exit0. 실제 Qwen+자연G1도exit0:5결정216틱·원목1직접획득·pause_verified=true·초기오류0/1·재생성0/0·복구0/1. G1기준reset=observe·0틱·빈인벤토리·체력20과서버종료확인. bridge/runtime/fingerprint입력변경없음/63조건재실행없음. 원시artifacts/issue-10.
- Standards2/Spec3 지적(중복 포함 결함3건)을 3failed→17passed로 수정: 비용 위반 후 영속 차단/비용 보존, HTTP 요청 오류와 접근 불가 구분, CUDA 오류 call/summary 보존. 기본 pilot 명령의 local_7b 연결도 실패 재현 후 수정했다(Planner18개 통과). 최종 pytest229·mypy src/tests31파일 통과. 수정 뒤 독립 재리뷰는 하지 않았다.
- Astra는공개후보만확인. 실제계정/버전/지원옵션/과금/별도금액·호출상한은승인대기이며유료호출0·키읽기0. F핵심비교를유지한다. Jev#12/6상태#17/예산lock#20후속. 학습/전체C4·G4/7B+NanoJev동시VRAM은미실행.
- 로컬PDF2개: reports/issue-010-T09-{report,code-guide}.pdf. 중간파일은/tmp/Git제외·보고서때문에게임재실행금지. 코드기준/검수근거는evidence와PROGRESS에기록한다.
- 사용자가 한국어 안내를 재요청했으므로 설명/승인 요청을 모두 한국어로 한다.

# #11 T10 — 실제 공개 NanoJev 검증 완료, 사용자 승인으로 게시·병합·종료 진행

전용 worktree `Minecraft_learning-issue11`, 브랜치 `feat/issue-11-nanojev`, 시작 HEAD `e839a8e`. 사용자 요청으로 #11/#5/#1 본문·댓글과 관련 PLAN·현재 코드를 확인했다. #5는 Closed이며, main/다른 작업공간은 수정하지 않았다.
- 구현: 공통 제한 입력, 공개 Choice 보존·frozen/no_grad backbone·dropout 0, 독립 local/full critic, seed sampling/argmax, head 저장/복원, 공개 `smoke-model`. 상세 결정은 DECISIONS 2026-11-09 #11 절.
- 실제 모델: tag revision `047b927b30882a1138fc504821b82ac145a4b81a`, 초기 weight sha256 `f68c47d6…ffe1b`. FP32/BF16 forward/tokenization/EOS pooling/logits 오차 0, Choice/두 critic gradient·변경, backbone hash 불변, 초기 head 복원을 확인했다. 실제 CUDA RTX5070Ti에서 실행했다.
- 게임은 mock이다. sampling/argmax smoke exit0; 기본 pilot 단일 후보는 확률1·actor 제외지만 복수 후보 진단 부재로 의도한 exit1이다. 전체 pytest211, 모델 검사8, mypy src/tests28파일 통과. 원시 `artifacts/issue-11/`.
- 7B/Jev/Astra·유료 API·실제 Minecraft 연결·PPO/본 학습·평가·7B 동시 VRAM/처리량은 미검증. 평가 A/B 연결은 현재 mock stand-in으로 남으며 후속 실험 연결과 구분한다.
- 사용자 후속 지시로 commit/push/PR/원격 main 병합/#11 종료를 진행한다. 기존 main checkout·다른 세션 파일은 수정하지 않는다. 그 전의 미수행/Open 상태는 아래 검증 이력이다. 최종 원격 상태는 #11 완료 기록/PDF를 따른다.
- 로컬 한국어 PDF 두 개는 `reports/issue-011-T10-report.pdf`, `reports/issue-011-T10-code-guide.pdf`; Git 제외. 상세 검증/검수 결과는 PROGRESS 최신 절.

# #13 T12 병합·종료, 다음 작업 대기

평가 슬롯(`evaluate`)을 main에 병합하고 #9·#13을 닫았다(사용자 지시). 결정은 DECISIONS 2026-11-09 #13 두 절, 결과는 PROGRESS 같은 날 #13 절.
- mock 검증만 했다(pytest 203, mypy src tests). 실제 S C4 1회는 T22.
- 다음: Codex 세션의 pathfinder 이동 비교가 확정될 때까지 대기. 그 뒤 #10 T09(7B 계획기)와 #11·#12(후보 직렬화)를 정한다.

# #9 T08 — 목표 처리·재계획·규칙 복구·S 선택기 구현과 실제 회귀 완료

브랜치 `issue-9-t08`(로컬, push 안 함). 결정은 DECISIONS 2026-11-09 #9 절, 결과는 PROGRESS 같은 날 두 절이다.
- 사용자 결정: 복구 목표 escape/explore, 즉시 전제조건, S 규칙 순서(최근 실패 → 위험 → 관련성 → 작업량 → 저장 순서).
- mock: pytest 188, mypy. 실제(`1f081e3`, `artifacts/issue-9/real-1/`): 정보 감사·자연 G4(다이아 성공)·G2(철 0, 기록만)·G3·T05·T04 회귀 통과, 결함 없음. 선택이 바뀐 결정 없음.
- 사용자 지시로 PR 병합, #9는 Open 유지(남은 일: #13 S 슬롯 연결). 계획기·S의 실제 게임 동작은 미검증.

# #38 T07C — 후보 상한 16개 병합·종료, 실제 검증은 T08 뒤

후보 상한 16개·자리 걷기 6·tunnel 5·계단 4·기타 1(빈 자리는 생성 순서)을 main에 병합하고 #38을 닫는다(사용자 지시). 결정은 DECISIONS 2026-11-09 #38 두 절, 측정은 PROGRESS 같은 날 절에 있다.
- 실제 정보 감사·T04–T07 자연 회귀는 T08(#9) 구현 뒤에 한다. 범위를 DECISIONS에 먼저 등록한다. bridge가 같으면 4차 63조건 인증서를 쓴다.
- 상황별 후보 보장은 상황별 기록이 더 쌓이면 다시 정한다(사용자 결정).
- 다음 작업은 T08(#9)이다.

# #36 — 연구용 고정 월드 교체 준비, 사용자 입력 대기

main `5a1a316` 위에서 문서만 고쳤다(커밋 안 함). 결정은 DECISIONS 2026-11-08 "고정 월드 교체", 계획·입력 양식은 [#36](https://github.com/sion0507/Minecraft_RL/issues/36)에 있다.
- 사용자가 버전·시드·시작 좌표·동굴 입구 좌표를 줄 때까지 코드·설정·월드·snapshot을 바꾸지 않는다. 시드를 직접 찾지 않는다.
- 기존 시드 `20261102` 환경은 백업만 한다. 이전 실행의 추가 분석·보고서·재검증을 시작하지 않는다.
- 입력이 1.16.5가 아니면 업그레이드하지 않고 호환성 영향을 먼저 보고한다.
- 아래 #8 기록은 이전 환경 이력이다. #8의 자연 G2·G4 인수는 새 월드에서 판정한다.
- 자연 G2/G4는 성공 필수가 아닌 가능성 진단이다. 실행기 결함이 없고 사용자가 코드가 만든 매크로 후보만 골라 성공할 수 있으면 통과다(사람 선택 진단, DECISIONS 최상단). 대화형 선택 모드는 아직 구현하지 않았다.

# T07 #8 — 결함 수정·재인증 후 자연 G2 2차도 철3 미달, Open

현재 기준은 `issue-8-t07`의 `d86ce4b`다(로컬, push 안 함). 1차 결함 두 개를 고쳤다. 낙하 블록이 채운 자기 칸은 stair/tunnel이 먼저 파낸다. 바뀌지 않는 1틱 스텝이 20회 이어지면 `repeated_stall`로 끝낸다.
- 새 fingerprint는 `d482a51c…c598`이고 63/63이다. 정보 감사·tunnel 6장면(`tunnel_sand` 포함)·fixture·T06 회귀가 통과했다. T05/T04는 1회째 실패, 재실행 통과다(PROGRESS 참조). 원시 자료는 artifacts/issue-8/attempt2/에 있다.
- 자연 G2 2차는 `repeated_stall`(93결정·1,073틱), 철 0이다. 모래 수정은 실제로 작동했다. 그 뒤 tunnel이 물을 노출해 침수되었고 후보 0개 대기로 멈췄다. 침수 복구는 T08 책임이다.
- 다음 수정·시도, G4 snapshot, push·PR은 사용자 결정이다.

# T07 #8 — 구현·인증 실행 완료, 자연 G2 철3 미달로 Open

현재 기준은 `issue-8-t07`의 `ee76c2c`(로컬 commit, push 안 함)다. 추가한 것은 tunnel 매크로, 다이아 채굴, 드롭 병합 귀속, 관리자 판정 로그, G4 상한, 자연 G2 사전 등록이다.
- 새 fingerprint는 `ab713f1a…0495`이고 63/63으로 인증했다. 정보 감사, tunnel 장면 5개, 다이아/철 구성 fixture가 통과했다. 원시 자료는 artifacts/issue-8/final/에 있다.
- 자연 G4 smoke는 `diamond_success=true`(2결정·49틱)다. 다만 시작 방 벽에 자연 다이아가 처음부터 보여서 탐색 증거가 아니다. snapshot 유지 여부는 사용자 결정이다.
- 자연 G2(사전 등록 1회)는 미달이다(`wall_time_limit`, 철 0). 원인은 tunnel 진입 뒤 떨어진 모래가 봇 발 칸을 채워 생긴 즉시 중단 무한 반복이다. 코드 결함이며 서버 오류가 아니라 재시도하지 않았다.
- 다음 단계, 즉 결함 수정과 새 사전 등록 시도는 사용자 승인이 필요하다. 수정이 bridge를 바꾸면 63조건 재인증과 회귀를 다시 해야 한다.

# T06 #7 — 독립 리뷰 반영 후 재인증 완료, main 미병합

현재 기준은 `issue-7-t06`의 `882d5e8`이다. 리뷰 반영 내용은 자갈 재판정 틱 상한, T05 `required < 1` 복원, 숨은 철/용암 감사 쌍, 드롭 병합 stderr 진단이다.
이 코드로 다음을 새로 통과했다: 63/63, 정보 감사 29, 12장면, 자연 G3, G2 4방향, T04/T05, pytest 101/mypy.
- fingerprint `c6760e81b4605129b69fc793730b6015b852a422c3ff5048357044f314c81db1`. 이전 `ab5f045f…`(`c905a12`)는 이력이다.
- 자연 G3와 G2의 결정별 결과는 이전과 같다.
- 자연 G2 철3은 미달이며 #8 책임이다.
- `acquired` 과소 집계는 드롭 병합으로 확인했다. 내용은 PROGRESS 2026-11-07 첫 절에 있다.
- 원시 자료는 artifacts/issue-7/review-final/에 있다. 사용자 지시로 push·PR·main 병합 후 #7을 종료한다(결과는 #7 종료 댓글). 재리뷰는 사용자 판단으로 생략했다.
- main 설치는 이 코드로 정지 인증을 다시 받아야 한다. 런타임이 같으면 같은 fingerprint가 나올 것으로 예상하지만 실행해 확인하지는 않았다.

# T06 #7 — #32 위 재인증 (`c905a12`, 위 절로 대체)

`c905a12`에서 63/63·정보 감사28·12장면·자연 G3·G2 4방향·T04/T05를 통과했다. fingerprint는 `ab5f045f…851f`이고 원시 자료는 artifacts/issue-7/post32-final/에 있다.

# T05A #32 완료 — 틱 위상 수정·전체 재검증

최종 코드 f915adc(도구 a2c0b9f). 실제 b0.050004초/틱·a1.195·75ms 초과0, 제작 로그 b0.0500.
새 63/63/drift0·즉시동기화3장면·T05 전체·T04 정보감사와 매크로7항목·pytest/mypy 통과.
자연 G2는 기존 기준선과 같은 64결정1778틱 예상 실패이며 철3 통합 인수는 #8에 남는다.
fingerprint `ad28e8582b70af35dcd4b3edd51fa5f10785ae3990ad2627fb5f93c25fef8b20`, mod `9242817e0d3375d8e971af43acb55e47fc34fac3a5330777460c3fc694282f6b`.
main 머지 후 mod를 다시 빌드해야 한다. T06의 재인증은 위 절.
원시 artifacts/issue-32/tick-wait/final-2/, 상세 PROGRESS 2026-11-07 첫 절.

## 이전 완료 기록(82e5fe5, 위 절로 대체)


최종 실행 코드82e5fe5. 실제b0.059591389초/틱·새63/63/drift0·즉시동기화3장면·
T05정보감사26/제작56결정1817틱/경계/취소/reset·pytest80/mypy22를 통과했다.
사용자가 T05 전체 통과로 이전 티켓을 충분히 검증한 것으로 판단하고 추가 검사
없이 완료·커밋·푸시하도록 명시 승인했다. 이에 추가 테스트를 중단했다.
T04 최종감사 CLI SIGINT(exit−2)/검사기exit1/reset통과, 후속매크로/자연G2미실행을
실제대로 기록한다. 자연G2 성공 주장은 없고 최종 통합 인수는#8에 남는다.

같은 원본 Git 저장소의 issue-32-t05a-resume 브랜치다. main4694d54/T06수정없음,
추가폴더이동없음. 사용자 승인으로 기록커밋·전용브랜치푸시를 수행한다.
기록커밋559f38f를 origin에 푸시하고 원격해시 일치를 확인했다.
#32는2026-11-07T05:25:56Z CLOSED, 완료댓글6702791874.
T06 통합 후 mod재빌드·새fingerprint63조건/감사/관련회귀는 별도로 필요하다.
새 원시 artifacts/issue-32/final-headroom/, 상세수치/미실행/승인 PROGRESS참조.
보고서/PDF 때문에 게임을 재실행하지 않는다. 아래는 이전 진행 이력이다.

## 이전 실행 상태(종료 이력)

- final/ 시도는 T04 정보감사 iron의 획득 부재로 exit1/reset통과로 종료됐다.
  높이3 기둥이 머리 공간을 막아 공개 수집 경로가 거부된 진단 fixture 문제다.
  iron만 높이1로 수정, strict 감사/정책/자연 snapshot은 그대로다.
  실제 iron-headroom/ 두 변형 각58틱·채굴1/획득1·signature일치/reset통과.
  새 pytest80통과26.97초/mypy22, Standards/Spec 추가지적0.
  아래 final/의63조건과 속도는 이전코드 근거이며 새코드로 승계하지 않는다.
  다음 실행은 /tmp/t05a-final-run.py artifacts/issue-32/final-headroom 이다.
  final-headroom/ 진행 중 중복 실행 금지. 최종 비교/PDF/문서커밋은 남았다.

- 최종 실행 코드 edc92cf(선행4f22bdf/787712f/3284ba0). 클라이언트 물리를 먼저
  완료하고 같은 TCP연결 nonce를 서버 실행기에서 확인한 뒤 실제 틱을 진행한다.
  mod27fe07bcbbbc100dbcbc4114d08426a66a50007ed1e243d5b722c81bebaa71a6.
- 늦은물리/입력nonce 모의RED→GREEN과 실제지연(0/5/20/45/75ms)보행2경로47틱/
  6.379블록·위치검사/reset통과. delayed-movement/은 인증전exit1/unverified다.
- 새 전체pytest79통과24.46초, mypy22, Node/Java빌드 통과. 두축재검토 잔여0.
  recovery/pytest-causal.txt,mypy-causal.txt. 코드 그대로면 반복하지 않는다.
- 이전 /tmp/t05a-final-run.py의 기록은 final-causal.stdout/stderr와
  artifacts/issue-32/final/run-status.json으로 실제 진행을 확인하고 중복 실행 금지.
  종료 session13460. 순서 final/final-speed→final-sync→final-t05(clock information
  production boundaries)→final-t04(information macros)→g2. 양성실패시중단,
  자연G2기존exit1/assert는보존하고서버오류/정지실패는허용하지않는다.
- 이전 artifacts/issue-32/{final-speed,final-sync,final-t05}는4f22bdf실행이며
  늦은물리수정때clock을SIGINT(-2)중단/reset통과. 최신인증으로사용하지않는다.
- 새최종원시비교/개발검사와구분한한국어PDF2종/전체페이지검수/기록커밋남음.
  PDF생성때문에게임재실행금지. 코드변경이없으면새시계/전체검사중복금지.

## 복구 경위와 아래 과거 기록

사용자의 재개 지시로 implement를 계속 적용한다. main/T06은 읽기 전용이며
#7을 수정/완료하지 않는다. 이전 /tmp worktree와 원시는 현재 없어서 재사용하지 않는다.
보존된787712f에서 새 branch issue-32-t05a-resume, 영속 worktree
/home/sion/.codex/worktrees/327b/Minecraft_learning을 생성했다. 이후 명령은 이 경로에서만 실행한다.

- main 기준4694d54, 보존 구현3284ba0→787712f. 마지막 미커밋 시설I/O 수정·회귀는
  대화 패치에서 복원했다. 현재 HEAD/미커밋 상태는 git log/status로 확인한다.
  push/merge/PR/이슈 종료는 요청되지 않았고 수행하지 않는다.
- 서버/snapshot/Node 환경을 별도 복사, 전용 포트25566과 uv 환경 설치 완료.
  새 mod hash c0ff66d5a455075e98ae3fea92ea94d520eaa9909c577b36878626486bbee3fe.
- 새 변경 전960틱 실제계측 a1.193834879,b.199745351. 유효 최종T05/T04 로그10개
  회귀 a1.225208660,b.199272347. artifacts/issue-32/recovery/{before-fixed,final-log-fit}.
- 복원 개별pytest11통과7.98초/mypy22. 새 전체pytest79통과24.41초,
  전체mypy결과는 recovery/mypy.txt 확인. 이전 소실 인증/원시를 승계하지 않는다.
- 최종코드 커밋 고정 뒤 final-speed→final-sync→final-t05(clock information
  production boundaries)→final-t04(information macros)→별도g2(원래assert/exit1유지).
  실제 서버는 순차 실행하고 원시/results/reset/새fingerprint를 직접 검토한다.
- 새 속도·시계·정보/T04/T05/G2·독립Standards/Spec·PDF2종·최종문서커밋 남음.
  PDF 중간파일은/tmp, 보고서는 reports/에 최신PDF2개만/Git제외.
- 이후 T06에 최종 #32 코드를 통합하고 해당 최종 fingerprint로63조건·감사·회귀를
  새로 수행해야 한다. 자연G2철3의 최종 통합 책임은#8이며 기존실패를 성공으로 쓰지 않는다.

## 아래는 이전 T05 완료 기록

- 2026-11-06 최신 사용자 승인: T05 범위를 제작·제련·노출 철 직접 채굴/획득 연결과 검증으로 정리한다. 자연 고정 G2 철3 실패를 성공으로 체크하지 않고 미달·후속 이관으로 보존한다. T06은 기존 G3와 별도 G2 접근 가능성, T07은 같은 snapshot/hash·시작점·돌 곡괭이1·10분/12000틱에서 발견→적절한 도구 파괴→해당 드롭 직접 획득3의 최종 통합 책임이다. 미달/장애면 #8은 미완료다. 현행 기준 PLAN §5.2.1·DECISIONS 최상단. 아래 과거 T05/T04의 금지·미완료·Git 상태는 당시 이력이다.
- 실행 순서는 #5→#6→#32→#7→#8, #7의 기존 #5 선행도 유지. 개정 T05 기준 충족 후 커밋/푸시·#6 종료·#32 ready 확인까지 이번 승인 범위다. **T05A 구현·계측은 아직 시작하지 말 것.** 사용자에게 착수 가능한 상태를 명시적으로 보고한다. PR/merge는 추가하지 않는다.
- main/origin 기준 ff75f365026c9ec8600d9d3a4a6a1a67ae2dd1b3. 미커밋 단차 이동7소스를 패치·파일 사본/hash로 artifacts/issue-6/excluded-natural-steps-2026-11-06/에 안전 보존 후 ff75f36과 바이트 동일하게 복원했다. 계획은 제외 이력으로 유지한다. 패치 SHA256 538437e2682009e6507b9acdf7693561ca52384ec1208b767376f9597794dc0b. 현재 변경은 인수 책임/기록 문서만이다.
- 제외 코드 실제 단차 fixture 상행24/하행17틱은 미인증·단차 정보 감사 미완료이며 scripted 슬라임 거리 상한 결함도 남았다. 자연G2 사전64결정/150틱/119.12초·철0·observed_hazard63·decision_limit·pause_verified=false·reset 통과. natural-step-preflight/ 및 g2-natural-step-preflight/ 원시 보존. 완료 코드/유효 G2 기준선/자연 성공과 혼합하지 않는다.
- 유효 실제 근거: final-3 시계63/63·drift0·정보26장면710.42초·배치 자원/빈 인벤토리 제작51결정/1702틱/413.17초. 직접 원목4/조약돌11/철광석3·직접 제련 철괴3·직접 제작 철 곡괭이1. 자연C4/G2 성공 아님. control-final 도구/연료 부족각1틱·위험1틱·취소40+새제작3=43틱·actor0/trace0·C4reset.
- 유효 자연G2 실패 기준선 g2-route-fix/:64결정/1778틱/446.39초·제공 돌 곡괭이1·방문155·철 관측/획득0·decision_limit·서버오류 없음·정지인증true. 같은 높이 관측 연결 영역155칸 탐색이며 전체 월드/12000틱 전체 불가능성을 입증하지 않는다. 기존 실제32공개관측 후보 순수 재생32/32동일. 새 실제 감사로 쓰지 않는다.
- 복원 후 fresh 개발 검사78pytest(18.39초)·mypy23·Node 문법 통과. 첫 mypy는 보존 Python 복사본의 중복 모듈로 실패해 사본 확장자를 .saved로 바꾼 뒤 통과했다. /tmp/t05-recompute.py 원시 재계산 통과, g2-route-fix manifest 소스 전체일치. 최종 fingerprint가 저장 인증6de2893387dc7971a1213cf939e056c07520edef6f6edfede0982b423e832804와 읽기 전용 재계산으로 일치했다. bridge/fingerprint 동일이면 새 게임 검사를 하지 않는다. 향후 입력 변경 시 각 티켓63조건 재인증·정보 감사·관련 T04/T05 회귀 필요.
- 최종 상태: 인수문서f16969647cd5c2f9cb993afe20d03272de190adb 커밋/푸시·실제원격해시 확인. #6 Closed(2026-11-06T11:38:26Z), 완료댓글 https://github.com/sion0507/Minecraft_RL/issues/6#issuecomment-6683924522 . #32 Open/ready-for-agent, 실제 유일한 선행#6 Closed확인. #7/#8 Open/미구현. 독립Spec0/Standards hard0·명확성1건해소,5개본문/댓글원문과기존의존성교차확인. 보고서2쪽/가이드3쪽의한글추출·모든글꼴포함·최종5페이지가독성확인. 상태기록문서도커밋/푸시하며 최신main은git log -1/원격ref로확인한다. **다음이슈T05A 착수가능이며이번에는구현하지않았다.**
- reports/는 최신PDF만·Git제외. 생성기 /tmp/t05-reports.py, 입력 /tmp/t05-evidence.json. 코드 기준ff75f36과 새 문서 커밋/이슈 상태를 구분해 갱신한다. PDF 때문에 게임 재실행 금지. 모델/API/학습/평가·연구 예산 증액·T05A 구현은 미실행.

## 아래는 이전 T04 완료 기록

2026-11-05 사용자의 `continue`로 아래 중지 요청이 해제됐다. 남은 실제 감사·매크로·취소/재선택·기준 reset을 완료했고 코드 변경은 없다. 이 보완을 현재 main의 로컬 커밋으로 마무리한다. push/PR/merge/이슈종료/댓글은 요청되지 않았으며 실행하지 않는다. 최신 커밋 ID는 `git log -1`로 확인한다. #5는 조회 시 Open이다. 후속 #6/T05는 자동 착수하지 않는다.

- 완료 시계: `artifacts/issue-5-review-2026-11-05/final-2/`의63/63. 전체 fingerprint/소스hash 동일 확인 후 재실행하지 않았다.
- 재개 최종: `artifacts/issue-5-review-2026-11-05/resume-1/`. 정보감사18장면494.08초·exit0, 실제 맨손81틱/장착103틱/파손51틱/드롭wait40틱 수집exit0. 위험72틱·0후보240틱은 예상목표미완료exit1.
- 실제 제어된 취소40틱 보존·trace단절·재선택 후121틱 목표완료. 전체 realtime 인증과 구분. 모든 최종 결과 paused/인증true. 기준G1 reset/observe 일치·0틱·빈인벤토리·체력20·검사/서버종료 확인.
- 원시 재계산: resume-1/evidence-recomputed.json. 개발68pytest/mypy20파일·독립Standards/Spec 각0건 이후 소스 그대로라 반복하지 않았다.
- reports의#5 보고서2쪽·가이드3쪽을 최신 교체한다. 로컬 전용/Git제외, 한글추출·전체글꼴포함·전체페이지 가독성 검수. 생성기는 이번 세션 `/tmp/minecraft-issue-5-review-report.py`, 원시재계산기 `/tmp/t04-review-evidence.py`. /tmp 영속성은 가정하지 않는다. 보고서 때문에 게임 재실행 금지.
- 최종 수치/미실행/실패 해석은 PROGRESS 최상단, 항목별 검토는 docs/reviews/issue-5-review-fixes-2026-11-05.md. 자연G1 사전실패·중단감사·미인증사전결과는 최종성공과 분리했다. 실제사망은mock만, 모델/API/학습/전체realtime/최종평가는 미실행이다.

## 이전 중지 시점 인계 (이하 과거 기록)

아래의 중지 지시·미완료 목록·미커밋 상태는 재개 전 기록이며 위 완료 상태로 대체한다.

2026-11-05 사용자가 “내일 다시 continue로 진행”하도록 중지를 요청했다. **continue 전에는 추가 구현·검증을 실행하지 않는다.** 정보 감사를 SIGINT로 중단했고 기준 G1 reset/observe 일치·0틱·빈 인벤토리·체력20 복원과 검사/서버 프로세스 종료를 확인했다.

## 목표와 상태

- GitHub sion0507/Minecraft_RL #5/T04. 원 `$implement` 요청 뒤 handoff 지적을 검증했고, 확인된 부분을 모두 보완·재검토하라는 사용자 요청을 수행 중이다.
- 기준/현재 HEAD는 main `9f9aca543703791be538240b841ca32690188dfa`. 이번 보완은 **미커밋·미푸시**. 기존 HEAD도 origin보다 앞선 기존 로컬 커밋이므로 이력 보존. PR/merge/이슈종료/댓글 없음. #5 마지막 조회 Open.
- 시작 작업 트리는 깨끗했고 현재 코드/테스트/README/DECISIONS 및 새 tools·계획·검토 문서는 이번 작업이다. 기존 파일/이력을 보존한다.
- 원 handoff: `/tmp/claude-1000/-home-sion-Documents-projects-RL-projects-Minecraft-learning/6f9e7446-9fec-48f0-a0fe-f0f54984bd34/scratchpad/t04-review-handoff.md`.
- 요구: 기존 실행기 재사용·TDD·최종 전체 검사·독립 Standards/Spec 검토·현재 브랜치 로컬 커밋. push/merge/종료는 요청되지 않았다. 모델/API/PPO/연구 실험/전체 realtime 운용 추가 금지.

## 수정 완료

1. E1: 완료 틱 위험/파손/사망에도 air 갱신을 확인해 mined/confirmed와 정당한 후속 획득을 보존(배포 bridge 회귀 RED→GREEN).
2. S5/C2: stop_rule_id는 정책 메타데이터다. 일반 wait20/100/200 또는 남은20미만 절단만 허용. 내부 recoveryWait만 짧은 취소 허용. 위조7·임의350 거부/마지막7·내부5 허용 회귀.
3. 0후보 failed는 저장 후보 집합을 아는 episode에서 생성. 반드시 실제 wait 사건을 먼저 확인(빈 사건 거부 RED→GREEN). actor_exclusion_reason 기록.
4. S2–S4: 공통 근거/반환 병합, MacroEvidence·executeMacro 명명, 죽은 wait 분기 제거. 이동 고유 검증과 Python/JS 신뢰 경계별 검증 유지.
5. 공개 CLI `--diagnostic-fixture wood|wood_tool|wood_break|wood_hazard|wood_drop|empty`: rpc smoke-macros만 허용, 관리자 준비·natural_task=false·준비 틱 출력. wood_drop은 실제 직접 채굴 드롭을 준비 단계에서 이동·Motion0·PickupDelay40 설정. 준비5+채굴61+후속5=71틱을 에피소드와 분리.
6. 정보 감사: 독립 장착·wait20/100/200·dropwait·0후보의 숨은 광석/용암 쌍 추가(총18장면 예정). 실제 wait/equipped 사건 필수.
7. Git 추적할 `tools/verify_t04.py`: 공개 CLI/시계/감사/제어된 실제 stale취소 재현, 명령/hash/stdout/stderr/결과 보존, 성공/실패/일부 검사 모두 finally 기준 reset. 실제20틱 진전+취소20틱=40틱을 공통 episode에 기록하며 전체 realtime 인증과 구분.

## 완료한 검사와 원시

- 전체 pytest **68 passed(16.60초)** `/tmp/t04-final-pytest.txt`, strict mypy **20파일 통과** `/tmp/t04-final-mypy.txt`, Node 문법·diff 검사 통과. 이후 코드 변경 없음(문서/인계 제외).
- 독립 Standards/Spec 재검토 남은 지적 **각0건**. 감사 사건 누락과 실패 시 reset 누락을 수정했다. Standards는 마지막 0후보 wait 증거·준비71틱 합산도 확인. 기존 idle agents `/root/issue5_standards`, `/root/issue5_spec`.
- 잘못된 backend/명령의 진단 옵션 guard2건 exit2: `artifacts/issue-5-review-2026-11-05/diagnostic-guards.json`.
- `.../macros-preflight/`: 실제 맨손1결정81틱/장착2결정52틱/파손3결정52틱 각각1개 획득. 채굴직후 위험61틱에 mined+observed_hazard(전체12결정72틱, 목표미완료 예상). dropwait2×20=40틱에1개 획득. 0후보12×20=240틱 wait+failed. 실제취소40틱 보존·재선택 후 총121틱 목표완료. reset 통과. **새 인증 전이라 unverified/CLI exit1을 유지한 사전 물리 검사다. 인증 후 최종 성공으로 쓰지 않는다.**
- `.../preflight/smoke-macros.jsonl`: 자연 G1 공개 CLI12결정294틱 나무미발견/수집실패. 관리자 진단 성공과 구분. 결과를 보고 자연 경로/시드/선택기를 튜닝하지 않았다.
- **최종 시계 인증 완료** `.../final-2/verify-clock.jsonl`: exit0,63/63 고유 조건·준비63/63·최대 drift0.0. 독립 원시 재계산 `clock-recomputed.json`. manifest 소스 hash 일치. Java 확장/allow-flight 변경 없음.
- final-2 정보 감사는 **사용자 요청으로 -2(SIGINT), 미완료**. 원시45행·완료step13, information_summary 없음. results.json에 clock완료/audit중단/reset통과. driver AssertionError는 의도한 중단 뒤 종료코드 검사이며 새 결함이 아니다. 최종 macros 단계는 미시작.
- final-1 시계도 준비 틱 집계 수정 때문에 의도적 중단(-2)/복원. 성공으로 세지 않는다.

## continue 후 남은 작업

1. AGENTS/CONTEXT/git status와 프로세스·clock-verification.json을 확인. **bridge/clock/runtime/설정 fingerprint가 같으면 이미 완료한63조건을 재실행하지 않는다.**
2. 새 폴더에서 남은 실제 검사만 실행(로컬 서버 권한 필요):

   `UV_CACHE_DIR=.cache/uv .tools/uv run --locked python tools/verify_t04.py --output artifacts/issue-5-review-2026-11-06/resume-1 information macros`

   날짜/기존 폴더에 맞춰 새 경로 사용. 중단된 감사18장면 전체 완료, 인증 후 공개CLI 수집 exit0/paused, 위험·0후보 예상exit1, 실제 취소·재선택/reset 확인. 사전 unverified 결과를 최종 검사로 대체하지 않는다.
3. PROGRESS/검토 문서/계획 체크박스 갱신. 코드 변경 없으면68검사를 불필요하게 반복하지 않는다. 새 실패/수정이면 필요한 회귀/전체 검사.
4. **현재 reports의 #5 두 PDF는 이전 판본으로 이번 보완 미반영.** `issue-005-T04-report.pdf`와 `issue-005-T04-code-guide.pdf`만 최신 교체. 다른 PDF 보존, reports는 PDF만/Git 제외.
   생성기 초안 `/tmp/minecraft-issue-5-review-report.py` 준비/미실행. 현재 raw=final-2라 전체 완료 전제와 충돌하므로 **시계는 final-2, 감사/macros/results는 재개 폴더**로 읽도록 수정. 실제/mock/미실행·자연 실패·commit/push/merge/이슈 상태·코드 기준 명시. report2쪽/guide3쪽 목표이나 생성 후 페이지수 확인.
   기존 ReportLab 캐시 `/home/sion/.cache/uv/archive-v0/Gu1llcM_VZqnCBvS`, WQY font `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`. SimpleDocTemplate에도 initialFontName='Korean' 필수(미설정 시 Helvetica 미포함). pdftotext 한글, pdffonts 전체emb/sub/Unicode, pdftoppm 렌더 후 모든 페이지 시각검수. 중간 파일은 /tmp. 보고서 때문에 게임 재실행 금지.
5. 정확성/diff 확인 후 현재 main 로컬 커밋. 커밋 후 PDF metadata만 재생성하고 추출/폰트/모든 페이지 검수. push/merge/이슈종료는 하지 않는다. 최종 한국어 결과표·PDF 두 링크·커밋·제한 보고. 무결함 보장 대신 검토 범위 내 남은 지적0건.

계획 `docs/superpowers/plans/2026-11-05-T04-review-fixes.md`, 항목별/축별 검토 `docs/reviews/issue-5-review-fixes-2026-11-05.md`. DECISIONS/README 갱신됨. 과거 `/tmp/minecraft-issue-5-report.py`·`artifacts/issue-5/final-4/` 결과를 새 보완 결과와 혼동하지 않는다.
