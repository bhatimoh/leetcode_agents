# Vishleshan

Vishleshan analyzes a public LeetCode profile. Enter a username and two agents gather the records, score the last five contests, and write a study plan.

## What it does

Agent 1 loads the public profile, contest history, and recent submissions. Agent 2 scores the last five attended contests, chooses the topics to focus on, and writes a plan with LeetCode problem links and a deadline for each problem.

The page has two tabs. Analysis shows contest performance and the study plan. Agents shows each step while the run is in progress.

## Layout

- `frontend` is a Vite app written in React and TypeScript.
- `backend` is a FastAPI app. Both agents are LangGraph flows. Agent 2 calls OpenAI.

## Requirements

- Node.js 20 or newer
- Python 3.12 or newer
- An OpenAI API key

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set these values in `backend/.env`:

```
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini
```

Start the API from the `backend` directory:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

The API listens on `http://127.0.0.1:8000`.

- `POST /api/analysis` returns the full result.
- `POST /api/analysis/stream` sends progress events while the agents run.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api` to the backend.

## Tests

From the `backend` directory, with the virtual environment active:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python -m pytest
```

## Notes

Only public LeetCode profiles are supported. Do not commit `backend/.env`.
