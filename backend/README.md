# Backend (FastAPI)

## Run (dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints
- `GET /api/health`
- `GET /api/modules`
- `GET /api/modules/{module_id}`
