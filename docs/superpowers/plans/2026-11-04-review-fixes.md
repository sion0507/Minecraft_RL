# T01–T03 리뷰 검증·수정 계획

> 실행: 현재 작업 폴더에서 직접 수정한다. 기존 미커밋 보고서와 사용자 파일을 보존한다.

**목표:** `code-review-2026-11-04.txt`의 재현되는 결함만 수정하고 실제/모의 검증을 구분한다.
**기준:** GitHub #1 본문·댓글, #3/#4 수락 기준, PLAN §§4.1–4.3/5.2/12–14.
**구조:** 기존 Python episode/schema/CLI 및 Node bridge를 유지한다. 새 실행기·테스트 계층·모델·학습은 추가하지 않는다.

## 범위와 검토 초점

- 인증서 없음/변경, 결정 경계의 상태 변화, 다중 step 중 실패가 검증된 정지로 집계되지 않아야 한다.
- 실제 Mineflayer error 이벤트가 RPC stdout에 섞이지 않아야 한다.
- 잘못된 이동 근거·사건 출처가 smoke 성공으로 인정되지 않아야 한다.
- mock backend 제한과 잘못된 설정 파일의 오류를 구분해 안내한다.
- Node lock에 이미 설치된 vec3 revision을 직접 의존성으로 선언한다.
- 중복 상수·언어별 검증·private RPC 메서드·fixture 구조는 실제 결함 여부를 따로 판정한다.

## 실행 순서

- [x] 기준 pytest를 실행하고 리뷰 각 항목의 호출자·자료형·fixture를 확인한다.
- [x] tests/test_cli.py에 정지 표시·이동 근거·CLI 안내 회귀 검사를 추가해 RED를 확인한다.
- [x] schema.py/episode.py/cli.py에서 공개 계약과 호출자를 함께 고치고 GREEN을 확인한다. mock_bridge는 변경 없이 완전한 fixture 근거를 사용한다.
- [x] 실제 Mineflayer 오류와 경계 상태 변화의 scripted 재현 검사를 추가해 RED를 확인한다.
- [x] minecraft.js의 logErrors·pause·step 결과 및 package.json/lock을 최소 수정하고 GREEN을 확인한다.
- [x] 전체 pytest/mypy·Node 문법·diff 검사를 실행했다. 최종 54 passed(13.78초), mypy 16파일 통과.
- [x] 변경된 fingerprint로 실제 verify-clock 63/63·인증 전/후 wait·이동·정보 감사를 검증했다. sandbox 실패를 따로 보존하고 C4 기준 reset/정상 종료를 확인했다.
- [x] DECISIONS/PROGRESS와 항목별 검증 기록, 검토용 HTML/PDF를 작성·검사했다. A4 3쪽 한글 추출·글꼴 포함·모든 페이지 이미지 가독성 통과, 보고서 목록 추가. 새 코드의 원격 commit이 없어 기준 코드 링크와 실제 수정 patch를 구분했다.

## 작업 상태

기준 main `893ff27`. commit/push/merge/이슈 변경은 요청 범위에 포함하지 않는다.
기존 PROGRESS.md·reports/README.md·TEMPLATE.html 및 code-guide 보고서는 작업 시작 때부터 변경되어 있었다.
