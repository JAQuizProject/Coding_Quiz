# Coding Quiz agent guidance

## Setup

- Run `powershell -ExecutionPolicy Bypass -File scripts/setup_live_demo.ps1` once before the live demo.
- Run `powershell -ExecutionPolicy Bypass -File scripts/start_live_demo.ps1` to start the local app.
- Run `powershell -ExecutionPolicy Bypass -File scripts/open_live_demo_codex.ps1` for the presentation Codex session.
- Use the isolated `chrome-devtools` MCP server for browser work.
- Use only `http://127.0.0.1:3000` and the local FastAPI server during the demo.

## Working agreement

- Reproduce a bug and collect browser and Network evidence before editing code.
- State acceptance criteria and expected files before implementing a fix.
- For bug fixes, add a failing regression test first.
- Keep changes limited to the grading implementation and its tests unless the evidence requires more.
- Do not change authentication, database schema, migrations, or API response contracts for the grading demo.

## Verification

- Backend target test: `.venv\Scripts\python.exe -m pytest tests/test_quiz_grading.py -q`
- Backend suite: `.venv\Scripts\python.exe -m pytest -q`
- Backend lint: `.venv\Scripts\python.exe -m ruff check app tests`
- Frontend tests: run `npm test` in `frontend`.
- Frontend lint: run `npm run lint` in `frontend`.
- Frontend build: run `npm run build` in `frontend`.
- After backend product code changes, run `powershell -ExecutionPolicy Bypass -File scripts/start_live_demo.ps1 -RestartBackend -SkipDataPreparation`.
- Re-run the same browser flow after a fix and report the `POST /quiz/submit` status and response.
