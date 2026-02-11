# Backend (FastAPI)

## Run (dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Env
Use `backend/.env.example` as reference.

Telemetry/logging env vars:
- `LOG_LEVEL` (default `INFO`)
- `TELEMETRY_LOG_FILE` (default `backend/logs/telemetry.log`)

## Endpoints (core)
- `GET /api/health`
- `GET /api/modules`
- `GET /api/modules/{module_id}`
- `GET /api/study/topics`
- `GET /api/study/topics/{topic_id}`
- `GET /api/study/exams`
- `GET /api/assets/pdfs/{pdf_name}`
- `GET /api/assets/modules/{module_id}/{file_path}`
- `GET /api/assets/exams/{file_path}`

## Endpoints (MVP foundation)
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/reset-password`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/progress/chapter`
- `POST /api/progress/chapter` accepta si `checklist_state` (item-level)
- `GET /api/progress/summary`
- `GET /api/progress/chapters`
- `GET /api/progress/games`
- `POST /api/progress/games`
- `POST /api/telemetry/event`
- `GET /api/export/progress.csv`
- `GET /api/quiz/{chapter_id}`
- `POST /api/quiz/{chapter_id}/submit`
- `GET /api/exam/sessions/official`
