# Advies: e-mail, hosting en kosten

Peildatum: oktober 2026. Prijzen kunnen veranderen; check ze opnieuw voordat je iets afsluit.

## Kort advies

| Fase | E-mail | Website | Kosten per maand |
|---|---|---|---|
| Prototype (nu) | Je eigen Gmail, alleen naar jezelf | Geen | ca. € 0 tot 1 (alleen AI) |
| Eerste lezers (tot ca. 300) | Brevo gratis of Laposta gratis | GitHub Pages (gratis) | ca. € 1 + domein (€ 1) |
| 1.000 lezers | Brevo Starter of Laposta | GitHub Pages | ca. € 10 tot 20 |

## E-mail

**Prototype: Gmail.** Zolang de mail alleen naar jou gaat, is een e-maildienst overbodig.
Je maakt in je Google-account een *app-wachtwoord* aan (een apart wachtwoord dat alleen dit
script mag gebruiken) en dat zetten we in GitHub Secrets. Gratis, geen nieuw account.

**Later: kiezen tussen Brevo en Laposta.** Beide zijn Europees, hebben een API en double opt-in.

| | Brevo (Frans) | Laposta (Nederlands) |
|---|---|---|
| Gratis | 300 mails per dag, onbeperkt veel contacten, API | Tot 2.000 contacten en 12.000 mails per maand, met Laposta-logo |
| Betaald | Starter vanaf ca. $ 9 per maand (geen daglimiet) | Abonnement vanaf € 210 per jaar (ca. € 17,50 per maand), of losse credits vanaf € 9 per verzending |
| Persoonlijke mail per lezer (eigen regio) | Ja, goed geschikt via de API voor losse mails | Vooral gemaakt voor één nieuwsbrief aan iedereen |
| Data in de EU | Ja | Ja, servers in Nederland |

**Mijn advies voor later:**
- Krijgt iedereen dezelfde mail? Dan **Laposta**. Nederlands, simpel, en tot 2.000 lezers gratis.
- Krijgt iedereen een eigen mail, gefilterd op postcode? Dan **Brevo**, omdat dat beter bij
  losse, persoonlijke mails past. Bij 1.000 lezers past de wekelijkse mail niet binnen 300 per
  dag, dus dan heb je Starter nodig (ca. $ 9 per maand).

Deze keuze hoeft pas in fase 3.

## Website (later)

**GitHub Pages**, gratis bij een openbare repository. De site wordt na elke update automatisch
opnieuw gebouwd. Cloudflare Pages is een goed alternatief, maar dan heb je een extra account
nodig. Voor het organisatorenformulier is later één kleine gratis tussenstap nodig, bijvoorbeeld
een Cloudflare Worker, omdat een statische site zelf geen GitHub Issue mag aanmaken.

Domein: een `.nl`-domein kost ongeveer € 10 tot 15 per jaar. Dat is pas nodig als er lezers komen.

## AI (Claude API)

- Model: Claude Haiku 4.5, het goedkoopste model. Prijs: $ 1 per miljoen woorden-stukjes (tokens)
  die erin gaan, $ 5 per miljoen die eruit komen.
- Schatting voor 20 loopjes: een paar pagina's per dag die echt veranderen, elk ongeveer 5.000 tokens.
  Dat is ongeveer 100 aanroepen per maand en **minder dan € 1 per maand**.
- Bij 100 loopjes en elk uur controleren vlak voor openingen: naar schatting **€ 2 tot 5 per maand**.
- Let op: Anthropic werkt met vooruitbetaald tegoed. Het minimum is $ 5. Dat is de enige
  uitgave die het prototype nodig heeft.

## GitHub Actions

Gratis en onbeperkt bij een openbare repository. Een privé-repository heeft 2.000 gratis
minuten per maand. Een dagelijkse controle van 20 loopjes kost ongeveer 2 minuten per run,
dus ook dat zou passen.
