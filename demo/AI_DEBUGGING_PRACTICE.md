# AI 시대의 디버깅 실습

## 실습 목표

AI에게 바로 수정을 맡기지 않고 다음 증거 기반 루프를 직접 수행한다.

```text
브라우저 재현 -> 증거 수집 -> 실패 테스트 -> 최소 수정 -> 자동 검증 -> 브라우저 재검증
```

도구의 역할은 다음으로 제한한다.

| 도구 | 역할 |
|---|---|
| Chrome DevTools MCP | 화면 조작, Console, Network 증거 수집 |
| Codex | 코드 경로 조사, 테스트 작성, 최소 수정 |
| pytest | 백엔드 요구사항과 회귀 여부 판정 |
| Node test | 프론트엔드 채점 정책 판정 |

별도의 pytest MCP는 사용하지 않는다. 로컬 테스트 실행은 Codex의 터미널 도구가 가장 직접적이며, MCP는 브라우저 관찰과 조작에만 사용한다.

## 1. 실습 시작

저장소 루트에서 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_live_demo.ps1
powershell -ExecutionPolicy Bypass -File scripts\check_ai_debugging_practice.ps1 -RunTests
powershell -ExecutionPolicy Bypass -File scripts\open_live_demo_codex.ps1
```

실습 계정:

```text
URL: http://127.0.0.1:3000/login
Email: live-demo@example.com
Password: Demo1234!
Category: LiveDemo
```

사전 점검의 채점 상태는 반드시 다음과 같아야 한다.

```text
[False, True, True]
```

## 2. 1단계: 수정 없이 재현

Codex에 다음 프롬프트를 입력한다.

```text
Chrome DevTools MCP로 http://127.0.0.1:3000/login 에 접속하세요.

live-demo@example.com / Demo1234! 로 로그인하고 LiveDemo 카테고리를 선택하세요.
다음 답안을 각각 확인한 뒤 퀴즈를 제출하세요.

- DEMO 1: 10.00
- DEMO 2: java3
- DEMO 3: user 404

아직 파일을 수정하지 마세요. 다음 증거만 보고하세요.
1. 답안별 화면 판정
2. Console 오류
3. POST /quiz/submit 상태 코드와 응답 본문
4. 결과를 만든 프론트엔드와 백엔드 코드 경로
5. 확인된 사실과 아직 검증되지 않은 가설
```

통과 조건:

```text
10.00 vs 10              -> 오답
java3 vs python3         -> 정답
user 404 vs order 404    -> 정답
POST /quiz/submit        -> 200, correct=2, total=3
```

핵심은 AI가 원인을 추측한 것과 실제 브라우저 및 Network에서 확인한 사실을 분리하는 것이다.

## 3. 2단계: 실패 테스트로 정책 고정

```text
확인된 채점 버그를 제품 코드 수정 전에 회귀 테스트로 고정하세요.

백엔드:
- tests/test_quiz_grading.py를 만드세요.
- 공개 함수 is_answer_accepted만 직접 테스트하세요.
- pytest.mark.parametrize와 읽을 수 있는 case id를 사용하세요.

프론트엔드:
- frontend/tests/answerMatcher.test.mjs를 확장하세요.
- 공개 함수 isAnswerAccepted를 테스트하세요.

정책:
- 두 입력 전체가 숫자 표현일 때만 숫자 허용 오차를 적용합니다.
- 쉼표, 부호, 소수를 지원합니다.
- 숫자가 같더라도 서로 다른 텍스트는 정답이 아닙니다.
- 빈 입력은 정답이 아닙니다.

제품 코드는 수정하지 말고 대상 테스트를 실행해 예상한 이유로 실패하는지 보고하세요.
```

좋은 회귀 테스트 체크리스트:

- 테스트 이름이 요구사항을 설명한다.
- 정상, 경계, 거부 사례가 구분된다.
- 단순 입력값은 fixture로 숨기지 않는다.
- 구현 내부 함수와 정규식 모양을 직접 검증하지 않는다.
- 실패 메시지에서 어떤 정책이 깨졌는지 확인할 수 있다.

예상 결과는 백엔드와 프론트엔드 모두 실패다. 테스트가 처음부터 통과하면 버그를 재현하지 못한 것이므로 다음 단계로 넘어가지 않는다.

## 4. 3단계: 최소 수정과 자동 검증

```text
실패한 회귀 테스트를 통과시키는 최소 수정만 적용하세요.

제약:
- 백엔드와 프론트엔드 판정 정책을 동일하게 유지합니다.
- API 스키마, DB 모델, 인증, 마이그레이션은 변경하지 않습니다.
- 의존성을 추가하지 않습니다.
- 기존 유사도 로직 전체를 재작성하지 않습니다.

다음을 순서대로 실행하세요.
1. .venv\Scripts\python.exe -m pytest tests/test_quiz_grading.py -q
2. .venv\Scripts\python.exe -m pytest -q
3. .venv\Scripts\python.exe -m ruff check app tests
4. frontend에서 npm test
5. frontend에서 npm run lint

모두 통과하면 다음 명령으로 백엔드를 명시적으로 재시작하세요.
powershell -ExecutionPolicy Bypass -File scripts\start_live_demo.ps1 -RestartBackend -SkipDataPreparation

아직 브라우저 검증이 끝났다고 말하지 마세요.
```

테스트 통과는 코드 수준의 증거다. 실행 중인 서버가 새 코드를 사용하는지는 별도로 확인해야 한다.

## 5. 4단계: 같은 흐름 재검증

```text
Chrome DevTools MCP로 같은 LiveDemo 흐름을 깨끗한 상태에서 반복하세요.

- DEMO 1: 10.00
- DEMO 2: java3
- DEMO 3: user 404

다섯 줄로 다음을 보고하세요.
1. DEMO 1 화면 판정
2. DEMO 2 화면 판정
3. DEMO 3 화면 판정
4. POST /quiz/submit 상태와 correct/total
5. 결과 페이지 오답 목록과 Console 오류 수
```

최종 통과 조건:

```text
10.00 vs 10              -> 정답
java3 vs python3         -> 오답
user 404 vs order 404    -> 오답
POST /quiz/submit        -> 200, correct=1, total=3
오답 목록                -> DEMO 2, DEMO 3
Console                  -> 새 오류 없음
```

환경 상태만 빠르게 확인하려면 다음 명령을 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check_ai_debugging_practice.ps1 -ExpectedState Fixed
```

## 6. 실습 정리

다음 질문에 답할 수 있으면 실습이 완료된 것이다.

1. AI의 첫 번째 가설은 어떤 증거로 확인했는가?
2. 회귀 테스트가 고정한 사용자 정책은 무엇인가?
3. 최소 수정 범위를 어떻게 제한했는가?
4. 테스트 통과 후 브라우저 재검증이 별도로 필요한 이유는 무엇인가?
5. 최종 결과를 다시 재현할 수 있는가?

발표용 수정이 막히면 `scripts\apply_live_demo_solution.ps1`을 사용한다. 이는 실습 풀이용이 아니라 라이브 발표 복구용이다.
