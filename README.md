# Admitere-Academia-de-Politie

Platforma educationala pentru pregatirea admiterii la Academia de Politie:
- studiu academic structurat (Romana, Istorie, Limba straina),
- informatii organizatorice de inscriere,
- arhiva de subiecte si raspunsuri din anii precedenti,
- progres, HUD personal si mini-jocuri de consolidare.

## Obiective proiect

1. Utilitate academica reala: explicatii clare, exemple, capcane, exercitii, citari.
2. Claritate organizatorica: etape, termene, acte necesare, contestatii.
3. Experienta buna pe sesiuni lungi de invatare: UI reactiv, light/dark, progres vizibil.
4. Evolutie continua: adaugare periodica de continut si resurse.

## Stack tehnic

- Backend: `FastAPI` (Python)
- Frontend: `SvelteKit` + `Vite`
- PDF viewer: `pdfjs-dist`
- Persistenta progres: local (`localStorage`) + backend (cand user-ul este autentificat)
- CI: GitHub Actions (`ci.yml`)
- Deploy frontend static: GitHub Pages (`pages.yml`)

## Structura repo

- `backend/` API, auth, progres, telemetry, endpoints studiu/PDF
- `frontend/` UI principal, HUD, surse, antrenament oficial
- `guide/` continutul educational pe module/capitole
- `Subiecte-raspunsuri-din-anii-precedenti/` arhiva oficiala de PDF-uri (ani anteriori)
- `Startup.md` ghid rapid de pornire
- `Deploy.md` note si configurare deploy
- `Documentatie.md` documentatia extinsa de proiect

## Functionalitati cheie (stare actuala)

- Navigare pe module de studiu:
  - `01_admitere`
  - `02_proba_fizica`
  - `03_proba_scrisa`
  - `04_medical`
  - `05_calendar`
  - `06_intrebari`
  - `07_resurse`
- Viewer PDF inline in aplicatie (fara download fortat).
- Pagina `Surse complete` cu citari agregate.
- Pagina `HUD personal` pentru progres pe capitole/checklist.
- Mini-jocuri de consolidare in studiu (flash, match, timeline, corectare).
- Pagina `Antrenament oficial`:
  - selector categorie/an/fișier din arhiva de examene,
  - vizualizare PDF,
  - marcare set rezolvat,
  - sesiune cronometrata cu XP.

## Pornire locala

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host
```

Frontend: `http://127.0.0.1:5173`  
Backend: `http://127.0.0.1:8000`

## Endpoint-uri importante (backend)

- `GET /api/health`
- `GET /api/study/topics`
- `GET /api/study/topics/{topic_id}`
- `GET /api/study/exams`
- `GET /api/assets/pdfs/{pdf_name}`
- `GET /api/assets/exams/{file_path}`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/reset-password`
- `GET /api/progress/summary`

## GitHub Actions si Pages

- CI: `.github/workflows/ci.yml`
- Pages deploy: `.github/workflows/pages.yml`

Pentru GitHub Pages:
1. `Settings > Pages` -> Source: `GitHub Actions`
2. `Settings > Secrets and variables > Actions > Variables`:
   - `VITE_API_BASE_URL` = URL-ul backend public

Observatie: GitHub Pages hosteaza doar frontend static. Backend-ul Python trebuie deployat separat.

## Politica de continut

- Sursele oficiale/institutionale au prioritate.
- Wikipedia este folosita ca suport de orientare si context, nu ca unica sursa.
- Fiecare extindere de continut urmareste formatul:
  - ce inveti,
  - ce pregatesti,
  - explicatie detaliata,
  - exemple,
  - checklist,
  - surse.

## Contributii

Directii de lucru recomandate:
1. Extindere `03_proba_scrisa` (prioritate maxima)
2. Extractie itemi din PDF-urile oficiale in question bank structurat
3. Extindere simulator oficial pe ani/categorii
4. Refinement UI/UX si gamification
