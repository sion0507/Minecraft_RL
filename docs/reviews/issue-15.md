# #15 / T14 독립 코드 리뷰

기준: 시작 commit `f48ccf117c6d4a3b12d67862d022f9bfd113f123` 대비 staged/working diff. 명세: GitHub #15 및 #1 본문·댓글, PLAN §§6.1–6.2, 7.1, 10, 11.3. `implement`가 요청한 `code-review`의 Standards/Spec을 서로 다른 에이전트가 읽기 전용으로 검토했다. 실제 게임/모델은 리뷰 때문에 재실행하지 않았다.

## Standards

최초 P2 2건:

1. 모델/PPO가 에피소드 중간에 실패하면 pre-start용 error_summary를 사용해 이미 수행한 결정·활성 틱·직접 획득·보상이 0으로 표시됐다. 압축 원시 trace의 완료 prefix를 스트림으로 복구하고 원래 오류와 미업데이트 pending 전이를 보존한다. 공개 CLI에서 초기 평가320결정 뒤 학습8결정/160틱/원목1 다음 모델 오류를 주입해 RED→GREEN으로 확인했다.
2. 선택적 모델 의존성 import 실패가 pilot_wood의 handler 진입 전에 발생했다. 기존 smoke-ppo와 같은 CLI import guard로 설치 안내 JSONL과 exit2를 제공한다. 다운로드 모델 import 경계 차단 검사 RED→GREEN으로 확인했다.

같은 Standards 리뷰어의 수정 재검토: 두 지적 해결, 새 material 지적 0.

## Spec

최초 P2 1건: 위 부분 에피소드 회계 누락(Standards와 중복). 같은 Spec 리뷰어가 수정 코드와 8결정/160틱/원목1 회귀를 다시 읽고 해결을 확인했다. 목표·독립 초기화·완전 rollout·선택 규칙·슬롯/재시도·복원에서 추가 material 지적은 없다.

최종: **Standards 미해결0 / Spec 미해결0**. 실제 실행 결과의 성공률이나 학습 개선을 판정한 리뷰가 아니다.

## 에피소드별 actor 집계 추가 점검

실제 로그를 점검하면서, 이번에 learner를 여러 에피소드에 재사용하므로 기존 run_episode가 누적 actor 수를 각 EpisodeSummary에도 반복 표시한다는 점을 발견했다. 공개 CLI에서32에피소드 요약의 합을 설정 합계1,024와 비교해 RED(16,896)를 재현했다. reset 전/후 기준 누적값을 잡고 종료 시 차이를 보고하도록 수정했다. 관련27검사/39.02초·strict mypy38파일 통과. 같은 Standards/Spec 리뷰어가 수정과 offline 집계 방법을 읽고 새 지적0/0을 확인했다. 후보·보상·전이·PPO 업데이트는 바꾸지 않는다.

이미 실행 중인 실제 프로세스는 이전 코드를 유지하므로 원시 EpisodeSummary.actor_transitions는 누적값이다. 이를 합산하지 않는다. 최종 실제 actor 수는 transition.actor_valid의 합과 setting.actor_transitions를 대조하며, /tmp/issue15-audit.py에서 검증해 artifacts/issue-15/offline-final-audit.json으로 남긴다. 실행 중인 원시 자료는 교체하거나 변조하지 않는다.
