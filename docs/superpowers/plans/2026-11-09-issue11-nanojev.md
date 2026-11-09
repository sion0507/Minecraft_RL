# T10 NanoJev Implementation Plan

**Goal:** #11의 공개 초기 Choice 선택·독립 critic·실제 gradient/복원 검증을 이 worktree에서 완료한다.
**Spec:** GitHub #11 본문/댓글, #1 본문/댓글, PLAN §§4.2, 5.2–5.4, 6.1–6.3, 12–14. #5는 Closed 확인.
**Architecture:** 공개 immutable bundle의 구조/가중치를 엄격하게 로드한다. backbone EOS 표현만 no_grad로 추출하고 공개 Choice를 재계산한다. local/full critic은 masked candidate mean→256/GELU→scalar다. 정책 입력은 검증된 Observation/Goal/CandidateSet에서만 만든다.
**Tech stack:** 기존 Python CLI/RPC + optional PyTorch/Transformers/Safetensors/Hub. 게임 bridge 수정 없음.

사용자는 이 세션에서 구현·실행 검증을 요청했고 공개 다운로드/의존성을 승인했다. 설계 선택은 위 명세 안에서 수행한다. main/다른 세션 수정·유료 API·본 학습·push/merge/이슈 종료는 수행하지 않는다.

## Scope and checks

1. 공통 입력 직렬화와 ID/순서/mask: `src/mc_diamond/model_input.py`, `prompts/action_selector.txt`, `tests/test_model.py`. 알려진 정보만 전달하고 stale 후보·전부 mask·빈 집합·중복 ID는 거부한다. 경로 초과는 조용히 자르지 않는다.
2. 모델 adapter: `src/mc_diamond/nanojev.py`, `pyproject.toml`, `uv.lock`. 공개 norm/scalar/set attention 보존, backbone frozen/no_grad/dropout 0. 저장 특징 재사용 시 Choice는 매번 재계산. sampling seed·argmax·독립 critic·단일 후보 actor 제외·저장/복원 수치 검사. 먼저 실패하는 테스트를 작성·실행한다.
3. 공개 `smoke-model`: `cli.py`, `schema.py`, `model_smoke.py`, 설정·테스트. 실제 모델과 mock 게임을 분리한다. 초기 public forward/tokenization/pooling/logits 대조, 실제 gradient/optimizer update/hash/유한 손실/복원 증거를 남기고 기존 reset→관측→목표→후보→선택→실행→보상→요약을 사용한다. dependency 없는 기존 CLI 동작을 보존한다.
4. `README.md`, `third_party/README.md`, `DECISIONS.md`, `PROGRESS.md`, `CONTEXT.md`에 사용 허용·revision/file hashes·실제/mock/미실행 상태 기록. 전체 pytest/mypy와 실제 smoke-model 실행. 로컬 `reports/`에는 한국어 PDF 두 개만 두고 한글 추출·폰트 포함·모든 페이지 가독성 확인.

## Review focus

- mask 후보가 set attention/critic/sampling에 영향을 주지 않아야 한다.
- 단일 유효 후보는 확률 1, actor loss 제외이며 critic 갱신은 가능해야 한다.
- inference_mode 특징을 학습 경로에 재사용하지 않는다. dropout은 train() 이후에도 0, backbone gradient/hash는 불변이어야 한다.
- public weights가 일부 빠지거나 파일 hash가 다르면 임의 초기화로 계속하지 않는다.
- 관리자/숨은 정보·ID 기반 우회·silent truncation이 없어야 한다.

## Execution ledger

- 조사: clean linked worktree `feat/issue-11-nanojev`, base e839a8e. #11 Open/no comments, #5 Closed 2026-11-05, #1 본문과 댓글 확인. ADR 없음. GPU는 샌드박스 밖에서 RTX5070Ti/16GB 확인.
- 공개 tag: 047b927b30882a1138fc504821b82ac145a4b81a. 모델카드는 인증 없는 배포와 MIT source / upstream Qwen license를 설명한다. predict는 inference_mode, EOS pooling + attention Choice 구조다.
- 완료: 입력/모델/CLI/테스트 구현. 공통 행동 기준은 별도 prompt 파일 대신 `model_input.INSTRUCTIONS` 하나로 두었다(패키지 설치 후에도 같은 입력 유지).
- 검증: pytest211, 모델 검사8, strict mypy src/tests28파일, 실제 CUDA sampling/argmax exit0. source forward와 FP32/BF16 tokenization/EOS pooling/logits 오차0. 단일 후보 pilot은 의도한 exit1. 독립 read-only 코드 리뷰 필수 지적0.
- 문서/로컬 PDF 완료: 한국어 보고서2쪽·코드 가이드3쪽, 한글 추출·모든 폰트 포함·5페이지 직접 렌더 검수. Git commit/push/merge/issue close 없음. 보고서 때문에 게임 재실행 없음.
- 후속 사용자 승인: 두 축 code-review Standards0/Spec0 확인 뒤 commit/push/PR/원격 main 병합/#11 종료 요청. 앞의 Git 미수행은 검증 시점 이력이다. 실제 완료 상태는 원격 조회·#11 완료 기록·최신 로컬 PDF에 남긴다. main checkout은 그대로 둔다.
