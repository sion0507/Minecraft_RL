# 이슈 검토 보고서

사용자가 이슈별 구현과 검증 결과를 검토하는 폴더다. **이슈 구현 완료를 보고할 때 PDF와 편집 가능한 HTML 원본을 함께 저장한다.**

## 보고서 목록

| 이슈 | 파일 | 작성 기준과 상태 |
| --- | --- | --- |
| #2 / T01 환경 진단·모의 에피소드 | [PDF](issue-002-T01-2026-11-03.pdf) · [HTML](issue-002-T01-2026-11-03.html) | 2026-10-10 완료·PR #26 main 반영 기록을 2026-11-03에 재구성 |
| #3 / T02 실제 월드 reset·시계 | [PDF](issue-003-T02-2026-11-03.pdf) · [HTML](issue-003-T02-2026-11-03.html) | 2026-11-03 작성 / 2026-11-02 구현·실제 검증 완료, 코드 미커밋·미푸시·미머지, 이슈 종료 미처리 |
| #3 / T02 PR 검토 후속본 | [PDF](issue-003-T02-2026-11-03-v2.pdf) · [HTML](issue-003-T02-2026-11-03-v2.html) | 2026-11-03 독립 검토·의존성 인증 보완·실제 재검증 63/63, 코드 21a6359 푸시 완료, PR #28 머지 전 기록 |
| #4 / T03 제한 관측·이동·정보 감사 | [PDF](issue-004-T03-2026-11-03.pdf) · [HTML](issue-004-T03-2026-11-03.html) | 2026-11-03 실제 정지 63/63·이동·정보 감사 통과, ticket-4 미커밋·미푸시·미머지, 이슈 종료 미처리 |

## 작성 규칙

목록과 PDF의 Git 상태는 각 보고서 작성 당시의 기록이다. 후속 커밋·푸시 결과는 Git 이력과 [PROGRESS.md](../PROGRESS.md)의 최신 기록을 확인한다.

2026-11-03 첫 푸시 당시 기록: 구현 코드와 보고서를 [1312252](https://github.com/sion0507/Minecraft_RL/commit/1312252e200df81e352a34570a8561ef049fb84c)로 커밋하고 `origin/ticket-3`에 푸시했다. 당시 PR 생성·main 머지·이슈 종료는 미처리였다. 이후 PR #28 검토·수정 기록은 v2 보고서를 참조한다. 기존 PDF의 작성 당시 상태는 보존한다.

1. `issue-NNN-TNN-YYYY-MM-DD.html`과 같은 이름의 `.pdf`를 만든다. NNN은 GitHub 이슈 번호, TNN은 작업 코드, 날짜는 보고서 작성일이다. 실제 실행·검증일은 본문에 별도로 적는다. 이슈 #2는 T01, #3은 T02다.
2. [TEMPLATE.html](TEMPLATE.html)을 복사하고 [report.css](report.css)를 사용한다. 한국어로 목적·수락 기준별 구현·변경 파일/구조·검증 명령/결과·실패/수정·미실행/제한·근거 경로를 적는다.
3. 실제 환경 검증, mock/scripted 검사, 미실행을 구분한다. 과거 기록을 재구성하면 실행일을 적고 이번에 다시 실행한 것처럼 쓰지 않는다.
4. 코드 기준 commit/branch와 작성 시점의 commit/push/PR merge/이슈 종료 상태를 각각 적는다. 구현 검증만 끝난 상태를 main 반영이나 GitHub 종료로 표시하지 않는다.
5. 비밀키·인증 토큰·계정 비밀번호·숨은 광석 좌표는 넣지 않는다. 로컬 raw artifact 경로와 필요한 hash는 기록할 수 있다.
6. 한글 추출·글꼴 포함·모든 페이지의 가독성을 확인하고 목록에 추가한다. 기존 완료 보고서는 보존하며 후속 수정본은 새 날짜나 `-v2` 같은 이름으로 남긴다.

## PDF 생성과 확인

이 작업공간은 WeasyPrint **70.0**을 `.cache/uv`의 별도 도구 환경에 설치했다. 게임 실행 의존성에는 추가하지 않았다. 시스템 Pango와 Noto Sans CJK KR 글꼴을 사용한다.

저장소 루트에서 실행한다. 새 환경에서 도구 설치가 필요하면 `--offline`을 빼고 설치한 뒤 사용한다.

```bash
UV_CACHE_DIR=.cache/uv \
UV_TOOL_DIR="$PWD/.cache/uv-tools" \
UV_TOOL_BIN_DIR="$PWD/.cache/uv-tool-bin" \
.tools/uv tool run --offline --from weasyprint==70.0 weasyprint \
  reports/issue-003-T02-2026-11-03.html \
  reports/issue-003-T02-2026-11-03.pdf

pdfinfo reports/issue-003-T02-2026-11-03.pdf
pdffonts reports/issue-003-T02-2026-11-03.pdf
pdftotext -layout reports/issue-003-T02-2026-11-03.pdf /tmp/issue-003-report.txt
pdftoppm -scale-to 1400 -png reports/issue-003-T02-2026-11-03.pdf /tmp/issue-003-page
```

추출 텍스트에서 핵심 수치·한글을 확인하고 페이지 이미지에서 잘림·글자 깨짐·표 행 분리·문장 하나만 남은 페이지를 확인한다. 출력 실패나 검증 누락을 완료로 보고하지 않는다. 보고서 작성 때문에 Minecraft 실험을 자동 재실행하지 않는다.
