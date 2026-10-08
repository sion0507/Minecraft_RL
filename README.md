# Minecraft 행동 선택 강화학습

고정된 Minecraft 환경에서 NanoJev 행동 선택 정책의 추가 강화학습 효과와 기존 Jev의 조건부 대체 성능을 비교하는 학부 연구 프로젝트입니다.
고정된 7B 계획기가 하위 목표를 정하고, 공통 코드가 최대 8개 매크로 후보를 생성하면 행동 모델이 하나를 선택합니다.
목표는 자연 생성 다이아몬드 광석을 적절한 도구로 직접 파괴하고 해당 드롭을 획득하는 것입니다.

## 현재 상태

연구 방향과 스펙은 확정되었으며, 현재 저장소에는 문서만 있습니다.
구현 코드·패키지 설정·테스트·CLI는 아직 없고, 설치·API 접근·학습 효과·실험 결과는 미검증입니다.

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

아래는 패키지와 CLI 구현 후 사용할 명령입니다. 현재 바로 실행 가능한 설치 안내는 아닙니다.

```bash
uv sync
npm --prefix bridge ci
uv run mc-diamond doctor --config configs/pilot.yaml
```

시계·정보 경계·모델·학습 연결 진단 및 예산 확인 후 실험 설정을 고정합니다.
전체 실행 계약은 [PLAN.md §14](PLAN.md#14-구현-후-사용할-명령), pytest·타입체크 예정 명령은 [AGENTS.md](AGENTS.md)에 있습니다.

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
