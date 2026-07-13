# 풀스택 AI 디버깅 발표자 런북

이 문서는 발표자 전용이다. 화면 공유에는 `FULLSTACK_AI_DEBUGGING_NOTION_SCREEN.md`, 실제 AI 입력에는 `demo/LIVE_DEMO_PROMPTS.md`를 사용한다.

## 1. 발표 목표

> AI가 코드를 많이 생성하는 장면이 아니라, 실제 사용자 흐름을 재현하고 화면·Network·프론트·백엔드 근거를 연결한 뒤 같은 흐름으로 수정 결과를 검증하는 과정을 보여준다.

운영 원칙:

1. 브라우저에서 잘못된 결과를 먼저 보여준다.
2. 원인을 미리 말하지 않는다.
3. 조사와 수정을 분리한다.
4. 테스트가 실패하는 장면을 생략하지 않는다.
5. 완료 판단은 테스트와 동일 브라우저 흐름의 재검증으로 한다.
6. Claude와 Codex 중 하나만 사용한다.

## 2. 25분 진행표

| 구간 | 시간 | 화면 |
| --- | ---: | --- |
| 문제와 기준 | 0:00~5:00 | Notion |
| MCP 역할과 공식 사례 | 5:00~8:00 | Notion, 영상 최대 20초 |
| 실제 버그 재현 | 8:00~11:00 | 격리 Chrome |
| AI 조사와 근거 확인 | 11:00~15:00 | Codex + Chrome |
| 실패 테스트와 최소 수정 | 15:00~21:00 | Codex + VS Code |
| 동일 흐름 재검증 | 21:00~23:00 | 격리 Chrome |
| 결론 | 23:00~25:00 | Notion |

## 3. 화면 구성

| 데스크톱 | 화면 | 용도 |
| --- | --- | --- |
| 1 | Notion | 문제, 기준, 결론 |
| 2 | Codex가 연 격리 Chrome | 재현, Network, 재검증 |
| 3 | VS Code + Codex | 테스트, diff, 검증 명령 |

개인 Chrome, `.env`, 토큰, 메신저와 알림은 화면에 노출하지 않는다.

## 4. T-30분 준비

최초 setup을 완료하지 않았다면 실행한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_live_demo.ps1
```

발표 서버를 시작한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_live_demo.ps1
```

발표용 Codex를 새로 연다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\open_live_demo_codex.ps1
```

별도 터미널에서 설정과 baseline을 확인한다.

```powershell
codex mcp get chrome-devtools
git status --short
& '.venv\Scripts\python.exe' -m pytest -q
Set-Location frontend
npm test
npm run lint
```

체크리스트:

- [ ] `chrome-devtools`가 enabled 상태다.
- [ ] 백엔드와 프론트 URL이 열린다.
- [ ] 로그인 계정이 동작한다.
- [ ] `LiveDemo` 카테고리에 3문제가 보인다.
- [ ] baseline 테스트가 통과한다.
- [ ] 현재 제품 코드에는 채점 버그가 남아 있다.
- [ ] `scripts/apply_live_demo_solution.ps1 -CheckOnly`가 통과한다.
- [ ] 발표 자료와 프롬프트를 미리 열었다.

## 5. 화면 1: 문제 제시

발표 멘트:

> 사용자는 퀴즈 결과가 이상하다고 말합니다. 지금은 프론트 문제인지 백엔드 문제인지 정하지 않고, 실제 화면과 Network에서 확인되는 사실부터 모으겠습니다.

보여줄 정책:

```text
10.00 vs 10          -> 같은 숫자이므로 정답
java3 vs python3     -> 텍스트가 다르므로 오답
user 404 vs order 404 -> 숫자만 같으므로 오답
```

## 6. 화면 2: 실제 브라우저 재현

Codex에 `demo/LIVE_DEMO_PROMPTS.md`의 `1. Reproduce and investigate only`를 입력한다.

Codex가 수행할 흐름:

1. `http://127.0.0.1:3000/login` 열기
2. `live-demo@example.com / Demo1234!` 로그인
3. 퀴즈 화면에서 `LiveDemo` 선택
4. `10.00`, `java3`, `user 404` 입력
5. 각 `정답 확인` 클릭
6. 퀴즈 제출
7. Console과 `POST /quiz/submit` 확인

버그 상태에서 보여야 할 결과:

```text
DEMO 1 -> Incorrect
DEMO 2 -> Correct
DEMO 3 -> Correct
POST /quiz/submit -> 200
response -> correct=2, total=3
```

발표 멘트:

> API는 200으로 성공했지만 비즈니스 결과는 틀렸습니다. HTTP 성공과 사용자 성공은 같은 의미가 아닙니다.

## 7. 화면 3: 조사 결과

AI 응답은 아래 다섯 줄로 다시 압축한다.

```text
1. 재현 결과
2. Network 근거
3. 프론트 코드 근거
4. 백엔드 코드 근거
5. 권장 수정 범위
```

반드시 확인할 코드:

```text
frontend/app/quiz/page.js
frontend/utils/answerMatcher.js
app/modules/quiz/service.py
app/modules/quiz/grading.py
```

핵심 근거:

- 프론트와 백엔드가 같은 숫자 추출 오류를 각각 구현하고 있다.
- 숫자 판정이 전체 문자열이 아니라 문자열 안의 숫자 하나에 적용된다.
- 소수점을 제거한 compact 값에서 숫자를 파싱한다.
- 기존 17개 백엔드 테스트와 3개 프론트 테스트는 이 정책을 다루지 않는다.

## 8. 화면 4: 실패 테스트

`demo/LIVE_DEMO_PROMPTS.md`의 `2. Add failing regression tests`를 입력한다.

예상 실패:

```text
backend -> 4 failed
frontend -> 4 failed
```

발표 멘트:

> 빨간 테스트는 실패가 아니라 자연어 정책을 실행 가능한 완료 조건으로 바꾼 결과입니다.

AI가 테스트 대신 기대값을 현재 구현에 맞추거나 제품 코드를 먼저 수정하면 중단하고 범위를 다시 지정한다.

## 9. 화면 5: 최소 수정과 자동 검증

`demo/LIVE_DEMO_PROMPTS.md`의 `3. Implement the minimum fix`를 입력한다.

허용 변경:

```text
app/modules/quiz/grading.py
tests/test_quiz_grading.py
frontend/utils/answerMatcher.js
frontend/tests/answerMatcher.test.mjs
```

금지 변경:

- API schema와 응답 필드
- 인증과 권한
- DB model과 migration
- unrelated refactor
- 신규 라이브러리

정상 검증 결과:

```text
backend target -> 7 passed
backend full -> 24 passed
frontend -> 10 passed
Ruff -> passed
ESLint -> passed
```

검증 후 브라우저 재실행 전에 백엔드를 명시적으로 재시작한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_live_demo.ps1 -RestartBackend -SkipDataPreparation
```

## 10. 화면 6: 동일 브라우저 흐름 재검증

`demo/LIVE_DEMO_PROMPTS.md`의 `4. Re-verify the same browser flow`를 입력한다.

수정 후 기대 결과:

```text
DEMO 1 -> Correct
DEMO 2 -> Incorrect
DEMO 3 -> Incorrect
POST /quiz/submit -> 200
response -> correct=1, total=3
incorrect_items -> DEMO 2, DEMO 3
Console error -> 0
```

발표 멘트:

> 완료 기준은 AI가 수정했다고 말한 것이 아닙니다. 같은 입력과 같은 사용자 흐름에서 화면과 API가 함께 정책을 만족하는 것입니다.

## 11. 라이브 실패 대응

| 실패 | 즉시 전환 |
| --- | --- |
| MCP가 시작되지 않음 | `codex mcp get chrome-devtools` 확인 후 `open_live_demo_codex.ps1`로 재실행 |
| 서버가 꺼짐 | `scripts/start_live_demo.ps1` 재실행 |
| 로그인이 안 됨 | `.venv\Scripts\python.exe scripts\prepare_live_demo.py` 실행 |
| AI 조사가 2분 이상 걸림 | 저장한 5줄 조사 결과를 열고 코드 근거만 확인 |
| 테스트 작성이 지연됨 | `demo/fixtures/`의 예제 테스트 사용 |
| 수정이 꼬임 | diff 확인 후 `scripts/apply_live_demo_solution.ps1` 실행 |
| 브라우저 재검증 실패 | 실패를 숨기지 말고 Network 응답과 남은 원인을 설명 |
| 영상이 재생되지 않음 | 공식 사례 문장만 말하고 영상 생략 |

백업 패치는 발표 전 다음 명령으로 확인한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\apply_live_demo_solution.ps1 -CheckOnly
```

## 12. 마무리

결론 세 문장:

1. AI에게 수정부터 시키지 말고 실제 사용자 흐름과 실행 증거를 먼저 보여준다.
2. 사람이 정한 정책을 실패 테스트로 고정하고 프론트·백엔드에 같은 기준을 적용한다.
3. 테스트 결과와 동일 브라우저 흐름이 모두 통과해야 리뷰 가능한 변경이 된다.

발표 종료 후 서버를 정리한다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop_live_demo.ps1
```
