# 기반 도구 출처와 사용 범위

이슈 #2는 배포 패키지를 의존성으로 설치한다. 외부 데모 코드·프롬프트 파일을 복사·번역·변형하지 않았다. schema/RPC/실행기/모의 backend와 PTX 커널은 자체 구현이다.
모델·Minecraft/Carpet 바이너리는 아직 다운로드하거나 고정하지 않았으며 이후 실제 연결 티켓에서 출처·revision/hash·허용 근거를 기록한다.

|도구|고정 배포 버전 / revision|허용 근거·사용|
|---|---|---|
|[uv](https://github.com/astral-sh/uv)|0.12.23|[MIT/Apache-2.0](https://github.com/astral-sh/uv/blob/main/LICENSE-MIT), 공식 설치 binary; Git 제외|
|[Pydantic](https://github.com/pydantic/pydantic)|2.14.0|[MIT](https://github.com/pydantic/pydantic/blob/main/LICENSE), schema 검증|
|[PyYAML](https://github.com/yaml/pyyaml)|6.0.3|[MIT](https://github.com/yaml/pyyaml/blob/main/LICENSE), safe_load 설정 읽기|
|[pytest](https://github.com/pytest-dev/pytest)|9.1.1|[MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE), 공개 CLI 검사|
|[mypy](https://github.com/python/mypy)|1.20.2|[MIT](https://github.com/python/mypy/blob/master/LICENSE), 타입 검사|
|[types-PyYAML](https://github.com/python/typeshed)|6.0.12.20260906|Apache-2.0, YAML 타입 stub|
|[Hatchling](https://github.com/pypa/hatch)|1.32.4|MIT, Python 패키지 build backend; pyproject.toml에 고정|
|[Mineflayer](https://github.com/PrismarineJS/mineflayer)|4.39.0; npm gitHead `c168635cf2f6602069fc5e408bec864702335581`|[MIT](https://github.com/PrismarineJS/mineflayer/blob/c168635cf2f6602069fc5e408bec864702335581/LICENSE), 설치/import만, 실제 연결은 후속 작업|

Python의 정확한 전이 의존성·배포 URL·SHA-256은 uv.lock, Node 배포 URL·무결성 값은 bridge/package-lock.json을 기준으로 한다. 설치 패키지에 동봉된 라이선스를 보존하며 코드를 vendoring하지 않는다.
Python 전이 의존성은 pydantic-core/annotated-types/typing-inspection/iniconfig/librt/mypy_extensions/pluggy(MIT), typing_extensions(PSF-2.0), Pygments(BSD-2-Clause), packaging(Apache-2.0 OR BSD-2-Clause), pathspec(MPL-2.0)다. Hatchling의 격리 build에는 tomlkit 0.15.1, trove-classifiers 2026.9.21.13, editables 0.6(MIT)도 설치됐다. build backend 자체는 고정했으며 이 build 전이 의존성은 uv.lock 대상이 아니다.

## 실제 확인한 잔여 위험

2026-10-09 npm audit는 [uuid 버퍼 범위 검사 권고](https://github.com/advisories/GHSA-w5hq-g745-h8pq)의 영향을 uuid→yggdrasil/MSAL→prismarine-auth/minecraft-protocol→Mineflayer로 전파해 moderate 6건을 보고했다.
현재 설치 소스에서 yggdrasil과 MSAL은 uuid.v4를 호출한다. 해당 경로의 실제 인증/게임 연결은 미실행이며 안전을 인증했다고 해석하지 않는다.
자동 fix 제안은 Mineflayer 1.4.0으로 major downgrade하는 것이므로 적용하지 않았다. 호환 검증 없는 uuid major override도 하지 않았다. 실제 연결 티켓에서 사용 경로와 호환 수정 버전을 검토한다.
