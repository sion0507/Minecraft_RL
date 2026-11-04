# 2026-11-04 T01–T03 리뷰 지적 검증

대상: `code-review-2026-11-04.txt`, main `893ff27` 위 미커밋 수정.
기준: GitHub #1 본문·댓글(댓글 없음), #3/#4 수락 기준, PLAN §§4.1–4.3/5.2/12–14, GLOSSARY.
기존 사용자 PROGRESS/보고서 변경과 원문 리뷰 파일은 보존한다. commit/push/merge/이슈 변경은 수행하지 않는다.

## 기능 지적

| 지적 | 검증 결과 | 처리 |
| --- | --- | --- |
| Mineflayer error가 stdout을 오염시킬 수 있음 | 맞음. 설치된 Mineflayer 4.39.0의 실제 createBot/error forwarding을 사용하고 네트워크 client만 EventEmitter로 대체해 재현. 기존 bridge의 stdout에 여러 줄 Error가 출력돼 JSON 파싱 실패 | logErrors=false. 민감한 오류 원문 없이 stderr에 연결 오류를 남김. 같은 주입 검사가 JSON 단일 출력으로 통과 |
| 미인증 step/summary가 paused로 표시됨 | 맞음. 기존 bridge의 wait/이동 결과는 인증 여부와 무관하게 paused. 외부 scripted RPC의 paused/false도 exit 0 | StepResult paused↔pause_verified 일치 강제, unverified 허용. bridge는 인증 없으면 unverified, EpisodeSummary에 pause_verified 보존. 실제 미인증 smoke는 exit 1 |
| 에피소드 끝의 한 값으로 앞의 미검증 상태를 숨길 수 있음 | 요약은 에피소드 전체 근거여야 함 | 여러 step 모드가 다르거나 오류가 나면 unverified/false. 미인증→인증/인증→미인증 두 순서의 CLI 검사 통과 |
| T03 이동 근거가 최종 summary에 없음 | 맞음. 기존 step JSONL에는 있으나 summary에는 없음 | movement_steps에 결정별 후보 ID·원본 관측 ID·지도 버전·사건·경로·중단 근거·이유·시간·거리·안정 경계 보존 |
| 이동 smoke가 사건·근거 연결을 검사하지 않음 | 맞음. 잘못된 source_obs_id/map_version/path/stop_evidence와 빈 events가 성공 처리됨 | 공개 CLI에서 다섯 변형이 각각 invalid_step/exit 1인지 RED→GREEN 확인. 정상 대조군도 통과 |
| T02 매 결정 경계의 실제 정지 확인이 인증서로 대체됨 | 맞음. 이전 advance의 서버 틱 비교는 실행 길이만 검사하며 양쪽 상태 정지 검사가 아님 | reset 및 wait/이동 종료에서 입력 해제/물리 중지 후 client/server의 두 전체 표본·실제 틱 불변 확인. 변화·freeze 거부 시 인증 해제 및 backend_error. 장기 인증서는 별도 유지 |
| freeze 명령 응답을 무시함 | 맞음. Carpet 1.4.44의 tick freeze deep은 toggle이므로 무조건 재송신하면 오히려 해제됨 | 필요한 경우에만 전송하고 깊은 정지 응답을 확인. 서버가 이미 frozen이면 상태 표본으로 검증 |
| audit-information의 실제 backend 필요 오류가 설정 파싱 오류로 바뀜 | 맞음. broad ValueError 처리에 들어가 원인이 사라짐 | exit 2/invalid_config는 설정과 명령의 불일치에 맞으므로 유지하고 메시지에 실제 backend 필요와 configs/minecraft.yaml을 명시. AGENTS 명령 예시도 수정 |
| uv가 PATH에 없으면 명령/검사가 안 됨 | 설치 전제이며 별도 코드 결함은 아님. README에 .tools/uv 설치와 PATH export가 이미 명시됨 | 영구 셸 설정은 변경하지 않음. 검증 명령에 PATH를 적용 |

## 구조 지적

| 지적 | 판단·처리 |
| --- | --- |
| episode/information 틱 회계 중복 | 실제 중복이나 현재 오동작은 없음. 서로 다른 공개 검사 경로의 신뢰 경계 검증을 유지 |
| Python/JS 보행 안전 규칙 중복 | 서로 다른 프로세스/언어 경계에서 후보 생성과 실행 전제조건을 각각 확인하는 구조. 제거하지 않음 |
| 과제 목록 반복 | 유지보수 지적은 유효하나 현재 목록/예산 불일치는 없음. 공통 설정 계층을 추가하지 않음 |
| 장면 목록 반복 | Python 진단과 Node 검증의 목록이 일치. 현재 결함 아님 |
| 63 숫자 반복 | 7장면×3지연×3회로 모두 일치. 현재 결함 아님 |
| 메서드 권한 목록 반복 | Python wire schema와 관리자/정책 권한 검증 역할이 다름. 허용 목록 불일치 없음 |
| private session._call 사용 | 내부 API 유지보수 지적. 현재 외부 코드 호환/권한 우회 결함은 확인되지 않음 |
| 물리 fixture의 소스 자르기 | 실제 순서 의존성이 있음. 새 경계 검사를 fixture에 연결하면서 전체 bridge를 VM에 로드하는 기존 방식으로 교체. 생산 코드에 테스트 전용 export를 추가하지 않음 |
| exactKeys({payload:…},['payload']) | 항상 참인 검사 맞음. 제거하고 실제 payload 객체 검사는 유지 |
| vec3 직접 의존성 누락 | 맞음. 현재 직접 require하는 설치본 0.1.10을 package.json/lock에 선언. 버전 변경/새 패키지 다운로드 없음 |

## 검증

- 변경 전 pytest: 38 passed, 9.90초.
- Python 공개 계약 회귀: 12 failed(필드 누락·잘못된 성공·오류 원인 은폐) → 12 passed.
- 실제 Mineflayer 오류/경계 상태 주입: 5 failed(stdout JSON 파싱·누락된 거부) + 정상 대조 1 passed → 6 passed.
- 물리 fixture까지 포함한 Node 관련 검사: 7 passed. stone/slime 거리 상한·얼음 거부·실패 1틱 실제 변위 유지.
- 전체 pytest: 최종 **54 passed, 13.78초**. 두 다중 결정 회귀를 포함한다.
- strict mypy: 16개 소스 파일 통과. Node 문법·git diff --check 통과. npm ls vec3는 직접 0.1.10을 정상 확인.
- 별도 읽기 전용 최종 코드 검토: 추가 구체적 결함 없음. 검토자는 주입 시나리오/물리 fixture도 재실행했다.
- 실제 미인증 smoke: exit 1, 2결정·40틱, unverified/false, 오류 없음. 과거 fingerprint 인증을 새 코드의 근거로 사용하지 않았다.
- sandbox 시도는 서버 디렉터리 flock 제한으로 backend_error. 권한 있는 실제 실행 결과와 분리해 보존한다.
- 실제 verify-clock: **exit 0, 63/63**, 위험 장면 준비 63/63, 양쪽 최대 위치 drift 0.0. 새 인증 저장.
- 인증 후 wait smoke: **exit 0**, 2결정·40틱·14.19초, paused/true.
- 실제 이동: **exit 0**, 2결정·47틱·6.37928897648239블록·21.03초. summary에 이동 근거 2개, paused/true.
- 실제 정보 감사: **exit 0**, information_verified=true, 57.43초. 숨은 두 장면의 입력 hash 동일, 양쪽 모두 18틱·2.1548446042413616블록 이동/안정 경계, 벽을 연 양성 대조 통과.
- 최종 C4 reset/observe 일치·활성 틱 0·빈 인벤토리·체력 20과 정상 종료 확인. raw/개발 검사/실패 시도/복원: `artifacts/review-2026-11-04/`.

물리/실제 게임 검증은 scripted 검사와 별개다. 모델·PPO·유료 API·본 학습·최종 평가·새 월드 실험은 수행하지 않는다.
