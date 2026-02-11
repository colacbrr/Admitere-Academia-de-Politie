# Decizii MVP - Raspunsuri finale (etapa curenta)

Acest document este sursa oficiala pentru directia de produs si implementare.
Data consolidarii: 2026-02-11.

## 1) Produs si scop imediat
1. Obiectiv milestone: continut academic mai profund + UX.
2. KPI 30 zile: rata de revenire + scor/completion jocuri.
3. Onboarding: universal.
4. Invatare intern vs extern: 70% intern / 30% extern (adaptat per subiect).
5. "Util" acum: raspunsuri academice complete + navigare clara + progres vizibil.

## 2) Continut academic
6. Capitol prioritar: `03_proba_scrisa` -> Romana + Istorie, in paralel.
7. Adancime minima subcapitol: FULL (definitii + mecanism + exemple + capcane + exercitii).
8. Sectiune "Capcane frecvente": DA, unde are sens (mai ales la capitole dificile).
9. Surse: citare completa vizibila + pagina dedicata "Surse".
10. Surse fara consens: se alege sursa oficiala.
11. Standard editorial `guide/`: liber (fara template strict), dar cu prag de calitate.
12. Capitol "gata": prag numeric 90%.

## 3) Gamification si jocuri
13. Impact XP: prioritate jocuri de acuratete + memorie, dar toate jocurile conteaza.
14. XP jocuri: influenteaza badge-uri, NU nivelul global.
15. Penalizari greseli: NU, doar feedback pozitiv.
16. Daily Challenge: NU in etapa curenta.
17. Leaderboard: local acum; multi-user mai tarziu.
18. Joc extins primul: jocul cu valoare educationala cea mai mare.

## 4) Auth, progres si date
19. Refresh token / expirare robusta: sprintul urmator.
20. Reset parola: DA (chiar si varianta simpla initial).
21. Progres temporal: minim (fara istoric temporal detaliat).
22. Sync: local-first.
23. Conflict local vs remote: "cel mai complet castiga".
24. Export CSV: decizie amanata; implicit MVP = progres capitole.

## 5) UX/UI si navigare
25. Actiuni cont in home: decizie amanata; recomandare curenta = card informativ discret.
26. Redesign prioritar: `Proba scrisa`.
27. Progress bar sticky: decizie amanata; recomandare = DA pe desktop.
28. Mod Focus: NU.
29. Iconografie/ilustratii: doar pe capitole-cheie.
30. Densitate text: automata (fara switch explicit acum).

## 6) Arhitectura si livrare
31. Migrari DB (Alembic): amanat; fara urgenta in etapa curenta.
32. Deploy: staging rapid (ex: Vercel + API separat).
33. Teste automate: smoke tests minime (`auth` + `progres`).
34. CI: `lint + build` blocant; testele pot fi warning.
35. Telemetrie UX minima: DA (`capitol deschis`, `joc finalizat`, `login`).

## 7) Roadmap imediat
36. Focus sprint urmator: continut academic.
37. "Release public intern": continut cheie complet.
38. Risc major: continut insuficient.
39. Pre-conditie simulator examen: continut complet.
40. Calendar livrari: fara calendar fix; model sprint-based.

## Reguli implicite de implementare
- Nivelul global nu trebuie distorsionat de XP din mini-jocuri.
- Continutul educational are prioritate fata de extinderile tehnice non-critice.
- Pentru conflicte de sync, se aplica strategia "cel mai complet castiga" in favoarea progresului utilizatorului.
