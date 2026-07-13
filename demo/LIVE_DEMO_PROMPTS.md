# Live browser debugging prompts

## Demo account

```text
URL: http://127.0.0.1:3000/login
Email: live-demo@example.com
Password: Demo1234!
Category: LiveDemo
```

## 1. Reproduce and investigate only

```text
Use the chrome-devtools MCP server and the local repository.

Open http://127.0.0.1:3000/login and sign in with:
- email: live-demo@example.com
- password: Demo1234!

Go to the quiz page, select the LiveDemo category, and enter these answers:
- DEMO 1: 10.00
- DEMO 2: java3
- DEMO 3: user 404

Click each answer check button, then submit the quiz.

Do not edit files yet. Report only:
1. The visible result for each answer
2. Console errors
3. The POST /quiz/submit request status and response body
4. The frontend and backend code paths that produced the result, with file:line evidence
5. Confirmed facts versus hypotheses
```

Expected buggy result:

```text
10.00 vs 10       -> incorrect
java3 vs python3  -> correct
user 404 vs order 404 -> correct
POST /quiz/submit -> 200, correct=2, total=3
```

## 2. Add failing regression tests

```text
Turn the confirmed grading policy into regression tests before changing product code.

Backend:
- create tests/test_quiz_grading.py
- test the public is_answer_accepted function

Frontend:
- extend frontend/tests/answerMatcher.test.mjs
- test the public isAnswerAccepted function

Required policy:
- numeric tolerance applies only when both complete values are numeric expressions
- parse numbers before punctuation is compacted
- support comma separators, signs, and decimals
- text containing the same number is not automatically equal

Run both target test suites and report the expected failures. Do not modify product code yet.
```

Backup test contents are in `demo/fixtures/`.

## 3. Implement the minimum fix

```text
Apply the minimum fix needed to pass the new backend and frontend regression tests.

Constraints:
- keep backend and frontend grading behavior equivalent
- do not change API schemas, database models, authentication, or migrations
- do not add a dependency
- do not rewrite the existing similarity logic

Run:
- .venv\Scripts\python.exe -m pytest tests/test_quiz_grading.py -q
- .venv\Scripts\python.exe -m pytest -q
- .venv\Scripts\python.exe -m ruff check app tests
- npm test in frontend
- npm run lint in frontend

After the checks pass, restart the backend so the browser uses the new code:
- powershell -ExecutionPolicy Bypass -File scripts/start_live_demo.ps1 -RestartBackend -SkipDataPreparation

Then summarize the diff and remaining risks. Do not claim browser verification yet.
```

## 4. Re-verify the same browser flow

```text
Use chrome-devtools MCP to repeat the same LiveDemo flow from a clean quiz state.

Enter:
- DEMO 1: 10.00
- DEMO 2: java3
- DEMO 3: user 404

Verify:
- visible result for all three answers
- POST /quiz/submit is 200
- response is correct=1 and total=3
- the result page lists DEMO 2 and DEMO 3 as incorrect
- there are no new Console errors

Return the browser and Network evidence in five lines.
```
