# T03 제한 관측·이동 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 이슈 #4의 관측·이동과 실제 숨은 정보 불변 감사를 구현한다.
**Architecture:** 기존 JSONL RPC/실행기를 확장한다. Node는 눈 위치에서 반경 8 이내의 광선을 불투과 셀에서 끊고, 통과한 공기와 첫 노출 표면만 기억한다. Python은 이 지도에서만 같은 높이의 경로를 생성하며 Node도 동일 공개 셀로 실행 전제조건·위험·안정 경계를 판단한다.
**Tech Stack:** 기존 Python/Pydantic/pytest, Node/Mineflayer 및 표준 라이브러리.
**Spec:** GitHub #1/#4, PLAN §§4.1–4.3, 5.2, 12–14.

## Global Constraints

- 반경 8블록, 후보 최대 8개, 이동 최대 16블록/400 활성 틱.
- hidden_hazard_peek=false; 관리자 fixture 준비와 정책 관측을 별도 채널로 유지.
- 실제 검증과 mock을 구분하고 실제 시간·틱·근거 ID/지도 버전을 출력.
- 기존 snapshot/보고서 보존; 제작·하강·tunnel, 모델·학습·API는 후속 티켓.

## Review Focus

- 벽 뒤 블록/미로딩 셀/대각선 틈으로 정보가 새지 않는가.
- 기억한 길이 공개 변경으로 막히면 실행을 중단하는가.
- 숨은 경로·오래된 지도·과장된 경로/틱 요청은 거부되는가.
- 위험 중단을 안정화 대기로 지연하지 않는가; reset 기억은 비우는가.
- 실제 fixture 결과 불일치/오류 시 감사가 실패하는가.

### 1. 공개 이동 흐름과 관측 계약

Files: schema.py, episode.py, cli.py, 새 navigation.py, tests/test_cli.py.
- [x] 공개 smoke-movement에서 알려진 바닥/공기만 통과하고 미관측 목적지는 제외하는 RED 확인.
- [x] 지도 버전·방향·방문 이력·공개 이동 근거 계약 및 BFS 경로 후보 연결.
- [x] 기존 mock smoke와 전체 pytest/mypy 통과.

### 2. 실제 관측·이동

Files: 새 bridge/terrain.js, bridge/minecraft.js, 기존 공개 CLI 검사.
- [x] 벽 뒤 변경/미관측 경로 거부의 실행 가능한 fixture 검사 RED 확인.
- [x] ray 경계·기억·같은 높이 이동/위험 중단/안정화와 실제 틱 연결.
- [x] 실제 smoke-movement와 시계 인증 재검증(기존 63개 진단).

### 3. 실제 정보 감사와 검토 산출물

Files: 새 information.py, RPC 메서드, README/DECISIONS/PROGRESS, reports.
- [x] mock을 실제 근거로 받지 않고 불일치를 실패시키는 CLI 검사 RED 확인.
- [x] 관리자 전용 벽 뒤 광석/용암 fixture, 정책 관측/후보/경로/중단 비교.
- [x] 실제 audit-information, 전체 검사, 검토, PDF/HTML 및 모든 페이지 가독성 확인.

실행 결정: 사용자 요청의 기존 확정 티켓을 이 세 작업으로 직접 구현한다. 현재 checkout의 ticket-4 브랜치를 사용하며 별도 worktree/의존성/새 실험은 추가하지 않는다. commit/push/merge/이슈 종료는 별도로 상태를 보고한다.
