# 실행 기록

## 2026-11-07 — T05A 영속 worktree 복구·최종 검증 재시작

사용자가 작업 재개를 요청했다. 기존 /tmp worktree와 원시 로그가 현재 없고
두 구현 커밋3284ba0/787712f는 Git에 남아 있음을 확인했다. 보존 커밋에서
`/home/sion/.codex/worktrees/327b/Minecraft_learning`, branch`issue-32-t05a-resume`을
생성했다. main4694d54와 Claude의issue-7-t06은 읽기 전용이다. 기존 사용자
파일/브랜치/누락 worktree의 등록은 보존했다. 서버·snapshot·Node 환경은 별도
복사하고 포트25566·전용 uv 환경을 설치했다. sudo/API/새 라이선스/학습은 없다.

마지막 미커밋 시설I/O 수정과 영구 회귀를 대화 패치에서 복원했다. 기본조작마다
실제1틱과 관측 후 정지 I/O를 기다리고, 확인 timeout은 후속 조작을 막고 failed
사건을 남긴다. 소실된 이전63조건·시계/감사 원시는 현재 근거로 재사용하지 않는다.

복구 후 실제 변경 전 고정 장면 wait20/100/200 각3회·960틱은
1.193834879초/결정+0.199745351초/틱이다. 실제 구간별 JSONL도 새로 수집했다.
유효 최종T05/T04 로그10개 회귀도1.225208660+0.199272347로 재확인했다.
경로 artifacts/issue-32/recovery/{before-fixed,final-log-fit}. 제외 단차/preflight는
기준선에 섞지 않았다. 관리자 고정 장면이며 자연 과제 성공이 아니다.

복원 후 개별pytest11통과(7.98초)·mypy22파일 통과. mod재빌드 hash는
c0ff66d5a455075e98ae3fea92ea94d520eaa9909c577b36878626486bbee3fe로 보존 코드와
일치한다. 전체 개발 검사와 새 최종 속도/동기화/63조건/정보 감사·T04/T05/G2를
진행한 뒤 결과 비교와 PDF2종을 마무리한다. push/merge/이슈 종료는 미실행이다.

## 2026-11-07 — T05A 즉시 관측 지연 수정·재인증 준비

Spec 검토의 P1을 실제 재현했다. `sync-red/`에서 침수 첫 틱 산소300/서버299,
화로 첫 틱 litfalse/서버true, drop 둘째 틱 y101/서버100.8808로 모두 실패했다.
`sync-before/`도 첫 산소 차이를 확인했다. 각 진단의 assert/exit1 및 finally reset을
보존한다. 추가 게임 틱 없이 vanilla dirty block/metadata/attributes·슬롯을
보내고 drop 위치+상대이동 기준을 동기화한 뒤 `sync-green/`은 모두 일치/exit0,
C4 reset 통과다. accessor/invoker는 기존 watcher와 vanilla dirty 전송만 호출한다.

첫 최종 시계는57/63 통과/drift0에서 의도적 SIGINT(-2) 중단했다. 검사기 exit1과
결과/리셋을 보존하며 인증 완료로 세지 않는다. 이전688f...mod 및 속도 결과를
새c0ff66d...mod의 인증으로 승계하지 않는다. final-speed에서 같은960틱을
재측정 중이며 이어 새 final-v2-t05의63조건·감사·제작·경계, 별도T04/G2를 실행한다.
수시 mypy22파일/새scripted회귀1개·새mod빌드 통과, 최종 전체 suite는 남았다.
독립 Spec은 P1해결/잔여 확정 지적0, Standards도 위반·smell0이다.

## 2026-11-06 — T05A #32 구현·최종 실제 검증 진행 중

현재 사용자의 즉시 구현 지시로 T05A에 착수했다. 기준 main4694d54에서 새
`issue-32-t05a` 브랜치와 `/tmp/Minecraft_learning-t05a-32` worktree를 생성했다.
main과 T06 worktree는 읽기 전용이며 별도 runtime/snapshot·포트25566을 사용한다.
코드는3284ba0에 커밋했으며 push/merge/이슈 종료는 하지 않았다.

`implement` 스킬(/home/sion/.agents/skills/implement/SKILL.md)을 실제 확인·적용했다.
공개 CLI/RPC와 기존 배포 bridge harness를 테스트 경계로 사용했다. 새 회귀는
기존 코드의 per-tick console polling 때문에 RED, receipt 구현 뒤 GREEN이다.
매 틱 관측·피해 즉시 중단·클라이언트 physics 상한/늦은 physics 대기·예상 밖
실제2틱 보존/실패·nonce 불일치 무시·불량응답·끊김·listener 정리를 mock으로 확인했다.
실제 물리/정지 인증과 구분한다. 제작 baseline10pytest, 새 scripted1pytest,
수시 strict mypy21파일·Java 빌드·Node 문법이 통과했다. 전체 suite는 최종에 실행한다.

실제 속도: 최종T05/T04 유효 로그의 같은 회귀식 재계산은1.225208660초/결정+
0.199272347초/틱. 제외 단차/preflight 로그는 쓰지 않았다. 같은 고정 관리자 장면
wait20/100/200 각3회·960틱은 변경 전1.174859334+0.199932601 → 최종
1.195367608+0.050001196이다. 실제20틱/초에 가깝고 필수0.10/목표0.06을 충족한다.
평균 advance 구간은197.55ms→47.98ms다. receipt만 적용한 중간0.100186100은
필수 미달 시도로 남겼다. 모델/PPO 포함 예산 검증이나 자연 과제 성공은 아니다.

첫 계측은 잘못된fixture scope로 invalid_request, 다음은 sandbox의 flock 실패였다.
권한 실행 후 유효 기준선/최종 측정을 완료했다. 승인된 EULA/기존 바이너리만
별도 복사했으며 sudo/새 라이선스/API/학습/유료 호출은 없었다.
사전 장착/채굴은2결정52틱·원목1, 보행은2결정47틱·6.379블록·위치검사 통과다.
둘 다 인증 전 exit1/pause_verified=false로 보존한다.

최종 시계/회귀: `artifacts/issue-32/final-t05/`에서 clock information production
boundaries 진행 중이다. 완결 전 완료로 세지 않는다. 다음은 별도 final-t04와 g2
출력 폴더이며 G2의 기존 실패 exit1/direct_iron_verified=false/assert를 유지한다.
이후 결과 비교·전체 pytest/mypy·독립 Standards/Spec·한국어 PDF2종을 마무리한다.

원시 경로: artifacts/issue-32/baseline/{final-log-fit.json,fixed-3/},after-fixed/,
after-scheduled/,profile-comparison.json,movement-preflight/. 소스/hash·실패 시도도 보존한다.
T06 코드에는 이번 최적화를 넣지 않으며 이후 최종 코드 통합과63조건 재인증을
별도 수행해야 한다. 자연G2철3의 최종 통합 인수는#8이며 기존 실패를 성공으로 쓰지 않는다.

## 2026-11-06 — 개정 T05 완료·T05A 착수 가능 (구현 미착수)

**완료:** 사용자 승인으로 개정한 T05 인수7항목을 충족했다. 인수 책임 문서 커밋 `f16969647cd5c2f9cb993afe20d03272de190adb`를main/origin에 푸시하고 실제원격해시 일치를 확인했다. [#6 완료 댓글](https://github.com/sion0507/Minecraft_RL/issues/6#issuecomment-6683924522)을 남기고 #6을2026-11-06T11:38:26Z에Closed 처리했다. PR/merge는 수행하지 않았다. 이 완료 상태 기록도 별도 문서 커밋으로 보존하며 실행 코드는ff75f36과 동일하다.

**자연 G2는 여전히 미달이다.** 유효 기준선64결정/1778틱/철 관측·획득0·정지 인증true를 보존했고, 제외 단차의64/150틱/철0·미인증 결과와 구분했다. 성공으로 체크하지 않았으며 같은snapshot/시작점/돌곡괭이/10분에서 철 발견→적절한 도구 파괴→해당 드롭 직접 획득3의 최종 통합 책임은#8이다. #7은 기존G3와별도G2접근 확인을 맡는다.

[#32](https://github.com/sion0507/Minecraft_RL/issues/32)는Open/ready-for-agent이며 실제blocked_by 조회에서 유일한 선행#6이Closed임을 확인했다. **다음 이슈 T05A에 착수해도 되는 상태다. 이번에는 구현·advance 계측·속도 개선을 시작하지 않았다.** #7/#8은Open/미구현이고 기존선행그래프를 유지한다. 기존실패회귀·최종코드63조건재인증·정보감사·관련T04/T05회귀 조건은모든본문/PLAN에 반영했다.

보고서 `reports/issue-006-T05-report.pdf`2쪽과 코드가이드 `reports/issue-006-T05-code-guide.pdf`3쪽을 최신교체했다. 실제/mock/미인증/미실행·G2미달이관·제외코드·구현ff75f36/인수문서f169696·commit/push/merge/종료/ready 상태를 구분했다. 한글추출·대체문자 없음·모든사용글꼴embedded/subset/Unicode·최종5페이지렌더 가독성을 확인했다. 코드가이드는 파일/함수/시작줄·확인할로직·SHA256을 제공한다. PDF/원시/백업은Git제외,생성중간물은/tmp이며 게임재실행은없다.

남은 위험: 자연G2철3 성공 가능성과 굴착 필요성은 미입증이다. 단차 실험은슬라임거리상한/인증미완료로제외했으며향후채택시별도교정/검증이필요하다. T05A는속도만개선하므로탐색문제해결을보장하지않는다. 모델/API/학습/평가·연구조건/예산변경은미실행이다. 아래 Open/종료전/미완료 문구는각게시·검증시점의 이력이다.

## 2026-11-06 — 사용자 승인에 따른 인수 재배치·최종화

**현행 판단:** 자연 고정 G2 철3은 미달이며 성공으로 바꾸지 않는다. 사용자가 T05를 제작·제련·노출 철 직접 채굴/획득 연결과 검증으로 정리하고 G2를 후속 통합 인수로 이관하도록 승인했다. PLAN §5.2.1/PRD/#1/#6/#7/#8/#32를 이 기준으로 맞춘다. 아래의 #6 Open 유지·종료 금지 문구는 변경 전 이력이며 이 승인으로 대체된다. T05는 개정 기준 충족·커밋/푸시·GitHub 확인 뒤에만 완료하며 T05A 구현은 이번에 시작하지 않는다.

### 코드 범위와 미검증 단차 변경 제외

시작 상태 main `ff75f365026c9ec8600d9d3a4a6a1a67ae2dd1b3`/origin 동일, 단차 관련8파일 미커밋이었다(소스/검사7+계획1). 모든 변경을 패치·파일 사본·SHA-256 manifest로 `artifacts/issue-6/excluded-natural-steps-2026-11-06/`에 보존하고 7개 소스/검사/드라이버를 ff75f36과 바이트 동일하게 복원했다. 계획은 제외 경위의 이력으로 남긴다. 보존 패치 SHA-256은 `538437e2682009e6507b9acdf7693561ca52384ec1208b767376f9597794dc0b`다. 백업 Python 사본 때문에 첫 mypy가 중복 모듈로 실패했고 파일명을 .saved로 바꾼 뒤 strict mypy23파일을 통과했다. 백업이나 사용자 코드를 삭제하지 않았다.

제외한 코드의 실제 단차 fixture는 상행24/하행17틱·위치/착지 확인이었으나 정지 미인증이다. 새63조건·단차 정보 감사는 수행하지 않았고 scripted 슬라임 하강 거리 상한 초과도 미해결이었다. 해당 자연 G2 사전 실행(`g2-natural-step-preflight/`)은64결정/150틱/119.12초·철 관측/획득0, observed_hazard63회·decision_limit·pause_verified=false·reset 통과다. dryland 인근 위험 판정의 원인은 미확정이다. 이 결과를 인증된 기준선/단차 구현 완료/자연 성공으로 합치지 않는다.

### 개정 T05 근거와 후속 책임

복원 후 전체 pytest **78 passed(18.39초)**, strict mypy **23파일**, bridge/minecraft.js·terrain.js Node 문법 통과. 원시 재계산은 기존 실제63조건/26장면/직접 사건·틱 합계/후보 상한·사건 중복 없음/reset을 확인했다. g2-route-fix manifest의 모든 소스 hash가 일치한다. final-3의 navigation/driver, control-final의 navigation 차이는 이전의 공개 후보 누락 수정과 취소 후 재선택 드라이버 보완이며, 기존 실제32관측의 후보 순수 재생32/32 일치 근거를 유지한다. 이번 문서·인수 변경 때문에 게임을 재실행하지 않는다.

|근거|결과·한계|
|---|---|
|실제 시계/정보 감사|final-3:63/63·drift0,26장면 통과. 복원한 bridge/runtime/설정/snapshot fingerprint가 저장 인증6de2893387dc7971a1213cf939e056c07520edef6f6edfede0982b423e832804와 읽기 전용 재계산으로 일치했다. 새 게임 실행이 아니다.|
|실제 제작/직접 철 연결|final-3:빈 인벤토리/관리자 배치 자원,51결정/1702틱. 직접 원목4·조약돌11·철광석3, 직접 제련 철괴3, 직접 제작 철 곡괭이1. 자연 C4/G2 성공 아님.|
|실제 전제조건/제어|control-final:도구·연료 부족각1틱,위험1틱. 취소40틱 actor제외/trace0 뒤 새 제작3틱,총43틱·선택2/실행1. 기준 C4 reset·서버 종료.|
|자연 G2 실패 기준선|g2-route-fix:제공 돌 곡괭이1,64결정/1778틱/446.39초·철 관측/획득0·방문155칸·decision_limit·서버오류 없음·정지 인증true.10분 전체 소진이나 전체 월드 불가능성의 근거 아님.|

T05A는 #6 개정 범위 완료 뒤에만 착수하며 기존 G2 실패를 회귀 기준선으로 보존한다. T06은 기존 G3와 별도 고정 G2 접근/노출/실패 확인, T07은 같은 snapshot/hash·시작점·돌 곡괭이1·10분/12000틱에서 자연 철 발견→적절한 도구 직접 파괴→해당 드롭 직접 획득3의 최종 책임이다. T07 미달 시 #8은 미완료다. #5→#6→#32→#7→#8의 기존 그래프와 #7의 #5 선행을 유지한다. 최종 bridge/fingerprint 변경 때 각 티켓63조건 재인증·정보 감사·관련 매크로 회귀를 요구한다. G2 기존 실패/제외 코드 사전 실패/새 회귀 결함을 구분하고 검사기 assert를 우회하지 않는다.

GitHub 반영 확인: #1/#6/#7/#8/#32 본문과 변경 댓글을 게시 후 다시 조회해 준비한 원문과 모두 일치함을 확인했다. #6 개정 인수7항목 체크, 자연 G2는 별도 미달·#8 이관 문구로 보존, #7/#8/#32 구현 항목은 미체크다. 실제 선행은 #6←#5(Closed), #32←#6(Open), #7←#5(Closed)/#32(Open), #8←#7(Open)로 기존 그래프와 일치했고 역의존은 없다. 재계산·게시 교차확인 결과는 로컬 acceptance-reallocation-check.json에 보존했다. 독립 Spec 지적0, Standards hard breach0·명확성1건(PRD/#1 과거 미검증 문단)을 해소했다.

변경 댓글: [#1](https://github.com/sion0507/Minecraft_RL/issues/1#issuecomment-6683790490), [#6](https://github.com/sion0507/Minecraft_RL/issues/6#issuecomment-6683803025), [#7](https://github.com/sion0507/Minecraft_RL/issues/7#issuecomment-6683827942), [#8](https://github.com/sion0507/Minecraft_RL/issues/8#issuecomment-6683839319), [#32](https://github.com/sion0507/Minecraft_RL/issues/32#issuecomment-6683846771). 댓글 게시의 첫 sandbox 네트워크 실패는 권한 실행으로 재시도했고 게시 후 원문을 확인했다. 당시 #6은 완료 처리 전 Open이었고, 커밋/푸시·원격 확인 뒤 최상단 완료 기록과 같이 닫았다.

게시·최종 문서·PDF 검수와 Git 상태는 아래 완료 확인에 기록한다. 모델/API/PPO/학습/평가·PC180시간 증액·T05A 구현은 하지 않는다. reports 두 PDF는 최신 교체하되 로컬 전용/Git 제외이며 보고서 때문에 게임을 실행하지 않는다.

## 2026-11-06 — T05 재개 후 탐색 후보 누락 수정·최종 인수 미달 보존

사용자가 사용량 제한으로 중단된 T05만 이어서 검증·PDF·커밋/푸시·이슈 절차를 처리하도록 요청했다. 이전의 push 금지는 이 추가 요청으로 대체한다. T05A(#32)나 다른 티켓 구현은 시작하지 않았다. 현재 #6의 고정 자연 G2 직접 철광석3 기준은 그대로이므로 미달인 채로 이슈를 닫지 않는다.

final-3 G2의 마지막 공개 관측을 다시 읽어 도달 경로155개 중 미방문55개가 남았는데도 후보0이던 결함을 재현했다. 방향별 대표 경로를 고른 뒤 방문한 끝점을 버리는 순서 때문에 다른 새 경로까지 가려졌다. 공통 `generate_movement_candidates`가 방향별 미방문 끝점을 우선 보존하도록 수정했다. 후보 최대8·관측 지도·같은 높이·16블록/400틱·실행 방식과 G2 상한은 유지한다. 공개 CLI 회귀 RED→GREEN, 저장된 마지막 G2 상태에서 후보4개 생성 확인. 전체 **78 pytest passed(18.72초)**, strict mypy **23파일**, Node 문법·diff 검사 통과다.

같은 고정 G2를 `artifacts/issue-6/g2-route-fix/`에서 실제 재검증했다. **CLI exit1,64결정·1,778틱(88.9 활성초)·446.39 실제초·철0·decision_limit·서버 오류 없음·paused/인증true**다. 돌 곡괭이1 제공, 방문155칸·철 관측0·경로 완료39·0후보 대기25회다. 저장된 공개 지도 전체의 같은 높이 연결 성분155칸에서 미방문0임도 확인했다. 후보 누락은 보완됐지만 **직접 철3 인수 조건은 여전히 미달**이다. 이는 전체 월드나12,000틱 전체 불가능성의 증거가 아니다. 최종 C4 reset/observe·0틱·빈 인벤토리·체력20 및 검사/서버 종료를 확인했다.

게임/시계/bridge/runtime 변경은 없고 새 G2의 인증도 true라 시계63은 반복하지 않았다. 기존 실제26장면 감사의 공개 관측32개를 수정된 후보 생성기로 순수 재생해 저장된 후보 ID/내용/순서/mask가 **32/32 모두 동일**함을 확인했다(`candidate-replay.json`). 이는 새 실제 감사가 아니라 기존 실제 근거에 대한 후보 재생 확인이다. final-3의 실제 시계63·정보26·전체 제작51결정/1702틱과 control-final의43틱 제어 근거를 함께 보존한다. 최신 통합 재계산은 `g2-route-fix/evidence-recomputed.json`, G2 상세는 같은 폴더 `g2-recomputed.json`이다.

보고서와 코드 가이드는 최종78검사·수정 전후 G2·실제/mock/미실행·커밋/푸시/이슈 상태와 코드 줄/hash로 갱신한다. PDF 생성 때문에 게임을 재실행하지 않는다. 구현과 유효 근거를 현재 브랜치에 커밋·푸시하고 #6에는 충족한 항목과 G2 미달을 기록한다. **#6 Open 유지, 다른 티켓 미착수**가 이번 종료 상태다. 이하 추가 요청 전의 push 금지·77검사·G2 1687틱 기록은 해당 시점 이력으로 보존하며 위 최신 상태가 우선한다.

## 2026-11-06 — T05 구현 보존, 고정 자연 G2 인수 조건 미달

**#6 전체는 미완료이며 Open을 유지한다.** 빈 인벤토리/배치 자원에서의 제작 사슬과 실행 경계는 실제 검증했지만, 관리자 지원 없는 고정 자연 G2에서는 철광석3을 획득하지 못했다. 후속 티켓 자동 착수, snapshot/시드/시작점 변경, 하강/터널 추가, 모델/API/학습, 연구 예산 증액은 하지 않는다. 현재 main의 구현과 검증 기록을 로컬 커밋으로 보존하며 push·PR·merge·이슈 종료/댓글은 수행하지 않는다. 최신 커밋은 `git log -1`로 확인한다.

|구분|실제 최종 결과|
|---|---|
|시계|final-3 exit0,63/63. 고유63·준비63·전후 전체 상태 동일·최대 위치 drift0. 인증 `6de2893387dc7971a1213cf939e056c07520edef6f6edfede0982b423e832804`.|
|정보 감사|final-3 exit0,26장면·710.42초. 기존 관측/보행/목재/장착/대기/드롭/0후보에 제작3틱·설치7틱·화로207틱·철44틱의 숨은 광석/용암 쌍 불변과 벽 개방 양성 대조 통과.|
|배치 자원 제작|final-3 exit0,51결정·1,702틱(85.1 활성초)·413.17 실제초. 시작 인벤토리 비움. 원목4/조약돌11/철광석3 직접 획득, 철괴3 직접 제련·회수, 작업대/나무·돌 곡괭이/화로/철 곡괭이 직접 제작. 지급 철 곡괭이가 아니다. actor0·진단 수집 보상18.|
|전제조건·위험|control-final exit0. 돌 곡괭이 없는 철 채굴·연료 없는 투입 각각 invalid/1실제틱. 관측 용암 위험은1틱·observed_hazard·불안정 경계로 투입 중단. 유효 채굴/투입/제련 사건 없음.|
|취소·재선택|control-final의 제작 준비 지원 장면. 실제 진전20+취소 대기20=40틱을 원 선택에 보존, actor제외/trace0. 새 선택으로3틱에 철 곡괭이 직접 제작. 총43틱·선택 요청2·실행 결정1·목표완료·paused/인증true. 전체 realtime 인증은 아니다.|
|고정 자연 G2|final-3 CLI exit1,64결정·1,687틱(84.35 활성초)·428.40 실제초. 시작 제공은 돌 곡괭이1개, 철 획득0·goal_completed=false·decision_limit·서버 오류 없음·paused/인증true. 직접 철3 인수 조건 미달.|
|최종 복원·종료|final-3/control-final 모두 기준 C4 reset/observe 일치·0틱·빈 인벤토리·체력20 복원. 권한 ps로 검사/bridge/Java 서버 잔여 프로세스 없음을 확인.|

G2 원시 재계산: 시작 `[-240.5,65,186.5]`, 공개 관측 방문100칸, 관측 철 셀0. 경로 완료22·거리 상한3·0후보 대기39회다. 현재 같은 높이의 관측 경로 탐색이 철 확보로 이어지지 않았다. 전체 월드에 철이 없거나 활성 상한12,000틱 전체에서도 불가능하다는 증거가 아니다. 결과를 보고 시작점·월드·규칙·예정 횟수를 튜닝하지 않았다. **재개 시 남은 항목은 고정 자연 G2 직접 철3 조건**이며 기존 통과 검사를 다시 실행하는 일이 아니다.

최종 개발 검사는 전체 pytest **77 passed(19.57초)**, strict mypy **23파일 통과**, Node 문법·diff 공백 검사 통과다. 별도 Standards/Spec 검토 후 확인된 지적을 회귀로 보완했고, 실제 화로 창 재고 문제와 검증 도구의 취소 후 재선택 누락도 보완했다. 상세는 docs/reviews/issue-6.md다. final-3의 초기 취소 검사는40틱 보존만 확인했으며 최신 control-final의43틱 결과로 재선택 근거를 보완한다. 따라서 final-3 manifest와 현재 driver만 다르고 게임/후보/시계 소스는 동일하며 control-final manifest는 전부 일치한다. 시계63·정보26·전체 제작은 반복하지 않았다.

원시: `artifacts/issue-6/final-3/`, `artifacts/issue-6/control-final/`. 재계산 `control-final/evidence-recomputed.json`, `final-3/g2-recomputed.json`. 사전 실패/중단은 아래 기록과 원시에 보존하고 최종 성공과 합치지 않는다. 실제 사망·8개 배치 중단·제공 화로 출력 제외·소비 중 동시 드롭 등 일부 경계는 mock/scripted 검사다. 자연 C4/다이아 성공·모델/유료 API·과금·PPO/본 학습·최종 평가·일반화·전체 realtime은 미실행이며 PC180시간의 충분성을 재확정하거나 증액하지 않았다.

보고서 `reports/issue-006-T05-report.pdf`와 코드 가이드 `reports/issue-006-T05-code-guide.pdf`는 위 미완료 판정·실제/mock/미실행·함수 시작 줄/코드 hash·Git 상태를 담는 로컬 전용 최신본이다. 중간 파일은 /tmp에 두고 한글 추출·모든 글꼴 포함·전체 페이지 가독성을 검수해 공유한다. PDF 때문에 게임 검사를 다시 실행하지 않는다. 이하 T05 진행 중 기록보다 이 최종 상태가 우선한다.

## 2026-11-06 — T05 재개, 실제 최종 검증 진행 중

현재 main/기준 `2188120`에서 기존 미커밋 #6 구현을 재개했다. GitHub #1/#6 본문·댓글(없음), #6 Open, 선행 #5 병합/Closed와 관련 PLAN/GLOSSARY를 대조했다. 사용자는 필요한 실행 권한을 허용하고 확인 질문 없이 진행하도록 요청했다. 구현 범위와 현재 브랜치 로컬 커밋 지시를 유지하며 push/merge/PR/이슈 종료는 수행하지 않는다.

개별 제작·설치·화로 투입/회수·철 채굴·도구 전제조건과 직접/제공 요약, 공유 허용 레시피, 실제 진단 실행기·생성물 출처를 연결했다. 기존 CLI/RPC/후보·관측 지도·보행·활성 틱 실행을 재사용한다. 독립 Standards/Spec 검토와 실제 사전 실패를 바탕으로 가려진 작업대 왕복, 일부 제공 목표 완료, 비참나무 연료, 소비 중 드롭 수집, 늦은 설치/투입/회수 응답을 보완했다. 상세는 docs/reviews/issue-6.md 및 DECISIONS의 T05 기록이다.

최종 개발 검사: 전체 pytest **77 passed(18.49초)**, strict mypy **23파일 통과**, Node 문법·diff 공백 검사 통과. mock/scripted 검사이며 실제 게임 물리 근거와 구분한다. 이후 런타임 소스 변경 없이 실제 검증을 수행 중이다.

사전 원시: artifacts/issue-6/preflight-1은 sandbox 서버 잠금 실패, preflight-2는 응답 중단과 잔여 서버로 미완료, preflight-3은 잔여 소유권 충돌이다. preflight-2 잔여 bridge를 SIGTERM으로 정상 종료하고 서버 종료를 확인했다. preflight-4는 **빈 인벤토리/배치 자원에서 50결정·1,681틱·408.19초**에 실제 철 곡괭이를 제작했다. 원목4·조약돌11·철광석3 직접 획득, 작업대/나무·돌 곡괭이/화로/철 곡괭이 직접 제작 사건은 남았으나 화로 입력의 늦은 인벤토리 반영으로 직접 제련 출처가 누락돼 검사 도구는 실패했다. unverified/exit1이며 최종 성공으로 쓰지 않는다. 마지막 기준 C4 reset/observe·0틱·빈 인벤토리·체력20 복원은 통과했다. 투입/회수 갱신 확인·출처 연결을 수정하고 배포 bridge 회귀를 통과시켰다.

final-1은 시계63/63·고유/준비63·상태 동일/drift0 완료 후 정보 감사22장면까지 진행했으나 화로에서 RPC timeout(624.27초)으로 실패했다. 기준 C4 reset은 통과했다. 설치된 Mineflayer의 열린 창에서 플레이어 슬롯 재고를 갱신하는 구조를 확인했고 inventory()가 현재 창의 items()를 우선 읽도록 한 줄 수정했다. 설비 입력/출력을 보유량에 합치지 않는다. load_window/collect_window 배포 bridge 회귀 RED→GREEN, 전체77passed(18.48초)·mypy23파일 통과. 실제 furnace-preflight는 투입5+wait200+회수2=207틱·직접 제련1·목표완료·reset을 확인했다. 미인증 사전 결과는 최종 성공과 구분한다.

새 production/G2 설정은 관측을 동반한400틱 실행의 벽시계 지연을 수용하도록 RPC180초이며 활성400/12000틱 상한은 그대로다. final-2는 기존 schema60초 제한으로 서버 실행 전 설정 거부됐고 공개 CLI RED→GREEN으로 schema 상한도180초로 맞췄다. 현재 실제 실행은 `.tools/uv run --locked python tools/verify_t05.py --output artifacts/issue-6/final-3 clock information production boundaries g2`다. bridge 변경으로 새 fingerprint63 → 26장면 감사 → 제작 → 경계 → 자연G2를 실행하고 마지막 기준 C4 reset을 시도한다. 최종 결과는 아직 없다.

고정 자연 G2에서 직접 철광석3이 없으면 전체 T05 인수 조건 미완료로 표시하고 관리자 iron/production 성공으로 대체하지 않는다. 자연 snapshot·시드·시작점·하강/터널·모델/API/학습·연구 예산을 바꾸지 않는다. 보고서/가이드 PDF 두 개는 실제 최종 결과 확인 후 로컬 reports에 생성하며 보고서 때문에 게임을 다시 실행하지 않는다.

## 2026-11-05 — T04 재개, 남은 실제 검사 완료

사용자의 `continue`로 중지한 #5 보완을 재개했다. GitHub #1/#5 본문·댓글(모두 댓글 없음, Open), AGENTS/CONTEXT/관련 PLAN/GLOSSARY와 작업 트리를 확인했다. final-2 manifest의 모든 소스 hash가 일치하고 bridge·Node/Java runtime·snapshot·설정 fingerprint도 기존 인증 `a15976b0849d81fc6d48d4ef73635fc4dfc4a88ce30318b6c161eee70886c789`와 같아 완료한 **시계63/63을 반복하지 않았다**. 코드·테스트 변경 없이 이미 완료한 pytest **68 passed**, strict mypy **20파일 통과**, 독립 Standards/Spec 재검토 **각0건**도 유지했다. 이번 재개는 남은 실제 진단·저장 근거 재계산·문서/PDF·로컬 커밋 범위다.

실행: `UV_CACHE_DIR=.cache/uv .tools/uv run --locked python tools/verify_t04.py --output artifacts/issue-5-review-2026-11-05/resume-1 information macros`. 드라이버 exit0. 실제 결과는 다음과 같다.

|검사|최종 결과|
|---|---|
|확장 정보 감사|18장면 통과, exit0, 494.08초. 관측/이동/군집·회수와 독립 장착·드롭 wait·0후보·wait20/100/200 숨은 광석/용암 쌍 불변, 벽 개방 양성 대조 통과.|
|맨손 수집|1결정·81틱·직접1개 획득·목표 완료·exit0.|
|장착 후 수집|3결정·103틱·직접1개 획득·목표 완료·exit0.|
|실제 파손|3결정·51틱·목표 완료·exit0. 같은 step의 mined/tool_broken 보존 후 직접1개 회수.|
|완료 틱 위험|12결정·72틱, mined/observed_hazard 동시 보존. 목표 미완료·exit1은 예상 결과.|
|독립 드롭 대기|2회 wait·40틱·직접1개 회수·목표 완료·exit0. 관리자 준비71틱은 에피소드와 별도.|
|0후보|12회 실제 wait+failed·240틱·actor 제외. 목표 미완료·exit1은 예상 결과.|
|실제 취소/재선택|실제 상태 진전20+취소 대기20=40틱을 원 선택에 보존, actor 제외·trace_mask=0 뒤 재선택. 총121틱·1실행 결정·목표 완료. 전체 realtime 인증과 구분.|
|최종 복원|G1 reset/observe 일치, 활성0틱·빈 인벤토리·체력20. 검사·서버 프로세스 종료 확인.|

모든 최종 step/summary는 paused·pause_verified=true이며 actor 전이0이다. `resume-1/evidence-recomputed.json`에 시계/재개 manifest hash 일치·실제 step 틱 합계·목표/예상 실패·취소 원 선택·reset을 원시에서 재계산한 결과를 보존했다. `final-1`과 `final-2` 감사 중단, `macros-preflight` 미인증 결과와 자연 G1 사전 실패(12결정294틱 나무 미발견)를 최종 성공으로 바꾸지 않았다. 최종 장착/파손 소요량은 이번 실제 드롭 이동 결과이며 사전 수치로 대체하지 않았다.

한국어 보고서 `reports/issue-005-T04-report.pdf`(2쪽)와 코드 가이드 `reports/issue-005-T04-code-guide.pdf`(3쪽)를 이번 보완·최종 실제 결과·코드 함수/시작 줄/hash·Git/이슈 상태로 교체한다. 한글 추출·사용 글꼴 전체 포함/subset/Unicode·모든 페이지 렌더 가독성을 확인하며, 생성 중간 파일은 /tmp에만 둔다. reports는 Git 제외, 다른 티켓 PDF는 보존한다. 보고서 때문에 게임 검사를 다시 실행하지 않는다.

검증본은 기존 main 이력을 보존해 현재 브랜치의 로컬 커밋으로 마무리한다. **push·PR·merge·이슈종료/댓글은 수행하지 않으며 #5는 Open**이다. 관리자 실제 진단 성공은 자연 C4/다이아·모델 성능의 근거가 아니다. 실제 사망은 mock 주입만 확인했다. 전체 realtime 운용, 제작/제련/하강/터널, 모델/API/과금/PPO/본 학습/최종 평가/일반화는 미실행이고 PC180시간 예산을 재확정하거나 증액하지 않았다. 후속 #6/T05는 이번에 착수하지 않는다.

## 2026-11-05 — T04 보완, 사용자 요청으로 중지

main `9f9aca5` 대비 완료 틱 증거 유실·위조 stop_rule_id/임의 wait·중복 근거/명명/죽은 분기, 공개 진단·감사 범위와 재현 실행기를 보완했다. 전체 pytest **68 passed(16.60초)**, strict mypy **20파일 통과**, Node 문법·diff 검사 통과. 독립 Standards/Spec 수정본 재검토 남은 지적은 각 **0건**이다. 항목별 처리는 `docs/reviews/issue-5-review-fixes-2026-11-05.md`.

실제 맨손/장착/파손 수집·완료 틱 위험·독립 dropwait·0후보·실제 제어된 취소/재선택은 macros-preflight에서 확인했으나 새 인증 전이라 unverified/exit1을 유지했다. 자연 G1 사전 공개CLI는12결정294틱에 나무미발견이며 관리자 진단 성공과 구분한다. 최종 코드 **verify-clock63/63**, 고유63/준비63/위치 drift0.0 재계산은 완료했다.

사용자가 내일 continue하도록 중지를 요청해 정보 감사를 SIGINT로 중단했다. `artifacts/issue-5-review-2026-11-05/final-2/`에 clock exit0·audit exit-2/미완료(요약 없음)·G1 reset/observe 일치·0틱·빈 인벤토리·체력20 복원을 기록했고 검사/서버 프로세스 종료를 확인했다. 중단 뒤 driver AssertionError는 의도한 중단의 종료코드 검사이며 감사 완료나 새 결함으로 세지 않는다. final-1도 준비 틱 집계 수정 전 중단/복원 기록이다.

현재 **미커밋·미푸시**, PR/merge/이슈종료 없음. 확장 감사18장면·인증 후 최종 공개CLI/macros·최신 PDF 생성/검수·로컬 커밋이 남았다. reports의 #5 두 PDF는 이전 판본이며 교체하지 않았다. 재개 명령과 상세 상태는 `CONTEXT.md`에 보존했다. continue 전에는 추가 작업을 실행하지 않는다.

## 2026-11-04 — 이슈 #5 / T04 원목 후보·채굴·획득

기준: 시작 시 깨끗한 main `e60493612125ea8803e533838acefc089005f818`, GitHub #1/#5 본문·댓글(둘 다 댓글 없음), PLAN §§4.1–4.3/5.2/5.4/12–14, GLOSSARY. #2–#4는 Closed이므로 선행 조건을 충족했고 다음 티켓은 #5임을 확인했다. `implement` 지시에 따라 현재 main에 구현·검증 변경을 로컬 커밋한다. push·merge·PR 생성·#5 종료는 실행하지 않으며 GitHub #5는 Open이다.

### 구현

- 공개 `smoke-macros`, mock pilot과 실제 G1 `configs/macros.yaml`. 제한 관측의 현재 노출 원목·같은 높이 접근 경로·장착·1/최대 8블록 작업량을 중복 제거해 최대 8후보로 저장한다. ID·내용·순서·mask·source obs/map과 결정별 macro_steps를 보존한다.
- 기존 보행/정지와 실제 활성 틱 기반 채굴 패킷, 서버 파괴 확인·직후 2틱 내 드롭 생성·자기 수집·인벤토리 증가 연결. 선택 밖 군집으로 확장하지 않는다. 노출 군집 최대 8블록/400틱, wait 20/100/200틱, 매 기본 조작 관측과 위험·피해·산소·파손·실패·시간·사망 중단을 연결했다.
- 0후보 실제 wait+failed, 1후보 확률 1과 actor 제외. 취소된 원 후보/선택·대기 사건/시간·비용을 보존하고 trace_mask=0 뒤 재선택한다. 미실행 매크로 상한과 취소 대기를 구분하고 사건 ID의 중복 집계를 거부한다. smoke actor 전이는 항상 0이다.
- 실제 회수 실패를 추적해 기존 정지 확장이 클라이언트 이동 패킷을 버려 서버 플레이어는 출발점에 남는 결함을 확인했다. 서버 스레드에서 최신 위치/방향을 보관하고 활성 틱에 vanilla 검증으로 적용하며 순서·텔레포트 경계를 보완했다. 이동 종료에서 서버/클라이언트 위치도 0.001블록 이내로 일치해야 한다. 관리자 위치는 검증에만 사용한다.
- 정지 중 공중 상태의 벽시계 비행 추방을 막도록 표준 allow-flight=true를 공통 서버 설정으로 고정했다. Survival 비행 능력/물리·행동 권한은 바꾸지 않는다. backend 시작 전에 검사하고 fingerprint에 포함한다. 자체 확장 jar SHA-256은 `83d8fdc54807e788087c4800298d8f3da46e803ad76a65e0632614dcd5ffcfc8`이다.

### 검증

- 새 CLI·후보/단일 확률·0후보, 관측 드롭 회수·실제 위치 기준 회수 거리, 취소 20/450틱·짧은 취소 상한, 중복 사건, 현재 시야/중복 제거/8후보, 오래된·실패한 파괴 출처, 위치 불일치 거부를 공개 CLI/배포 bridge로 검사했다. 회귀는 RED→GREEN을 확인했다.
- 최종 전체 pytest **65 passed(16.32초)**, strict mypy **19개 파일 통과**, Node 문법·diff 공백 검사 통과. 실제 Java 소스를 설치된 jar와 컴파일한 5개 패킷 순서/정지/텔레포트 assert도 통과했다. mock/scripted 검사는 실제 물리 근거가 아니다.
- 독립 code-review: Standards 1건, Spec 2건을 재현·수정했다. 추가 Java 경계 검토의 패킷 순서 2건도 재현하고 5개 assert로 수정 검증했다. 상세는 docs/reviews/issue-5.md.
- 최종 실제 서버 이동 사전 검사: **2결정·47틱**, 정상 경로 완료, 각 이동 종료의 서버/클라이언트 위치 일치 검사 통과. 이 사전 검사 당시에는 새 인증 전이라 unverified를 유지했다.
- 최종 실제 verify-clock: **63/63 통과**, 낙하 10초 사전 검사도 통과. 새 Java 확장·bridge·allow-flight 설정 fingerprint로 인증했다.
- 실제 audit-information: **통과, 148.19초**, 현재 관측·보행·원목 군집 채굴·드롭 회수 범위. 숨은 광석/용암 입력 쌍은 일치하고 이동은 각각 **18틱**, 목재 군집은 각각 **156틱·원목 2개 직접 획득·정지 인증/안정 경계 true**로 일치했다. 벽 개방 양성 대조도 통과했다. 무작위 드롭 좌표·사건/entity ID만 정규화하고 정책 상태·item/count·경로·중단 근거는 비교했다.
- 실제 맨손 수집: **2결정·162틱·직접 2개 획득**. 도끼 장착 포함: **3결정·103틱·직접 2개 획득**. 모두 goal_completed=true, paused/인증 true, actor 0, 진단 보상 2.0이다. 용암 위험에서 **1틱·observed_hazard·stable_boundary=false**를 확인했다.
- 진단 뒤 **기준 G1 snapshot reset/observe 일치·0틱·빈 인벤토리·체력 20**을 확인하고 서버를 종료했다. 진단 지형을 자연 task snapshot으로 저장하지 않았다. 최종 raw는 `artifacts/issue-5/final-4/`, 실행기/패킷 재현 검사는 `artifacts/issue-5/`에 보존한다.

### 실패와 해석·상태

샌드박스의 서버 소유권 잠금 차단은 권한 재실행과 구분했다. 최초 probe는 2개 중 1개만 회수(271틱)해 실패했고 수정했다. 해당 최초 JSONL은 두 번째 probe에 의해 교체됐으므로 도구 출력의 실패 요약을 별도 JSON으로 남겼고 이후 final-1~4 원시는 분리 보존했다. final-1은 시계 63회 통과 후 목재 감사/회수에 실패했다. 진단 위치 대조에서 client `[-239.5597,100,187.7220]`, server `[-240.5,100,186.5]`를 확인해 실제 이동 결함을 수정했다. final-2 사전 검사는 정상 이동을 unverified 때문에 실패로 판정한 실행기 조건을 보완했다. final-3은 서버 이동 통과 후 시계 37회 지점에서 낙하의 floating 자동 추방으로 중단됐으며 공통 설정을 수정하고 final-4에서 63회 전체를 다시 통과했다. 이전 클라이언트 보행 성공만으로 실제 서버 이동을 입증했다고 해석하지 않는다.

실제 원목은 관리자 진단용 배치다. 자연 C4/다이아 성공이나 학습·모델 성능 결과가 아니다. 실제 realtime 전환·제작/제련/하강/터널·7B/NanoJev/Jev/Astra·과금·PPO·본 학습·최종 평가·일반화는 미실행이며 PC 180시간의 충분성을 재확정하거나 증액하지 않았다. 다음 티켓은 #6/T05다. 보고서 작성 때문에 게임 검사를 추가 실행하지 않는다. `reports/issue-005-T04-report.pdf`, `reports/issue-005-T04-code-guide.pdf` 두 개를 로컬 전용으로 생성했다. 각각 A4 2쪽이며 한글 추출·모든 사용 글꼴 embedded/subset/Unicode mapping·전체 4페이지 가독성 검수가 통과했다. HTML/중간 파일은 /tmp에만 두고 PDF는 Git 추적·커밋에서 제외한다.

## 2026-11-04 — 리뷰 수정본 재검토 후 사망 경로 결함 수정

수정본 재검토(Standards/Spec)에서 이전 지적은 모두 해소됐고 새 결함 1건이 확인됐다. 거부된 이동 경로도 bridge가 1틱을 실행하므로 그 틱에 사망하면 `invalid=false`, `path=[]`인데 episode의 이동 근거 검사가 후보 경로를 기대해 사망을 `invalid_step`으로 바꿨다. 기대 경로를 `invalid` 또는 `reason=invalid_path`일 때 빈 경로로 판정하도록 고쳤다. 공개 CLI 회귀 `test_movement_death_during_rejected_path_tick_stays_terminal`이 수정 전 실패(invalid_step)·수정 후 통과함을 확인했다. 전체 pytest **55 passed**, mypy·diff 공백 검사 통과. Python 검사 한 줄만 바꿨고 bridge는 변경하지 않아 실제 Minecraft 재실행은 하지 않았다. 남은 판단 사항(이동 근거 검사의 episode/information 중복, MovementEvidence 필드 재선언)과 결정당 약 1.2초의 경계 확인 지연은 T19 예산 실측에서 다룬다.

## 2026-11-04 — 로컬 보고서 폴더 정리

사용자 요청으로 reports에는 #2/T01 최종본, #3/T02·#4/T03 최신 v2의 보고서/코드 가이드 PDF 한 쌍씩 총 6개만 유지한다. 나머지 이전 PDF·통합 리뷰 PDF·HTML·README·템플릿·CSS·patch는 삭제한다. 남긴 PDF는 내용 변경 없이 보존한다. 기존 보고서 보존·HTML 동봉 규칙은 이번 명시적 요청으로 대체하고 AGENTS를 갱신했다. reports를 .gitignore 및 Git 추적 제외 대상으로 변경하며 새 보고서·코드·게임 검사는 만들거나 실행하지 않는다. 기존 Git 이력은 재작성하지 않으며 commit/push는 수행하지 않는다.

## 2026-11-04 — T01–T03 로컬 리뷰 지적 재현·수정

사용자가 작업 폴더의 `code-review-2026-11-04.txt` 지적을 실제로 검증하고 맞으면 고치도록 요청했다. main `893ff27`에서 #1 본문·댓글(없음), #3/#4 본문·댓글(없음), PLAN §§4.1–4.3/5.2/12–14와 GLOSSARY를 대조했다. 시작 때 이미 존재한 PROGRESS/보고서 README/TEMPLATE 변경과 code-guide HTML/PDF, 원문 리뷰는 보존했다. 현재 수정은 미커밋·미푸시이며 새 PR·merge·GitHub 게시/이슈 변경은 수행하지 않았다. #2/#3/#4는 조회 시 이미 Closed였다.

### 재현과 구현

- 실제 Mineflayer 4.39.0의 error forwarding을 쓰고 네트워크 client만 대체한 주입 검사에서 stdout의 여러 줄 Error로 JSON 파싱 실패를 재현했다. logErrors=false로 끄고 연결 오류는 민감한 원문 없이 stderr에 남긴다.
- 인증 없는데 paused로 반환하는 경로를 수정했다. StepResult는 paused↔pause_verified 일치를 강제하며 미인증 실제 결과는 unverified다. summary에도 pause_verified를 남기고 에피소드 중 모드 불일치·오류를 마지막 정상 step으로 덮지 않는다. 실제 미인증 smoke는 exit 1이다.
- 기존 인증서가 매 결정의 실제 정지 확인을 대체하던 공백을 보완했다. reset·wait/이동 종료에서 입력 해제/클라이언트 물리 정지 후 양쪽 전체 상태 두 표본과 실제 틱의 불변을 확인한다. freeze 요청을 보냈으면 깊은 정지 응답도 검사한다. 변화·거부 시 인증 해제/backend_error다. 관리자 player 표본은 시계 검사에만 사용한다.
- 이동 summary의 movement_steps에 결정별 후보 ID·원본 obs·map·사건·path/stop 근거·이유·시간·거리·안정 경계를 남긴다. 잘못된 source_obs_id/map_version/path/stop_evidence와 빈 events가 성공 처리되던 다섯 변형을 공개 CLI에서 invalid_step으로 거부한다.
- 실제 backend 필요 오류는 exit 2/invalid_config를 유지하고 원인과 configs/minecraft.yaml을 안내한다. AGENTS의 잘못된 감사 설정 예시를 고쳤다. vec3 0.1.10 직접 의존성/lock 선언, 항상 참인 payload 검사 제거, 전체 bridge 로드로 물리 fixture의 함수 순서 의존성도 제거했다.
- 단순 중복 틱/안전 검사·과제/장면/권한 목록·63 상수·private RPC 호출은 현재 기능 불일치가 없어 구조를 유지했다. README에 uv PATH 설정이 이미 있으므로 영구 셸 변경은 하지 않았다. 전체 판정은 `docs/reviews/review-fixes-2026-11-04.md`, 선택 이유는 DECISIONS에 기록한다.

### 개발 검사

변경 전 pytest **38 passed(9.90초)**. Python 회귀 12개 RED→GREEN, Mineflayer 오류/경계 drift·freeze 거부 5개 RED+정상 대조 1개→모두 GREEN을 확인했다. 미인증→인증/인증→미인증의 두 다중 결정 회귀도 추가했다. 최종 전체 pytest **54 passed(13.78초)**, strict mypy **16개 파일 통과**, Node 문법·git diff --check·npm ls vec3 통과다. 기존 scripted 물리의 거리 상한·얼음 거부·실패 1틱 변위를 유지했다. 독립 읽기 전용 코드 검토에서 추가 구체적 결함은 없었고 검토자도 주입 시나리오/물리 fixture를 재실행했다. scripted 검사를 실제 정지 근거로 표시하지 않는다.

### 실제 Minecraft 재검증 (2026-11-04)

- sandbox 최초 smoke는 서버 디렉터리 flock 제한으로 backend_error였고, 권한 재실행과 별도로 보존했다. 실제 미인증 smoke는 **exit 1**, 2결정·40틱·14.30초, step/summary 모두 **unverified/false**, error=null이다. 새 코드와 다른 과거 인증을 재사용하지 않았다.
- 새 공개 verify-clock은 **exit 0, 63/63**, 63개 고유 조합·위험 장면 준비 63/63·양쪽 위치 최대 drift **0.0**, 다른 상태·사건·틱 불변이다. 새 코드/package-lock fingerprint로 실제 다시 인증했다.
- 인증 후 공개 smoke-episode는 **exit 0**, 2결정·40틱·14.19초, **paused/pause_verified=true**다. 실제 wait이며 원목 획득·학습 결과가 아니다.
- 공개 smoke-movement는 **exit 0**, **2결정·47틱·6.37928897648239블록·21.03초**, movement_completed=true, paused/인증 true다. 두 결정의 사건/원본 obs/map/이유/시간이 최종 movement_steps에 남았다. actor 0·보상 0·다이아 성공 false, 정상 decision_limit 절단이다.
- 공개 audit-information은 **exit 0, information_verified=true, 57.43초**다. 숨은 광석/용암 두 장면의 공개 입력 hash는 모두 `7c35ab78e49d07ccd3a42abb987471f493db1acb65147cddb88f554e4e4dc38d`이며 셀 1,161개·후보 8개다. 두 이동은 모두 **18틱·2.1548446042413616블록·path_completed·지도 버전 6·정지 인증/안정 경계 true**로 같다. 벽을 연 두 양성 대조도 통과했다.
- 진단 뒤 C4 기준 snapshot reset/observe 일치, 활성 틱 0·빈 인벤토리·체력 20을 확인하고 서버를 종료했다. 자연 snapshot을 덮어쓰지 않았다. 모든 시도/검사·복원 근거는 `artifacts/review-2026-11-04/`에 저장했다.

기존 같은 이동 17.63초 대비 이번 21.03초는 추가 경계 확인의 벽시계 비용을 포함한다. 활성 틱/거리는 같지만 처리량 보장은 아니며 본 학습 전 예산을 새로 실측해야 한다. 현재 180시간을 충분하다고 재확정하거나 늘리지 않는다. 모델·PPO·유료 API·본 학습·최종 평가·새 월드 일반화·자연 다이아 성공은 미실행/미검증이며 새 의존성 다운로드·결제는 없다.

후속 보고서는 `reports/issue-003-004-T02-T03-2026-11-04-review-fixes.{html,pdf}`다. A4 **3쪽**, 한글·핵심 수치 추출과 세 글꼴 embedded/subset/Unicode mapping을 확인하고 모든 페이지 이미지를 직접 읽었다. 잘림·깨짐·표 행 분리·외딴 문장 페이지가 없다. WeasyPrint fontTools fallback 경고는 출력/가독성 실패가 아니며 새 시스템 패키지는 설치하지 않았다. 현재 코드는 미커밋이므로 원격 링크는 고정 main의 수정 전 비교 위치임을 명시하고, 실제 변경본은 신규 fixture까지 포함한 동봉 `.patch`로 보존했다. patch SHA-256 `ed5117837573387b7739c18103c0e315b94d61b0e9a848e6d46cc082f5114a67`, `git apply --reverse --check` 통과다. 기존 보고서와 사용자 문서 변경을 보존했으며 최종 프로세스 목록에 Minecraft/Java 서버가 남아 있지 않다.

## 2026-11-03 — 보고서별 핵심 구현 코드 안내 추가

사용자 요청으로 이슈 #2/#3/#4의 기존 보고서 5개 각각에 핵심 변경·구현 → 파일·함수/클래스·시작 줄 → 확인할 로직 표와 권장 읽기 순서를 추가한 `-code-guide.{html,pdf}` 판본을 만들었다. 기존 HTML/PDF는 바이트까지 보존했다. 코드 링크는 원문 범위에 맞춰 각각 d809cd9 / 1312252 / 21a6359 / 0b92880 / ad2790b에 고정했다. 최신 main의 후속 기능을 과거 구현으로 혼동하지 않도록 기준을 명시했다. reports/README.md에 5개 추가본 링크와 작성 규칙을, TEMPLATE.html에 같은 코드 안내 항목을 반영했다.

검증: 코드 링크 **77개** 모두 로컬 Git에서 해당 커밋의 파일·시작 줄/정의를 확인했고 PDF의 URL annotation에도 남아 있음을 확인했다. 새 PDF는 각각 3/4/3/3/3쪽(총 16쪽)이다. 한글 추출·모든 글꼴 포함/subset/Unicode mapping 통과. 기존 본문 11쪽은 텍스트와 페이지 이미지가 원본과 같음을 비교했다(전체 쪽수 표시가 달라지는 푸터 제외). 추가 코드 안내 5쪽은 직접 이미지를 읽어 잘림·깨진 글자·표 행 분리·외딴 문장 페이지가 없음을 확인했다.

문서와 보고서만 변경했다. pytest/mypy·실제 Minecraft·모델·학습은 재실행하지 않았으며 기존 수치를 새 실행 결과로 표시하지 않았다. 현재 변경의 commit·push는 수행하지 않았다.

## 2026-11-03 — PR #29 수정본 실제 재검증 완료

수정 코드 `ad2790b`를 `origin/ticket-4`에 푸시했다. Standards의 P2 두 건을 재현·수정했고 수정본 독립 재검토는 남은 중대한 문제 없음, Spec도 남은 차단 지적 없음이다. GitHub 계정의 approve 리뷰로 표시하지 않는다.

- 수정본 공개 verify-clock은 **exit 0, 63/63 통과**다. backend/terrain 변경으로 무효화된 과거 인증을 사용하지 않고 새 코드 fingerprint로 실제 다시 검사했다.
- 공개 audit-information은 **exit 0, information_verified=true, 46.63초**다. 숨은 두 경우의 공개 셀 1,161개·후보 8개·입력 hash `7c35ab78e49d07ccd3a42abb987471f493db1acb65147cddb88f554e4e4dc38d`와 실행/중단 결과가 같다. 두 이동 모두 **18틱·2.1548446042413616블록·path_completed·정지 인증/안정 경계 true**다. 벽을 연 두 양성 대조에서 해당 광석/용암을 관측했다.
- 자연 지형 smoke-movement는 **exit 0, movement_completed=true, 2결정·47 활성 틱·6.37928897648239블록·17.63초**다. 두 step 모두 path_completed·pause_verified=true·stable_boundary=true. actor 0·보상 0·다이아 성공 false이며 decision_limit 절단이다.
- 마지막 C4 기준 reset 후 active_ticks=0·빈 인벤토리·체력 20·reset/observe 일치를 확인하고 서버를 종료했다. 수정본 검사 코드와 raw artifact는 기존 파일을 덮지 않고 `artifacts/issue-4/pr29/`의 `final-check-pr29.py`, `verify-clock.jsonl`, `audit-information.jsonl`, `smoke-movement.jsonl`, `restore.json`, `final-checks.json`에 저장했다.

최종 코드의 전체 pytest **38 passed(9.96초)**, strict mypy **16개 파일 통과**, Node 3개 파일 구문·공백 검사 통과다. 임시 검증 스크립트를 같은 이름으로 복사해 mypy의 Duplicate module 오류가 발생한 것은 검증 파일명을 `final-check-pr29.py`로 구분해 해결했고 재실행이 통과했다. 제품 설정/의존성은 바꾸지 않았다.

기존 보고서를 보존하고 검토·수정·새 실제 재검증과 Git 상태를 `reports/issue-004-T03-2026-11-03-v2.{html,pdf}`에 기록했다. A4 2쪽의 한글/수치 추출·모든 글꼴 포함/subset/Unicode mapping과 두 페이지 이미지를 직접 확인했으며 잘림·깨진 글자·표 분리·문장만 남은 페이지가 없다. 최종 기록을 같은 PR에 반영한다. PR #29는 Open이며 main 머지·이슈 #4 종료는 수행하지 않는다. 얼음류 보행은 실제 제동 교정 전까지 제외하며 채굴·제작·계단·터널·모델/API·학습은 미실행이다.

## 2026-11-03 — 이슈 #4 PR #29 생성·독립 검토 수정

구현·문서·원본 보고서 18개 파일을 `0b928808b6f5855b754219a23ca0a920d66dfc58`로 커밋하고 `origin/ticket-4`에 푸시했다. [PR #29](https://github.com/sion0507/Minecraft_RL/pull/29)를 생성했으며 원격 head 일치·base main `624b9c6`·MERGEABLE·Open, 원격 statusCheckRollup 비어 있음을 확인했다. PR 본문에 실제와 mock/scripted 검증을 구분하고 #4를 연결했다. main 머지·이슈 종료는 수행하지 않는다.

두 독립 검토자의 Standards/Spec 검토를 수행했다. Standards에서 P2 두 건을 재현했다. (1) 얼음 관성으로 이동 상한 16블록을 넘는 경우: ice/packed/frosted 16.8120, blue_ice 17.0373블록. 네 종류는 관측하되 제동 교정 전까지 support=false로 제외한다. (2) 무효 경로의 필수 1틱에서 실제 0.1블록 움직였지만 거리 0·stopped로 기록하는 경우: 중복 tick 처리를 합쳐 실제 변위를 기록한다.

설치된 Physics/PlayerState와 실제 Terrain 관측을 쓰는 scripted fixture에서 첫 상한 초과 RED, 수정 후 실패 tick 거리 RED를 차례로 확인한 뒤 전체 pytest **38 passed(9.96초)**·strict mypy **15개 파일**·Node 3개 파일 구문·diff 공백 검사를 통과했다. 이 fixture는 실제 서버 검증이 아니다. 돌/슬라임은 각각 15.3222/15.8764블록으로 상한 안이며 얼음 네 종류는 경로를 거부하고 실패 1틱의 변위는 실제 0.1블록과 일치한다.

수정본 재검토에서 Standards 두 건 해결·남은 중대한 문제 없음, Spec 남은 차단 지적 없음이다. 사용자 요청에 따라 수정 commit을 같은 PR에 푸시하고 실제 정지 인증·정보 감사·이동을 새 코드로 재검증한다. 이 문단 작성 시 실제 재검증은 진행 중이며 완료를 주장하지 않는다. 과거 보고서와 raw artifact는 보존한다.

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
