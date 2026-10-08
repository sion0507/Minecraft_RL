## Agent skills

### Issue tracker

Issues and specs are tracked in GitHub Issues for `sion0507/Minecraft_RL`.
See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context layout: root `GLOSSARY.md` and `docs/adr/`.
See `docs/agents/domain.md`.

## 스택

- Python + uv: 모델 추론, PPO 학습, 평가, `mc-diamond` CLI.
- Node.js + Mineflayer: Minecraft 연결, 제한 관측, 후보·매크로 실행.
- Minecraft Java Edition 1.16.5, Survival/Peaceful; 서버·클라이언트 정지는 실제 검증한다.
- 계획기: `Qwen/Qwen2.5-7B-Instruct`, 초기 4비트 추론, 가중치 고정.
- 행동 모델: `C-Tianyu/NanoJev` (`unified-games-v1`); Choice 및 local/full 가치 헤드만 학습.
- J: OpenRouter alpha decisions API의 기존 Jev; 실제 ID·응답·과금을 확인해 고정.
- 기본 장비: RTX 5070 Ti 16GB, RAM 32GB. Python/Node/Java/CUDA 버전은 설치 때 확인한다.

## 설치·실행·검사 명령

현재 doctor·smoke-episode·pytest·mypy와 Python/Node 패키지 설정을 구현했다. 아래 후속 실험 명령은 각 기능 구현 후 사용한다.
설치·실행 계약은 `PLAN.md` §14, 검사 도구는 아래 개발 명령을 설정할 때 의존성을 명시한다.
모든 명령은 저장소 루트에서 실행한다.

```bash
uv sync
npm --prefix bridge ci
uv run mc-diamond doctor --config configs/pilot.yaml
uv run mc-diamond smoke-episode --config configs/pilot.yaml
uv run mc-diamond verify-clock --config configs/pilot.yaml
uv run mc-diamond audit-information --config configs/pilot.yaml
uv run mc-diamond smoke-macros --config configs/pilot.yaml
uv run mc-diamond smoke-planner --config configs/pilot.yaml
uv run mc-diamond smoke-model --config configs/pilot.yaml
uv run mc-diamond smoke-jev --config configs/pilot.yaml
uv run mc-diamond pilot-wood --config configs/pilot.yaml
uv run mc-diamond diagnose-g4 --phase pretrain --config configs/pilot.yaml
uv run mc-diamond benchmark --config configs/experiment.yaml
uv run mc-diamond budget --config configs/experiment.yaml
uv run mc-diamond freeze-experiment --config configs/experiment.yaml
uv run mc-diamond train --group B --train-seed 11 --lock configs/experiment_lock.json
uv run mc-diamond compare-checkpoints --lock configs/experiment_lock.json
uv run mc-diamond evaluate --groups A,B,J --task C4 --lock configs/experiment_lock.json
uv run mc-diamond evaluate --groups A,B --task G4 --lock configs/experiment_lock.json
uv run mc-diamond analyze --runs runs --output artifacts --lock configs/experiment_lock.json
uv run pytest
uv run mypy .
```

`pytest`/`mypy` 의존성은 pyproject.toml의 dev 그룹이다. 실행 불가·미실행은 그대로 보고한다.

## 폴더 구조

- 현재: 기준 문서, `PROGRESS.md`, `src/mc_diamond/`, `configs/pilot.yaml`, `fixtures/`, `tests/`, `bridge/` 패키지 설정.
- `CONTEXT.md`가 있으면 작업 맥락을 읽고, 관련 `docs/adr/`가 있으면 결정을 따른다.
- 예정 `configs/`: base/pilot/experiment/goals/curriculum 설정 및 `experiment_lock.json`.
- 예정 `bridge/`: JSONL RPC, world/reset, clock/pause, 제한 관측, 매크로.
- 예정 Python 패키지(경로 미정): schema/env/rpc, 목표·후보, 모델·selector, PPO, 평가·CLI.
- 예정 `prompts/`: 공통 계획기·행동 선택 프롬프트; `tests/`: 공개 실행 흐름 검증.
- 예정 `third_party/README.md`: 출처·revision·허용 근거·자체 구현/재사용 구분.
- 예정 `runs/`, `artifacts/`, `checkpoints/`, `worlds/`: 실행 산출물; 대용량은 Git 제외.
- 기존 구현이 생기면 역할에 대응시키고 위 이름으로 강제 재구성하지 않는다.

## 규칙

- 구현 전 [스펙 이슈 #1](https://github.com/sion0507/Minecraft_RL/issues/1)의 본문·댓글과 관련 `PLAN.md` 절을 읽는다.
- 용어는 `GLOSSARY.md`를 따른다. ADR과 충돌하면 번호·이유를 명시한다.
- 구현 선택은 `DECISIONS.md`, 실제 실행 결과·실패·다음 작업은 `PROGRESS.md`에 기록한다.
- 기존 사용자 파일·Git 이력을 보존하고 기존 도구·표준 라이브러리·허용된 의존성을 우선한다.
- 테스트는 공개 CLI의 reset→관측→목표→후보→선택→실행→보상→학습/평가→요약 흐름을 검증한다.
- 최소 모의 backend와 짧은 수치 예제를 사용하고, 실제 물리·모델·과금은 실제 진단으로 확인한다.
- A/B/J는 공통 관측·후보·실행·복구·시간 규칙을 사용한다. BC와 F/Astra는 이번 범위에서 제외한다.
- 본 학습은 B 1회, local/full 각 15,000결정이다. 필수 G4를 유지하고 추가 실험은 자동 실행하지 않는다.
- 본 학습 전 모델 revision/hash, snapshot, 난수, 설정, 시계·평가 방식과 예산을 lock에 고정한다.
- 정책·계획기·후보·경로·중단 판단은 같은 제한 관측을 사용한다. 숨은 광석/위험·시드·전체 청크·관리자 정보는 차단한다.
- 성공은 자연 다이아 광석의 적절한 도구 직접 파괴와 해당 드롭 획득으로 판정한다.
- RPC stdout은 JSONL 전용, 진단은 stderr다. 관리자 reset/freeze와 정책 step 권한을 분리한다.
- 후보는 최대 8개; 수집 당시 ID·내용·순서·마스크를 저장해 PPO에 사용한다.
- 단일 후보·무효·취소·fallback·critic-only 경험은 actor 학습에서 제외하고 시간·비용은 보존한다.
- 정지 실패는 먼저 수정한다. 실시간 대안은 본 학습 전 공통 검증·예산 확인 후 적용한다.
- 복구는 원자 저장한 에피소드 경계로 되돌린다. reset 게임과 중간 ledger를 섞지 않고 폐기 경험·시간·비용을 기록한다.
- 평가는 예정 슬롯 분모를 유지한다. 서버 오류만 같은 snapshot/RNG로 최대 1회 재시도하고 모든 시도를 기록한다.
- Jev 총 모델 API 비용은 실패·재시도 포함 US$5 이내다. 비밀키는 Git·문서·로그·lock에서 제외한다.
- 외부 코드·프롬프트는 명시적 허용 범위에서만 재사용하고 출처를 기록한다.
- 미실행·mock 결과를 실제 검증으로 표시하지 않는다. 고정 환경 적응과 새로운 월드 일반화를 구분한다.
