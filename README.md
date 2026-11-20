# AI Literacy voor docenten – HU-versie (concept)

Bewerking voor de Hogeschool Utrecht van de e-learning **“AI Literacy voor docenten”** van TLC Central & TLC Science (Universiteit van Amsterdam), gebruikt met toestemming van de makers.

- `index.html` – de e-learning als losse webpagina (open in een browser). Plekken die nog moeten worden aangepast zijn gemarkeerd.
- `HU-aanpassingen-en-advies.docx` – lijst van wat nog moet worden vervangen, met advies voor HU-alternatieven en bronnen.
- `lessons/` – handmatig bewerkte hoofdstukken (nu 1 en 2). Overige hoofdstukken worden automatisch uit `data/course.json` opgebouwd.
- `assets/` – HU-logo (aangeleverd door team Huisstijl; niet onder de CC-licentie, alleen in een privé-repository delen).
- `template.html`, `build.py` – opmaak en bouwscript (`data/cont.json` bepaalt waar de "Doorgaan"-knoppen staan, zoals in het origineel). Opnieuw bouwen: `python3 build.py`.
- `make_docx.py`, `data/rows.json`, `data/links.json` – genereert het Word-bestand (`python-docx`).

## Licentie en bronvermelding
Origineel: “AI Literacy voor docenten”, TLC Central & TLC Science, Universiteit van Amsterdam – [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.nl).
Deze bewerking bevat wijzigingen (aanpassingen voor de HU) en wordt onder dezelfde licentie gedeeld: **CC BY-NC-SA 4.0**. Niet voor commercieel gebruik.
Logo’s en huisstijlelementen van de UvA en de HU vallen niet onder deze licentie.
