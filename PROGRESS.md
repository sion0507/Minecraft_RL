# 실행 기록

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
