# 기반 도구 출처와 사용 범위

이슈 #2는 배포 패키지를 의존성으로 설치한다. 외부 데모 코드·프롬프트 파일을 복사·번역·변형하지 않았다. schema/RPC/실행기/모의 backend와 PTX 커널은 자체 구현이다.
모델의 현재 다운로드·검증 상태는 아래 T10 절을 따른다. 이슈 #3에서 사용자 EULA 승인 후 Minecraft/Fabric/Carpet 공식 바이너리를 설치했다. 외부 게임 실행 코드·프롬프트를 복사하지 않았으며 Node 실행기·snapshot 처리·정지 진단·플레이어 정지 확장은 자체 구현이다.

## T10 공개 NanoJev 연결 (2026-11-09, #11)

- 배포: [C-Tianyu/NanoJev unified-games-v1](https://huggingface.co/C-Tianyu/NanoJev/tree/047b927b30882a1138fc504821b82ac145a4b81a), immutable revision `047b927b30882a1138fc504821b82ac145a4b81a`.
- 초기 모델은 루트의 공개 step-400 `best.safetensors`다. 이 프로젝트의 A/B 초기값이며 upstream의 `training_initialization/` 가중치와 혼동하지 않는다. SHA-256 `f68c47d66998231b86b7e91b4ed5e82ae23acf104c8b7cd6d165c3ac7b7ffe1b`, 2,385,039,280 bytes.
- 모델카드는 인증 없는 공개 다운로드와 source MIT / Qwen 원본 라이선스 유지를 명시한다. 새 사용 약관 동의·계정 로그인·키·결제 없이 공개 파일만 받았다. 배포 전체를 별도 MIT 라이선스로 재명명하지 않는다.
- 기반: [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B), 원본 revision `c1899de289a04d12100db370d81485cdf75e47ca`, Apache-2.0. 기반 모델을 다시 다운로드하거나 학습하지 않았다.
- 허용된 재사용: 같은 immutable bundle의 `source/scripts/train_toy_decisions.py`의 Choice(norm/scalar/set attention)와 EOS pooling, `predict_toy_decisions.py`의 segmented tokenization을 `src/mc_diamond/nanojev.py`에 필요한 Choice 경로만 수정·적용했다. `third_party/nanojev-LICENSE.txt`에 MIT 저작권·허용문 전문을 보존한다.
- 변경: backbone no_grad/frozen, dropout 0, 외부 mask, 독립 local/full critic, seed sampling/argmax·ID 매핑·head 저장/복원·엄격한 hash 검사. Boolean/Score·게임 데모·프롬프트·학습 파이프라인을 복사하지 않았다. `model_input.py`의 공통 게임 요약/행동 기준과 `model_smoke.py`의 진단은 자체 구현이다.
- 공개 원본 두 Python 파일은 `checkpoints/`에 그대로 두고, hash 확인 후 진단 oracle로만 실행한다. `trust_remote_code=False`, 모든 모델/토크나이저 로드는 local_files_only다. 실제 공개 forward와 tokenization·pooling·logits를 FP32/BF16 양쪽에서 비교했으며 결과는 PROGRESS의 T10 절을 따른다. 추론용 predict의 inference_mode를 학습에 쓰지 않는다.
- source forward SHA-256 `4f39babd5575e43d7acf3eca357329a93c60041f334bc2bd7424929bf9c0da86`, predictor `6eedc49aaf9a81763677e3cff4e87fc4e499bfc5decf0bb4678f452f578dd92b`, tokenizer.json `be75606093db2094d7cd20f3c2f385c212750648bd6ea4fb2bf507a6a4c55506`. 사용한 9개 파일의 고정 SHA-256은 `nanojev.FILES`와 실행 `model_loaded`에 모두 보존한다.
- 모델 extra: PyTorch 2.14.0(BSD-3-Clause), Transformers 5.17.0·Safetensors 0.8.0·Hugging Face Hub 1.33.0(Apache-2.0). 정확한 전이 의존성·wheel hash는 `uv.lock`이다. 공개 bundle과 다른 구형 버전으로 시작한 설치는 실행 진단 전에 위 버전으로 교체했다. 새 시스템 패키지/sudo는 사용하지 않았다.

이슈 #4의 voxel 광선·공개 지도 BFS·보행 제어·정보 fixture/감사도 자체 구현이다. 설치된 Mineflayer와 전이 의존성 `vec3`의 공개 API만 사용하며 외부 데모의 경로/코드/프롬프트는 복사하지 않는다. 새 패키지나 모델은 추가하지 않았고 정확한 배포 무결성은 기존 `bridge/package-lock.json`을 따른다. 시드·숨은 블록·전체 청크를 후보/경로에 제공하지 않는다.

이슈 #5의 목재 후보·장착·활성 틱 채굴·드롭 회수·취소 집계는 자체 구현이다. 설치된 Mineflayer 4.39.0의 digging.js를 읽어 digTime과 1.16.5 block_dig 시작/완료/취소의 연결을 확인했다. 기본 dig의 벽시계 완료/낙관적 블록 제거를 재사용하지 않고, 해당 설치 의존성이 제공하는 클라이언트 전송 API와 실제 서버 블록 갱신을 사용한다. 외부 데모 코드를 복사하지 않았고 게임 의존성은 추가하지 않았다. 보고서 작성에는 기존 로컬 캐시의 ReportLab 5.0.1과 시스템 WenQuanYi Zen Hei 글꼴을 사용하며 프로젝트 런타임/lock에는 넣지 않는다.

|도구|고정 배포 버전 / revision|허용 근거·사용|
|---|---|---|
|[uv](https://github.com/astral-sh/uv)|0.12.23|[MIT/Apache-2.0](https://github.com/astral-sh/uv/blob/main/LICENSE-MIT), 공식 설치 binary; Git 제외|
|[Pydantic](https://github.com/pydantic/pydantic)|2.14.0|[MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE), schema 검증|
|[PyYAML](https://github.com/yaml/pyyaml)|6.0.3|[MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE), safe_load 설정 읽기|
|[pytest](https://github.com/pytest-dev/pytest)|9.1.1|[MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE), 공개 CLI 검사|
|[mypy](https://github.com/python/mypy)|1.20.2|[MIT](https://github.com/python/mypy/blob/master/LICENSE), 타입 검사|
|[types-PyYAML](https://github.com/python/typeshed)|6.0.12.20260906|Apache-2.0, YAML 타입 stub|
|[Hatchling](https://github.com/pypa/hatch)|1.32.4|MIT, Python 패키지 build backend; pyproject.toml에 고정|
|[Mineflayer](https://github.com/PrismarineJS/mineflayer)|4.39.0; npm gitHead `c168635cf2f6602069fc5e408bec864702335581`|[MIT](https://github.com/PrismarineJS/mineflayer/blob/c168635cf2f6602069fc5e408bec864702335581/LICENSE), 로컬 offline 실제 연결·자기 상태·wait·물리 중지|
|[Minecraft Java 서버](https://www.minecraft.net/en-us/download/server)|1.16.5, 공식 SHA-1 `1b557e7b033b583cd9f66746b7a9ab1ec1673ced`|[Minecraft EULA](https://www.minecraft.net/en-us/eula), 2026-11-02 사용자 명시적 동의 후 로컬 설치; 바이너리·월드는 Git 제외|
|[Fabric Loader](https://github.com/FabricMC/fabric-loader)|0.16.14|[Apache-2.0](https://github.com/FabricMC/fabric-loader/blob/0.16.14/LICENSE), 공식 Maven 배포 의존성|
|[Fabric installer/server launcher](https://meta.fabricmc.net/v2/versions/loader/1.16.5/0.16.14/1.1.1/server/jar)|1.1.1|[Apache-2.0](https://github.com/FabricMC/fabric-installer/blob/master/LICENSE), 공식 launcher API 다운로드; Git 제외|
|[Carpet](https://github.com/gnembon/fabric-carpet/releases/tag/1.4.44)|`fabric-carpet-1.16.5-1.4.44+v210714.jar`|[MIT](https://github.com/gnembon/fabric-carpet/blob/1.16.5/LICENSE), 공식 release의 1.16.5 jar; freeze/step 및 공개 확장 API 사용|
|[Sponge Mixin (Fabric build)](https://github.com/FabricMC/Mixin)|0.15.5+mixin.0.8.7|배포 jar의 LICENSE.txt(MIT)를 보존하고 주입 API를 사용한다. Fabric이 설치한 라이브러리이며 별도 의존성 추가 없음|
|[WeasyPrint](https://github.com/Kozea/WeasyPrint)|70.0|배포 wheel의 BSD-3-Clause 라이선스를 확인. reports/ HTML→PDF 변환용 별도 uv 도구 캐시이며 게임 실행 의존성에는 추가하지 않음|
|[Yarn mappings](https://maven.fabricmc.net/net/fabricmc/yarn/1.16.5%2Bbuild.10/yarn-1.16.5%2Bbuild.10-v2.jar)|1.16.5+build.10|[CC0-1.0](https://github.com/FabricMC/yarn/blob/1.16.5/LICENSE), 1.16.5 intermediary 메서드 식별 참조; 소스 복사 없음|

Minecraft 공식 server jar와 Fabric이 실제로 받은 `.fabric/server/1.16.5-server.jar` 모두 위 SHA-1과 일치한다. SHA-256은 Minecraft jar `58f329c7d2696526f948470aa6fd0b45545039b64cb75015e64c12194b373da6`, Fabric launcher `0aae5206659acfa2f7639a2bf4d0c500f516efb181bdc2bfca70af10e5c78c59`, Carpet jar `480e4afe497bab4c9a43637d159e3f8b395ea767af725ec714f0ecfeaee63625`다. 실제 설치한 16개 jar의 전체 SHA-256은 로컬 `worlds/server/installation.json`에 보존한다.

자체 `bridge/pausemod/`는 외부 mixin 코드를 복사하지 않고 Carpet의 `TickSpeed`/확장 API와 Sponge Mixin 주입 API를 호출한다. Java 21.0.12.1의 javac `--release 8`로 빌드하고 배포 파일명·클래스명·zip timestamp를 고정한다. T04에서 정지 중 이동 패킷 보관과 활성 틱 적용을 보완했다. dirty chunk 순회에는 Carpet 내부 mixin 인터페이스 `carpet.fakes.ThreadedAnvilChunkStorageInterface`를 호출하며 복사하지 않는다. 서버 틱 대기 시각은 자체 accessor로 설정한다. T05A에서 설치된 1.16.5 jar의 메서드/실행 순서를 javap로 확인해 관리자 step의 서버 실행 큐 전달과 틱 종료 확인 패킷을 자체 구현했다. 늦은 dirty block/metadata·인벤토리와 드롭 위치는 기존 vanilla watcher 전송 API와 accessor/invoker로 동기화하며 tracker 주기를 추가하지 않는다. 같은 클라이언트 연결의 nonce 확인은 선행 이동 핸들러와 동일 실행기에 예약해 입력을 틱보다 먼저 반영한다. 외부 소스 복사·새 의존성은 없다. T05A jar SHA-256은 `27fe07bcbbbc100dbcbc4114d08426a66a50007ed1e243d5b722c81bebaa71a6`이다. 1.16.5 외 버전에 대한 호환성은 주장하지 않는다.

Python의 정확한 전이 의존성·배포 URL·SHA-256은 uv.lock, Node 배포 URL·무결성 값은 bridge/package-lock.json을 기준으로 한다. 설치 패키지에 동봉된 라이선스를 보존하며 코드를 vendoring하지 않는다.
Python 전이 의존성은 pydantic-core/annotated-types/typing-inspection/iniconfig/librt/mypy_extensions/pluggy(MIT), typing_extensions(PSF-2.0), Pygments(BSD-2-Clause), packaging(Apache-2.0 OR BSD-2-Clause), pathspec(MPL-2.0)다. Hatchling의 격리 build에는 tomlkit 0.15.1, trove-classifiers 2026.9.21.13, editables 0.6(MIT)도 설치됐다. build backend 자체는 고정했으며 이 build 전이 의존성은 uv.lock 대상이 아니다.

이슈 #6의 소규모 레시피 허용 목록·전제조건 해석·제작/설치/화로 실행과 직접 사건 연결도 자체 구현이다. Minecraft 1.16.5의 설치된 minecraft-data/prismarine-recipe 자료와 Mineflayer craft/furnace/place/inventory API를 확인해 연결했다. 레시피 전체 데이터나 외부 데모 코드·프롬프트는 복사하지 않았으며 새 게임 의존성·모델을 추가하지 않는다. `recipes.json`은 두 실행 언어가 공유하는 자체 허용 목록이다.

## 실제 확인한 잔여 위험

2026-10-09 npm audit는 [uuid 버퍼 범위 검사 권고](https://github.com/advisories/GHSA-w5hq-g745-h8pq)의 영향을 uuid→yggdrasil/MSAL→prismarine-auth/minecraft-protocol→Mineflayer로 전파해 moderate 6건을 보고했다.
현재 설치 소스에서 yggdrasil과 MSAL은 uuid.v4를 호출한다. 이슈 #3은 loopback offline 접속만 검증했으며 해당 Microsoft/yggdrasil 인증 경로는 미실행이다. 이 경고를 해결했거나 온라인 인증의 안전을 확인했다고 해석하지 않는다. 이번 작업에서 npm audit를 재실행하지 않았다.
자동 fix 제안은 Mineflayer 1.4.0으로 major downgrade하는 것이므로 적용하지 않았다. 호환 검증 없는 uuid major override도 하지 않았다. 실제 연결 티켓에서 사용 경로와 호환 수정 버전을 검토한다.
