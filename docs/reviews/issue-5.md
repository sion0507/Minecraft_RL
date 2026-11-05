# 이슈 #5 / T04 검토

기준: 시작 시 깨끗한 main `e60493612125ea8803e533838acefc089005f818` 대비 이번 작업본의 추적/신규 파일. 명세는 GitHub #1 본문·댓글(없음), #5 본문·댓글(없음), PLAN §§4.1–4.3/5.2/5.4/12–14, AGENTS/GLOSSARY다. `implement`의 필수 `code-review`를 Standards/Spec 두 읽기 전용 독립 검토자로 수행했다. 검토 자체는 실제 게임 진단을 대신하지 않는다.

## Standards

중요 지적 1건: 취소 시 bridge가 항상 20틱을 기다리는데 원 후보의 max_ticks가 1–19틱이면 episode가 invalid_step으로 거부해 실제 시간·사건 집계를 잃는다. AGENTS/PLAN §4.1의 취소 시간/비용 보존에 어긋난다. 배포 bridge를 기존 harness로 로드한 max_ticks=1 사례에서 20틱 실행을 재현했다. 별도의 실질적인 코드 냄새는 없었으며 Python/Node의 신뢰 경계별 검증 중복은 유지한다.

수정: bridge의 취소 대기는 선택 상한/남은 예산 안으로 제한한다. max_ticks=5 회귀에서 20 != 5로 RED를 확인했고 수정 후 5틱·cancelled=true·invalid=false로 GREEN이다. `fixtures/wood_macros.cjs`를 기존 공개 pytest가 실행한다.

## Spec

검토 지적 2건:

1. **직접 획득 출처 오인**: 과거 채굴 좌표 또는 실패한 완료 요청의 좌표 근처에 생긴 외부 원목 드롭도 직접 획득으로 인식했다. 검토자가 배포 bridge의 실제 connect 이벤트 등록을 사용해 채굴 없이 공급한 원목 entity 70이 acquired로 반환되는 것을 재현했다. 파괴 요청과 실제 서버 블록 갱신을 구분하고, 요청 직후 2 활성 틱 내 단일 원목 드롭 생성·확인된 파괴·자기 playerCollect·인벤토리 증가를 연결하도록 수정했다. 오래된/실패한 표적은 acquired를 만들지 않으며 정상 대조 1건만 통과한다. 같은 배포 이벤트 연결을 사용하는 회귀를 남겼다. 이는 Minecraft 직접 파괴 출처 진단이며 자연 다이아 성공 판정은 후속 T07이다.
2. **긴 취소 대기 누락**: 원 매크로 max_ticks=400보다 긴 401틱 취소 대기를 거부해 summary active_ticks=0과 재선택 누락을 만들었다. 실행되지 않은 매크로 상한과 취소 대기를 분리했다. 에피소드/관측 ID, 실제 틱 연속성과 남은 예산은 계속 검사한다. 공개 CLI의 450틱 취소→20틱 재선택 회귀가 수정 전 invalid_step으로 RED, 수정 후 총 470틱·선택 요청 2·실행 결정 1·취소 1·reward 1·actor 제외·trace_mask=0으로 GREEN이다.

이 단계의 검토 지적은 모두 수정했고 전체 pytest **63 passed(15.74초)**, strict mypy **19개 파일 통과**, Node 문법 및 diff 공백 검사가 통과했다. 이후 실제 검증에서 추가로 발견한 결함과 최종 검사 결과는 아래 및 PROGRESS에 별도로 기록한다.

축별 원 지적 수: Standards 1건, Spec 2건. 취소 상한/시간 문제는 두 축에 걸친 같은 계약의 서로 다른 경계다. 새 검토 반복으로 수정 여부를 대신하지 않고 재현 회귀와 전체 검사 결과로 확인했다.

## 실제 게임 검증 중 발견한 서버 이동 결함

첫 시계 63회는 통과했지만 목재 감사와 회수가 실패했다. 자기 위치만 관리자 표본으로 대조한 `artifacts/issue-5/pickup-positions-debug.jsonl`에서 client `[-239.5597,100,187.7220]`, server `[-240.5,100,186.5]`를 확인했다. 기존 MovementPause가 틱 사이의 이동 패킷을 버렸고 과거 보행 성공은 서버 이동까지 증명하지 않았다. 진단용 출력 코드는 제거했다.

정지 중 패킷을 보관하는 첫 수정에 대해 새 Java 경계만 독립 검토했다. 2건(과거 look이 최신 position/look을 덮음, 과거 frozen 위치가 최신 active 위치를 덮음)을 실제 소스와 설치된 Minecraft/Carpet jar의 reflection 재현으로 확인했다. vanilla의 서버 스레드 인계 이후 수신을 직렬화하고 최신 필드 순서를 보존하며, active 수신 전 이전 pending을 처리하고 텔레포트 이전 pending/확인 전 이동은 비우도록 수정했다.

5개 assert 검사(정지 중 불변, 최신 방향, active 위치 순서, 텔레포트 초기화, 확인 전 오래된 이동 제외)가 통과했다. 소스/검사는 로컬 `artifacts/issue-5/MovementChecks.java`와 `movement-packet-checks.txt`에 보존한다. build.py 컴파일 성공과 실제 이동 종료의 서버/클라이언트 위치 0.001블록 일치도 확인한다. 위치 불일치를 거부하는 shipping bridge 회귀는 RED→GREEN이다. 드롭 대기 판단도 격자 중심 대신 실제 플레이어 위치를 사용하도록 공개 CLI 회귀 RED→GREEN으로 보완했다. 새 확장의 시계/정보 감사는 최종 fingerprint로 다시 실행한다.

최종 개발 검사: pytest **65 passed(16.32초)**, strict mypy **19개 파일 통과**, Node 문법·diff 공백 검사 통과. Java 패킷 경계 5개 assert도 통과했다. 이후 낙하 정지에서 vanilla floating 자동 추방이 재현돼 표준 `allow-flight=true`를 공통 서버 설정으로 고정하고 backend 시작 시 검사한다. 이 설정은 Survival 비행 능력을 부여하지 않으며 fingerprint에 포함한다.

최종 실제 검사: 서버 이동 위치 일치, verify-clock 63/63, audit-information(이동18틱/원목군집156틱 동일), 맨손162틱/장착103틱 직접 원목2개씩, 위험1틱 중단, G1 reset 모두 통과했다. 최종 원시는 artifacts/issue-5/final-4/다.
