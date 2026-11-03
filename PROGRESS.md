# 실행 기록

## 2026-11-03 — 이슈 #4 커밋·푸시·PR 검토 준비

사용자가 이슈 #4의 커밋·푸시·PR 생성과 검토를 요청했다. `ticket-4`와 최신 `origin/main`의 공통 기준은 `624b9c6`이다. 이슈 #4는 Open이며 기존 ticket-4 PR은 없고 최신 #1/#4 본문·댓글을 재조회했다. 실제 코드·보고서·문서만 커밋하며 월드/원시 artifact/캐시를 제외한다. 기존 PDF/HTML의 작성 당시 미커밋 상태는 보존한다.

직전 전체 pytest **37 passed(9.65초)**, strict mypy **15개 파일 통과**, Node 두 파일 구문·diff 공백 검사 통과. 코드/게임 환경을 바꾸지 않았으므로 기존 실제 정지 63/63·이동·정보 감사를 이 단계에서 불필요하게 재실행하지 않는다. PR 검토에서 런타임을 바꾸면 정지 인증과 실제 검증을 다시 확인한다. main 머지·이슈 종료는 이번 요청에 포함하지 않는다.

## 2026-11-03 — 이슈 #4 / T03 제한 관측·이동·정보 감사 완료

사용자 요청으로 다음 티켓을 확인했다. #2/T01과 #3/T02는 Closed이며 #3은 PR #28로 main에 머지됐다. main `624b9c6`에서 `ticket-4`를 생성했다. 샌드박스의 Git ref 쓰기 제한 후 승인된 재실행으로 브랜치를 만들었다. GitHub #1/#4 본문·댓글(댓글 없음), PLAN §§4.1–4.3/5.2/12–14와 기존 실행기를 기준으로 구현했다. 현재 변경은 미커밋·미푸시이며 PR 생성·main 머지·이슈 #4 종료는 수행하지 않았다.

### 구현

- `bridge/terrain.js`는 눈 위치에서 반경 8블록 셀 중심으로 광선을 보내 처음 충돌 표면/위험에서 중단한다. 통과한 공기·비충돌 식물과 직접 보인 표면·관측 지도·방문/최근 결과만 저장하고 reset마다 비운다. 미로딩 셀을 통행 지도로 넣지 않고 시드·관리자 상태·전체 청크·숨은 블록을 후보/경로/중단에 제공하지 않는다.
- 공개 지도 BFS로 같은 높이의 바닥·발/머리 공간을 연결해 최대 8개·16블록/400틱의 보행 후보를 만든다. Node도 원본 obs/map과 경로 연속성·공개 전제조건을 검증하며 각 기본 이동 뒤 관측을 갱신한다. 공개 위험·피해·길 변경·정체에서 중단하고 정상 종료는 입력 해제 후 공개 지면·수평 정지를 확인한다. 보행 중 클라이언트 물리도 서버 실제 틱 수만큼만 실행한다.
- 기존 공개 episode 흐름에 `smoke-movement`를 추가했다. moved/stopped 사건, source obs·map 버전·경로·중단 근거·틱·거리·경과 시간을 기록하고 안정된 경로 완료가 없으면 exit 1이다. RPC 시작 오류를 실제 mock 시계로 표시하지 않고 unverified로 구분한다.
- `audit-information`은 관리자 전용으로 진단용 벽 뒤 광석/용암 장면을 준비하고 일반 정책 observe/step으로 비교한다. run ID·벽시계만 제외해 관측·후보·경로·실행/중단 근거의 일치를 요구하고, 벽을 연 양성 대조에서 노출도 확인한다. 관리자 준비 데이터를 정책 관측에 섞지 않는다. 실제 정지 인증·최대 틱·거리·사건 출처·관측/지도/경로 근거도 검사한다. 자연 snapshot은 보존한다.

### 실제 Minecraft 검증 (2026-11-03)

- 공개 `verify-clock`: **exit 0, 63/63 통과**, 위치 허용 오차 0.001블록. 평지·제련·드롭·용암·낙하·침수·화염의 0/5/10초 각 3회다. 변경된 backend/terrain을 포함한 새 fingerprint로 인증했고 과거 인증을 재사용하지 않았다. 원시 근거 `artifacts/issue-4/verify-clock.jsonl`.
- 공개 `audit-information`: **exit 0, information_verified=true**, 46.71초. 숨은 두 장면은 노출 전 각각 공개 셀 1,161개·후보 8개이고 입력 SHA-256 `7c35ab78e49d07ccd3a42abb987471f493db1acb65147cddb88f554e4e4dc38d`가 같다. 두 실행 모두 **18틱·2.1548446042413616블록·path_completed·안정 경계**, 지도 버전 6이며 관측·경로·사건·중단 근거가 정확히 같았다(벽시계 제외). 벽을 연 광석/용암 장면은 각각 공개 셀 1,175개에서 해당 대상을 직접 관측했다. `hidden_hazard_peek=false`; 실제 관리자 진단 장면이며 자연 광석 성공이 아니다. 원시 근거 `artifacts/issue-4/audit-information.jsonl`.
- 최종 공개 `smoke-movement`: **exit 0, movement_completed=true**, 2결정·47 활성 틱·총 6.37928897648239블록·17.56초. 두 step 모두 path_completed·pause_verified=true·stable_boundary=true. 각각 15/32틱, 지도 버전 12/42다. actor 전이 0·보상 0·다이아 성공 false이며 유효 decision_limit 절단이다. 원시 근거 `artifacts/issue-4/smoke-movement.jsonl`.
- 진단 뒤 C4 기준 snapshot으로 다시 reset했다. 활성 틱 0·빈 인벤토리·체력 20과 reset/observe 일치를 확인하고 서버를 정상 종료했다. 진단 장면을 현재 월드로 남기지 않았다. 검사 코드/근거: `artifacts/issue-4/final-check.py`, `restore.json`, `final-checks.json`.

### 실패·수정·독립 검토

최초 sandbox 실행은 서버 소유권 확보 실패였고 승인된 실제 장비 실행으로 재검증했다. 첫 실제 이동은 풀을 불투과 셀로 분류해 발밑 지면이 누락되어 중단됐다. 공개 관측으로 원인을 확인하고 비충돌 식물은 통과하도록 고쳤다. 다음 시도는 접지 중의 정상 `vy=-0.0784000015258789`를 이동으로 오인해 안정화가 끝나지 않고 RPC timeout이 발생했다. 실제 T02 기록·설치 물리 코드를 대조하고 접지·수평 정지 판정을 RED→GREEN으로 고쳤다. timeout 시도는 완료된 step이 없어 부분 활성 틱을 확정값으로 주장하지 않으며 actor 경험은 없다. 실패/중간 결과 `movement-attempt-1.jsonl`, `movement-attempt-2.jsonl`, `movement-before-final-check.jsonl`을 보존했다.

별도 읽기 전용 코드 검토에서 3축 광선 동률의 뒤 모서리 조회 결함을 재현했다. 첫 차단에서 즉시 반복을 중단해 숨은 셀 조회 7회→0회로 고쳤다. smoke가 대기/불안정만으로 성공하는 문제와 죽은 플레이어의 physicsTick 대기도 보완했다. 수정본 독립 재검토는 남은 중대한 문제 없음이다. 후속 자가 검토로 감사의 동일한 401틱 응답 허용을 RED→GREEN으로 수정했다. 검토 상세 `docs/reviews/issue-4.md`.

전체 pytest **37 passed(9.66초)**, strict mypy **14개 파일 통과**, Node 두 파일 구문·diff 공백 검사 통과. 모의/transport 검사는 실제 물리 근거와 구분한다. 검토 PDF·HTML을 `reports/issue-004-T03-2026-11-03.{pdf,html}`에 저장했다. PDF는 A4 2쪽이며 한글/핵심 수치 추출·모든 글꼴 포함/subset/Unicode mapping을 확인했다. 두 페이지를 PNG로 렌더링해 직접 읽었고 잘림·표 분리·깨진 글자·문장만 남은 페이지가 없다. WeasyPrint의 fontTools fallback 경고는 있었으나 출력/가독성 검사는 통과했다. 기존 보고서는 보존했다.

### 제한과 다음 작업

현재 보행은 같은 높이의 확인된 온전한 지면만 다루며 유리/부분 충돌 표면은 보수적으로 시야를 가린다. 일반 높이 차·점프·채굴·제작·계단·터널, 모델/API·PPO·전체 C4/G4 평가·온라인 인증은 미실행이다. 후속 제작/하강/터널 감사는 담당 티켓과 최종 lock 전에 추가한다. 새로운 월드 일반화·자연 다이아 성공·행동 모델 성능을 주장하지 않는다. 새 의존성·모델 다운로드·학습·유료 호출·결제는 없다. 다음은 #5/T04 관측 원목 직접 수집이다.

## 2026-11-03 — PR #28 수정본 검토·실제 재검증 완료, 통합 준비

리뷰 수정 코드 `21a63593992eb0b51630a1110c535ed83f85de51`을 `origin/ticket-3`에 푸시했다. 두 독립 검토자는 수정 diff를 재검토해 Standards 남은 차단 문제 0건, Spec 추가 차단 문제 0건으로 판정했다. Spec의 실제 재검증 조건도 아래 실행으로 충족했다. GitHub 계정의 승인 리뷰로 표시하지 않는다.

수정본 공개 verify-clock은 **exit 0, 63/63**이다. 63개 고유 조합 모두 위험 장면 준비 상태를 만족하고 before/after 측정값이 정확히 같으며 위치 drift 0, 낙하 9건 모두 공중 상태다. 원시 결과 `artifacts/issue-3/verify-clock-pr28.jsonl`, 새 인증 fingerprint `d9aeb6f565cea776a90a4be6912835e2a93c2553520cfb38395af67e231aca50`. 과거 인증을 새 코드의 근거로 재사용하지 않고 실제로 다시 검사했다.

후속 공개 실제 smoke도 **exit 0, 2결정·40틱·10.97초**, 두 step pause_verified=true, actor 0·보상 0·다이아 성공 false, 정상 decision_limit 절단이다. reset 뒤 새 인증 재사용을 확인했고 CLI가 서버를 종료했다. 원시 결과 `artifacts/issue-3/smoke-episode-pr28.jsonl`. pytest 29개·mypy 12개 파일과 Node/공백 검사는 코드 수정 후 통과한 결과이며 문서 작성 중 불필요하게 다시 실행하지 않았다.

후속 PDF는 A4 2쪽으로 출력해 모든 페이지 이미지를 직접 확인했다. 한글·핵심 수치 추출, 전체 글꼴 embedded/subset/Unicode mapping, 잘림·표 분리 없음도 확인했다. 기존 PDF/HTML을 보존하고 `reports/issue-003-T02-2026-11-03-v2.{html,pdf}`에 독립 검토·수정·새 실제 검증·미실행과 작성 당시 Git 상태를 구분해 기록한다. 이 기록 작성 시 PR #28은 Open, main 미머지·이슈 #3 Open이다. 검토 문서/보고서를 같은 PR에 반영한 후 요청대로 merge하고 종료 상태를 확인한다. 최종 통합 상태는 PR/이슈의 GitHub 기록을 따른다. 모델/PPO·유료 API·전체 예산 검증을 수행하거나 완료로 주장하지 않는다.

## 2026-11-03 — PR #28 독립 검토와 정지 인증 보완

사용자 요청으로 `ticket-3`→`main` PR [#28](https://github.com/sion0507/Minecraft_RL/pull/28)을 생성했다. 기준 main `1de47b7`, 최초 검토 head `29c962d`다. 별도 읽기 전용 Standards/Spec 검토를 병렬 수행했다. Spec은 T02 범위에서 추가 차단 지적이 없었다. Standards는 Fabric Loader/Mixin/intermediary/ASM 및 실제 remapped game jar가 fingerprint에서 빠져, 의존성 변경 후 옛 정지 인증을 재사용할 수 있는 P2를 발견했다.

서버의 `.fabric/`, `libraries/`, `mods/` 전체 트리와 bootstrap/game jar를 실제 내용으로 hash하도록 보완했다. 기존 snapshot treeHash를 재사용하고 추가 모드도 hash 변화에 포함한다. 회귀 검사는 누락된 메서드에서 먼저 실패한 뒤 변경·원복·모드 추가의 hash 동작을 통과했다. 기존 drift 검사 fixture가 미준비 상태여서 실패 이유를 구분하지 못하던 부분도 준비된 샘플과 무변경 성공 대조군으로 고쳤다. 이 scripted 검사는 물리 근거가 아니다.

수정 후 전체 pytest **29 passed(9.23초)**, strict mypy **12개 파일 통과**, Node 구문·diff 공백 검사 통과다. 새 fingerprint로 실제 공개 63회 정지 검증을 실행 중이며 `artifacts/issue-3/verify-clock-pr28.jsonl`에 저장한다. 이 시점 실제 재검증·수정본 독립 재검토·main 머지·이슈 종료는 미완료다. 기존 보고서는 보존하고 최종 결과는 별도 후속 PDF/HTML에 기록한다.

## 2026-11-03 — ticket-3 구현 커밋·원격 푸시 완료

구현·설정·검토 문서·PDF 보고서·완료 보고 규칙 28개 파일을 `1312252e200df81e352a34570a8561ef049fb84c` (`feat: implement real Minecraft reset and verified pause (#3)`)로 커밋하고 `git push -u origin ticket-3`가 성공했다. 원격 신규 브랜치 생성과 upstream 설정, 로컬/추적 브랜치의 일치를 확인했다. 게임 jar·월드·raw artifact·캐시·비밀값은 포함하지 않았다.

커밋 직전 pytest 27개·strict mypy 12개 파일·Node 구문·공백 검사와 기존 실제 시계 검증 fingerprint 일치 확인을 통과했다. 실제 게임 63회는 재실행하지 않았다. 기존 PDF의 작성 당시 미커밋 상태를 보존하고 보고서 목록에 후속 코드 커밋/푸시 기록을 연결한다. 이 후속 문서 기록도 별도 커밋으로 같은 브랜치에 푸시한다. main 머지·PR 생성·이슈 종료·브랜치 삭제는 수행하지 않았다.

## 2026-11-03 — ticket-3 커밋·푸시 준비 검사

사용자가 `ticket-3` 변경의 커밋·푸시를 명시적으로 요청했다. main 머지·PR 생성·이슈 종료는 이번 요청에 포함하지 않는다. 원격을 fetch한 결과 기존 origin/ticket-3는 없다. 커밋 직전 전체 pytest **27 passed(8.24초)**, strict mypy **12개 파일 통과**, Node backend/lifecycle 구문 검사와 diff 공백 검사 통과를 확인했다. 현재 시계 엔진·설치 환경 fingerprint가 보존된 실제 63/63 검증 기록과 일치하고, 보고서 PDF 2쪽/3쪽의 한글 추출도 재확인했다. 실제 63회 게임 검사는 재실행하지 않았다.

코드·설정·문서·보고서만 커밋하며 게임 jar·월드·원시 실행 산출물·캐시·비밀값은 제외한다. 기존 PDF의 Git 상태는 작성 당시 기록으로 보존한다. 커밋·푸시 결과는 원격 확인 후 이어서 기록한다.

## 2026-11-03 — 이슈별 검토 PDF와 완료 절차 추가

사용자가 이슈 완료마다 별도 폴더에 검토 PDF를 저장하도록 요청했다. `reports/`를 만들고 #2/T01 회고 보고서 2쪽, #3/T02 구현·검증 보고서 3쪽 및 편집 가능한 HTML 원본·공통 CSS·템플릿·목록/출력 규칙을 저장했다. 작성일은 2026-11-03, 검증 기준일은 2026-11-02로 구분한다. #2의 당시 검사 기록과 main 반영, #3의 현재 미커밋·미푸시·미머지/이슈 종료 미처리 상태를 명시했다.

`AGENTS.md`에 이슈 완료 보고 전 PDF·HTML 저장과 가독성 검사 규칙을 연결했고, root README에 보고서 목록 링크를 추가했다. 기존 완료 보고서를 보존하고 후속본은 날짜/버전으로 구분한다. 사용자 검토 승인을 새로 요구하는 절차나 백그라운드 자동화는 만들지 않았다.

직접 Pango/Cairo를 연결하는 첫 출력 시도는 GI cairo Context 연결 모듈 부재로 실패했다. WeasyPrint 70.0을 Git 제외 `.cache/uv`의 별도 도구 환경에 설치해 출력했다. pyproject.toml/uv.lock/Node lock은 변경하지 않았다. Noto CJK KR 글꼴은 fontTools fallback으로 subset되며 HarfBuzz-Subset 권고 경고가 있었으나 실제 출력·포함·텍스트 추출을 확인했다.

PDF 검사: A4, #2 2쪽/#3 3쪽, 각 페이지에 충분한 본문, 모든 사용 글꼴 embedded/subset/Unicode mapping 확인. pdftotext로 한글·핵심 수치·미커밋 상태를 대조하고 5개 페이지를 PNG로 렌더링해 직접 확인했다. 초안의 짧은 문장/표 행 단독 페이지는 간격·구성 조정으로 제거했다. PDF/HTML은 모두 reports/에 저장하며 Git 제외 대상이 아니다.

이번 작업은 보고서와 작업 지침 추가다. Minecraft·모델/API·학습·pytest/mypy를 새로 실행하지 않았으며 문서의 실험/검사 수치는 보존된 원시 결과와 PROGRESS/검토 문서를 재구성한 것이다. 커밋·푸시·머지·이슈 종료는 수행하지 않았다.

## 2026-11-02 — 이슈 #3 실제 서버·snapshot·정지 구현 및 검증

사용자가 Minecraft EULA에 명시적으로 동의하고 서버 실행을 승인했다. 보유 계정이 필요한지 추가로 물었으며 서버 프로세스와 loopback offline 봇 접속에는 계정 인증을 사용하지 않는다고 설명했다. 계정·비밀번호·토큰·유료 서비스는 사용하지 않았다. 브랜치는 `ticket-3`, 기준은 main `1de47b7`이다.

### 실제 설치와 구현

- Java 21.0.12.1, Node 24.20.0, Mineflayer 4.39.0, Minecraft 1.16.5, Fabric Loader 0.16.14, launcher/installer 1.1.1, Carpet 1.4.44+v210714를 연결했다. 게임 바이너리·16개 jar의 SHA-256·승인일·버전은 Git 제외 경로 `worlds/server/installation.json`에 보존했고 출처·라이선스·주요 hash는 third_party/README.md에 기록했다. Mojang server.jar와 Fabric이 실제 받은 jar 모두 공식 SHA-1 `1b557e7b033b583cd9f66746b7a9ab1ec1673ced`와 일치한다.
- 서버는 `127.0.0.1:25565`, Survival/Peaceful, offline 인증, RCON 비활성이다. 실제 Done과 ResearchBot 접속·체력 20·위치를 확인했다. Microsoft/yggdrasil 인증 경로와 기존 npm audit 경고를 해결·검증했다고 표시하지 않는다.
- 최초 수동 서버는 로그상 15:09:03에 준비됐고 21:30에 저장·종료했다. 이 대기 중 실행을 학습/평가 경험으로 세지 않는다. 이후 진단은 CLI가 서버를 시작·정리한다. GPU 모델·API 지출은 없으며 PC 180시간의 충분성은 미확인이다.
- 기존 Python 실행기·자료형·JSONL을 유지하고 Node backend를 연결했다. 관리자 FD는 reset·snapshot 준비·시계 진단/검증만, 정책 stdin은 observe/step만 허용한다. 시드·숨은 블록·관리자 정보·자유 콘솔 실행을 정책에 제공하지 않는다. 현재 실제 관측은 자기 상태, 지형 지도는 빈 목록이며 실행은 wait다. 미지원 유효 행동의 실패도 실제 1틱을 실행해 invalid로 기록한다. 지형 관측·다른 매크로는 후속 티켓이다.
- `prepare-world`, `configs/minecraft.yaml`, `verify-clock`을 추가했다. 시드 `20261102`는 최초 생성 전에 기록했다. C4/G1은 첫 자연 지상 spawn `[-240.5,65,186.5]`·빈 인벤토리, G2/G3는 같은 위치에 돌/철 곡괭이 각 1개다. G4는 동일 x/z의 y=11에서 철 곡괭이를 제공하며 y=10의 3×3 바닥·y=11–13의 3×3 공간을 관리자 준비했다. 광석이나 모델 성적을 조회해 고르지 않았고 자연 C4 도달/다이아 성공으로 세지 않는다.
- 과제별 snapshot.json에 전체 월드 hash·좌표·제공 상태·준비 출처를 보존했다. C4/G1 `f8c9dfe69babead6d1d32fd5f4d3e54a22e5815b29d3c59fff7a0d6c3b3448c2`, G2 `0372a21c3501f5ad9a437522a75fe7bdb1a932a9c279d18e31e762a57c7bb969`, G3 `a189a17386976c74b3d4db82467a6bd62e42bf35fd384f78a3eacdd7dea551bb`, G4 `e56ebc58e4536e319af3e0440eafdb25d44973ce8780a301479eb4c20592ee0b`다.
- reset은 원본 hash 확인→staging 복사/재검증→디렉터리 교체→서버/새 bot 재시작을 따른다. 새 관측 UUID·episode/attempt·입력·이력·시간·사건 상태로 이전 에피소드를 섞지 않는다. 원본 덮어쓰기·심볼릭 링크를 거부한다. 서버 디렉터리는 `flock` 커널 잠금으로 소유하고 종료/충돌 시 해제한다.

### 실제 정지 실패와 보완

- Carpet freeze와 `physicsEnabled=false`만 쓴 실제 침수 5초 시험은 게임 틱이 같은데도 Air 281→172로 실패했다. 원시 기록은 `artifacts/issue-3/carpet-water-before-repair.json`이다.
- 자체 `bridge/pausemod/`는 Carpet이 paused이며 활성 틱이 아닌 동안 player tick/playerTick과 이동·차량 이동을 중지한다. 네트워크/keepalive는 유지하며 시작부터 월드를 정지한다. 초기 로그인용 체력·인벤토리·metadata는 실제 저장 상태에서 따로 전송한다. 모드 jar SHA-256은 `169c35019242042f8e93c32a72d9b5d866d130f589234eae89d44d39e3bd5cbb`다.
- 개발 중 Mixin namespace의 initializer 로딩 오류, 초기 체력 패킷 부재로 인한 spawn timeout, 2초 종료 유예로 인한 소유권 파일 잔류를 실제 로그로 확인했다. namespace·초기 상태 전송·제한된 spawn 대기·15초 종료 유예·진행 작업 중단·커널 잠금으로 보완했다.
- 보완 후 침수 5초와 7장면의 짧은 실제 시험은 준비 상태/불변을 확인했다. 첫 전체 실행은 상태 변화가 없었지만 화염 한 건이 아직 발화하지 않아 **62/63**, pause_verified=false로 실패했다. `verify-clock-attempt-1.jsonl`에 보존했다. 화염 준비를 실제 25틱 접촉으로 수정했다.
- 최종 공개 `verify-clock --config configs/minecraft.yaml`: **7장면×0/5/10초×3회, 63/63 통과, exit 0**. 전후 전체 측정값은 같고 위치 drift는 모두 0이다. 낙하 장면은 모두 공중 상태임도 원시 기록에서 확인했다. 전체 경과 **459.35초**, user 109.96초, sys 3.14초. 원시 JSONL·실패 시도·경과시간은 `artifacts/issue-3/`에 보존했다.
- 성공 실행만 검증 기록을 원자 저장한다. 코드·게임 jar·의존성 lock·Java/Node·서버 설정·과제 snapshot manifest의 fingerprint가 일치할 때만 후속 step의 pause_verified를 인정한다. 현재 `37929b6539994f39799f7e1e220637077e26bb0fa8b42bfa6c7f6326136942a9`이며 최종 실험 lock은 T19에서 수행한다.

### 개발 검증과 최종 확인

최종 전체 pytest **27 passed(8.14초)**, strict mypy **12개 파일 통과**(로컬 실제 reset 검사 스크립트 포함), diff 공백 검사 통과. 관리자 권한 거부, 상태 변화·미준비/잘못된 시계 응답 거부, 손상/symlink snapshot에서 현재 월드 보존, 느린 backend 종료 정리의 공개 CLI 회귀 검사를 포함한다. mock/scripted RPC 검사를 실제 물리 근거와 구분한다. 마지막 CLI 오류 처리도 RED→GREEN으로 확인해 실제 clock 오류를 mock smoke summary로 표시하지 않고 unverified clock_summary로 끝낸다. 이 오류 응답 보완은 검증한 시계 엔진/게임 모듈을 바꾸지 않는다.

읽기 전용 검토의 중요 지적 6건(관측 ID의 reset 간 재사용, 종료 유예, 연결 종료 후 cached 관측, snapshot 루트 symlink, 드롭 timestamp 비교, 마지막 틱 실패의 invalid/truncated 중복)을 확인·수정했다. symlink와 종료 정리는 RED→GREEN으로 확인했다. 상세는 docs/reviews/issue-3.md다. 별도 재검토, 커밋·푸시·머지·이슈 종료는 수행하지 않았다.

최종 실제 확인:

- 공개 smoke exit 0, 2결정·실측 40틱·11.18초, 두 step의 pause_verified=true, actor 전이 0·진단 보상 0·다이아 성공 false·decision_limit 유효 절단이다. 원시 결과는 `artifacts/issue-3/smoke-episode.jsonl`이다.
- C4에서 3틱 wait 후 다시 reset해 위치·속도·체력·산소·인벤토리·활성 시간 0의 복원을 확인했다. reset 전 후보는 invalid_selection으로 거부됐고 활성 시간은 여전히 0이었다. 미지원 행동은 실제 1틱을 실행해 invalid=true/truncated=false로 반환했다. 해당 Java 서버에 SIGTERM을 보내 연결을 종료한 뒤 cached 관측을 반환하지 않고 backend_error로 거부함을 확인했다.
- G1–G4도 각각 실제 재기동/reset 후 고정 좌표·제공 도구·체력 20·활성 틱 0, reset/observe 일치를 확인했다. 마지막에 flock을 다시 획득할 수 있어 소유권이 남지 않았음을 확인했다. 검사 코드/결과는 `artifacts/issue-3/reset-check.py`와 reset-check.json이다.
- 최종 C4 복원 후 실제 level.dat의 Time=457156, DayTime=1001, 비/천둥 여부와 타이머가 원본 snapshot과 같음을 NBT로 확인했다. `artifacts/issue-3/reset-world-clock.json`에 기록했다.
- 사용자 요청대로 C4 기준으로 수동 서버를 다시 실행했다. 23:22:20 Done, `127.0.0.1:25565`, 자체 확장의 정지 상태이며 23:24:57 list에서 접속자 0/1을 확인했다. 수동 실행도 동일 flock을 소유하므로 다음 실험 CLI 전 콘솔 stop으로 종료한다. 현재 실제 서버가 실행 중이라는 사실과 이슈 #3의 검증 완료를 구분한다.

모델/학습/PPO·전체 C4/G4 평가·온라인 계정 인증·공개 서버는 미실행이다. doctor의 기존 환경 probe를 새 게임 검증으로 바꾸지 않았으며 전체 실험 준비 완료를 주장하지 않는다. 향후 게임/버전/실행기 수정 시 시계를 다시 검증하고 T19에서 예산과 최종 lock을 고정한다.

## 2026-11-02 — 이슈 #3 / ticket-3 착수

사용자 요청으로 main `1de47b7`에서 `ticket-3` 브랜치를 생성·전환했다. 최초 생성은 샌드박스의 `.git/refs` 쓰기 제한으로 실패했으며 권한을 허용한 재실행은 성공했다. 기존 파일·Git 이력을 보존했으며 commit/push/merge는 수행하지 않았다.

- GitHub #1/#3 본문·댓글을 재조회했다. 둘 다 댓글이 없으며 #1 본문은 로컬 PRD와 일치한다. 선행 #2는 완료됐다. PLAN §§4.1–4.3, 12–14와 기존 schema/RPC/episode/CLI·Mineflayer 물리 코드를 확인했다.
- 구현 범위는 실제 Minecraft 1.16.5 Survival/Peaceful 연결, 사전 선정한 단일 시드와 C4/G1–G4 기준 snapshot/hash, 완전 reset, 실제 wait/실패 틱 계측, 관리자·정책 권한 분리를 유지하는 결정 경계 정지 및 공개 `verify-clock`이다. 평지·제련·드롭·용암·낙하·침수·화염의 0/5/10초 지연 각 3회, 위치 오차 0.001블록과 상태·사건·틱 불변을 실제 검증해야 한다.
- 현재 Python RPC의 별도 관리자 FD와 정책 stdin을 재사용할 수 있다. Mineflayer의 `physicsEnabled=false`만으로 서버 정지를 증명할 수 없다. Fabric/Carpet 연결을 제안했으며 서버·플레이어의 실제 정지 여부에 따라 보완해야 한다. 공식 Carpet 1.4.44 release에 `fabric-carpet-1.16.5-1.4.44+v210714.jar`가 있음을 확인했지만 설치·revision/hash 고정이나 호환 검증은 아직 수행하지 않았다.
- 저장소 파일 조사에서 Minecraft 서버 jar·server.properties·eula.txt를 찾지 못했다. AGENTS.md의 라이선스 동의 규칙에 따라 사용자에게 [Minecraft EULA](https://www.minecraft.net/en-us/eula) 동의와 로컬 서버 다운로드·실행 승인을 요청했으며 답변 대기 중이다. 구현 방식의 위임 또는 설계 선검토 선호도 함께 요청했다. EULA를 대신 수락하거나 서버를 다운로드·실행하지 않았다.

기준 검증: `UV_CACHE_DIR=.cache/uv .tools/uv run --locked --no-sync pytest` 17 passed(3.39초), 같은 환경의 `mypy .` 9개 파일 통과. 현재 Java 21.0.12.1과 Node 24.20.0을 확인했다. 실제 Minecraft 호환·reset·정지·위험 장면 검증은 미실행이며 이슈 #3을 완료로 표시하지 않는다. 다음 작업은 승인 답변을 반영해 서버 구성·출처/버전 고정과 구현 설계를 확정하고 기존 공개 CLI 테스트를 확장하는 것이다.

## 2026-10-10 — S 필수 진단·연구 동기와 기존 이슈 동기화

기준 원격 main은 `d809cd9bbbe2deda0ed193a9120c4964911a9185`다. PR #26은 2026-10-10 06:09:35 UTC에 main으로 머지됐고 T01(#2)은 Closed, T02(#3)는 Open이다. 나머지 구현 티켓 T03–T24도 Open이다. Issue #1과 24개 구현 티켓의 본문·댓글(모두 없음)·상태·라벨·blocking 관계 및 원격 main의 기준 문서를 읽었다. 로컬 main은 처음부터 같은 commit이며 미커밋 변경/분기 커밋이 없었다. `git merge --ff-only origin/main`은 샌드박스의 `.git/ORIG_HEAD` 쓰기 제한으로 실패했으나 이미 원격과 일치해 최신화할 commit은 없었다. 기존 파일/이력/T01 코드는 보존했다.

- PLAN v1.9-core-F-S, PRD v1.2-core-F-S, DECISIONS v1.3-core-F-S와 AGENTS/README/GLOSSARY를 갱신했다. 기존 선택 S=규칙 계획/규칙 행동 정의를 동일 최종 7B+별도 규칙 선택기로 바로잡았다. 규칙 복구/매크로 실행과 구분하고 공통 Observation/Goal/최대 8개 Candidate/mask·candidate_id 계약·일반 규칙·정보 경계·동률/실패 처리/hash 고정을 명시했다.
- 핵심 A/B/J/F C4 22+G4 6=28회/축소 14+6=20회는 보존하고 별도 필수 S C4 결정적 1회를 더해 총 29/21회로 정했다. 최대 활성 13/9시간, 최초 시도 게임 경과 상한 39/27시간이며 reset/검증/서버 재시도는 별도다. S1의 성공/최고 단계·시간·선택/7B 계획 호출·실패·비용은 별도 분모/표이며 단 한 번으로 통계적 우월성·일반적 신경망 대체를 주장하지 않는다.
- S 선택 연산·7B 계획 호출·GPU/PC·실행 비용과 계획 여유를 사전 예산/lock에 포함한다. 180시간의 충분성은 미확인이며 임의 증액/핵심군 삭제를 허용하지 않는다. F 핵심 지위·조건부 7B 학습의 최후 제안/여섯 조건/별도 승인·30,000결정·보상/PPO/curriculum/checkpoint/G4·BC 제외·고정 월드/시작 상태·Jev US$5/Astra 별도 승인 조건을 유지했다.
- 외부 상위 계획과 로봇 내부 소형 행동 선택의 계층 구조를 응용 동기로 추가했다. 현재 7B는 로컬이고 NanoJev는 고수준 매크로 선택 정책이다. 실제 로봇/온디바이스/분산 구조·CPU 실시간/특정 하드웨어 성능은 미검증이며 관련 실험은 추가하지 않는다.
- GitHub #1, #9(T08), #13(T12), #20(T19), #23(T22), #25(T24)만 갱신했다. T08 구현, T12 슬롯 기반/후속 S 연결, T19 사전 비용/규칙/lock, T22 최종 S1, T24 별도 보고로 배치했으며 기존 blocking 그래프를 그대로 활용한다. 새 티켓/테스트 계층은 만들지 않는다.

검증: 전체 pytest 17개 통과(3.38초), strict mypy 9개 파일 통과, diff 공백 검사 통과. 일회성 문서 검사로 PLAN §§6.1–6.2/8/9.4 및 PRD §§4–6 원문 보존, 과거 DECISIONS 이력 보존, 기준 파일 SHA-256, 기본/축소 횟수·활성/경과 상한·180시간 산술을 확인했다. src/tests/configs/fixtures/bridge/의 변경은 없다.

GitHub 게시 직전 전체 25개 이슈가 초기 조회와 같음을 확인했다. 검증된 로컬 문서/hash → #1 → 영향받는 미완료 티켓 5개의 순서로 게시하고 전체를 재조회했다. #1 본문은 로컬 PRD와 정확히 일치하며 여섯 변경안의 본문/제목도 일치한다. 미수정 이슈 19개(Closed #2 포함) 원문과 모든 상태·라벨·댓글·blocking 링크를 보존했다. #1만 새 버전에 맞춰 제목을 바꾸고 다른 제목은 유지했다. 새 이슈·댓글·라벨·상태 변경은 없다. 원격 main은 PR 검토 전 이전 버전이므로 Issue #1의 명세 버전/hash를 기준으로 구분한다.

이번 작업은 문서·이슈 명세 보완이다. 실제 S/Minecraft/T02 이후 구현·학습·유료 모델 API·결제·CPU/네트워크/로봇 실험은 수행하지 않았다. 현재 모의 고정 선택/collect 실행을 S 구현으로 표시하지 않는다. 후속 검증에서 S 구현/실제 수행·규칙 고정·예산 충분성을 확인해야 한다. 사용자 마지막 요청에 따라 로컬 main에 이 변경을 커밋하고 같은 commit의 별도 PR 브랜치를 준비한다. 원격 main 반영/최종 PR 머지와 기존 브랜치 삭제는 수행하지 않는다.

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
