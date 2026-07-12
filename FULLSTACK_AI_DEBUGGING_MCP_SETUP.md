# Chrome DevTools MCP 실습 준비 절차

이 문서는 `Coding_Quiz` 프로젝트에서 **Codex + Chrome DevTools MCP**를 처음 연결하고, 정상 화면을 읽는 데까지의 준비 절차다.

처음에는 Claude와 Codex를 동시에 설정하지 않는다. Codex에서 한 번 성공한 뒤 같은 MCP를 Claude에 추가한다.

---

## 0. 무엇을 연결하는가

```text
Codex
  -> Chrome DevTools MCP
      -> 테스트 전용 Chrome
          -> Next.js :3000
              -> FastAPI :8000
```

- Codex: 조사 지시를 내리는 AI 클라이언트
- Chrome DevTools MCP: Chrome의 화면, Console, Network를 Codex에 제공하는 도구
- Coding_Quiz: 실제로 조사할 로컬 애플리케이션

MCP를 설치하는 것과 프로젝트 서버를 실행하는 것은 별개다. 둘 다 정상이어야 실습할 수 있다.

---

## 1. 현재 확인된 환경

| 항목 | 확인 결과 |
| --- | --- |
| Python | `3.13.0` |
| 프로젝트 가상환경 | `.venv` 존재 |
| Node 설치 버전 | `20.12.1`, `22.12.0` |
| 실습에 사용할 Node | `22.12.0` |
| Chrome | `149.0.7827.200` |
| Codex CLI | `0.144.1` |
| Chrome DevTools MCP | `1.5.0` 실행 확인 |
| 백엔드 테스트 | `17 passed` |
| 프론트 lint/build | 통과 |

최신 `chrome-devtools-mcp`는 Node `20.19.0` 이상이 필요하므로 현재 기본값인 `20.12.1`로는 실행되지 않는다.

PowerShell을 새로 열 때 다음 명령으로 Node 22를 우선 사용한다.

```powershell
$env:PATH = "$env:APPDATA\nvm\v22.12.0;$env:PATH"
node --version
npm --version
```

성공 기준:

```text
v22.12.0
```

관리자 PowerShell을 사용할 수 있다면 `nvm use 22.12.0`으로 기본 버전을 전환해도 된다.

---

## 2. Codex MCP 설치 상태 확인

이 PC에는 `chrome-devtools` 서버를 Codex 사용자 설정에 추가해 두었다.

```powershell
codex mcp get chrome-devtools
codex mcp list
```

다음 값이 보이면 설치된 상태다.

```text
chrome-devtools
enabled: true
transport: stdio
```

설정을 지우고 다시 설치해야 할 때만 다음 명령을 사용한다.

```powershell
codex mcp remove chrome-devtools

codex mcp add chrome-devtools -- cmd /d /s /c `
  'set "PATH=%APPDATA%\nvm\v22.12.0;%PATH%" && npx -y chrome-devtools-mcp@latest --isolated --no-usage-statistics --no-performance-crux --redact-network-headers'
```

옵션의 의미:

| 옵션 | 이유 |
| --- | --- |
| `--isolated` | 개인 Chrome 프로필과 분리된 임시 프로필 사용 |
| `--no-usage-statistics` | MCP 사용 통계 전송 중지 |
| `--no-performance-crux` | 성능 분석 중 URL 기반 CrUX 조회 중지 |
| `--redact-network-headers` | Network 결과의 민감 헤더 마스킹 |

---

## 3. Codex 재시작

MCP를 추가한 뒤에는 기존 Codex 세션에 도구가 자동으로 생기지 않는다.

1. 현재 Codex 창 또는 CLI를 완전히 종료한다.
2. `Coding_Quiz` 폴더에서 Codex를 다시 연다.
3. Codex에서 `/mcp`를 실행한다.
4. 목록에서 `chrome-devtools`와 도구 목록을 확인한다.

발표 연습처럼 로컬 임시 브라우저의 도구 호출을 자동 승인하려면 해당 실행에만 다음 설정을 적용한다.

```powershell
Set-Location C:\Users\gram\tvcf\Coding_Quiz
codex -c 'mcp_servers.chrome-devtools.default_tools_approval_mode="approve"'
```

일반 업무에서는 기본 승인 모드를 유지하고 브라우저 동작을 직접 확인한다.

---

## 4. 프로젝트 실행

PowerShell 창을 두 개 연다.

### 터미널 1: FastAPI

```powershell
Set-Location C:\Users\gram\tvcf\Coding_Quiz
& '.\.venv\Scripts\python.exe' -m uvicorn main:app --reload --port 8000
```

확인 주소:

```text
http://127.0.0.1:8000/docs
```

### 터미널 2: Next.js

```powershell
$env:PATH = "$env:APPDATA\nvm\v22.12.0;$env:PATH"
Set-Location C:\Users\gram\tvcf\Coding_Quiz\frontend
npm run dev
```

확인 주소:

```text
http://127.0.0.1:3000
```

첫 개발 모드 컴파일은 `next/font/google` 요청 재시도로 약 1분 걸릴 수 있다. 발표 직전에 처음 열지 말고, 준비 단계에서 `/`, `/login`, `/quiz`, `/result`를 한 번씩 열어 둔다.

---

## 5. MCP 첫 연결 테스트

Codex에 아래 요청을 그대로 입력한다.

```text
Chrome DevTools MCP만 사용해서 http://127.0.0.1:3000을 여세요.
페이지 로딩이 끝나면 다음 세 가지만 알려주세요.

1. 현재 URL
2. document.title
3. Console error 개수

코드와 페이지 데이터는 수정하지 마세요.
```

현재 프로젝트의 확인 결과:

```text
페이지 열기 성공
document.title: 비어 있음
Console error: 0개
```

제목이 비어 있는 것은 현재 루트 레이아웃에 title metadata가 없기 때문이다. MCP 연결 실패로 판단하지 않는다.

---

## 6. Network까지 확인하는 두 번째 테스트

```text
Chrome DevTools MCP로 http://127.0.0.1:3000을 조사하세요.

1. 페이지 스냅샷을 확인하세요.
2. Console의 error와 warning을 구분하세요.
3. localhost:8000 또는 127.0.0.1:8000으로 향하는 Network 요청을 찾으세요.
4. 각 요청의 method, URL, status만 표로 정리하세요.

아직 파일은 수정하지 말고 관찰 결과와 추정은 분리해서 작성하세요.
```

이 단계에서는 AI가 코드를 고치는 것이 목적이 아니다. 브라우저를 실제로 읽고 근거를 반환하는지만 확인한다.

---

## 7. 정상 사용자 흐름 준비

1. 테스트 전용 계정을 `/signup`에서 만든다.
2. `/login`에서 로그인한다.
3. `/quiz`에서 문제를 선택하고 제출한다.
4. `/result`에서 점수와 오답 목록을 확인한다.
5. 이 정상 흐름을 MCP로 한 번 더 조사한다.

회사 계정이나 개인 계정은 사용하지 않는다. 로컬 SQLite에만 존재하는 발표용 계정을 사용한다.

정상 흐름 확인이 끝난 뒤에만 실습용 버그 브랜치를 만든다.

```powershell
git switch -c demo/fullstack-mcp-debug
```

---

## 8. 자주 막히는 지점

| 증상 | 원인 | 확인 방법 |
| --- | --- | --- |
| `does not support Node v20.12.1` | Node 버전 부족 | Node 22 PATH 설정 후 재실행 |
| `/mcp`에 서버가 없음 | Codex 재시작 전 | Codex 완전 종료 후 다시 실행 |
| `user cancelled MCP tool call` | 비대화형 승인 정책 | 연습 실행에만 `default_tools_approval_mode="approve"` 적용 |
| MCP는 연결됐지만 페이지가 안 열림 | 프론트 미실행 | `http://127.0.0.1:3000` 직접 확인 |
| 화면은 열리지만 API가 실패 | 백엔드 미실행 또는 환경 변수 | `:8000/docs`, `NEXT_PUBLIC_API_URL` 확인 |
| 첫 화면이 오래 걸림 | Next.js 첫 컴파일과 외부 폰트 재시도 | 발표 전에 주요 경로 미리 열기 |
| 개인 로그인 정보가 보임 | 기존 Chrome 프로필 사용 | `--isolated` 유지 |

---

## 9. 준비 완료 기준

- [ ] `codex mcp list`에 `chrome-devtools`가 enabled로 표시됨
- [ ] Codex 재시작 후 `/mcp`에서 도구가 보임
- [ ] `http://127.0.0.1:8000/docs`가 열림
- [ ] `http://127.0.0.1:3000`이 열림
- [ ] MCP가 현재 URL과 Console 오류 개수를 반환함
- [ ] 테스트 계정으로 퀴즈 정상 흐름을 완료함
- [ ] 정상 상태 테스트, lint, build가 통과함
- [ ] 그 다음에만 실습용 버그를 주입함

---

## 공식 문서

- [Chrome DevTools for agents 시작하기](https://developer.chrome.com/docs/devtools/agents/get-started)
- [Chrome DevTools MCP 공식 저장소](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Codex MCP 설정](https://learn.chatgpt.com/docs/extend/mcp)
- [Claude Code MCP 설정](https://code.claude.com/docs/en/mcp)
- [Node.js 지원 버전](https://nodejs.org/en/about/previous-releases)
