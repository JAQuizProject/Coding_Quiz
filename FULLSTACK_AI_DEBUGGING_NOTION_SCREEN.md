# 화면에서 API까지

## Claude·Codex와 Browser MCP로 풀스택 버그 추적하기

> 코드만 읽고 추측하는 AI에서, 실제 화면과 Network를 확인하고 검증하는 AI로.

`25 MIN`  `FRONTEND + BACKEND`  `LIVE DEBUGGING`

---

## 01. PROBLEM

# "제출했는데 결과 화면이 이상해요"

> 사용자에게는 하나의 문제지만, 개발팀은 여러 계층을 따로 확인한다.

| 화면 | 브라우저 | API | 서버 |
| --- | --- | --- | --- |
| 이벤트·상태 | Console·Network | 요청·응답 계약 | Router·Schema·Service |

```text
프론트 확인 → 캡처 전달 → 백엔드 재확인 → 수정 → 다시 프론트 확인
```

**병목은 코드를 작성하는 시간이 아니라 실행 증거를 모으고 계층 사이를 이동하는 시간이다.**

---

## 02. SHIFT

# AI에게 코드를 더 주는 것이 아니라 실행 환경을 보여준다

### BEFORE · 코드만 보는 AI

```text
저장소
  → 관련 파일 검색
  → 정적 코드로 원인 추정
```

### AFTER · 실행 결과를 보는 AI

```text
사용자 조작
  → DOM / Console / Network
  → Chrome DevTools MCP
  → 프론트 + API + 백엔드 추적
  → 같은 흐름으로 재검증
```

> MCP는 AI 모델을 바꾸는 기능이 아니라, AI가 실제 실행 환경을 조사할 수 있게 도구를 연결하는 규격이다.

---

## 03. WHY NOW

# 소스 생성에서 실행 검증으로

| 공식 흐름 | 확인할 내용 |
| --- | --- |
| Chrome DevTools for agents | DOM, Console, Network, 실제 사용자 조작 |
| Claude Build → Test → Verify | 코드 작성 후 브라우저에서 직접 검증 |
| Codex Computer Use QA | 실제 제품 흐름과 재현 가능한 버그 리포트 |
| CyberAgent 사례 | 32개 컴포넌트, 236개 Story 런타임 점검 |

[Chrome DevTools for agents](https://developer.chrome.com/docs/devtools/agents) · [Claude in Chrome](https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome) · [Codex QA](https://learn.chatgpt.com/use-cases/qa-your-app-with-computer-use)

> 공통점은 하나다. AI가 작성한 코드를 설명하는 데서 끝나지 않고, 실행된 결과를 다시 확인한다.

---

## 04. LIVE DEMO

# API는 성공했는데 채점 정책은 실패한다

| 구분 | 내용 |
| --- | --- |
| 사용자 동작 | 로그인 → `LiveDemo` → 답안 3건 제출 → 결과 확인 |
| 기대 결과 | `10.00`만 정답, `correct=1`, `total=3` |
| 실제 결과 | `POST /quiz/submit`은 `200`, `correct=2`, `total=3` |
| 조사 범위 | 브라우저, 프론트 판정 함수, FastAPI 채점 함수 |

```text
브라우저 제출
  → frontend/api/quiz.js
  → POST /quiz/submit
  → FastAPI Service / Grading
  → HTTP 응답
  → 결과 화면
```

### AI에게 맡길 일

```text
문제를 실제 브라우저에서 재현하세요.
아직 수정하지 말고 Console과 Network를 확인하세요.
확인된 사실과 추정을 구분하세요.
프론트와 백엔드 코드 근거를 file:line으로 연결하세요.
가능한 수정안의 API 호환성 영향을 비교하세요.
```

**완료가 아니라 조사부터 시작한다.**

---

## 05. EVIDENCE

# "AI가 그렇게 말했다"는 근거가 아니다

| 확인 항목 | 필요한 증거 |
| --- | --- |
| 재현 | 사용자가 수행한 조작 순서 |
| 브라우저 | Console 오류, Network URL·status·body |
| 프론트 | 실제로 읽는 응답 필드와 상태 처리 코드 |
| 백엔드 | 응답 Schema와 Router·Service 코드 |
| 판단 | 확인된 사실과 추가 확인이 필요한 추정 분리 |

### 조사 결과는 다섯 줄로 제한한다

```text
1. 재현 결과
2. Network 근거
3. 프론트 코드 근거
4. 백엔드 코드 근거
5. 권장 수정안과 영향 범위
```

> 프론트 문제인지 백엔드 문제인지 먼저 정하지 않는다. 실행 증거가 가리키는 계층을 수정한다.

---

## 06. VERIFY

# 수정했다고 말하지 말고 같은 흐름으로 증명한다

### 수정 전

```text
POST /quiz/submit → 200, correct=2
결과 화면 → DEMO 2·3을 잘못 정답 처리
```

### 수정 후

```text
같은 로그인·제출 흐름 재실행
  + DEMO 1만 정답 확인
  + API correct=1 확인
  + DEMO 2·3 오답 목록 확인
  + Console 오류 없음
```

| AI가 수행 | 사람이 결정 |
| --- | --- |
| 재현, 증거 수집, 코드 추적, 최소 수정, 재실행 | 기대 동작, API 계약, 호환성, 최종 승인 |

> 완료 기준은 AI의 답변이 아니라, 같은 사용자 흐름에서 화면과 API가 함께 정상 동작하는 것이다.

---

## 07. APPLY

# 회사에서는 작은 사용자 흐름 하나부터

### 먼저 적용

- 로컬·테스트 환경에서 재현 가능한 문제
- 로그인, 검색, 폼 제출처럼 흐름이 명확한 기능
- API 경계가 보이고 수정 결과를 화면에서 확인할 수 있는 문제

### 측정

| 재현 시간 | 첫 원인 후보 시간 | 근거 완전성 | 재검증 성공률 |
| --- | --- | --- | --- |
| 제보 → 동일 증상 | 조사 → 근거 있는 후보 | 화면·Network·양쪽 코드 | 동일 흐름 통과 여부 |

### 제한

- 테스트 계정과 별도 브라우저 프로필만 사용
- 운영 DB, 결제, 실제 고객 데이터 접근 금지
- 조사와 코드 읽기부터 허용하고 수정은 사람이 승인

---

## 08. TAKEAWAY

# 화면과 API가 같은 증거를 보게 만든다

```text
사용자 흐름
  → Browser MCP로 실행 증거 수집
  → AI가 프론트와 백엔드 코드 연결
  → 사람이 수정 방향 결정
  → 동일 흐름으로 재검증
```

> AI가 코드를 얼마나 많이 작성했는지가 아니라, 실제 사용자 문제를 얼마나 빠르게 재현하고 화면부터 API까지 근거를 연결했는지를 측정해야 한다.

**REPRODUCE · TRACE · DECIDE · VERIFY**
