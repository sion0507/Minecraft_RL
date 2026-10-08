# Minecraft 행동 선택 강화학습

고정된 Minecraft 환경에서 NanoJev 행동 선택 정책의 추가 강화학습 효과와 기존 Jev의 조건부 대체 성능을 비교하는 학부 연구 프로젝트입니다.
고정된 7B 계획기가 하위 목표를 정하고, 공통 코드가 최대 8개 매크로 후보를 생성하면 행동 모델이 하나를 선택합니다.
목표는 자연 생성 다이아몬드 광석을 적절한 도구로 직접 파괴하고 해당 드롭을 획득하는 것입니다.

## 현재 상태

연구 방향과 스펙은 확정되었으며, 이슈 #2의 환경 진단·공통 자료형·JSONL RPC·모의 에피소드·pytest/mypy를 구현했습니다.
실제 Minecraft 연결·정지·모델/API·PPO·학습 효과·실험 결과는 미검증입니다. 실행 결과와 남은 작업은 [PROGRESS.md](PROGRESS.md)에 기록합니다.

## 실험 범위

| 비교군 | 계획기 | 행동 정책 |
| --- | --- | --- |
| A | 고정 Qwen2.5-7B-Instruct | 공개 초기 NanoJev |
| B | A와 같은 계획기 | A와 동일 초기화에서 PPO로 추가 학습한 NanoJev |
| J | A와 같은 계획기 | 프로젝트 내 추가 학습 없는 기존 Jev |

월드 시드 하나와 과제별 고정 시작 상태를 사용합니다. B 본 학습은 한 번, local/full 각각 15,000결정입니다.
기본 최종 평가는 C4 전체 과제 17회와 필수 G4 탐색·직접 채굴 진단 6회입니다. BC와 F/Astra는 이번 범위에서 제외합니다.
결과는 고정 환경 적응으로 해석하며, 새로운 월드 일반화의 근거로 삼지 않습니다.

## 예정 스택과 실행

- Minecraft Java Edition 1.16.5, Survival/Peaceful.
- Python + uv: 모델·PPO·평가·`mc-diamond` CLI.
- Node.js + Mineflayer: 게임 연결·제한 관측·매크로 실행.
- `Qwen/Qwen2.5-7B-Instruct` 고정 계획기, `C-Tianyu/NanoJev` Choice 및 local/full 가치 헤드 학습.
- 기본 장비: RTX 5070 Ti 16GB, RAM 32GB.

Python 3.12 이상과 Node 22 이상이 필요합니다. `uv`를 설치하고 아래 명령을 저장소 루트에서 실행합니다.
이번 작업공간에는 `uv`를 `.tools/uv`에 설치했으므로 `export PATH="$PWD/.tools:$PATH"`로 사용할 수 있습니다.

```bash
uv sync
npm --prefix bridge ci
uv run mc-diamond doctor --config configs/pilot.yaml
uv run mc-diamond smoke-episode --config configs/pilot.yaml
uv run pytest
uv run mypy .
```

`doctor`는 실제 도구·연산 결과를 stdout JSONL로, 부재·오류 설명을 stderr로 내보냅니다. 검사가 모두 사용 가능하면 0, 부재·오류가 있으면 1을 반환합니다.
GPU 검사는 CUDA 드라이버 API로 직접 작은 산술 커널을 실행합니다. `nvcc` 부재와 GPU 연산 실패를 별도로 표시합니다. 제한된 샌드박스에서는 GPU 접근 실패가 실제 장비 상태와 다를 수 있습니다.

`smoke-episode`는 제공된 모의 fixture를 subprocess backend로 실행하고 reset→관측→고정 목표→후보→선택→실행→진단 보상→요약을 출력합니다.
모의 보상은 획득 사건 수이고, 실제 local/full 보상·PPO·다이아 성공 판정의 검증이 아닙니다. 정상 종료/유효 절단은 0, backend 오류/무효 경험은 1, 설정 오류는 2입니다.
실제 backend는 설정의 `backend: rpc`와 `command`로 같은 실행 경로에 연결할 수 있으며 `fixture`는 제거합니다. 현재 실제 게임 backend는 제공하지 않습니다.

RPC backend는 `--admin-fd <fd>`로 전달받은 파이프에서 reset만, stdin에서 observe/step만 받아야 합니다. 두 채널의 응답은 request_id에 맞춰 stdout JSONL로 반환하고 진단은 stderr에 기록합니다.
요청은 `request_id/method/payload`, 응답은 `request_id`와 정확히 하나의 `result/error`를 가지며 현재 호출은 직렬입니다.
자료형과 허용 필드는 [schema.py](src/mc_diamond/schema.py)에 있습니다. 결과·후보 ID·원본 관측·mask와 episode/attempt ID를 로그에 보존합니다.
알 수 없는 관측 필드와 RPC 결과는 오류로 종료하고 원본 오류 입력을 로그에 출력하지 않습니다.

시계·정보 경계·모델·학습 연결 진단 및 예산 확인 후 실험 설정을 고정합니다.
후속 명령은 아직 구현되지 않았습니다. 전체 실행 계약은 [PLAN.md §14](PLAN.md#14-구현-후-사용할-명령), 개발 지침은 [AGENTS.md](AGENTS.md)에 있습니다.

## 문서

| 문서 | 내용 |
| --- | --- |
| [스펙 이슈 #1](https://github.com/sion0507/Minecraft_RL/issues/1) / [PRD.md](PRD.md) | 확정된 구현 스펙과 테스트 경계 |
| [PLAN.md](PLAN.md) | 상세 실험 규격과 구현 순서 |
| [DECISIONS.md](DECISIONS.md) | 확정한 결정과 근거 |
| [GLOSSARY.md](GLOSSARY.md) | 도메인 용어 |
| [AGENTS.md](AGENTS.md) | 에이전트 작업 규칙과 예정 명령·폴더 구조 |

## 저장소 관리

API 키·로컬 환경값은 Git·문서·로그·실험 lock에 넣지 않습니다. Jev 모델 API 비용 상한은 실패·재시도 포함 총 US$5입니다.
[.gitignore](.gitignore)는 비밀 파일, 가상환경·캐시, 다운로드 모델·게임 바이너리, 월드·체크포인트·실험 산출물을 제외합니다.
설정·실험 lock·의존성 lockfile은 비밀값을 제거한 뒤 버전 관리합니다.
외부 코드·프롬프트는 명시적 허용 범위에서만 재사용하고 출처와 변경점을 기록합니다.
