# Planificare - proiect ghid admitere

**Scop**
Acest proiect va deveni un "Guide throughout the preparation for academic entry exam" pentru admiterea la Academia de Politie. Ghidul final va explica complet probele de admitere si va oferi trimiteri catre surse online de incredere pentru studiu aprofundat, astfel incat oricine poate verifica informatia.

**Surse principale**
- Regulamentul oficial din `Regulament-admitere-licenta-2026-actualizare-18-01-2026.pdf`
- Pagina oficiala de admitere a Academiei (pentru actualizari si materiale)
- `Documentatie.md` ca rezumat intern, care va fi sincronizat cu regulamentul

**Surse online oficiale (de citat)**
- Academia de Politie - admitere licenta: `https://admitere.academiadepolitie.ro/`
- Regulament oficial 2026 (link public): `https://admitere.academiadepolitie.ro/docs/2026/licenta/Regulament-admitere-licenta-2026-actualizare-18-01-2026.pdf`
- MAI - ordin examinare medicala (baza legala): `https://legislatie.just.ro/Public/FormaPrintabila/00000G02FVPQBRGW38Z0Y7A95OP50LVD`

**Ce trebuie sa includa ghidul final**
- Descrierea etapelor de admitere.
- Proba scrisa: structura, durata, notare, criterii de promovare.
- Proba fizica: explicata clar, cu referinte la regulament.
- Examinarea medicala: rolul ei si cadrul general.
- Pentru fiecare materie de la proba scrisa:
  - descriere clara a probei
  - capitolele oficiale din tematica
  - explicarea fiecarui capitol pe inteles
  - link-uri de incredere (academice / institutionale) pentru aprofundare

**Cerinte de calitate**
- Toate informatiile despre admitere trebuie sa aiba trimitere la regulamentul oficial.
- Orice completare din afara PDF-ului trebuie citata (link in format cod).
- Evitam formulari ambigue, explicam cu date concrete (ex: calendar, durata probei).
- Diferentiem clar ce este "din regulament" vs "explicatie suplimentara".

**Metoda de lucru propusa**
1. Extragem din PDF toate articolele relevante despre etapele admiterii.
2. Extragem tematica oficiala pe discipline.
3. Construim structura ghidului pe capitole.
4. Pentru fiecare subcapitol, cautam surse online credibile si le citam in ghid.
5. Verificam coerenta intre ghid si regulamentul oficial.
6. Verificam periodic daca au aparut actualizari pe pagina oficiala.

**Nota despre citari**
- Orice informatie adaugata din exterior trebuie sa aiba o citare clara in format cod: `https://...`
- Daca exista contraditii intre surse, se noteaza explicit.

**Rezultat final asteptat**
Un ghid complet si usor de urmarit care acopera:
- procesul complet de admitere
- cerintele fiecarui test
- structura exacta a materiilor
- link-uri utile pentru studiu detaliat

**Observatie despre actualizari**
Regulamentele pot suferi modificari; ghidul trebuie sa precizeze daca se refera la sesiunea 2026 sau la o sesiune ulterioara.

**Directie viitoare - aplicatie web**
Proiectul va evolua intr-o aplicatie cu interfata web. Utilizatorul va rula un executabil local care porneste un server si hosteaza pagina web. Interfata va oferi:
- navbar cu teme, materii, capitole
- pagini dedicate pentru proba scrisa, fizica, medicala
- sectiune viitoare pentru Q&A
- cautare rapida in continut

**Note pentru structura UI**
- Continutul trebuie impartit pe unitati mici (capitol/subcapitol) pentru navigare rapida.
- Fiecare unitate include rezumat + surse.

**Arhitectura folderelor**
Structura folderelor este definita in `guide/00_meta/STRUCTURA.md`.
