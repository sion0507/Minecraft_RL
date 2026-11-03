# 기반 도구 출처와 사용 범위

이슈 #2는 배포 패키지를 의존성으로 설치한다. 외부 데모 코드·프롬프트 파일을 복사·번역·변형하지 않았다. schema/RPC/실행기/모의 backend와 PTX 커널은 자체 구현이다.
모델은 아직 다운로드하지 않았다. 이슈 #3에서 사용자 EULA 승인 후 Minecraft/Fabric/Carpet 공식 바이너리를 설치했다. 외부 게임 실행 코드·프롬프트를 복사하지 않았으며 Node 실행기·snapshot 처리·정지 진단·플레이어 정지 확장은 자체 구현이다.

이슈 #4의 voxel 광선·공개 지도 BFS·보행 제어·정보 fixture/감사도 자체 구현이다. 설치된 Mineflayer와 전이 의존성 `vec3`의 공개 API만 사용하며 외부 데모의 경로/코드/프롬프트는 복사하지 않는다. 새 패키지나 모델은 추가하지 않았고 정확한 배포 무결성은 기존 `bridge/package-lock.json`을 따른다. 시드·숨은 블록·전체 청크를 후보/경로에 제공하지 않는다.

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

자체 `bridge/pausemod/`는 외부 mixin 코드를 복사하지 않고 Carpet의 `TickSpeed`/확장 API와 Sponge Mixin 주입 API를 호출한다. Java 21.0.12.1의 javac `--release 8`로 빌드하고 배포 파일명·클래스명·zip timestamp를 고정한다. 현재 자체 jar SHA-256은 `169c35019242042f8e93c32a72d9b5d866d130f589234eae89d44d39e3bd5cbb`다. 1.16.5 외 버전에 대한 호환성은 주장하지 않는다.

Python의 정확한 전이 의존성·배포 URL·SHA-256은 uv.lock, Node 배포 URL·무결성 값은 bridge/package-lock.json을 기준으로 한다. 설치 패키지에 동봉된 라이선스를 보존하며 코드를 vendoring하지 않는다.
Python 전이 의존성은 pydantic-core/annotated-types/typing-inspection/iniconfig/librt/mypy_extensions/pluggy(MIT), typing_extensions(PSF-2.0), Pygments(BSD-2-Clause), packaging(Apache-2.0 OR BSD-2-Clause), pathspec(MPL-2.0)다. Hatchling의 격리 build에는 tomlkit 0.15.1, trove-classifiers 2026.9.21.13, editables 0.6(MIT)도 설치됐다. build backend 자체는 고정했으며 이 build 전이 의존성은 uv.lock 대상이 아니다.

## 실제 확인한 잔여 위험

2026-10-09 npm audit는 [uuid 버퍼 범위 검사 권고](https://github.com/advisories/GHSA-w5hq-g745-h8pq)의 영향을 uuid→yggdrasil/MSAL→prismarine-auth/minecraft-protocol→Mineflayer로 전파해 moderate 6건을 보고했다.
현재 설치 소스에서 yggdrasil과 MSAL은 uuid.v4를 호출한다. 이슈 #3은 loopback offline 접속만 검증했으며 해당 Microsoft/yggdrasil 인증 경로는 미실행이다. 이 경고를 해결했거나 온라인 인증의 안전을 확인했다고 해석하지 않는다. 이번 작업에서 npm audit를 재실행하지 않았다.
자동 fix 제안은 Mineflayer 1.4.0으로 major downgrade하는 것이므로 적용하지 않았다. 호환 검증 없는 uuid major override도 하지 않았다. 실제 연결 티켓에서 사용 경로와 호환 수정 버전을 검토한다.
