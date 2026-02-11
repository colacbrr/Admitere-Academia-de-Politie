# Sprinturi-MVP

## Scop
Transformam deciziile finale din `Decizii-MVP.md` in backlog executabil.

## Principii active
- Prioritate maxima: continut academic (`03_proba_scrisa`, in special Romana + Istorie).
- Sync progres: `local-first`, reconciliere "cel mai complet castiga".
- XP jocuri: badge-uri, nu nivel global.
- Daily Challenge: exclus in aceasta etapa.
- Infrastructura: fara investitii mari acum (fara urgenta Alembic).

## Sprint A - Continut academic intensiv (urmatorul sprint)
Obiectiv: crestere semnificativa a valorii educationale reale.

### Livrabile produs
1. Extindere `Romana` + `Istorie` cu structura FULL: definitii, mecanism, exemple, capcane, exercitii.
2. Prag de calitate pentru "capitol gata": 90%.
3. Citari complete vizibile in capitole + pagina dedicata "Surse".
4. Redesign prioritar sectiune `Proba scrisa` (lizibilitate + orientare + progres).

### Task-uri tehnice
1. Continut `guide/03_proba_scrisa/**`
- completare pe subcapitole, nivel academic.
- introducere explicita a sectiunii "Capcane frecvente" unde e cazul.

2. Frontend `frontend/src/routes/+page.svelte`
- rafinare UI `Proba scrisa` (ierarhie, spacing, claritate pedagogica).
- afisare citari complete, nu doar format minimal.

3. Meta/QA
- verificare consistenta terminologie.
- verificare prag 90% pentru marcarea capitolului.

### Definition of Done
- minim 2 module din `Romana` + 2 module din `Istorie` ridicate la standard FULL.
- citari complete vizibile in UI.
- validare manuala de studiu (parcurgere cap-coada fara blocaje de intelegere).

## Sprint B - Auth hardening + progres robust
Obiectiv: consolidare autentificare si coerenta progres.

### Livrabile produs
1. Reset parola (varianta simpla initiala).
2. Reconciliere conflict local/remote cu regula "cel mai complet".
3. HUD aliniat complet cu progresul sincronizat.

### Task-uri tehnice
1. Backend
- endpoint-uri simple pentru reset parola (mock sau token local).
- ajustare logica progres, daca apar conflicte reale in testare.

2. Frontend
- pagina `/auth` extinsa cu flux reset parola.
- tratament explicit pentru stari de sync (pending/success/fallback local).

### Definition of Done
- login/register/reset functionale.
- progres checklist/capitol ramane coerent dupa relogin si refresh.

## Sprint C - Calitate release + staging rapid
Obiectiv: stabilitate tehnica pentru testare publica controlata.

### Livrabile produs
1. Staging rapid (UI + API).
2. Smoke tests automate minime pentru `auth` + `progres`.
3. Telemetrie minima UX: `capitol deschis`, `joc finalizat`, `login`.

### Task-uri tehnice
1. CI/CD
- `lint + build` blocant.
- testele pot ramane warning in etapa curenta.

2. Deploy
- flux de staging rapid (Vercel + API separat, conform deciziei).

3. Observabilitate
- logs basic + evenimente UX minime.

### Definition of Done
- pipeline stabil pe branch principal.
- staging functional pentru testare interna.

## Note de executie
- Alembic ramane amanat momentan.
- Fara calendar fix de release; executie sprint-based.
- Simulatorul complet de examen intra doar dupa ce continutul este considerat complet.
