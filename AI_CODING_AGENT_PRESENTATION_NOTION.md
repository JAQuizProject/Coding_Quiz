# AI 코딩 에이전트 실무 적용: 테스트로 요구사항을 고정하고 PR까지 검증하기

## 발표 주제 한 줄

Claude와 Codex를 단순한 코드 생성기로 소개하는 대신, 실제 결함 한 건을 **작업 명세 -> 실패 테스트 -> 최소 수정 -> 자동 검증 -> 사람 리뷰** 순서로 처리하는 팀 개발 방식을 보여준다.

## 발표에서 전달할 한 문장

> AI가 코드를 작성하게 할 수는 있지만, 무엇이 올바른 코드인지는 팀이 요구사항과 테스트로 먼저 정의해야 한다.

## 이 발표가 다루는 범위

- 대상: 제품 코드를 수정하고 리뷰하는 개발팀
- 도구: Claude Code, Codex 등 저장소를 읽고 파일과 명령을 다루는 AI 코딩 에이전트
- 중심 문제: AI가 만든 변경을 어떻게 신뢰 가능한 PR 후보로 만들 것인가
- 실습: 이 저장소의 실제 채점 로직 오류를 테스트부터 수정하는 과정
- MCP: 실습의 주제가 아니라, 이슈·문서·로그를 AI에게 전달하는 다음 단계

## 이 발표가 다루지 않는 것

- 모델 성능 비교
- 프롬프트 문장 작성 요령만 나열하기
- AI가 개발자를 대체하는지에 대한 전망
- AI가 작성한 코드의 양 자랑하기
- 운영 배포나 DB 변경까지 완전 자동화하기

---

# 전체 발표 순서

30분 발표 기준이다.

| 순서 | 내용 | 시간 | 청중이 이해해야 할 것 |
| --- | --- | ---: | --- |
| 1 | 주제 설명 | 7분 | AI 활용의 핵심은 코드 생성보다 검증 구조다 |
| 2 | 실제 사례와 외부 근거 | 6분 | 현업 도구들도 탐색·계획·테스트·리뷰 흐름을 강조한다 |
| 3 | 라이브 실습 | 12분 | 실제 오류를 테스트로 고정하고 AI로 최소 수정한다 |
| 4 | MCP와 회사 적용안 | 4분 | 컨텍스트 연결은 MCP, 정답 검증은 테스트가 맡는다 |
| 5 | 마무리 | 1분 | 작은 작업부터 팀 규칙으로 표준화한다 |

---

# 1. 주제 설명

## 1-1. 발표 시작은 정의가 아니라 오류 화면으로 한다

첫 화면에서 아래 두 결과를 보여준다.

```text
java3     vs python3  -> 정답 처리
10.00     vs 10       -> 오답 처리
```

발표 멘트:

> 지금 보이는 결과는 AI가 만든 예제가 아니라 이 프로젝트의 현재 서버 채점 결과입니다.  
> 여기서 AI에게 "채점 버그를 고쳐줘"라고 말하면 AI는 코드를 만들 수 있습니다.  
> 하지만 `10점`도 허용할지, 소수 오차는 얼마까지 허용할지, 영문과 숫자가 섞인 답은 어떻게 비교할지는 AI가 결정할 문제가 아닙니다.

이 장면으로 발표의 질문을 바로 제시한다.

> AI에게 어떤 코드를 만들게 할 것인가보다, 올바른 결과를 어떤 기준으로 고정할 것인가?

## 1-2. 회사에서 생기는 실제 문제

Claude나 Codex를 회사에서 사용할 수 있어도 다음 문제가 남는다.

1. 같은 작업도 개발자마다 요청 방식과 결과 품질이 다르다.
2. 프로젝트 규칙을 매번 채팅에서 반복한다.
3. AI가 수정 범위를 불필요하게 넓힐 수 있다.
4. 코드는 빨리 만들어지지만 리뷰어가 확인할 내용은 더 많아진다.
5. AI가 사내 이슈, 장애 로그, API 규칙을 몰라 잘못된 문제를 풀 수 있다.
6. "테스트를 통과했다"는 말은 남지만 실제 실행 명령과 결과는 남지 않을 수 있다.

따라서 회사의 기준은 "누가 더 좋은 프롬프트를 쓰는가"가 아니라 다음 흐름이어야 한다.

```text
업무 맥락
  -> 성공 조건
  -> 실패 테스트
  -> 최소 코드 변경
  -> 자동 검증
  -> diff 리뷰
  -> PR
```

## 1-3. AI에게 전달할 것은 프롬프트가 아니라 작업 명세다

실무 작업은 아래 다섯 항목으로 고정한다.

| 항목 | 답해야 하는 질문 | 이번 실습 예시 |
| --- | --- | --- |
| 문제 | 현재 무엇이 잘못됐는가 | 숫자가 포함됐다는 이유로 다른 문자열을 같은 답으로 처리한다 |
| 성공 조건 | 어떤 입력이 통과·실패해야 하는가 | `10.00`과 `10`은 일치, `java3`와 `python3`은 불일치 |
| 변경 범위 | 어디까지 수정할 수 있는가 | 서버 채점 함수와 해당 단위 테스트만 수정 |
| 금지 범위 | 무엇을 건드리지 않는가 | 프론트, DB, API 응답 형식은 변경하지 않음 |
| 검증 방법 | 무엇을 실행하면 완료인가 | 대상 테스트, 전체 테스트, Ruff가 모두 통과 |

이 다섯 항목이 있으면 Claude와 Codex 중 어떤 도구를 사용해도 같은 품질 기준을 적용할 수 있다.

## 1-4. AI에게 맡기기 좋은 작업을 고르는 기준

처음부터 큰 기능 개발을 맡기지 않는다. 아래 조건을 많이 만족할수록 첫 적용에 적합하다.

- 현재 동작을 재현할 수 있다.
- 성공과 실패를 테스트나 명령으로 판정할 수 있다.
- 변경 파일을 1~3개로 제한할 수 있다.
- 기존 코드 안에 참고할 패턴이 있다.
- 운영 데이터나 권한 변경이 필요하지 않다.
- 사람이 10분 안에 diff를 이해할 수 있다.

### 작업 위험도 기준

| 등급 | 예시 | AI 사용 방식 |
| --- | --- | --- |
| Green | 회귀 테스트 추가, 작은 버그 수정, 반복 코드 정리, 문서 갱신 | 구현과 검증까지 맡기고 사람이 diff 리뷰 |
| Yellow | API 계약 변경, 성능 개선, 의존성 업그레이드, 여러 모듈 수정 | 계획과 테스트를 사람이 먼저 승인한 뒤 구현 |
| Red | 인증·권한, 결제, DB migration, 데이터 삭제, 운영 배포, secret 처리 | AI는 분석 보조만 사용하고 실행은 별도 승인 |

이번 발표 실습은 **Green 작업** 하나를 끝까지 처리한다.

## 1-5. 용어는 이렇게 통일한다

| 사용할 표현 | 의미 |
| --- | --- |
| AI 코딩 에이전트 | 저장소를 읽고, 파일을 수정하고, 테스트 명령을 실행하는 도구 |
| 작업 명세 | 문제·성공 조건·범위·검증 방법을 적은 입력 |
| 회귀 테스트 | 같은 오류가 다시 생기지 않도록 현재 결함을 고정한 테스트 |
| 검증 근거 | 실행한 명령, 테스트 결과, lint 결과, diff 요약 |
| 팀 규칙 파일 | `AGENTS.md`, `CLAUDE.md` 등 도구가 저장소에서 읽는 개발 규칙 |
| MCP | AI가 GitHub, 문서, 로그 같은 외부 시스템의 컨텍스트와 도구에 연결되는 표준 |

피할 표현:

- 서버 개발자는 무엇을 검증해야 하나
- AI Agent 시대의 거버넌스
- 프롬프트 엔지니어링 발표
- AI 코딩 자동화

---

# 2. 실제 사례와 외부 근거

## 2-1. 이 저장소에서 확인한 실제 사례

대상 파일:

```text
app/modules/quiz/grading.py
```

현재 결과를 재현하는 명령:

```powershell
& '.venv\Scripts\python.exe' -c "from app.modules.quiz.grading import is_answer_accepted; cases=[('java3','python3'),('status 404','http 404'),('10.00','10')]; print([(u,c,is_answer_accepted(u,c)) for u,c in cases])"
```

현재 출력:

```text
[
  ('java3', 'python3', True),
  ('status 404', 'http 404', True),
  ('10.00', '10', False)
]
```

### 원인

현재 구현에는 두 문제가 같이 있다.

1. 문자열에서 숫자를 하나씩 찾으면, 나머지 글자가 달라도 숫자만 비교한다.
2. 숫자를 파싱하기 전에 `.` 같은 기호를 제거해 `10.00`을 `1000`처럼 만든다.

### 이 사례가 발표 실습에 적합한 이유

- 결과가 눈에 바로 보인다.
- 서버의 실제 비즈니스 로직이다.
- DB나 외부 API가 필요 없다.
- 테스트로 요구사항을 명확히 표현할 수 있다.
- 수정 파일을 채점 함수와 테스트 파일로 제한할 수 있다.
- AI가 과하게 수정했는지 사람이 diff로 쉽게 판단할 수 있다.

## 2-2. 왜 테스트가 필요한가: 사용은 많지만 신뢰는 낮다

Stack Overflow 2025 Developer Survey에서는 AI 도구의 정확성을 신뢰하지 않는 응답이 46%, 신뢰한다는 응답이 33%였다. "매우 신뢰한다"는 응답은 약 3%였다.

발표에서 사용할 해석:

> AI 사용 여부는 이미 핵심 쟁점이 아닙니다. 결과를 검증할 수 있는 구조가 있는지가 핵심입니다.

출처: [Stack Overflow 2025 Developer Survey - AI](https://survey.stackoverflow.co/2025/ai)

## 2-3. Claude Code도 탐색과 계획을 구현에서 분리한다

Anthropic의 Claude Code best practices는 복잡한 작업에서 다음 흐름을 안내한다.

```text
Explore -> Plan -> Implement -> Commit
```

또한 구체적인 파일, 시나리오, 테스트 조건을 요청에 포함하고, 별도 세션을 Writer와 Reviewer로 나누는 방식도 제시한다.

발표에서 사용할 메시지:

> AI에게 바로 수정부터 시키면 잘못 이해한 문제를 빠르게 구현할 수 있습니다. 먼저 관련 코드와 테스트를 읽게 하고, 계획을 검토한 뒤 수정해야 합니다.

출처: [Claude Code best practices](https://code.claude.com/docs/en/best-practices)

## 2-4. Codex는 저장소 규칙과 테스트 결과를 작업 근거로 사용한다

OpenAI 공식 문서에 따르면 Codex는 작업 전 저장소의 `AGENTS.md`를 읽고, 프로젝트별 명령과 기대사항을 적용할 수 있다. OpenAI의 Codex 소개에서도 테스트, lint, typecheck 실행 결과와 사람이 검토할 수 있는 근거를 중요하게 다룬다.

발표에서 사용할 메시지:

> 반복해서 말하는 규칙은 개인 프롬프트에 두지 말고 저장소 안에 둬야 합니다. AI가 바뀌어도 팀의 완료 기준은 남아야 합니다.

출처:

- [Codex AGENTS.md 공식 문서](https://developers.openai.com/codex/guides/agents-md)
- [OpenAI - Introducing Codex](https://openai.com/index/introducing-codex/?video=1084810944)

## 2-5. 현업 결과물은 채팅 답변이 아니라 branch와 PR로 이동하고 있다

GitHub Copilot cloud agent 공식 문서는 에이전트가 저장소를 조사하고, 구현 계획을 만들고, branch에서 코드를 변경하며, 테스트와 lint를 실행한 뒤 개발자가 diff를 검토하고 PR을 만들 수 있다고 설명한다.

발표에서 사용할 메시지:

> AI 코딩 도구의 결과물은 이제 코드 블록이 아니라 리뷰해야 할 변경사항입니다. 그래서 생성 속도보다 PR 진입 조건이 중요합니다.

출처: [GitHub Copilot cloud agent 공식 문서](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)

## 2-6. 발표에 넣을 영상

영상은 제품 홍보를 위해 길게 틀지 않는다. 20~30초만 사용해 "AI가 파일 수정, 테스트 실행, PR 후보 생성까지 한다"는 공통 인식을 만드는 용도다.

추천 1, Claude Code 실무 흐름:

- [Anthropic YouTube - Mastering Claude Code in 30 minutes](https://www.youtube.com/watch?v=6eBSHbLKuN0)
- 사용할 부분: 코드베이스 탐색, 작업 지시, 검증 루프를 설명하는 장면

추천 2, Codex의 작업 결과와 검증 근거:

- [OpenAI - Introducing Codex](https://openai.com/index/introducing-codex/?video=1084810944)
- 사용할 부분: 저장소 작업, 테스트 결과, 리뷰 가능한 변경사항이 보이는 장면

추천 3, branch와 PR까지 이어지는 에이전트 작업:

- [GitHub YouTube - Run code generation in the background with GitHub Copilot coding agents](https://www.youtube.com/watch?v=S1ch_6fjp5M)
- 참고 글: [What's new with GitHub Copilot coding agent](https://github.blog/ai-and-ml/github-copilot/whats-new-with-github-copilot-coding-agent/)
- 사용할 부분: 에이전트가 branch에서 작업하고 PR 후보를 준비하는 장면

영상 직후 멘트:

> 도구별 화면은 다르지만 공통점은 같습니다. 저장소를 읽고, 변경하고, 검증하고, 사람이 리뷰합니다. 지금부터 이 흐름을 실제 코드로 보여드리겠습니다.

---

# 3. 라이브 실습

## 3-1. 실습 제목

> 숫자 채점 오류를 실패 테스트부터 수정하고 리뷰 가능한 변경으로 만들기

## 3-2. 실습에서 보여줄 것

```text
오류 재현
  -> AI의 코드 탐색
  -> 성공 조건 확정
  -> 실패 테스트 작성
  -> 최소 수정
  -> 대상 테스트
  -> 전체 테스트와 lint
  -> 별도 관점의 diff 리뷰
  -> PR 설명 생성
```

## 3-3. 발표 전 준비

라이브 실습 전에 다음을 준비한다.

- 현재 버그가 남아 있는 시작 commit
- 수정이 끝난 백업 commit 또는 patch
- `tests/test_quiz_grading.py`의 백업 내용
- 터미널 글자 크기 확대
- 네트워크 없이도 실행 가능한 로컬 환경
- Claude 또는 Codex가 실패할 경우 보여줄 diff 캡처

현재 저장소의 정상 기준:

```powershell
& '.venv\Scripts\python.exe' -m pytest -q
& '.venv\Scripts\python.exe' -m ruff check app/modules/quiz/grading.py
```

발표 준비 시 확인한 결과:

```text
17 passed
All checks passed!
```

주의:

```text
전역 Python에는 watchdog과 ruff가 없을 수 있다.
발표에서는 반드시 .venv\Scripts\python.exe를 사용한다.
```

## 3-4. 0단계: 오류를 먼저 보여준다

실행:

```powershell
& '.venv\Scripts\python.exe' -c "from app.modules.quiz.grading import is_answer_accepted; cases=[('java3','python3'),('status 404','http 404'),('10.00','10')]; print([(u,c,is_answer_accepted(u,c)) for u,c in cases])"
```

발표 멘트:

> 코드부터 보지 않고 사용자에게 보이는 잘못된 결과를 먼저 고정하겠습니다. 이 결과가 오늘 작업의 출발점입니다.

## 3-5. 1단계: 바로 수정하지 말고 탐색만 시킨다

Claude 또는 Codex에 입력:

```text
app/modules/quiz/grading.py의 정답 판정 흐름을 분석해줘.

다음 두 현상의 원인을 함수 호출 순서에 따라 설명해줘.
- java3가 python3의 정답으로 처리된다.
- 10.00이 10의 오답으로 처리된다.

아직 파일을 수정하지 말고 다음만 보고해줘.
1. 관련 함수와 조건문
2. 각 입력이 어떤 중간값으로 변환되는지
3. 수정 시 깨질 수 있는 기존 동작
4. 먼저 추가해야 할 테스트 목록
```

확인할 것:

- 숫자 비교가 `_compact` 이후 실행되는 것을 찾았는가
- 텍스트가 포함된 문자열에도 숫자 비교를 적용하는 것을 찾았는가
- 기존 exact, compact, token, similarity 비교의 회귀 위험을 언급하는가

발표 멘트:

> 이 단계의 목적은 AI의 설명을 믿는 것이 아니라, AI와 사람이 같은 문제를 보고 있는지 확인하는 것입니다.

## 3-6. 2단계: 사람이 성공 조건을 확정한다

AI가 임의로 정책을 정하지 않도록 아래 기준을 사람이 제공한다.

| 사용자 입력 | 저장된 정답 | 기대 결과 | 이유 |
| --- | --- | --- | --- |
| `10` | `10` | 정답 | 완전 일치 |
| `10.00` | `10` | 정답 | 순수 숫자는 값으로 비교 |
| `10.009` | `10` | 정답 | 기존 허용 오차 `0.01` 이내 |
| `10.02` | `10` | 오답 | 허용 오차 초과 |
| `1,000` | `1000` | 정답 | 숫자 천 단위 구분 허용 |
| `java3` | `python3` | 오답 | 숫자가 같아도 텍스트가 다름 |
| `status 404` | `http 404` | 오답 | 숫자가 같아도 의미가 다른 문자열 |

정책 문장:

> 숫자 오차 비교는 양쪽 값 전체가 숫자 표현일 때만 적용한다. 텍스트가 섞여 있으면 기존 문자열 비교 규칙을 적용한다.

## 3-7. 3단계: 실패 테스트를 먼저 작성한다

입력:

```text
방금 확정한 표를 tests/test_quiz_grading.py의 pytest parameterized test로 작성해줘.

조건:
- 제품 코드는 아직 수정하지 않는다.
- 공개 함수 is_answer_accepted만 테스트한다.
- 테스트 이름에서 숫자 전용 비교 정책이 드러나게 한다.
- 테스트를 실행하고 현재 어떤 케이스가 왜 실패하는지 보고한다.
```

발표자용 백업 테스트:

```python
import pytest

from app.modules.quiz.grading import is_answer_accepted


@pytest.mark.parametrize(
    ("user_answer", "expected_answer", "accepted"),
    [
        ("10", "10", True),
        ("10.00", "10", True),
        ("10.009", "10", True),
        ("10.02", "10", False),
        ("1,000", "1000", True),
        ("java3", "python3", False),
        ("status 404", "http 404", False),
    ],
)
def test_numeric_tolerance_applies_only_to_numeric_answers(
    user_answer: str,
    expected_answer: str,
    accepted: bool,
) -> None:
    assert is_answer_accepted(user_answer, expected_answer) is accepted
```

실행:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_quiz_grading.py -q
```

현재 구현에서는 4개 케이스가 실패하는 것이 정상이다.

발표 멘트:

> 빨간 테스트는 실패가 아니라 작업 범위가 코드로 표현됐다는 뜻입니다. 이제 AI에게 줄 완료 기준이 생겼습니다.

## 3-8. 4단계: 최소 수정만 요청한다

입력:

```text
tests/test_quiz_grading.py의 실패 테스트를 통과시키는 최소 수정만 해줘.

구현 조건:
- 숫자 허용 오차 비교는 양쪽 전체가 숫자 형식일 때만 적용한다.
- 숫자 파싱은 마침표를 제거하는 compact 처리 전에 수행한다.
- 쉼표 천 단위, 부호, 소수를 지원한다.
- exact, compact, token, similarity의 기존 순서는 필요한 범위 외에는 바꾸지 않는다.
- frontend와 API schema는 수정하지 않는다.
- 새로운 외부 라이브러리를 추가하지 않는다.

수정 후 다음을 보고해줘.
1. 변경 파일
2. 핵심 변경 이유
3. 실행한 검증 명령과 결과
4. 남은 위험
```

사람이 diff에서 확인할 것:

- 숫자 전체 일치를 확인하는 조건이 생겼는가
- 원래 문자열에서 숫자를 파싱하는가
- 기존 문자열 유사도 로직을 불필요하게 재작성하지 않았는가
- 테스트를 통과시키기 위해 기대값을 바꾸지 않았는가
- 요청하지 않은 파일을 건드리지 않았는가

## 3-9. 5단계: 검증을 좁은 범위에서 넓은 범위로 실행한다

1차, 변경한 로직의 대상 테스트:

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_quiz_grading.py -q
```

2차, 기존 기능 회귀 확인:

```powershell
& '.venv\Scripts\python.exe' -m pytest -q
```

3차, 정적 검사:

```powershell
& '.venv\Scripts\python.exe' -m ruff check app/modules/quiz/grading.py tests/test_quiz_grading.py
```

완료 조건:

```text
[ ] 새 회귀 테스트가 모두 통과한다.
[ ] 기존 17개 테스트가 계속 통과한다.
[ ] Ruff 오류가 없다.
[ ] 변경 파일이 의도한 범위 안에 있다.
[ ] 테스트 출력이 PR 설명에 기록된다.
```

## 3-10. 6단계: 작성자와 리뷰어의 관점을 분리한다

가능하면 새 Claude/Codex 세션에서 리뷰한다. 같은 대화의 AI는 자신이 선택한 접근을 정당화하는 방향으로 볼 수 있기 때문이다.

리뷰 입력:

```text
현재 git diff를 코드 리뷰해줘.

우선순위:
1. 숫자 파싱의 잘못된 허용 또는 거부
2. 기존 문자열 정답 판정의 회귀
3. 경계값 0.01과 부동소수점 문제
4. 테스트 누락
5. 요청 범위를 벗어난 수정

코드를 다시 작성하지 말고, 발견한 문제를 심각도 순으로 파일과 근거를 붙여 보고해줘.
문제가 없으면 남아 있는 테스트 공백을 명시해줘.
```

사람 리뷰 체크리스트:

```text
[ ] 성공 조건과 테스트가 일치하는가
[ ] 테스트가 구현 세부사항이 아니라 사용자 동작을 검증하는가
[ ] diff가 작고 설명 가능한가
[ ] 테스트를 우회하는 하드코딩이 없는가
[ ] 에이전트가 보고한 테스트를 실제로 실행했는가
[ ] 최종 merge 판단을 사람이 했는가
```

## 3-11. 7단계: PR 설명까지 같은 형식으로 남긴다

입력:

```text
현재 변경사항의 PR 설명 초안을 작성해줘.

형식:
## 문제
## 원인
## 변경 내용
## 검증
## 영향 범위와 남은 위험

검증에는 실제 실행한 명령과 결과만 적고, 실행하지 않은 검증은 적지 마.
```

좋은 PR 설명의 예:

```md
## 문제

숫자가 하나 포함된 서로 다른 문자열이 숫자만 같으면 정답으로 처리됐고,
소수점이 제거되어 순수 숫자 비교도 잘못될 수 있었습니다.

## 원인

숫자 비교가 전체 문자열의 숫자 여부를 확인하지 않았고,
기호 제거 이후의 값을 숫자로 파싱했습니다.

## 변경 내용

- 양쪽 전체가 숫자 표현인 경우에만 숫자 허용 오차를 적용했습니다.
- 숫자 파싱을 compact 처리 전에 수행했습니다.
- 숫자 및 문자 혼합 입력의 회귀 테스트를 추가했습니다.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/test_quiz_grading.py -q`
- `.venv\Scripts\python.exe -m pytest -q`
- `.venv\Scripts\python.exe -m ruff check app/modules/quiz/grading.py tests/test_quiz_grading.py`

## 영향 범위와 남은 위험

- 서버 채점 함수에만 영향을 줍니다.
- 단위가 포함된 숫자 표현은 순수 숫자로 처리하지 않습니다.
```

## 3-12. 12분 실습 진행표

| 시간 | 화면 | 설명 |
| ---: | --- | --- |
| 0:00~1:00 | 잘못된 채점 출력 | 사용자에게 보이는 문제부터 시작 |
| 1:00~3:00 | AI 분석 결과 | 수정 전에 원인과 회귀 위험 확인 |
| 3:00~4:00 | 성공 조건 표 | 정책은 사람이 결정 |
| 4:00~6:00 | 실패 테스트와 빨간 결과 | 테스트를 실행 가능한 요구사항으로 사용 |
| 6:00~8:00 | AI 수정 diff | 최소 변경인지 확인 |
| 8:00~10:00 | 대상·전체 테스트와 lint | 완료 근거를 실제 출력으로 확인 |
| 10:00~11:00 | 새 세션 리뷰 | 작성과 리뷰 관점 분리 |
| 11:00~12:00 | PR 설명 | 작업 결과를 팀이 검토할 형태로 마무리 |

---

# 4. MCP는 어디에 넣을 것인가

## 4-1. MCP의 역할을 과장하지 않는다

MCP 공식 문서는 MCP를 AI 애플리케이션과 외부 데이터·도구·워크플로우를 연결하는 공개 표준으로 설명한다.

출처: [Model Context Protocol 공식 소개](https://modelcontextprotocol.io/docs/getting-started/intro)

이 발표에서는 역할을 다음처럼 구분한다.

```text
MCP   = AI가 무엇을 왜 수정해야 하는지 파악할 컨텍스트를 연결
Test  = 수정 결과가 우리가 정한 조건을 만족하는지 검증
Review = 테스트가 놓친 설계·보안·운영 위험을 사람이 판단
```

핵심 멘트:

> MCP가 연결됐다고 코드가 자동으로 올바르게 되는 것은 아닙니다. MCP는 맥락 부족을 줄이고, 테스트는 결과의 정답 기준을 고정합니다.

## 4-2. 회사에서 연결할 순서

처음에는 조회 전용으로 시작한다.

| 순서 | 연결 대상 | AI가 얻는 정보 | 권한 |
| --- | --- | --- | --- |
| 1 | GitHub issue와 PR | 작업 배경, 논의, 리뷰 의견 | Read-only |
| 2 | 사내 개발 문서 | API 규칙, 코딩 규칙, 장애 대응 절차 | Read-only |
| 3 | 로그와 오류 추적 | 에러 메시지, 발생 조건, trace | Read-only, 민감정보 마스킹 |
| 4 | DB schema | 테이블과 관계 구조 | Read-only, 운영 데이터 제외 |
| 5 | PR comment | 분석·리뷰 결과 기록 | 제한적 Write |

초기에는 열지 않을 것:

- 운영 DB 쓰기
- 배포 실행
- migration 적용
- 권한 변경
- secret 조회
- 이슈나 PR의 자동 종료·merge

## 4-3. MCP를 붙인 실제 흐름

```text
GitHub issue
사내 API 문서
장애 로그
      |
      v
Read-only MCP
      |
      v
AI가 작업 명세 초안 작성
      |
      v
사람이 성공 조건 승인
      |
      v
저장소 수정 + 테스트 실행
      |
      v
사람 리뷰 + PR
```

MCP를 실습에 포함하고 싶다면 코드 수정 장면을 늘리지 말고, 시작 전에 다음 한 장면만 추가한다.

```text
GitHub issue와 오류 로그를 읽고,
문제·재현 조건·성공 조건·변경 금지 범위로 나눠
작업 명세 초안을 만들어줘.
아직 코드는 수정하지 마.
```

---

# 5. 회사 적용안

## 5-1. 여러 AI 도구를 써도 팀 기준은 하나로 둔다

Claude와 Codex별로 규칙을 따로 관리하면 내용이 어긋날 수 있다. 공통 규칙 문서를 하나 두고 각 도구의 파일에서 읽도록 지시한다.

```text
docs/AI_WORKFLOW.md     # 팀 공통 작업·검증 기준
AGENTS.md               # Codex가 공통 문서를 읽도록 안내
CLAUDE.md               # Claude가 공통 문서를 읽도록 안내
.github/pull_request_template.md
```

`docs/AI_WORKFLOW.md`에 들어갈 최소 내용:

```md
# AI-assisted development workflow

## Before editing

- Reproduce the current behavior first.
- Identify related code and existing tests.
- State the acceptance criteria and files expected to change.
- Ask before changing API contracts, auth, permissions, migrations, or production data logic.

## While editing

- For bug fixes, add a failing regression test first.
- Keep the diff focused on the approved scope.
- Do not weaken or delete tests only to make checks pass.

## Verification

- Run targeted tests first, then the broader suite.
- Run the repository's lint and type checks.
- Report exact commands, results, and checks that could not be run.

## Final report

- Summarize changed files and behavior.
- List test evidence.
- State remaining risks and assumptions.
```

## 5-2. 4주 파일럿

### 1주차: 기준 만들기

- 저장소 한 개를 선정한다.
- Green 작업만 대상으로 한다.
- 공통 작업 명세와 리뷰 체크리스트를 만든다.
- 테스트·lint 명령을 팀 규칙 파일에 적는다.

### 2주차: 실제 작업 5건 적용

- 작은 버그 수정 2건
- 회귀 테스트 추가 2건
- 문서 또는 단순 리팩토링 1건
- 모든 작업에 같은 PR 형식을 사용한다.

### 3주차: Read-only MCP 추가

- GitHub issue 또는 사내 문서 한 곳만 연결한다.
- AI가 읽은 출처를 작업 명세에 남긴다.
- 쓰기 권한과 운영 시스템 연결은 제외한다.

### 4주차: 결과 검토

- 반복해서 누락되는 컨텍스트를 팀 규칙에 추가한다.
- AI가 자주 넓히는 변경 범위를 금지 규칙으로 추가한다.
- 효과가 확인된 작업 유형만 범위를 넓힌다.

## 5-3. 측정할 지표

코드 생성량이나 AI 사용 횟수는 핵심 지표로 삼지 않는다.

| 지표 | 확인하려는 것 |
| --- | --- |
| 작업 시작부터 review-ready PR까지 걸린 시간 | 실제 리드타임이 줄었는가 |
| PR당 수정 요청 횟수 | 리뷰 부담이 줄었는가 |
| 검증 명령이 기록된 PR 비율 | 완료 근거가 남는가 |
| 회귀 테스트가 추가된 버그 수정 비율 | 같은 결함을 막는가 |
| merge 후 revert·hotfix 수 | 속도가 품질을 해치지 않았는가 |
| AI가 범위를 벗어난 횟수 | 작업 명세와 팀 규칙이 충분한가 |

## 5-4. 도입 여부 판단 기준

4주 뒤 다음 조건을 만족하면 다른 저장소로 확대한다.

- review-ready PR까지 걸린 시간이 줄었다.
- 리뷰 수정 횟수나 merge 후 결함이 늘지 않았다.
- 검증 결과가 PR에 일관되게 남았다.
- 팀원이 동일한 작업 명세 형식을 사용할 수 있다.
- MCP 없이도 기본 흐름이 동작하고, MCP 연결이 실제 컨텍스트 누락을 줄였다.

---

# 6. 마무리

## 결론 세 가지

1. AI에게 코드를 맡기기 전에 사람이 성공 조건과 금지 범위를 정한다.
2. 자연어 요구사항을 실패 테스트로 바꾸고, 테스트 결과를 PR의 완료 근거로 남긴다.
3. MCP는 업무 맥락을 연결하되, 코드의 정답 여부는 테스트와 사람 리뷰로 검증한다.

## 마지막 슬라이드 문장

> AI 코딩 에이전트의 실무 가치는 코드를 많이 생성하는 데 있지 않다.  
> 팀이 정의한 기준을 따라, 검증 가능한 작은 변경을 더 빠르게 만드는 데 있다.

## 마지막 발표 멘트

> 회사에서 바로 시작할 일은 거대한 AI 개발 플랫폼을 만드는 것이 아닙니다.  
> 저장소 하나와 작은 버그 하나를 고르고, 작업 명세와 실패 테스트를 먼저 만든 뒤, AI가 만든 변경을 같은 기준으로 리뷰해보는 것입니다.

---

# 발표자 최종 체크리스트

```text
[ ] 제목에서 서버 개발자, 거버넌스 같은 추상 표현을 제거했다.
[ ] 첫 1분 안에 실제 잘못된 결과를 보여준다.
[ ] AI보다 성공 조건과 테스트가 먼저라는 메시지가 반복된다.
[ ] 실습 시작 commit과 백업 patch를 준비했다.
[ ] .venv의 Python으로 전체 테스트와 Ruff를 확인했다.
[ ] 영상은 30초 이내로 잘라 두었다.
[ ] MCP는 코드 생성 기능이 아니라 컨텍스트 연결로 설명한다.
[ ] 운영 쓰기 권한은 초기 적용 범위에서 제외한다.
[ ] 마지막에 4주 파일럿이라는 구체적 제안을 남긴다.
```
