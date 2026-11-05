# Minecraft 행동 선택 강화학습

고정된 Minecraft 환경에서 NanoJev 행동 선택 정책의 추가 강화학습 효과와 기존 Jev의 조건부 대체 성능을 비교하는 학부 연구 프로젝트입니다.
고정된 7B 계획기가 하위 목표를 정하고, 공통 코드가 최대 8개 매크로 후보를 생성하면 행동 모델이 하나를 선택합니다.
별도 규칙 기반 행동 선택기 S는 동일 최종 7B 아래 공통 후보를 선택하며 C4 결정적 1회로 진단합니다.
핵심 참조 시스템 F는 계획기를 Astra로 바꾸고 J와 동일한 Jev를 사용해, 작은 로컬 모델과 RL 조합이 강력한 전체 시스템에 얼마나 접근하는지 비교합니다.
목표는 자연 생성 다이아몬드 광석을 적절한 도구로 직접 파괴하고 해당 드롭을 획득하는 것입니다.

## 현재 상태

이슈 #2의 공통 실행 흐름, #3의 실제 Minecraft reset·정지, #4의 제한 관측·보행에 이어 #5의 목재 후보·장착·채굴·드롭 회수와 `smoke-macros`를 구현했습니다.
현재 실제 backend는 자기 상태, 직접 보인 표면·공기/방문 기억, 관측 원목·직접 파괴와 연결된 드롭, wait와 같은 높이의 보행을 제공합니다. 제작·제련·계단·터널·모델/API·PPO는 후속 작업입니다. 실제 검사와 실패 기록은 [PROGRESS.md](PROGRESS.md)에 있습니다.

## 실험 범위

| 비교군 | 계획기 | 행동 정책 |
| --- | --- | --- |
| A | 고정 Qwen2.5-7B-Instruct | 공개 초기 NanoJev |
| B | A와 같은 계획기 | A와 동일 초기화에서 PPO로 추가 학습한 NanoJev |
| J | A와 같은 계획기 | 프로젝트 내 추가 학습 없는 기존 Jev |
| F | 고정 Astra | J와 동일한 기존 Jev/설정 |
| S (필수 진단) | A/B/J와 동일 최종 7B | 고정 규칙 기반 행동 선택기 |

월드 시드 하나와 과제별 고정 시작 상태를 사용합니다. B 본 학습은 한 번, local/full 각각 15,000결정입니다.
기본 최종 평가는 기존 C4 17회+F 5회+필수 G4 6회=28회입니다. 사전 축소는 A/B/J/F 주 평가를 모두 각 3회로 조정해 총 20회이며 G4 6회를 유지합니다. 별도 S C4 1회를 포함하면 총 29회/축소 21회이며 핵심/G4/S 결과와 분모를 구분합니다. S 학습이나 G4는 추가하지 않으며 1회로 통계적 우월성·일반적인 신경망 대체 가능성을 주장하지 않습니다. BC는 제외합니다.
A↔B는 행동 PPO 효과, B↔J는 동일 7B에서 모델 비교, J↔F는 동일 Jev에서 계획기 비교, B↔F는 전체 시스템 비교입니다. B↔F를 RL 하나의 인과적 효과로 해석하지 않습니다.
7B 가중치 고정과 로컬 지식 조회 우선을 유지합니다. 진단·지식/입력/검증/재계획 보완·공통 Astra 비교 후에도 중대한 계획 병목이 확인되고 [PLAN.md §5.6](PLAN.md#56-7b-계획기-추가-학습--최후의-조건부-대안)의 여섯 조건을 모두 충족해야만 학습을 별도 제안합니다. 분석·비용 보고와 명시적 사용자 승인 후 PPO 전에 완료·검증하고 A/B/J/S 최종 7B를 동일하게 고정합니다. 자동 학습 단계는 없습니다.
결과는 고정 환경 적응으로 해석하며, 새로운 월드 일반화의 근거로 삼지 않습니다.

## 연구 동기와 한계

실제 로봇에서는 연산량이 큰 상위 목표 계획을 클라우드 등 외부 연산 자원에서 수행하고, 상대적으로 작은 행동 선택 정책을 로봇 내부에서 실행하는 계층적 구조를 고려할 수 있다. 이러한 구조에서는 행동 선택 모델의 크기와 계산 비용이 중요한 설계 요소가 된다. 본 연구는 이와 관련된 동기에서 소형 행동 선택 정책의 추가 강화학습 효과와 규칙 기반 선택기 및 외부 모델과의 수행 차이를 조사한다.

이는 응용 가능성과 후속 연구 방향이며 이번 프로젝트의 실증 결론이 아니다. 실제 로봇이나 온디바이스 배포를 검증하지 않는다. 현재 7B 계획기는 로컬에서 실행하므로 클라우드-로봇 분산 구조를 구현·검증했다고 주장하지 않는다. NanoJev의 CPU 실시간 추론 가능성이나 특정 로봇 하드웨어 성능을 입증하지 않으며, NanoJev는 저수준 모터 제어기가 아닌 매크로 행동 후보를 선택하는 고수준 정책이다. CPU 추론 벤치마크·네트워크 지연 실험·실제 로봇 테스트·클라우드 API로의 계획기 이전·온디바이스 최적화 실험은 추가하지 않는다.

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
uv run mc-diamond smoke-macros --config configs/pilot.yaml
uv run pytest
uv run mypy .
```

`doctor`는 실제 도구·연산 결과를 stdout JSONL로, 부재·오류 설명을 stderr로 내보냅니다. 검사가 모두 사용 가능하면 0, 부재·오류가 있으면 1을 반환합니다.
GPU 검사는 CUDA 드라이버 API로 직접 작은 산술 커널을 실행합니다. `nvcc` 부재와 GPU 연산 실패를 별도로 표시합니다. 제한된 샌드박스에서는 GPU 접근 실패가 실제 장비 상태와 다를 수 있습니다.

`smoke-episode`는 제공된 모의 fixture를 subprocess backend로 실행하고 reset→관측→고정 목표→후보→선택→실행→진단 보상→요약을 출력합니다.
모의 보상은 획득 사건 수이고, 실제 local/full 보상·PPO·다이아 성공 판정의 검증이 아닙니다. 정상 종료/유효 절단은 0, backend 오류/무효 경험은 1, 설정 오류는 2입니다.
실제 backend는 설정의 `backend: rpc`와 `command`로 같은 실행 경로에 연결하고 `fixture`는 제거합니다. 제공하는 설정은 `configs/minecraft.yaml`입니다.

RPC backend는 `--admin-fd <fd>`로 전달받은 파이프에서 reset·snapshot 준비·시계/정보 fixture 진단만, stdin에서 observe/step만 받습니다. 두 채널의 응답은 request_id에 맞춰 stdout JSONL로 반환하고 진단은 stderr에 기록합니다.
요청은 `request_id/method/payload`, 응답은 `request_id`와 정확히 하나의 `result/error`를 가지며 현재 호출은 직렬입니다.
자료형과 허용 필드는 [schema.py](src/mc_diamond/schema.py)에 있습니다. 결과·후보 ID·원본 관측·mask와 episode/attempt ID를 로그에 보존합니다.
알 수 없는 관측 필드와 RPC 결과는 오류로 종료하고 원본 오류 입력을 로그에 출력하지 않습니다.

시계·정보 경계·모델·학습 연결 진단 및 예산 확인 후 실험 설정을 고정합니다.
아래 실제 Minecraft 검사 외의 후속 실험 명령은 아직 구현되지 않았습니다. 전체 실행 계약은 [PLAN.md §14](PLAN.md#14-구현-후-사용할-명령), 개발 지침은 [AGENTS.md](AGENTS.md)에 있습니다.

## 실제 Minecraft 실행

이 작업공간에는 사용자의 EULA 동의 후 Minecraft 1.16.5, Fabric Loader 0.16.14, Carpet 1.4.44를 `worlds/server/`에 설치했습니다. Java 21.0.12.1·Node 24.20.0·Mineflayer 4.39.0에서 실제 연결을 확인했습니다. Linux의 `flock`으로 서버 디렉터리 사용을 잠급니다. 출처와 정확한 해시는 `third_party/README.md` 및 로컬 `worlds/server/installation.json`에 있습니다.

서버는 `127.0.0.1:25565`에서만 열리며 로컬 봇은 `auth: offline`을 사용합니다. 계정 로그인·비밀번호·토큰은 사용하지 않습니다. Microsoft 계정 인증이나 공개 서버 운영을 검증한 결과가 아닙니다.

`worlds/server/server.properties`의 `allow-flight=true`가 필요합니다. 정지된 공중 상태를 서버의 벽시계 기반 비행 추방으로 오인하지 않게 하는 설정이며 Survival 플레이어에게 비행 능력을 지급하지 않습니다. backend는 누락 시 시작을 거부하고, 이 값도 시계 fingerprint에 포함합니다.

Carpet freeze만으로는 침수 중 플레이어 산소가 계속 줄었습니다. 자체 확장 `bridge/pausemod/`는 Carpet의 활성 틱 조건에 맞춰 플레이어 tick·이동을 멈추고, 초기 로그인 상태 패킷은 별도로 보냅니다. 설치된 Fabric 서버 라이브러리로 빌드합니다.

```bash
python3 bridge/pausemod/build.py
```

최초 snapshot이 없는 새 설치에서만 `uv run mc-diamond prepare-world --config configs/minecraft.yaml`을 실행합니다. 기존 snapshot 덮어쓰기는 거부합니다. 이 작업공간은 C4/G1–G4를 이미 준비했습니다. 단일 자연 월드의 시드와 지상 spawn을 광석 조사 전에 정했고, G2/G3/G4의 도구 지급과 G4의 고정 지하 준비 공간은 관리자 준비로 기록했습니다. 월드·snapshot·실행 산출물은 Git에서 제외합니다.

```bash
uv run mc-diamond verify-clock --config configs/minecraft.yaml
uv run mc-diamond smoke-episode --config configs/minecraft.yaml
uv run mc-diamond smoke-movement --config configs/minecraft.yaml
uv run mc-diamond smoke-macros --config configs/macros.yaml
uv run mc-diamond audit-information --config configs/minecraft.yaml
```

각 명령이 서버를 시작하고 종료합니다. `verify-clock`은 평지·제련·드롭·용암·낙하·침수·화염에서 0/5/10초를 각각 3회 검사합니다. 실제 위험 상태가 준비됐는지, 위치 오차 0.001블록과 다른 상태·사건·틱이 보존되는지 판정합니다. 전부 통과한 실행만 검증 기록을 원자 저장하며, 코드·게임 의존성·Java/Node 버전·서버 설정·snapshot hash가 바뀌면 다시 검사합니다. 모의 backend를 실제 정지 근거로 사용하지 않습니다.

인증서와 별개로 reset 및 매 행동의 결정 경계에서 입력을 해제하고 서버·클라이언트 상태와 틱의 불변을 다시 확인합니다. 이동 종료에서는 양쪽 플레이어 위치도 0.001블록 이내로 일치해야 합니다. 정지 중 받은 최신 이동·방향 패킷은 서버 스레드에서 보관하고 다음 활성 틱에 vanilla 검증을 거쳐 적용합니다. 패킷의 순서를 보존하고 텔레포트 전 요청은 비우며, 정지 중에는 위치를 바꾸지 않습니다. 상태가 바뀌거나 서버 위치가 따라오지 못하면 backend 오류로 중단합니다. 인증이 없는 step과 summary는 `clock_mode=unverified`, `pause_verified=false`이며 실제 smoke는 exit 1입니다. 63회 검증과 경계 확인을 통과한 실행만 `paused`로 표시합니다.

`smoke-episode`는 초기 실행 연결 진단입니다. 실제 목재 수집은 `smoke-macros`를 사용합니다. 활성 틱과 실제 경과 시간을 분리하고, 지원하지 않는 행동의 실패도 실제 한 틱을 실행해 기록합니다.

`smoke-macros`는 고정 목재 목표에서 현재 노출 원목의 대상·작업량 후보와 관측 지도 접근 경로를 최대 8개 제공합니다. 원목을 보지 못하면 관측한 같은 높이의 길에서 탐색하고, 직접 확인한 드롭을 먼저 회수합니다. 보유 도끼 장착, 선택한 노출 군집 최대 8블록/400틱 채굴, wait 20/100/200틱을 지원합니다. 채굴 완료 패킷은 Mineflayer의 벽시계 타이머 대신 실제 활성 틱에 맞춰 보내고, 서버 블록 갱신·드롭 생성·자기 수집·인벤토리 증가를 연결합니다. 매 기본 조작에서 관측을 갱신하고 위험·파손·실패·시간·사망에서 멈춥니다.

첫 후보를 실행하는 진단이며 행동 모델 성능이나 PPO 결과가 아닙니다. 후보 ID·내용·순서·mask, 단일 후보의 확률 1, 모든 결정의 `macro_steps`를 기록하고 actor 전이는 0입니다. 0후보는 실제 wait와 failed 사건을 남깁니다. 선택 무효화는 원 후보·선택·대기 사건/비용과 actor 제외·trace_mask=0을 보존하고 새 관측에서 재선택합니다. 선택 요청 수와 실행 결정 수를 구분하고 중복 사건 ID는 오류로 거부합니다. 목표의 직접 획득과 보유량이 충족돼야 exit 0이며 미인증 정지는 exit 1입니다.

자연 G1과 분리한 실제 매크로 회귀는 `uv run mc-diamond smoke-macros --config configs/macros.yaml --diagnostic-fixture wood`로 실행합니다. `wood_tool`은 도끼 장착, `wood_break`는 마지막 내구도, `wood_hazard`는 채굴 뒤 노출되는 용암, `wood_drop`은 직접 채굴한 드롭의 독립 대기, `empty`는 0후보를 준비합니다. 관리자 준비이며 `diagnostic_fixture` 사건에 `natural_task=false`와 준비 활성 틱을 기록합니다. `wood_drop`의 드롭 이동·초기 속도/획득 지연 설정도 진단 준비에만 적용합니다. 실패/위험 장면의 exit 1은 수집 성공과 구분합니다.

전체 재현 명령은 `uv run python tools/verify_t04.py --output artifacts/t04-new`입니다. 새 폴더에 명령·코드 hash·stdout/stderr·결과를 보존하고, 시계 63조건 → 확장 정보 감사 → 실제 공개 CLI → 실제 상태 진전으로 유도한 취소·재선택을 확인합니다. 취소 검사는 전체 realtime 운용 인증이 아닙니다. 성공·실패 모두 기준 G1 reset을 시도하고 복원 실패도 기록합니다. 개별 검사는 끝에 `clock`, `information`, `macros`를 붙이며, 정보 감사 전에 같은 코드의 시계 인증이 필요합니다. 보고서 작성만을 위해 이 명령을 재실행하지 않습니다.

`smoke-movement`는 같은 실행기에서 관측된 바닥·발/머리 공간만 연결해 최대 8개 경로를 만들고 첫 후보를 실행합니다. 같은 높이에서 최대 16블록/400 활성 틱이며, 위험·공개 경로 변경·진행 정체에서 멈춥니다. 얼음·꽁꽁 언 얼음·살얼음·푸른 얼음은 관측하되 제동 거리 검증 전에는 보행 지면으로 사용하지 않습니다. 후보 경로, 원본 관측 ID, 지도 버전, 중단 근거, 실제 이동 거리/틱/경과 시간과 안정 경계를 출력합니다. 최소 한 번의 안정된 경로 완료가 있어야 exit 0이며, 이는 행동 모델의 성능 검증이 아닙니다.

최종 summary의 `movement_steps`에도 후보 ID·원본 관측 ID·지도 버전·사건·경로·중단 근거·이유·실제 틱·경과 시간·거리·안정 경계를 결정별로 보존합니다. smoke는 후보/결과의 근거 연결과 사건 출처를 검사하며 누락·불일치는 `invalid_step`입니다.

`audit-information`은 관리자 채널에서 벽 뒤 광석/용암의 실제 장면을 준비합니다. 정책은 일반 observe/step으로만 접속하며 노출 전 관측·후보·경로·실행/중단 결과가 같아야 합니다. 벽을 연 양성 대조, 보이는 원목 군집 채굴·드롭 회수, 독립 도끼 장착·20/100/200틱 대기·드롭 대기·0후보를 검사합니다. 드롭의 무작위 흩어짐 좌표/사건 ID를 제외하고 종류·수량·정책 상태·경로·중단 근거를 비교하며, 대기/장착 사건이 없는 응답도 거부합니다. 이 장면의 원목은 관리자 진단용 배치이며 자연 C4 성공이 아닙니다. 원본 snapshot을 보존하고 진단 후 reset으로 기준 월드를 복원합니다. 실제 정지 인증이 없으면 감사가 통과하지 않습니다. 제작·하강·터널 감사는 후속 티켓입니다.

지형 관측은 눈에서 반경 8블록의 셀 중심으로 광선을 보내 처음 만나는 충돌 표면/위험에서 끊습니다. 지나간 공기·비충돌 식물과 첫 표면만 기억하고 미로딩 셀은 막힌 것으로 취급합니다. 유리·부분 충돌 블록을 보수적으로 가리개로 취급하며 숨은 이웃의 모양·청크 전체·시드·관리자 로그를 경로 판단에 쓰지 않습니다. `hidden_hazard_peek=false`를 기록하며 reset은 지도·방문·최근 결과를 초기화합니다.

수동으로 서버만 열 때는 실험 CLI를 종료한 뒤 아래 명령을 사용합니다. 확장 모드는 기동 시 정지 상태로 시작하며, 콘솔의 `stop`으로 저장·종료합니다.

```bash
cd worlds/server
flock -n .mc-diamond-owner java -Xms512M -Xmx3G -jar fabric-server-launch.jar nogui
```

## 문서

| 문서 | 내용 |
| --- | --- |
| [스펙 이슈 #1](https://github.com/sion0507/Minecraft_RL/issues/1) / [PRD.md](PRD.md) | 확정된 구현 스펙과 테스트 경계 |
| reports/ (로컬 전용) | 티켓별 최신 보고서·코드 가이드 PDF 한 쌍, Git 제외 |
| [PLAN.md](PLAN.md) | 상세 실험 규격과 구현 순서 |
| [DECISIONS.md](DECISIONS.md) | 확정한 결정과 근거 |
| [GLOSSARY.md](GLOSSARY.md) | 도메인 용어 |
| [AGENTS.md](AGENTS.md) | 에이전트 작업 규칙과 예정 명령·폴더 구조 |

## 저장소 관리

API 키·로컬 환경값은 Git·문서·로그·실험 lock에 넣지 않습니다. Jev 모델 API 비용 상한은 J/F·진단·실패·재시도 포함 총 US$5입니다.
F 접근·추가 시간·GPU/PC 점유·Astra 별도 비용을 본 학습 전에 우선 확인합니다. S 규칙은 본 학습 전 lock에서 고정하고 B/J/F 결과를 보고 조정하지 않습니다. S 선택 연산·7B 계획 호출·GPU/PC 점유·실행 비용도 사전 예산에 포함합니다. 기존 180시간은 재산정 기준이며 충분성은 미확인입니다. Astra 지출 상한도 아직 미승인입니다. F 불가 시 미실행과 관련 연구 질문 미검증을 남깁니다. 이번 문서 수정은 학습·유료 호출·결제 실행 승인이 아닙니다.
[.gitignore](.gitignore)는 비밀 파일, 가상환경·캐시, 다운로드 모델·게임 바이너리, 월드·체크포인트·실험 산출물을 제외합니다.
설정·실험 lock·의존성 lockfile은 비밀값을 제거한 뒤 버전 관리합니다.
외부 코드·프롬프트는 명시적 허용 범위에서만 재사용하고 출처와 변경점을 기록합니다.
