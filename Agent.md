# Agent - instructiuni pentru proiect

**Context proiect**
Proiectul urmareste crearea unui "Guide throughout the preparation for academic entry exam" pentru admiterea la Academia de Politie. Baza proiectului este regulamentul oficial din `Regulament-admitere-licenta-2026-actualizare-18-01-2026.pdf`, completat cu surse oficiale online.

**Scopul Agentului**
Agentul trebuie sa colecteze informatii relevante de pe internet, sa le citeze prin link-uri sau mentiuni, si sa le integreze in ghidul final. Oricine citeste documentele rezultate trebuie sa poata verifica sursele online.
Agentul trebuie sa prioritizeze surse oficiale (Academia de Politie, MAI, Ministerul Educatiei, legislatie).

**Prioritati strategice (obligatorii)**
- Prioritatea 1: informatie de studiu pentru candidat (ce invata, cum invata, ce intra la examen, explicat clar si detaliat).
- Prioritatea 2: informatie organizatorica de inscriere (etape, acte, termene, conditii, taxe/scutiri, contestatii).
- Aplicatia trebuie sa fie utila in primul rand pentru invatare, apoi pentru organizarea inscrierii.
- Agentul trebuie sa extinda permanent baza de continut cu informatii noi, relevante si verificabile.

**Reguli obligatorii**
- Informatiile de baza trebuie extrase din PDF-ul oficial oferit.
- Orice informatie externa trebuie insotita de citari clare (link sau mentiune).
- Sursele externe trebuie sa fie de incredere, preferabil academice sau institutionale.
- Continutul final trebuie sa fie clar, structurat si usor de urmarit.
- Nu se publica informatii speculative sau neconfirmate.
- Fiecare materie trebuie explicata cu exemple clare si verificabile.
- Fiecare capitol trebuie sa raspunda clar la: "ce trebuie sa stiu", "ce trebuie sa pregatesc", "unde verific informatia".
- Cautarea de continut nou trebuie sa fie continua (actualizari periodice, surse noi, explicatii mai bune).

**Surse oficiale recomandate (de prioritate)**
- Academia de Politie - admitere licenta: `https://admitere.academiadepolitie.ro/`
- Regulament oficial 2026: `https://admitere.academiadepolitie.ro/docs/2026/licenta/Regulament-admitere-licenta-2026-actualizare-18-01-2026.pdf`
- Legislatie (examinare medicala MAI): `https://legislatie.just.ro/Public/FormaPrintabila/00000G02FVPQBRGW38Z0Y7A95OP50LVD`

**Ce trebuie acoperit in ghid**
- Etapele concursului de admitere.
- Proba scrisa: durata, structura, notare, criterii de promovare.
- Proba fizica: descriere clara, conform regulamentului.
- Examinarea medicala: rol si rol in procesul de admitere.
- Materiile de la proba scrisa trebuie acoperite separat.
- Limba romana: capitole oficiale, explicare clara, resurse pentru fiecare capitol.
- Istorie: capitole oficiale, explicare clara, resurse pentru fiecare capitol.
- Limba straina (engleza / franceza / germana): capitole oficiale, explicare clara, resurse pentru fiecare capitol.

**Formatul citarii**
- Link-urile se scriu in format cod: `https://...`
- La fiecare sectiune, include o lista "Surse" cu link-urile folosite.
- Cand este posibil, noteaza si data ultimei verificari pentru sursele importante.

**Flux de lucru recomandat**
1. Citirea si extragerea sectiunilor relevante din PDF.
2. Construirea structurii ghidului pe capitole.
3. Cautarea surselor online pentru fiecare subcapitol.
4. Integrarea link-urilor si mentiunilor in ghid.
5. Revizuirea pentru coerenta si acuratete fata de regulament.
6. Verificarea periodica a actualizarilor pe pagina oficiala de admitere.

**Definitia succesului**
Un ghid complet, verificabil, cu informatii clare si citate, care acopera toate aspectele admiterii si permite oricarui cititor sa studieze in detaliu pe baza surselor indicate.
- Succesul real inseamna: candidatul gaseste rapid materia, intelege usor ce are de invatat si poate urma fara confuzie pasii de inscriere.

**Directie viitoare - aplicatie web**
Ghidul va fi integrat intr-o aplicatie cu interfata web. Utilizatorul va porni un executabil local care ruleaza un server si hosteaza pagina web. Aplicatia va include:
- navbar pe teme, materii, capitole
- pagini pentru proba scrisa, fizica, medicala
- categorie viitoare pentru Q&A
- cautare si filtrare
- mod light si dark, cu buton vizibil
- layout prietenos pentru sesiuni lungi de studiu

**Cerinte UI/UX detaliate**
- Interfata reactiva, moderna, dar cu estetica academica (nuante serioase, contrast bland pentru citit mult timp).
- Doua teme: light/dark, comutare prin buton clar + iconita.
- Tipografie lizibila, ierarhie vizuala clara, spatiu suficient intre elemente.
- Continutul pe fiecare materie trebuie detaliat pe capitole si subcapitole, cu exemple clare.
- Fiecare sectiune trebuie sa aiba surse citate (link-uri) pentru verificare.
- In pagini se vor putea copia usor link-urile citariilor pentru studiu ulterior.
- Structura de continut trebuie sa fie consistenta si mapabila direct in UI (titluri clare, liste, tabele unde e cazul).

Agentul trebuie sa structureze continutul astfel incat sa poata fi usor mapat in UI (capitole clare, titluri consistente, liste de surse).

**Stack ales**
- Backend: FastAPI
- Frontend: SvelteKit

**Directie viitoare - gamificare**
Se vor evalua mecanici simple (progres, badge-uri, streak-uri), dar numai dupa stabilizarea continutului.
- Directie asumata: sistem de nivel 1-10; nivel 10 presupune parcurgerea integrala a capitolelor, checklist-urilor si quiz-urilor.

**Documentatie obligatorie**
- `Documentatie.md` trebuie sa descrie toate componentele proiectului (continut, arhitectura, UI, flux de date, citare).
- Documentatia trebuie sa fie suficient de clara pentru orice programator care inspecteaza proiectul.

**Repo si publicare**
- Proiectul va fi publicat pe GitHub.
- `.gitignore` obligatoriu (Python + frontend + OS files).
- In etapa de staging: workflow cu GitHub Actions si/sau preview public (ex. Vercel).
