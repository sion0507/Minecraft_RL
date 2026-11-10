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
