# Arhitectura proiect

**Obiectiv**
Aplicatie locala cu server Python care hosteaza o interfata web pentru studiu. Continutul este generat din fisierele din `guide/`.

**Componente**
- Backend: Python (server static/dinamic pentru continut).
- Frontend: UI reactiv, tema light/dark, navbar pe capitole.
- Continut: Markdown in `guide/` + eventual build in `guide/99_output/`.

**Design UI**
- Stil academic, contrast redus pentru sesiuni lungi.
- Buton vizibil pentru light/dark.
- Navigare rapida pe capitole.
- Surse citate si accesibile direct.

**Tehnologii alese**
- Backend: FastAPI pentru servire statica + API de continut.
- Frontend: SvelteKit pentru UI reactiv, fluid si lizibil.
- Stocare continut: Markdown + index JSON pentru navigare si cautare.

**Plan evolutiv**
- V1: ghid static complet, navigare si cautare.
- V2: Q&A si referinte rapide.
- V3: gamificare (progres, badge-uri, streak-uri).
