# Keuzes

Elke belangrijke keuze, met de datum en waarom. Nieuwste onderaan.

---

## 2026-10-05 — Eerst een prototype met een kleinere scope

**Keuze:** De eerste versie draait om twee feiten per loopje: *wanneer is het loopje* en
*wanneer opent de inschrijving*. De mail bevat alle loopjes waarvan de inschrijving in de
komende 7 dagen opent. Nog geen filters op regio of afstand, geen "bijna vol", geen website,
geen aanmeldingen. De mail gaat alleen naar Dirk.

**Waarom:** Dirk wil eerst zien of de kern werkt voordat er een domein, lezers en een
e-maildienst bij komen. Postcode, straal, "bijna vol" en de website komen later terug.

## 2026-10-05 — Python, GitHub Actions, één YAML-bestand per loopje

**Keuze:** Zoals voorgesteld in de opdracht.

**Waarom:** Dirk kent GitHub Actions al. YAML-bestanden zijn met de hand te lezen en via de
GitHub-website aan te passen. Geen database nodig.

## 2026-10-05 — Prototype verstuurt mail via Gmail, geen e-maildienst

**Keuze:** Zolang alleen Dirk de mail krijgt, versturen we via zijn eigen Gmail-account met een
app-wachtwoord. Een e-maildienst (Brevo of Laposta) kiezen we pas als er lezers komen.

**Waarom:** Geen nieuw account, gratis, en zonder eigen domein komt een mail van een dienst
"namens" een gmail-adres vaak in de spam. Een mail van Gmail aan jezelf komt altijd aan.
Zie [docs/advies-email-en-hosting.md](docs/advies-email-en-hosting.md).

## 2026-10-05 — Repository openbaar (voorstel, nog te bevestigen)

**Keuze:** `dirkridhub/loopjespost`, openbaar.

**Waarom:** Gratis onbeperkte GitHub Actions-minuten en later gratis GitHub Pages. Er staan
geen geheimen in, alleen code en openbare feiten over loopjes.

## 2026-10-05 — Herkenbare bezoeker zonder e-mailadres in de code

**Keuze:** Het script stelt zich bij websites voor als
`LoopjespostBot/0.1 (+https://github.com/dirkridhub/loopjespost)`.

**Waarom:** Organisatoren kunnen zien wie er langskomt en hoe ze ons bereiken (via de
repository), zonder dat Dirks e-mailadres openbaar in de code staat. Als er een domein is,
komt er een contactadres bij.

## 2026-10-05 — AI: Claude Haiku 4.5, alleen bij een echte wijziging

**Keuze:** Het goedkoopste Claude-model. Het wordt alleen aangeroepen als de tekst van een
pagina anders is dan bij de vorige controle (vergeleken via een vingerafdruk/hash).

**Waarom:** Datums staan op sites in allerlei vormen ("opent 1 november om 20:00",
"vanaf medio januari"). Een vaste zoekregel mist die. Bij 20 loopjes kost dit naar schatting
minder dan 1 euro per maand.

## 2026-10-05 — Nooit gokken

**Keuze:** Geen bron, of de AI is niet zeker? Dan is de waarde "onbekend" en komt er een
GitHub Issue voor Dirk. Er wordt nooit een datum verzonnen.

**Waarom:** Een verkeerde datum in de mail is erger dan geen datum.
