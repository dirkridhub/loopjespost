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

## 2026-10-16 — De monitor schrijft in data/, niet in events/

**Keuze:** Wat de monitor vindt, komt in `data/state/<id>.json`. De bestanden in `events/` zijn
van Dirk. Vult Dirk daar zelf een inschrijfdatum in, dan gaat die voor (wordt gebruikt vanaf de mail in fase 2).

**Waarom:** Zo overschrijft de computer nooit een correctie van Dirk, en blijven de
YAML-bestanden met hun uitleg leesbaar.

## 2026-10-16 — Extra controle tegen verzonnen antwoorden

**Keuze:** De AI moet bij elke waarde een zinnetje letterlijk uit de pagina citeren. Staat dat
zinnetje niet echt op de pagina, of heeft de datum een raar formaat, dan telt het als lage
zekerheid en komt er een issue.

**Waarom:** Gratis te controleren en vangt het belangrijkste risico af: een AI die een datum verzint.

## 2026-10-16 — Bij twijfel wordt het hele resultaat vastgehouden

**Keuze:** Twijfelt de AI over één veld, dan wordt voor dat loopje niets bijgewerkt en komt er
één issue. Dezelfde pagina leidt de volgende dag niet tot een tweede issue.

**Waarom:** Simpel en veilig. Dirk zet de juiste waarde in het YAML-bestand en sluit het issue.

## 2026-10-16 — Eerste controle is een nulmeting

**Keuze:** De eerste keer dat een loopje wordt gecontroleerd, slaan we de status op zonder
"wijziging" te melden.

**Waarom:** Anders lijkt bij elk nieuw loopje alles in één keer "veranderd".

## 2026-10-16 — Controle om 03:00 UTC

**Keuze:** GitHub Actions draait om 03:00 UTC: 05:00 in de zomer, 04:00 in de winter.

**Waarom:** Eén regel in plaats van twee, en het maakt voor de mail niet uit.

## 2026-10-16 — Eén echte pagina als testmateriaal

**Keuze:** In `tests/fixtures/` staat de homepage van de Stuwwalloop (opgehaald op 16-10-2026)
en een nagemaakte versie met een verzonnen aankondiging voor 2027. Alleen als testmateriaal.

**Waarom:** Zo testen we het uitlezen zonder internet. We bewaren zo weinig mogelijk pagina's
van anderen; de overige twee opgehaalde pagina's zijn weer verwijderd.

## 2026-10-16 — Model: Claude Haiku 4.5 via gestructureerde output

**Keuze:** De AI moet antwoorden in een vast formaat (JSON-schema). Per veld: waarde, zekerheid
en bronzin.

**Waarom:** Geen los tekstantwoord dat we moeten ontleden. Of Haiku betrouwbaar genoeg is,
testen we op echte pagina's zodra de API-sleutel er is. Zo niet, dan stappen we over op Sonnet
(ongeveer 2x zo duur, nog steeds enkele euro's per maand).

## 2026-10-16 — Eerste 20 loopjes: rond Oosterbeek, binnen 25 km

**Keuze:** 20 loopjes binnen 25 km (rechte lijn, PDOK) van postcode 6861WX. Gevonden via
zoekmachines, maar elk loopje is gecontroleerd op de **eigen site van de organisator**; alleen die
site staat in het bestand. Datums van het loopje staan nog niet in het `datum_loopje`-veld, maar in de
notities: zo vult de monitor ze zelf in en kunnen we zijn antwoord vergelijken met wat wij zagen.

**Waarom:** Geen gegevens overnemen van hardloopkalenders. En een ingevulde datum "wint" van de
monitor, dus die laten we leeg tot er een correctie nodig is.

Afgevallen kandidaten:
- Groot Ginkelse Loop (Wekerom): het oude domein is nu een gokwebsite.
- Nijmeegse Nieuwjaarsloop (Cifla): de pagina laadt zijn tekst pas in de browser, met een
  gewoon verzoek zien we niets. Kan later met een headless browser, als dat nodig blijkt.
- Pietenloop (Bemmel): geen eigen website gevonden.

## 2026-10-18 — Strengere controle na de eerste echte runs

De eerste twee nachten (20 loopjes, 23 AI-aanroepen, $ 0,085) lieten zien waar het misging:
- De AI "rekende" een datum uit ("volgend jaar" werd 27 juni 2027) of gaf een onmogelijke datum (2027-02-00).
- Een vorige editie (Posbankloop 27-09-2026) werd als volgende editie opgeslagen.
- Een terechte bronzin werd afgekeurd door een krul-apostrof (Ciko’66 tegenover Ciko'66).

**Keuze:**
- Een datum telt alleen als dag én maand letterlijk in de bronzin staan, en de datum echt bestaat.
  Hetzelfde geldt voor de tijd.
- Ligt de gevonden datum van het loopje in het verleden, dan gaat het om de vorige editie: datum,
  status en opening van de volgende editie zijn dan "onbekend".
- Bij het vergelijken van de bronzin tellen krullende en rechte aanhalingstekens als gelijk.
- Een versienummer in de vingerafdruk: verandert de controle, dan wordt elk loopje één keer opnieuw gelezen.
- De nachtelijke run staat op 03:17 UTC in plaats van 03:00. GitHub startte de runs 4,5 uur te laat,
  en vertraagt het meest op het hele uur.

**Waarom:** Dit zijn gratis controles in code die precies de gevonden fouten afvangen,
zonder dat het een duurder model nodig heeft.

## 2026-10-22 — Minder ruis: vingerafdruk, één issue per loopje, niets weggooien

Na een week (19-22 oktober): 55 AI-aanroepen ($ 0,21) en 10 issues, waarvan veel dubbel. Oorzaken:
- De Lingezegen-site heeft een aftelklok, en de sites van de Stichting Zevenheuvelenloop zetten hun
  blokken elke keer in een andere volgorde. De pagina leek dus elke dag "veranderd".
- Elke nieuwe twijfel gaf een nieuw issue (Goffert Run Festival: drie keer).
- Als de AI een waarde de ene keer wel en de volgende keer niet vond, werd dat een issue.

**Keuze:**
- De vingerafdruk negeert aftelklokken ("134 dagen 17 uren") en de volgorde van de woorden.
  De AI leest wel de volledige tekst, in de goede volgorde.
- Per loopje staat er hooguit één issue open. Wordt de pagina later wel duidelijk, dan sluit de
  monitor het issue zelf (met een reactie).
- Vindt de AI een eerder gevonden waarde nu niet, dan houden we de oude waarde. Een waarde verdwijnt
  alleen als de pagina duidelijk iets anders zegt (zoals een editie die voorbij is).
- "Open" of "vol" publiceren we alleen als we ook weten voor welke datum. Anders: onbekend.

**Waarom:** Dirk moet hooguit een uur per week kwijt zijn aan checks. Issues zijn alleen voor
echte twijfel over een nieuwe datum of status.

**Nog open:** GitHub start de nachtelijke run elke dag ongeveer 5 uur te laat (rond 10:30 in plaats
van 05:17). Voor een wekelijkse mail maakt dat niet uit. Voor het "vaker controleren vlak voor een
opening" (fase 4) wel; daar kiezen we later een oplossing voor.
