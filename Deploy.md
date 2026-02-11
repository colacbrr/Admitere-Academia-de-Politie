# Deploy.md

## Status curent
Decizia de deploy public este amanata intre:
- Vercel (frontend) + API separat
- VPS unic (frontend + backend)
- GitHub Pages (frontend static) + API separat

## Constrangeri deja stabilite
- PostgreSQL din start
- Logs basic in MVP
- CI: warning pentru lipsa surse/citari (nu blocking initial)
- Criteriu release: teste + lint + performanta + continut minim

## Propunere tehnica pentru comparatie
### Optiunea Pages: GitHub Pages + API separat
- Pro: deploy gratuit pentru frontend static, simplu pentru demo public.
- Pro: workflow automat la push pe `main` prin GitHub Actions.
- Contra: backend Python nu ruleaza pe Pages; trebuie API extern.
- Contra: functiile care depind de API sunt limitate daca `VITE_API_BASE_URL` nu este setat.

### Optiunea A: Vercel + API separat
- Pro: setup rapid pentru frontend, preview simplu PR-by-PR
- Pro: scaling frontend usor
- Contra: split operational (doua suprafete de deploy)

### Optiunea B: VPS unic
- Pro: control total pe stack, cost predictibil
- Pro: backend + frontend + DB in acelasi perimetru
- Contra: operare/devops mai multa munca manuala

## Decizie recomandata (MVP)
- Daca obiectivul imediat este testare rapida publica: Optiunea A
- Daca obiectivul imediat este control complet infrastructura: Optiunea B

## TODO pentru inchiderea deciziei
1. Stabilim buget lunar tinta
2. Stabilim nivelul de trafic estimat in primele 60 zile
3. Stabilim cine administreaza operational deploy-ul
4. Alegem optiunea finala si documentam runbook-ul

## Implementare existenta (GitHub Pages)
- Workflow: `.github/workflows/pages.yml`
- Build static frontend cu SvelteKit adapter-static in CI.
- Publicare automata la push pe `main`.
- Variabila necesara in GitHub repo (`Settings > Secrets and variables > Actions > Variables`):
  - `VITE_API_BASE_URL`: URL backend public (ex: `https://api.exemplu.ro`).
