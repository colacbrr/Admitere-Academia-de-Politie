# Verificare surse - 2026-02-11

## Scop
Validare tehnica a link-urilor citate in `guide/` si corectarea link-urilor nefunctionale.

## Metoda
- Extragere URL-uri unice din toate fisierele `.md` din `guide/`.
- Verificare HTTP cu `curl` (status code).
- Inlocuire link-uri `404` cu alternative oficiale functionale.

## Rezumat rezultate
- URL-uri verificate: 18
- URL-uri cu status `200`: 15
- URL-uri cu status `520` la `curl`: 3 (toate pe `dictionary.cambridge.org`)

## Link-uri corectate
- Inlocuit link nefunctional programa LLR cu:
  - `https://www.edu.ro/sites/default/files/2_Anexa_%202_Limba_si_literatura_romana_TC_IX_90.pdf`
- Inlocuit link nefunctional programa Limba moderna cu:
  - `https://www.edu.ro/sites/default/files/_fi%C8%99iere/Minister/2025/programe_scolare_cons_pub/Lb_moderna_1_TC_CS_IX_EN_FR_SP_IT.pdf`

## Observatii
- Domeniul Cambridge returneaza `520` la verificare automata `curl` (probabil protectie anti-bot).
- Link-urile Cambridge sunt pastrate, dar trebuie verificate manual in browser la fiecare revizie periodica.

## Conformitate template
- Toate capitolele non-INDEX au acum sectiunile standard obligatorii.
- Toate capitolele cu `Identificare` includ `Ultima verificare surse: 2026-02-11`.
