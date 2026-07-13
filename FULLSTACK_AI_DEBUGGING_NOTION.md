# 화면에서 API까지

## Claude·Codex와 Chrome DevTools MCP로 풀스택 버그 추적하기

> 이 문서는 발표 후 공유하는 상세 자료다. 실제 화면 공유에는 `FULLSTACK_AI_DEBUGGING_NOTION_SCREEN.md`를 사용한다.

> 사용자가 겪은 문제를 AI가 실제 브라우저에서 재현하고, 화면 상태와 Network 요청을 프론트엔드 코드 및 백엔드 API까지 연결해 원인을 찾는 과정을 보여준다.

---

## 발표 정보

| 항목 | 내용 |
| --- | --- |
| 대상 | 프론트엔드, 백엔드, QA, 개발 리더 |
| 시간 | 25분 발표 + 질의응답 |
| 사용 도구 | Claude Code 또는 Codex 중 하나, Chrome DevTools MCP |
| 실습 프로젝트 | Next.js 프론트엔드 + FastAPI 백엔드 Coding Quiz |
| 실습 결과 | 문제 재현, 근거 수집, 원인 추적, 최소 수정, 브라우저 재검증 |

## 발표에서 전달할 한 문장

> 풀스택 AI 활용은 AI에게 양쪽 코드를 모두 작성시키는 것이 아니라, 하나의 사용자 흐름을 화면·Network·API·서버 코드까지 근거를 가지고 추적하게 만드는 것이다.

## 오늘 확인할 질문

1. 소스 코드만 읽는 AI는 실제 실행 문제를 어디까지 알 수 있는가?
2. Browser MCP를 연결하면 AI가 어떤 실행 정보를 확인할 수 있는가?
3. 프론트와 백엔드는 어떤 증거를 공통 기준으로 사용할 수 있는가?
4. AI가 찾은 원인을 사람이 어떻게 검토하고 최종 결정할 것인가?

---

# 1. 왜 풀스택 버그는 오래 걸리는가

## 사용자가 전달하는 문제

> "퀴즈 제출 버튼을 눌렀는데 결과 화면이 이상해요."

이 한 문장만으로는 원인이 어느 계층에 있는지 알 수 없다.

| 확인할 곳 | 가능한 원인 |
| --- | --- |
| 화면 | 버튼 이벤트, 입력 상태, 로딩 처리, 렌더링 조건 |
| 브라우저 | JavaScript 오류, Network 실패, CORS, 잘못된 요청값 |
| API 계약 | 필드 이름, 타입, 필수값, 상태 코드, 오류 응답 형식 |
| 백엔드 | Router, Schema, Service, DB 조회, 예외 처리 |
| 환경 | API 주소, 인증 토큰, 환경 변수, 배포 버전 |

기존에는 각 담당자가 자신의 영역을 따로 확인한다.

```text
사용자 제보
  -> 프론트엔드가 화면과 Network 확인
  -> 요청·응답 캡처를 백엔드에 전달
  -> 백엔드가 API와 로그 재확인
  -> 수정 후 프론트에서 다시 재현
```

문제는 코드 작성 속도가 아니라 **실행 증거를 모으고 계층 사이를 이동하는 시간**이다.

---

# 2. 코드만 보는 AI와 실행 결과를 보는 AI

## 코드만 제공했을 때

```text
저장소
  -> AI가 관련 파일 검색
  -> 정적 코드만 보고 원인 추정
```

AI는 다음 내용을 직접 알 수 없다.

- 사용자가 실제로 어떤 순서로 조작했는지
- 브라우저에서 어떤 요청이 발생했는지
- 실제 요청 body와 응답 body가 무엇인지
- 화면이 어떤 상태로 렌더링됐는지
- Console에 어떤 런타임 오류가 발생했는지

## Chrome DevTools MCP를 연결했을 때

```text
사용자 조작
  -> DOM / Console / Network
  -> Chrome DevTools MCP
  -> Claude 또는 Codex
  -> 프론트 코드 + API 계약 + 백엔드 코드 추적
  -> 같은 사용자 흐름으로 재검증
```

## 도구별 역할

| 구성 요소 | 역할 |
| --- | --- |
| Chrome DevTools MCP | 브라우저 조작, DOM 확인, Console 및 Network 정보 제공 |
| Claude·Codex | 실행 증거와 저장소 코드를 연결해 원인 후보 분석 |
| 프론트엔드 코드 | 화면 상태, 이벤트, API 호출, 응답 처리 확인 |
| 백엔드 코드 | 요청 검증, 응답 모델, 비즈니스 로직 확인 |
| 사람 | 기대 동작 정의, 수정 방향 선택, 최종 승인 |

MCP는 AI 모델을 더 똑똑하게 만드는 기능이 아니다. AI가 **실제 실행 환경을 조사할 수 있도록 도구를 연결하는 규격**이다.

---

# 3. 최근 공식 사례

## Chrome DevTools for agents

Google은 Chrome DevTools for agents를 통해 AI 코딩 도구가 실제 브라우저를 조작하고, Network 요청과 Console 메시지, 화면 상태를 확인할 수 있도록 제공하고 있다. 2026년 6월 Chrome 149에서 MCP 서버와 CLI가 안정 버전으로 전환됐다.

- [Chrome DevTools for agents](https://developer.chrome.com/docs/devtools/agents)
- [Chrome 149: DevTools for agents stable](https://developer.chrome.com/blog/new-in-devtools-149)
- [공식 영상: Supercharge your AI coding workflow with Chrome DevTools for agents](https://www.youtube.com/watch?v=1AD81ZselPk)

## Claude의 Build → Test → Verify

Anthropic은 Claude Code와 Chrome을 연결해 터미널에서 코드를 작성한 뒤 브라우저에서 테스트하고 검증하는 흐름을 안내한다. Claude는 Console 오류, Network 요청, DOM 상태를 읽어 디버깅에 사용할 수 있다.

- [Claude in Chrome](https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome)

## Codex의 실제 사용자 흐름 QA

OpenAI는 Codex가 실제 제품 흐름을 클릭하면서 문제를 찾고, 재현 단계·기대 결과·실제 결과·심각도를 포함한 보고서를 작성하는 QA 활용 방식을 제시한다.

- [QA your app with Computer Use](https://learn.chatgpt.com/use-cases/qa-your-app-with-computer-use)

## CyberAgent 사례

CyberAgent는 Claude와 Chrome DevTools MCP를 사용해 Storybook의 32개 컴포넌트와 236개 Story를 약 한 시간 동안 확인했다. AI는 브라우저 상태와 Console을 읽고 런타임 오류를 찾아 수정 후 다시 확인했다.

- [CyberAgent runtime debugging 사례](https://developer.chrome.com/blog/autofix-runtime-devtools-mcp)

## 사례에서 가져올 기준

> AI에게 "버그를 찾아줘"라고만 요청하지 않는다. 확인할 사용자 흐름과 기대 결과, 수집해야 할 증거를 먼저 지정한다.

---

# 4. 실습 시나리오

## 사용자 제보

> `10.00`은 `10`과 같은 숫자인데 오답이고, `java3`은 `python3`과 다른 문자열인데 정답으로 처리된다.

## 저장소에 존재하는 실제 결함

프론트와 백엔드 채점 로직에 같은 결함이 있다.

1. 전체 문자열이 숫자인지 확인하지 않고 문자열 안의 숫자 하나를 비교한다.
2. 숫자를 파싱하기 전에 소수점 같은 기호를 제거한다.

`scripts/prepare_live_demo.py`가 로컬 DB에 전용 계정과 `LiveDemo` 문제 3건을 준비하므로 매번 같은 입력으로 재현할 수 있다.

## 기대 동작과 실제 동작

| 구분 | 내용 |
| --- | --- |
| 사용자 동작 | 로그인 → `LiveDemo` 선택 → `10.00`, `java3`, `user 404` 입력 → 제출 |
| 기대 결과 | DEMO 1만 정답, `correct=1`, `total=3` |
| 실제 결과 | 제출 API는 `200`이지만 DEMO 2·3을 정답 처리해 `correct=2` |
| 조사 범위 | 브라우저, 프론트 판정 함수, FastAPI 채점 서비스와 판정 함수 |
| 제외 범위 | 운영 배포, 실제 사용자 데이터, DB migration, 외부 시스템 변경 |

## 조사할 실제 흐름

```text
브라우저 제출 버튼
  -> frontend/app/quiz/page.js
  -> frontend/utils/answerMatcher.js
  -> frontend/api/quiz.js
  -> POST /quiz/submit
  -> app/modules/quiz/service.py
  -> app/modules/quiz/grading.py
  -> HTTP 응답
  -> localStorage
  -> frontend/app/result/page.js
```

---

# 5. 라이브 실습

## 5-1. 브라우저에서 문제 재현

먼저 AI에게 코드를 수정시키지 않는다.

1. `live-demo@example.com` 계정으로 로그인한다.
2. 퀴즈 페이지에서 `LiveDemo`를 선택한다.
3. `10.00`, `java3`, `user 404`를 입력하고 각 정답 확인 버튼을 누른다.
4. 제출 후 잘못된 점수와 오답 목록을 확인한다.
5. Network에서 `POST /quiz/submit`의 `200`, `correct=2`, `total=3`을 확인한다.

이 단계의 질문:

> 화면이 실패했다고 해서 API도 실패했다고 말할 수 있는가?

## 5-2. AI에게 조사 요청

```text
Chrome DevTools MCP를 사용해 demo/LIVE_DEMO_PROMPTS.md에 정의된
LiveDemo 로그인부터 결과 확인까지 실행하세요.

목표:
- 제출 후 결과 화면이 잘못 표시되는 문제를 재현합니다.
- 아직 코드를 수정하지 않습니다.

조사 기준:
1. 사용자 조작 순서를 기록하세요.
2. Console 오류와 POST /quiz/submit Network 요청을 확인하세요.
3. 실제 request body, status, response body를 요약하세요.
4. 확인된 사실과 추정을 구분하세요.
5. 관련 프론트 파일과 백엔드 파일을 file:line 근거로 연결하세요.
6. 프론트와 백엔드 판정 정책을 동일하게 유지하는 최소 수정 범위를 제안하세요.

금지:
- 운영 환경 접근
- 실제 사용자 데이터 사용
- DB 변경
- 원인 확인 전 코드 수정
```

## 5-3. AI가 반환해야 할 조사 결과

| 항목 | 예시 |
| --- | --- |
| 재현 여부 | 재현 성공 또는 실패 |
| 화면 증상 | DEMO 1은 오답, DEMO 2·3은 정답으로 표시 |
| Network 근거 | `POST /quiz/submit`, `200`, `correct=2`, `total=3` |
| 프론트 근거 | compact 값에서 문자열 속 숫자를 추출해 비교 |
| 백엔드 근거 | 동일한 순서로 숫자를 추출해 비교 |
| 확인된 사실 | 실제 도구로 확인한 내용 |
| 추정 | 추가 확인이 필요한 원인 후보 |
| 수정안 | 하위 호환성, 영향 범위, 권장안 |

## 5-4. 사람이 수정 방향 결정

AI가 원인을 찾았더라도 수정 방향은 자동으로 결정하지 않는다.

검토 질문:

1. 숫자 허용 오차는 어떤 입력에만 적용할 것인가?
2. 쉼표, 부호, 소수 표현을 어디까지 지원할 것인가?
3. 프론트와 백엔드가 같은 정책을 구현하는가?
4. 기존 문자열·토큰·유사도 비교 순서를 불필요하게 바꾸지 않았는가?
5. 같은 문제가 다시 생기지 않도록 양쪽 공개 함수에 회귀 테스트를 남겼는가?

## 5-5. 최소 수정과 브라우저 재검증

수정 승인 후 AI에게 다음을 요청한다.

```text
승인한 수정안만 적용하세요.

- 관련 없는 리팩터링은 하지 마세요.
- 변경한 파일과 이유를 요약하세요.
- 기존 lint와 테스트를 실행하세요.
- 마지막에는 Chrome DevTools MCP로 동일한 사용자 흐름을 다시 실행하세요.
- Network 응답과 결과 화면이 모두 기대 동작과 일치하는지 보고하세요.
```

완료 조건:

```text
같은 사용자 흐름 재실행
  + DEMO 1 Correct 확인
  + DEMO 2·3 Incorrect 확인
  + POST /quiz/submit correct=1, total=3 확인
  + 결과 화면의 오답 목록에서 DEMO 2·3 확인
  + Console 오류 없음
```

발표에서는 PR 생성까지 진행하지 않는다. **수정 전과 수정 후의 실행 결과 비교**에서 실습을 끝낸다.

---

# 6. 프론트와 백엔드가 얻는 것

## 프론트엔드

- 실제 사용자 흐름을 AI가 반복 실행한다.
- DOM, Console, Network를 함께 확인한다.
- API 성공과 화면 성공을 구분할 수 있다.
- 모바일·느린 Network 같은 환경도 반복 확인할 수 있다.

## 백엔드

- 실제 브라우저가 보낸 request body를 기준으로 조사한다.
- 상태 코드와 응답 body가 화면에서 어떻게 사용되는지 확인한다.
- Schema 변경의 프론트 영향 범위를 빠르게 찾는다.
- CORS, 인증, API 오류 형식 문제를 사용자 흐름과 연결한다.

## 팀 공통

- "프론트 문제 같다" 또는 "서버 문제 같다"가 아니라 실행 근거로 대화한다.
- 재현 절차와 기대 결과가 작업 명세가 된다.
- 수정 완료 기준이 브라우저의 동일한 사용자 흐름으로 통일된다.

---

# 7. 회사에서 적용할 때의 기준

## 처음 적용할 작업

- 로컬 또는 테스트 환경에서 재현 가능한 문제
- 로그인, 검색, 폼 제출처럼 사용자 흐름이 명확한 기능
- API 요청·응답으로 프론트와 백엔드 경계가 보이는 문제
- 수정 결과를 브라우저에서 바로 확인할 수 있는 문제

## 처음부터 맡기지 않을 작업

- 운영 결제와 실제 주문 생성
- 운영 DB 수정 또는 migration
- 관리자 권한 변경
- 실제 고객 개인정보가 보이는 브라우저 세션
- 원인과 성공 조건이 정해지지 않은 대규모 리팩터링

## 측정할 값

| 지표 | 측정 방법 |
| --- | --- |
| 재현 시간 | 제보 확인부터 동일 증상 재현까지 걸린 시간 |
| 첫 원인 후보 시간 | 조사 시작부터 근거가 있는 첫 원인 후보까지 걸린 시간 |
| 증거 완전성 | 화면·Network·프론트·백엔드 근거 포함 여부 |
| 오진율 | 사람이 기각한 AI 원인 후보 비율 |
| 재검증 성공률 | 수정 후 동일 사용자 흐름 통과 여부 |

---

# 8. 안전하게 사용하는 방법

- 운영 브라우저가 아닌 별도 테스트 프로필을 사용한다.
- 테스트 계정과 가짜 데이터만 사용한다.
- MCP가 접근할 주소를 `localhost` 또는 테스트 도메인으로 제한한다.
- 토큰, 쿠키, 개인정보가 발표 화면에 표시되지 않게 사전 확인한다.
- 처음에는 브라우저 조사와 코드 읽기만 허용한다.
- 코드 수정과 외부 시스템 쓰기는 원인 확인 후 사람이 승인한다.

Chrome DevTools for agents는 연결된 브라우저 내용을 AI가 읽고 조작할 수 있으므로, 개인 계정이 로그인된 일반 브라우저와 분리해야 한다.

---

# 9. 결론

## Before

```text
프론트 확인
  -> 캡처 전달
  -> 백엔드 재확인
  -> 수정
  -> 다시 프론트 확인
```

## After

```text
하나의 사용자 흐름
  -> Browser MCP로 실행 증거 수집
  -> AI가 프론트와 백엔드 코드 연결
  -> 사람이 수정 방향 결정
  -> 동일 흐름으로 재검증
```

## 마지막 메시지

> AI가 코드를 얼마나 많이 작성했는지가 아니라, 실제 사용자 문제를 얼마나 빠르게 재현하고 화면부터 API까지 근거를 연결했는지를 측정해야 한다.

---

# 참고 자료

- [Chrome DevTools for agents](https://developer.chrome.com/docs/devtools/agents)
- [Chrome DevTools MCP 활용 예시](https://developer.chrome.com/blog/chrome-devtools-mcp)
- [CyberAgent runtime debugging 사례](https://developer.chrome.com/blog/autofix-runtime-devtools-mcp)
- [Claude in Chrome](https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome)
- [Codex QA your app with Computer Use](https://learn.chatgpt.com/use-cases/qa-your-app-with-computer-use)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
