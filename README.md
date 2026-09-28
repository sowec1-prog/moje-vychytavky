# Vychytávky.cz — launch-ready katalog

Český obsahový katalog praktických gadgetů a mobilního příslušenství. Aktuální verze obsahuje **72 veřejně ověřených produktových stránek** ve 5 kategoriích:

- MagSafe a Qi2
- Nabíječky a cestování
- Do auta
- Apple Watch
- Zásuvky a kabely

## Stav affiliate programu

Toto **není ještě monetizovaný web**. Všechny odkazy jsou běžné odkazy na obchod a nejsou provizní.

- Cubenest.cz — žádost o schválení odeslána v eHUBu
- Mobilegear.cz — připravený sortiment po schválení
- eshop.EVOLVEO.cz — připravený sortiment po schválení
- ApolloStore.cz — připravený sortiment po schválení

Po schválení se do webu vkládají pouze odkazy vygenerované přímo eHUBem. Nikdy se nevymýšlí partner ID ani parametry.

## Lokální spuštění ve Windows

```bash
uv run --with flask python app.py
```

Otevři `http://127.0.0.1:5055`. Stav serveru ověří `http://127.0.0.1:5055/healthz`.

## Ověření

```bash
python -m unittest discover -s tests -v
```

## Připravené nasazení

Projekt obsahuje `requirements.txt`, `Procfile` a `render.yaml` pro Python hosting. Než se vytvoří veřejná služba nebo začne platit hosting, je nutné:

1. mít schválený alespoň jeden affiliate program;
2. vložit právně správné označení partnerských odkazů a zásady soukromí pro zvolenou doménu;
3. potvrdit název domény a poskytovatele hostingu;
4. vytvořit neveřejný/veřejný GitHub repozitář a nasadit jej bez jakýchkoli tokenů či bankovních údajů v kódu.

`render.yaml` má `autoDeploy: false`, takže samotné nahrání repozitáře nevytvoří ani nezpoplatní veřejný hosting.
