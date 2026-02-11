# Startup Guide

Acest document descrie pornirea proiectului in starea curenta: backend FastAPI + frontend SvelteKit, autentificare, sync progres si mini-jocuri.

## 1. Cerinte

- `python3` (recomandat 3.10+)
- `node` (recomandat 20+)
- `npm`

Verificare rapida:

```bash
python3 --version
node -v
npm -v
```

## 2. Structura relevanta

- `backend/` API FastAPI, auth, progres, quiz, game stats
- `frontend/` interfata SvelteKit
- `guide/` continutul de studiu (module/capitole)
- PDF-ul principal in radacina proiectului (folosit in `Introducere`)

## 3. Pornire backend

Din radacina proiectului:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Optional in `.env`:

- `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/admitere_db`
- `CREATE_TABLES_ON_STARTUP=1`
- `CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173`
- `LOG_LEVEL=INFO`
- `TELEMETRY_LOG_FILE=backend/logs/telemetry.log`

Ruleaza API:

```bash
uvicorn app.main:app --reload --port 8000
```

Endpoint-uri utile:

- `GET http://127.0.0.1:8000/api/health`
- `GET http://127.0.0.1:8000/api/study/topics`

## 4. Pornire frontend

Terminal nou:

```bash
cd frontend
npm install
npm run dev -- --host
```

Frontend (implicit):

- `http://127.0.0.1:5173`

Daca vrei alt API base URL:

```bash
echo 'VITE_API_BASE_URL=http://127.0.0.1:8000' > frontend/.env
```

## 5. Flux recomandat de test

1. Deschide `http://127.0.0.1:5173`.
2. Verifica sectiunea `Introducere` si PDF-ul oficial.
3. Mergi in `Studiu`, bifeaza checklist-uri si joaca mini-jocurile.
4. Deschide `/auth` si fa `register/login`.
5. Revino in `Studiu` si verifica sync progres.
6. Deschide `/status` si verifica HUD (progres + statistici jocuri).
7. Deschide `/surse` si verifica citarile complete agregate.
8. Deschide `/antrenament` si verifica arhiva `Subiecte-raspunsuri` (selector an/categorie + PDF inline + sesiune cronometrata).

## 6. API (stare curenta)

Auth:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/reset-password`
- `POST /api/auth/logout`
- `GET /api/auth/me`

Progres:

- `POST /api/progress/chapter`
  - include `checklist_state` (item-level)
- `GET /api/progress/chapters`
- `GET /api/progress/summary`
- `GET /api/progress/games`
- `POST /api/progress/games`
- `GET /api/export/progress.csv`

Continut/studiu:

- `GET /api/study/topics`
- `GET /api/study/topics/{topic_id}`
- `GET /api/study/exams`
- `GET /api/assets/pdfs/{pdf_name}`
- `GET /api/assets/exams/{file_path}`

Quiz/simulator:

- `GET /api/quiz/{chapter_id}`
- `POST /api/quiz/{chapter_id}/submit`
- `GET /api/exam/sessions/official`

## 7. Verificari tehnice

Frontend:

```bash
cd frontend
npm run check
npm run build
```

Backend:

```bash
cd backend
python3 -m compileall app
.venv/bin/python -m unittest -q tests.test_smoke_unittest
```

## 8. Probleme frecvente

- `Permission denied` la push GitHub
  - verifica cheia SSH (`ssh -T git@github.com`) si remote-ul.

- PDF-ul nu apare
  - verifica existenta unui `.pdf` in radacina repo.
  - verifica `GET /api/study/topics`.

- Eroare DB legata de coloane noi (ex: `checklist_state_json`)
  - schema veche nu are ultimele campuri.
  - solutie rapida local: recreeaza DB sau aplica migrare.

- Frontend nu vede backend
  - verifica backend pe `:8000`.
  - verifica `VITE_API_BASE_URL`.

- Nu apar loguri de telemetrie in fisier
  - verifica `TELEMETRY_LOG_FILE` in `.env`.
  - verifica permisiuni de scriere in folderul `backend/logs`.

## 9. Oprire servicii

In terminalele backend/frontend:

```bash
Ctrl+C
```

## 10. GitHub Pages (frontend)

Fluxul e deja pregatit in `.github/workflows/pages.yml`.

Setari necesare in GitHub:

1. `Settings > Pages`:
- `Source`: `GitHub Actions`.

2. `Settings > Secrets and variables > Actions > Variables`:
- adauga `VITE_API_BASE_URL` cu URL-ul backend public.

3. Push pe `main`:
- workflow-ul face build static din `frontend/` si publica automat pe Pages.

Observatie:
- GitHub Pages publica doar frontend static. API-ul Python trebuie hostat separat.
