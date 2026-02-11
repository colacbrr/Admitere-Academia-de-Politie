# Startup Guide

Acest document explica pornirea proiectului local (backend + frontend).

## 0. Obiectiv functional al aplicatiei

- Aplicatia este in primul rand un instrument de studiu pentru examenul de admitere.
- Aplicatia este in al doilea rand un ghid organizatoric pentru inscriere.
- Continutul trebuie extins constant cu informatii noi pe teme relevante, validate prin surse credibile citate.

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

## 2. Pornire Backend (FastAPI)

Din radacina proiectului:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend disponibil la:

- API root: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/api/health`

## 3. Pornire Frontend (SvelteKit)

Deschide un terminal nou, din radacina proiectului:

```bash
cd frontend
npm install
npm run dev -- --host
```

Frontend disponibil, de obicei, la:

- `http://127.0.0.1:5173`

## 4. Flux de lucru recomandat

1. Porneste backend-ul.
2. Porneste frontend-ul.
3. Deschide frontend-ul in browser.
4. Verifica daca se incarca lista de teme si PDF-ul oficial.

## 5. Comenzi utile de verificare

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
```

## 6. Probleme frecvente

- `python: command not found`
  - Foloseste `python3` in loc de `python`.

- Frontend-ul nu poate accesa API-ul
  - Verifica daca backend-ul ruleaza pe portul `8000`.
  - Verifica CORS in `backend/app/core/config.py`.

- PDF-ul nu apare in interfata
  - Verifica existenta unui fisier `.pdf` in radacina proiectului.
  - Endpoint de test: `GET /api/study/topics`.

## 7. Oprire servicii

In fiecare terminal de rulare, foloseste:

```bash
Ctrl+C
```
