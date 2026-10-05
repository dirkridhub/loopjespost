# Loopjespost

Een gratis e-mail die hardlopers laat weten welke loopjes de komende week hun inschrijving openen.

> Status: **prototype** (fase 0, opzet). Er draait nog niets automatisch.

## Wat doet het (prototype)

1. Voor elk loopje staat een klein bestand in de map `events/`. Daarin staat vooral:
   - **wanneer het loopje is**, en
   - **wanneer de inschrijving opent**.
2. Elke dag kijkt een script op de website van de organisator of er iets veranderd is.
   Alleen als de pagina echt anders is, leest een AI de nieuwe datums uit.
3. Is de AI niet zeker? Dan komt er een GitHub Issue (een soort taakje) bij jou om te checken.
   Er wordt dan niets automatisch aangepast.
4. Elke donderdag krijg jij een mail met alle loopjes waarvan de inschrijving
   in de komende 7 dagen opent.

## De mappen

| Map / bestand | Wat staat erin | Mag jij hier zelf in werken? |
|---|---|---|
| `events/` | Eén bestand per loopje. `_voorbeeld.yaml` laat zien hoe het eruitziet. | Ja, ook via de GitHub-website. |
| `data/` | Wat het script vindt: eerdere controles en gevonden wijzigingen. | Liever niet, dit vult het script. |
| `loopjespost/` | De Python-code. | Nee. |
| `tests/` | Tests, met opgeslagen voorbeeldpagina's (fixtures). | Nee. |
| `docs/` | Advies en uitleg voor jou. | Lezen. |
| `DECISIONS.md` | Elke belangrijke keuze en waarom. | Lezen. |
| `.env.example` | Lijst met geheime sleutels die nodig zijn (zonder de sleutels zelf). | Lezen. |

## Een loopje toevoegen of corrigeren

1. Ga op GitHub naar de map `events/`.
2. Nieuw loopje: open `_voorbeeld.yaml`, kopieer de inhoud, en maak een nieuw bestand
   met de naam van het loopje, bijvoorbeeld `stuwwalloop.yaml`.
3. Corrigeren: open het bestand, klik op het potloodje, pas aan, en klik op "Commit changes".
4. Weet je iets niet? Laat het veld leeg. Nooit gokken.

## Geheimen

Sleutels en wachtwoorden staan **nooit** in de code. Ze staan in GitHub Secrets
(voor de automatische runs) en lokaal in een `.env`-bestand dat niet in git komt.
Zie [docs/accounts-en-sleutels.md](docs/accounts-en-sleutels.md).
