# Accounts en sleutels die jij zelf aanmaakt

Voor het prototype zijn er maar drie stappen. Deel sleutels **nooit** in de chat of in een
bestand dat in git komt. Zet ze alleen op de plekken die hieronder staan.

## 1. GitHub-repository (gratis)

1. Ga naar https://github.com/new (ingelogd als `dirkridhub`).
2. Naam: `loopjespost`. Kies **Public**. Vink niets anders aan (geen README, die hebben we al).
3. Klik op **Create repository**. Laat het mij weten, dan koppel ik de map op je Mac eraan.

## 2. Claude API-sleutel (kost geld: minimaal $ 5 tegoed)

1. Ga naar https://console.anthropic.com en maak een account aan.
2. Ga naar **Billing** en zet er $ 5 tegoed op. Zet automatisch bijladen **uit**.
3. Ga naar **Settings > Limits** en stel een maandlimiet in, bijvoorbeeld $ 5.
4. Ga naar **API Keys > Create Key**. Noem hem `loopjespost`. Kopieer de sleutel.
5. Zet hem in GitHub: repository > **Settings > Secrets and variables > Actions >
   New repository secret**. Naam: `ANTHROPIC_API_KEY`. Plak de sleutel en klik **Add secret**.

## 3. Gmail app-wachtwoord (gratis, nodig in fase 2)

1. Tweestapsverificatie moet aan staan op je Google-account.
2. Ga naar https://myaccount.google.com/apppasswords.
3. Maak een app-wachtwoord met de naam `loopjespost`. Je krijgt 16 letters te zien.
4. Zet ze in GitHub Secrets, net als bij stap 2:
   - `GMAIL_ADDRESS`: je gmail-adres
   - `GMAIL_APP_PASSWORD`: de 16 letters (zonder spaties)

## Lokaal testen (optioneel)

Wil je het script op je eigen Mac draaien? Kopieer `.env.example` naar `.env` en vul de
waarden in. `.env` staat in `.gitignore`, dus het komt nooit op GitHub.

## Later (niet nu)

- Domeinnaam (ca. € 10 tot 15 per jaar)
- Brevo of Laposta (zie het advies)
- Eventueel Cloudflare (gratis) voor het organisatorenformulier
