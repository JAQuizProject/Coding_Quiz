# Chrome DevTools MCP 라이브 데모 준비

이 문서는 `Coding_Quiz`에서 Codex가 격리된 Chrome을 직접 조작하고, 화면·Console·Network와 저장소 코드를 함께 조사하는 발표 환경의 기준 절차다.

## 1. 구성

```text
Codex
  -> project .codex/config.toml
  -> Chrome DevTools MCP 1.5.0
  -> isolated Chrome
  -> Next.js :3000
  -> FastAPI :8000
  -> local SQLite
```

프로젝트 전용 MCP 설정은 `.codex/config.toml`에 있다. Codex는 신뢰한 프로젝트에서 프로젝트 범위 설정을 읽는다.

- MCP 실행: `C:\Program Files\nodejs\npx.cmd`
- Chrome 실행: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- 브라우저 프로필: `--isolated`
- 발표 해상도: `1440x900`
- 사용 통계와 CrUX 조회: 비활성화
- Network 민감 헤더: 마스킹

공식 기준: [Codex config.toml reference](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml)

## 2. 확인된 환경

| 항목 | 확인 결과 |
| --- | --- |
| Python | `3.13.7` |
| Node | `26.4.0` |
| Chrome | `150.0.7871.101` |
| Codex CLI | `0.144.1` |
| Chrome DevTools MCP | `1.5.0` |
| 백엔드 baseline | `17 passed` |
| 프론트 baseline | 테스트·lint·build 통과 |

버전은 발표 전 다시 확인하되, Node나 MCP를 발표 직전에 임의 업그레이드하지 않는다.

## 3. 최초 1회 setup

저장소 루트에서 실행한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_live_demo.ps1
```

이 명령은 다음을 순서대로 처리한다.

1. 프로젝트 `.venv` 생성
2. `poetry.lock` 기준 백엔드 의존성 설치
3. `frontend/package-lock.json` 기준 `npm ci`
4. 로컬 데모 계정과 `LiveDemo` 퀴즈 3건 준비
5. Codex의 `chrome-devtools` MCP 인식 확인
6. 백엔드 테스트·Ruff와 프론트 테스트·lint·build 실행

setup은 명령 하나라도 실패하면 즉시 중단한다.

## 4. Codex 재시작과 MCP 확인

`.codex/config.toml`을 처음 추가한 뒤에는 현재 Codex 세션을 종료한다. 발표용 Codex는 다음 스크립트로 연다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\open_live_demo_codex.ps1
```

이 스크립트는 프로젝트의 Chrome MCP는 유지하고 발표에 필요 없는 전역 원격 MCP를 현재 세션에서만 꺼 인증 로그가 섞이지 않게 한다.

별도 터미널에서 설정 상태를 확인한다.

```powershell
codex mcp get chrome-devtools
codex mcp list
```

정상 기준:

```text
chrome-devtools
enabled: true
transport: stdio
default_tools_approval_mode: approve
```

발표용 Codex TUI에서는 `/mcp`를 열어 `chrome-devtools` 도구가 보이는지 확인한다.

## 5. 발표 당일 시작

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_live_demo.ps1
```

정상 출력:

```text
Backend is ready: http://127.0.0.1:8000/
Frontend is ready: http://127.0.0.1:3000/login
Login: live-demo@example.com
Password: Demo1234!
Category: LiveDemo
```

백엔드와 프론트는 숨김 프로세스로 실행되고 로그와 PID는 git에서 제외된 `.demo/`에 저장된다.

백엔드 코드를 수정한 뒤에는 새 코드를 확실히 반영하도록 백엔드만 재시작한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_live_demo.ps1 -RestartBackend -SkipDataPreparation
```

확인 주소:

- 프론트: `http://127.0.0.1:3000/login`
- 백엔드: `http://127.0.0.1:8000/`
- API 문서: `http://127.0.0.1:8000/docs`

## 6. MCP 연결 smoke test

새 Codex 세션에서 실행한다.

```text
Use only the chrome-devtools MCP server.
Open http://127.0.0.1:3000/login, wait until the page is fully loaded,
clear the Console, and reload once. Then report:
1. current URL
2. the visible page heading
3. Console error count
Do not edit files.
```

정상 기준:

```text
URL: http://127.0.0.1:3000/login
Heading: 로그인
Console error: 0
```

Next.js 개발 모드의 최초 컴파일 직후에는 일시적인 Console 항목이 남을 수 있으므로 발표 전 주요 경로를 한 번 열고 위 순서로 다시 확인한다.

## 7. 라이브 데모 데이터

로그인:

```text
live-demo@example.com / Demo1234!
```

`LiveDemo` 카테고리에서 입력할 값:

| 문제 | 입력 | 저장된 정답 | 버그 상태 |
| --- | --- | --- | --- |
| DEMO 1 | `10.00` | `10` | 오답으로 잘못 처리 |
| DEMO 2 | `java3` | `python3` | 정답으로 잘못 처리 |
| DEMO 3 | `user 404` | `order 404` | 정답으로 잘못 처리 |

버그 상태의 API 결과:

```text
POST /quiz/submit -> 200
correct=2, total=3
```

수정 후 기대 결과:

```text
POST /quiz/submit -> 200
correct=1, total=3
incorrect_items -> DEMO 2, DEMO 3
```

전체 조사·수정·재검증 프롬프트는 `demo/LIVE_DEMO_PROMPTS.md`에 있다.

## 8. 발표 종료

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop_live_demo.ps1
```

이 명령은 start 스크립트가 기록한 백엔드·프론트 프로세스 트리만 종료한다.

## 9. 문제 해결

| 증상 | 확인 |
| --- | --- |
| MCP가 목록에 없음 | 프로젝트를 신뢰했는지 확인하고 `open_live_demo_codex.ps1`로 재실행 |
| MCP 시작 시간 초과 | `npx -y chrome-devtools-mcp@1.5.0 --version` 실행 |
| Chrome을 찾지 못함 | `.codex/config.toml`의 `executablePath` 확인 |
| 프론트가 시작되지 않음 | `.demo/frontend.error.log` 확인, setup 재실행 |
| 백엔드가 시작되지 않음 | `.demo/backend.error.log` 확인, `:8000` 사용 프로세스 확인 |
| 수정 후 API가 이전 결과를 반환 | `-RestartBackend -SkipDataPreparation`로 백엔드 명시적 재시작 |
| 로그인 실패 | `scripts/prepare_live_demo.py` 재실행 |
| 카테고리가 없음 | start 스크립트를 다시 실행해 DB 데이터 재준비 |
| 수정이 꼬임 | 현재 diff 확인 후 `scripts/apply_live_demo_solution.ps1` 사용 |

## 10. 안전 기준

- MCP는 `--isolated` Chrome만 사용한다.
- 회사 계정, 개인 계정, 운영 토큰을 입력하지 않는다.
- 로컬 주소 외에는 열지 않는다.
- 조사 단계에서는 파일을 수정하지 않는다.
- DB schema, migration, 인증, API 계약은 데모 수정 범위에서 제외한다.
- 최종 완료 기준은 같은 브라우저 흐름과 Network 응답의 재검증이다.
