# T04 리뷰 지적 보완·재검토

기준은 main `9f9aca543703791be538240b841ca32690188dfa` 대비 이번 수정본이다. 사용자가 handoff 항목별 검증 뒤 확인된 부분의 수정을 요청했다. GitHub #1/#5 본문·댓글(없음), PLAN 관련 절, AGENTS/GLOSSARY를 대조했다. 원 handoff는 `/tmp/claude-1000/-home-sion-Documents-projects-RL-projects-Minecraft-learning/6f9e7446-9fec-48f0-a0fe-f0f54984bd34/scratchpad/t04-review-handoff.md`다.

|항목|최종 조치·판정|
|---|---|
|S1 경계 규칙 중복|후보 생성/실행의 각 신뢰 경계 검증을 유지한다. 외부 공유 설정 계층은 추가하지 않는다.|
|S2 근거/반환 중복|episode 공통 근거 검사와 MacroEvidence 구성 1회, Node stepResult로 공통 반환. 이동 고유 검증은 유지.|
|S3 이름|woodMacro→executeMacro, MovementEvidence→MacroEvidence. JSON 필드 계약은 유지.|
|S4 죽은 분기|중복 wait 분기 제거. 미지원 행동의 1틱 실행·invalid·사망 처리는 공통 실행기에 유지.|
|S5 위조 stop_rule_id|일반 정책 문자열로 짧은 취소 대기/failed 사건을 만들지 못한다. 내부 취소와 저장 후보 집합을 사용하는 실패 처리를 분리.|
|A1 실제 실행 범위|공개 CLI의 관리자 진단 장면을 명시하고 추적 가능한 tools/verify_t04.py로 실행. 자연 G1 사전 검사의 나무 미발견도 별도 실패로 보존.|
|A2 감사 누락|기존 이동/군집/회수에 독립 장착·20/100/200 대기·드롭 대기·0후보 숨은 쌍을 추가. 실제 사건 종류도 필수 검증.|
|A3 취소|실제 게임 상태 진전 20틱+취소 대기 20틱 뒤 재선택을 공통 episode로 검증. 450틱은 외부 wire mock 회귀이며 전체 realtime 운용은 범위 밖.|
|A4 actor 제외|단일 확률 1·actor=false 계약을 유지하고 reward 로그에 제외 이유를 명시.|
|C1 취소 시간|기존 취소 표시·원 후보 보존·실제 시간 집계를 유지. 실패 명령의 최소 실제 1틱을 0틱으로 바꾸지 않는다.|
|C2 임의 대기|잔여 예산과 우연히 같은 350틱도 거부. 정상 20/100/200·마지막 7틱 절단·내부 5틱 취소 회귀.|
|B1 정지 확장|입증된 실제 서버 이동 수정은 유지하고 최종 bridge fingerprint로 시계 63조건 재검증.|
|B2 allow-flight|공통 환경 호환 설정·fingerprint 규칙 유지. Survival 비행 권한/물리는 변경하지 않는다.|
|B3 오래된 선택|같은 epoch는 취소 대기·재선택, 다른 epoch 거부를 유지.|
|B4 계획 문서|기존 저장소의 계획·검토 기록 관례를 유지.|
|E1 완료 틱 사건 유실|중단 이유와 독립적으로 air 갱신을 확인해 mined/confirmed 보존. 위험·파손·사망 주입 및 실제 위험/파손 검사.|

## Standards

독립 검토에서 새 감사의 빈 wait/equip 사건을 놓치는 문제 1건을 발견했다. 사건 누락 주입이 감사에 통과하는 RED를 재현하고 expected wait/equipped 사건을 필수로 검사해 GREEN을 확인했다. S1의 경계 검증은 유지하고 S2–S5/C2/E1 수정은 적절하다고 판단했다. 수정본 재검토의 남은 지적은 **0건**이다.

## Spec

독립 검토에서 새 재현 실행기의 일부 실행/실패 경로에 기준 reset이 없는 문제 1건을 발견했다. 전체 checks finally로 복원·실패 기록을 옮겼고 실패한 clock 검사 뒤 reset을 확인하는 mock 회귀가 통과했다. 숨은 쌍 감사와 별도 실제 취소의 범위 문구도 분리했다. 수정본 재검토의 남은 지적은 **0건**이다.

공통 episode가 0후보 failed를 만들기 전에 실제 wait 사건이 있는지도 추가 RED→GREEN으로 확인했다. 드롭 장면의 준비 활성 틱 집계를 보완했고, 진행 중이던 인증은 중단·복원하여 해당 실행을 성공으로 세지 않는다. 최종 개발/실제 검사와 raw 위치는 PROGRESS에 기록한다. 검토의 지적 0건은 모든 월드/모든 실패에 대한 무결함 보장이 아니다.

## 최종 실제 근거

사용자 continue 뒤 소스와 전체 실행 지문 일치를 확인해 final-2의 시계63/63 인증을 유지했다. resume-1의 확장 정보 감사18장면은494.08초·exit0이다. 공개 CLI 맨손81틱/장착103틱/실제파손51틱/드롭wait40틱은 각각 직접1개 획득·exit0, 위험72틱과0후보240틱은 예상 목표미완료·exit1이다. 모든 결과는 paused/인증true다. 실제 상태 진전과 취소 대기40틱을 원 선택에 보존하고 trace_mask=0 뒤 재선택해 총121틱에 목표를 완료했다. 기준G1 reset·검사/서버 종료도 확인했다. 원시에서 틱 합계·선택·예상 실패·소스hash를 다시 검사한 결과는 `artifacts/issue-5-review-2026-11-05/resume-1/evidence-recomputed.json`이다.

코드 변경 없이 중지 전68 pytest/mypy20파일과 Standards/Spec 각0건을 유지했다. 실제 사망은 mock 주입만 검사했고 전체 realtime 운영은 인증하지 않았다. 중단 시도·미인증 사전 검사·자연G1 나무미발견을 이 최종 관리자 진단 성공과 분리한다. 새 모델/API/연구 실험은 없다.
