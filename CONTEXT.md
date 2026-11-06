# T05(#6) 최종 보존 — 고정 자연 G2 직접철3 인수 미달

- 사용자 최신 지시: T05만 검증·PDF·커밋/푸시·이슈 절차까지 처리. 이전 push 금지는 이 요청으로 대체한다. 다른 티켓/T05A(#32) 구현은 하지 않는다. #6 고정 자연G2 직접철3 기준은 그대로여서 미달인 상태로 닫지 않는다. 이슈에 충족5항목과 미달G2를 보고한다.
- main, 기준2188120. 최신 구현을 커밋·푸시하는 단계다(최종 commit ID는git log -1 및원격ref 확인). PR/merge는추가하지않는다. 최종#6은Open유지, 후속티켓자동착수금지.
- 재개 후보 결함: final-3 G2에 도달155/미방문55 경로가 있는데 후보0이었다. 방향 대표 끝점을 고른 뒤 방문 끝점을 걸러 새 경로까지 잃었다. navigation.generate_movement_candidates가 미방문 끝점을 먼저 보존하도록 보완. 공개CLI 회귀RED→GREEN, 저장상태후보4개. 최종pytest78passed(18.72초)·strictmypy23·Node문법·diff통과.
- 최종 실제G2: artifacts/issue-6/g2-route-fix/ g2.jsonl/results.json.64결정·1778틱·446.39초·철0·decision_limit·서버오류없음·paused/인증true·CLIexit1. 돌곡괭이1제공, 방문155·철관측0·경로완료39·0후보wait25. 공개같은높이연결성분155칸의미방문0도확인. 전체월드/12000틱전체불가능성주장아님. C4reset/observe일치·0틱·빈재고·체력20·검사/서버종료확인. **남은인수조건은고정G2직접철3**.
- 보존근거 final-3/: 실제clock63/63(고유/준비63·상태동일·drift0), 정보26장면710.42초, 배치자원/빈재고 전체제작51결정/1702틱/413.17초. 원목4/조약돌11/철광석3직접획득·철괴3직접제련·철곡괭이1직접제작. 자연C4/모델성공이아니다. final-3 G2는수정전64/1687틱/철0기록으로분리한다.
- control-final/: 도구/연료부족각1틱invalid·위험1틱중단. 제공철괴3/막대2의제작준비장면에서취소40틱보존/actor제외/trace0→새선택3틱제작, 총43틱·선택요청2·실행1·목표완료. 전체realtime인증아님. C4reset/종료통과.
- bridge/clock/runtime는후보수정전후동일, 인증fingerprint6de2893387dc7971a1213cf939e056c07520edef6f6edfede0982b423e832804 유지. **시계63/정보26/전체제작재실행금지**. 기존실제감사공개32상태를새후보생성기로재생해저장후보ID/내용/순서/mask가32/32동일(candidate-replay.json). 새실제감사로표시하지않는다. 새G2manifest전체소스hash일치. 예전manifest의driver/navigation차이는문서화된변경이다.
- 최신통합재계산g2-route-fix/evidence-recomputed.json, G2상세동폴더g2-recomputed.json. 사전실패/중단/final-1화로timeout/final-2설정거부는PROGRESS/원시에보존한다. 보고서때문에게임재실행금지.
- 로컬reports/issue-006-T05-report.pdf와issue-006-T05-code-guide.pdf 두개만최신교체한다. /tmp/t05-reports.py(생성기),/tmp/t05-evidence.json(입력),/tmp/t05-recompute.py(재계산기) 사용.78검사·1778틱G2를반영한2쪽/3쪽PDF의추출/폰트포함을확인했다. 커밋/원격확인값으로Git메타를맞추고최종전페이지를렌더검수해링크공유한다. 모든중간물/tmp, reports는Git제외. 이작업때문에게임재실행금지.
- models/API/PPO/본학습/최종평가/일반화/전체realtime/자연C4다이아미실행. 일부사망/배치/제공출력/동시드롭경계는mock/scripted. PC180시간재확정·증액없음. 하강/터널/S/T05A속도개선을추가하지않는다.

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
