PROIECT - GHID ADMITERE ACADEMIA DE POLITIE

**Scop**
Construim un ghid complet pentru admitere, bazat pe regulamentul oficial si pe surse online credibile. Ghidul va deveni o aplicatie web (server Python + UI reactiv) cu navigare pe capitole, surse citate si continut explicat clar.

**Misiune produs**
- Aplicatia este construita in primul rand pentru studiu eficient (continut de examen, clar, detaliat, usor de parcurs).
- In al doilea rand, aplicatia acopera complet partea organizatorica de inscriere.
- Continutul trebuie extins constant cu informatii noi relevante, doar din surse credibile si verificabile.

**Viziune**
- Produs educational pentru elevi: continut dens, dar lizibil, in sesiuni lungi.
- Continut verificabil: fiecare afirmatie importanta are sursa oficiala.
- Structura modulara: fiecare materie, capitol si subcapitol este o unitate de UI.
- Evolutie continua: periodic adaugam clarificari, exemple noi si resurse suplimentare pe teme relevante.

**Ce livram**
- Continut complet despre admitere: etape, probe, criterii, calendar.
- Proba scrisa explicata pe materii si capitole.
- Proba fizica explicata detaliat (inclusiv traseu, reguli, bareme).
- Examinarea medicala si cadrul legal.
- Surse online oficiale si academice pentru aprofundare.
- Exemple clare pentru fiecare subiect.

**Arhitectura**
- Server local in Python (FastAPI) care expune API-ul pentru continut si metadate.
- Interfata web reactiva (SvelteKit) care consuma API-ul si reda paginile.
- Rulare locala: utilizatorul porneste un executabil care lanseaza serverul si UI.
- Continutul este stocat local in repo si mapat in structura UI.

**Directie tehnica**
- Server local in Python (executabil) care hosteaza interfata web.
- UI reactiv, academic, cu doua teme (light/dark) si buton de comutare.
- Navigare cu navbar pe teme, materii, capitole.
- Continut structurat pe unitati mici, cu rezumat + detalii + surse.
- In viitor: Q&A si gamificare (progres, badge-uri, streak-uri).
- Tabele si figuri acolo unde clarifica materia.
- Stack ales: FastAPI (backend) + SvelteKit (frontend).

**UI/UX detaliat**
- Estetica academica: paleta sobria, contrast bland, fundaluri confortabile pentru citit mult timp.
- Doua teme: light si dark, cu buton + iconita vizibila permanent.
- Tipografie cu ierarhie clara (titlu, subtitlu, corp), spatii generoase.
- Controale pentru copiere rapida a link-urilor de citare.
- Layout pentru sesiuni lungi: nav fixa, continut pe coloana larga, scroll clar.
- Accesibilitate: contraste verificate, fonturi suficient de mari.
- Gamification roadmap: niveluri 1-10, cu nivel 10 atins la parcurgerea completa a capitolelor, checklist-urilor si quiz-urilor finale.

**Model de continut**
- Continutul este impartit pe module: admitere, proba fizica, proba scrisa, medical, calendar, resurse.
- Fiecare materie are capitole si subcapitole.
- Fiecare capitol are rezumat scurt, explicatii detaliate, exemple clare si lista de surse (link-uri).
- Toate sursele trebuie sa fie verificabile si preferabil institutionale.
- Pentru fiecare capitol se urmareste formatul: ce inveti, ce pregatesti, ce verifici din surse.
- Modulele de studiu au prioritate de continut fata de modulele administrative.

**Politica de citare**
- Link-urile se scriu in format cod: `https://...`
- Fiecare sectiune are lista "Surse".
- Pentru informatii extrase din PDF, se mentioneaza explicit documentul si sectiunea.
- Pentru surse externe se folosesc doar site-uri oficiale sau academice.
- Pentru sectiunile critice se recomanda si un camp "ultima verificare" (data calendaristica).
- Rezultatele verificarilor periodice de link-uri se arhiveaza in `guide/00_meta/`.

**Structura repo**
- `guide/` contine continutul pe module.
- `Documentatie.md` descrie arhitectura, fluxul de date si regulile de continut.
- `Agent.md` contine regulile operative pentru agent.
- `Planificare.md` urmareste roadmap-ul si pasii de implementare.
- `guide/00_meta/CONTENT_CHECKLIST.md` este template-ul standard pentru fiecare capitol/subcapitol.

**Build si rulare (urmeaza)**
- Backend: comanda de rulare FastAPI va fi documentata dupa initializarea proiectului.
- Frontend: comanda de rulare SvelteKit va fi documentata dupa initializarea proiectului.
- Vom adauga un script comun pentru pornire locala.

**Interactiune Frontend-Backend (implementat)**
- Frontend-ul consuma API local FastAPI pentru continutul de studiu.
- Model actual de UX: rezumat scurt in pagina + PDF oficial incarcat in `iframe`.
- Endpoint-uri disponibile:
- `GET /api/health`
- `GET /api/modules`
- `GET /api/modules/{module_id}`
- `GET /api/study/topics`
- `GET /api/study/topics/{topic_id}`
- `GET /api/assets/pdfs/{pdf_name}`
- Temele light/dark sunt persistate in `localStorage`.

**Repo si livrare**
- Proiectul va fi publicat pe GitHub.
- Vom adauga `.gitignore` relevant pentru Python si front-end.
- Mai tarziu: workflow de testare cu GitHub Actions sau preview public (ex: Vercel).

**CI/CD - schita**
- GitHub Actions: rulare teste, lint, build front-end.
- Preview public: Vercel sau GitHub Pages pentru demo (optional).

**Staging si publicare**
- Inainte de publicare: verificare continut, verificare citari, smoke test UI.
- Publicarea de preview: Vercel pentru UI, API local pentru continut static.

**Stare curenta**
- Structura ghidului este definita in `guide/`.
- Urmeaza documentarea online si adaugarea citariilor.
- Backend scaffold creat in `backend/` (FastAPI minimal).
- Frontend scaffold creat in `frontend/` (SvelteKit + TypeScript).
- Dependintele frontend sunt instalate, iar proiectul poate rula cu `npm run dev`.
- Setul oficial de decizii de produs pentru MVP este documentat in `Decizii-MVP.md`.
- Optiunile si statusul deciziei de deploy sunt documentate in `Deploy.md`.
- Backlog-ul executabil pe 4 sprinturi este documentat in `Sprinturi-MVP.md`.

**Criterii de utilitate (obligatorii)**
- Utilizatorul trebuie sa poata identifica rapid ce are de invatat pentru examen.
- Utilizatorul trebuie sa poata gasi separat si clar pasii de inscriere.
- Fiecare subiect important trebuie sa ofere atat explicatie, cat si sursa.
- Continutul se imbunatateste continuu pe baza surselor noi relevante.

-------------------------------------------------------------------------------

**Continut curent (draft)**

-------------------------------------------------------------------------------

🇷🇴 1. LIMBA ROMÂNĂ – CE ÎNVEȚI CONCRET

❗ DOAR GRAMATICĂ + SINTAXĂ, NU eseuri, NU autori.

🔹 A. Enunțul și propoziția

tipuri de enunțuri: asertiv, interogativ, exclamativ, imperativ

propoziția simplă vs. dezvoltată

propoziție afirmativă / negativă

punctuație (virgulă, punct și virgulă)

🔹 B. Fraza

coordonare: juxtapunere, joncțiune

conjuncții coordonatoare

subordonare: conjuncții, pronume și adverbe relative

punctuația frazei

🔹 C. Funcții sintactice (FOARTE IMPORTANT)

predicat verbal / nominal

nume predicativ + acord

subiect: exprimat / neexprimat

acordul predicatului cu subiectul

atribut (toate realizările)

apoziția

complemente:

direct

indirect

prepozițional

circumstanțiale:

loc, timp, mod, cauză, scop

topica propoziției

🔹 D. Propoziții subordonate

atributivă

completivă directă / indirectă / prepozițională

circumstanțială: loc, timp, mod, cauză, scop

📌 Cum se dau întrebările:
identificare funcții, alegerea variantei corecte, punctuație corectă.

📜 2. ISTORIE – DOAR TEMATICA OFICIALĂ

❗ Nu se cer date inutile, ci:

procese istorice

relații cauză–efect

contexte politice

🔹 A. Popoare și spații istorice

Romanitatea românilor (teorii + argumente)

🔹 B. Oamenii, societatea și lumea ideilor

Secolul XX:

democrație

totalitarism

ideologii politice în România și Europa

Constituțiile României

🔹 C. Statul și politica

autonomii locale și instituții (sec. IX–XVIII)

statul român modern:

Unirea

România Mare

România postbelică:

stalinism

național-comunism

disidență

democrația după 1989

🔹 D. Relații internaționale

spațiul românesc în Evul Mediu

România și marile alianțe

România în Războiul Rece

📌 Cum se dau întrebările:
cronologie, asociere eveniment–perioadă, interpretare istorică.

🌍 3. LIMBA STRĂINĂ (exemplu: ENGLEZĂ)

⚠️ Nu se cer texte lungi sau eseuri

🔹 Morfologie

substantive neregulate

adjective + comparație

articol (zero article!)

numerale

verbe:

pasiv

modale

infinitiv / participiu

adverbe

prepoziții, conjuncții

🔹 Sintaxă

ordinea cuvintelor

acord

tipuri de propoziții

propoziții condiționale (I, II, III)

📌 Cum se dau întrebările:
completare, alegere formă corectă, gramatică pură.

🎯 CUM SĂ TE PREGĂTEȘTI EFICIENT (sfat real)
📅 Plan minim (3–4 luni)

Română: 30–40 min / zi

Istorie: 20–30 min / zi

Limbă străină: 15–20 min / zi

Teste grilă: zilnic (după 1 lună)

📘 Materiale bune

manuale liceu (ediții recente)

culegeri grilă pentru Academia de Poliție

DOOM / DEX (pentru română)

🧠 REALITATEA EXAMENULUI

Nu este greu, dar:

e competitiv

greșelile mici te scot din joc

Contează:

atenția

antrenamentul pe grile

gestionarea timpului
