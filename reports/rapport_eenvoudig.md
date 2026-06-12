# Wat heb ik nu eigenlijk gedaan? — een simpele uitleg

**Auteur:** Quinten
**Datum:** juni 2026
**Voor wie:** familie, vrienden, iedereen zonder data science achtergrond

---

## De vraag waar ik mee begon

Mensen zeggen wel eens: *"Trump tweet iets en de beurs gaat omhoog of omlaag."* Klopt dat eigenlijk? Kun je dat meten? En, een zwaardere vraag: zou hij dat **bewust** kunnen doen — bijvoorbeeld om de olieprijs te beïnvloeden tijdens de oorlog met Iran die in februari is uitgebroken?

Dat wilde ik uitzoeken voor mijn eindwerk data science.

## Wat ik heb gebouwd

Stel je voor: een soort *meetstation* dat continu twee dingen tegelijk bijhoudt:

1. **Wat Trump schrijft op Truth Social** (zijn sociale media platform sinds hij van Twitter is gegooid). Ik heb meer dan 26.000 van zijn berichten verzameld uit de afgelopen vier jaar, plus alle nieuwe berichten sinds de oorlog begon — die haalt mijn programma elke keer automatisch op.

2. **Wat de olieprijs doet** — minuut voor minuut. Plus de algemene aandelenmarkt, en de aandelen van olie-bedrijven specifiek.

Daarna heb ik de computer geleerd om dingen te herkennen:

- **Hoe Trump zich voelt als hij schrijft.** Boos? Blij? Neutraal? De computer raadt dit nu in 83 van de 100 gevallen goed — dat is best aardig.
- **Of een bericht aanvallend ("toxic") is.** Scheldwoorden, beschuldigingen, dat soort taal. Hier scoort de computer nog beter: hij herkent het correct in 86 van de 100 gevallen.

Met die meetinstrumenten kon ik vervolgens kijken naar **wat er rond de olieprijs gebeurt** wanneer Trump iets over Iran schrijft.

---

## Van naaldje tot draadje: wat gebeurt er in elke notebook?

Mijn project is opgebouwd uit 13 "notebooks". Een notebook is gewoon een werkdocument waarin code, uitleg en resultaten naast elkaar staan — als een digitaal labjournaal. Ze volgen elkaar logisch op: de ene levert de grondstof voor de volgende. Hieronder leg ik per notebook uit wat er gebeurt, in gewone taal.

Even een paar termen vooraf, zodat de rest leesbaar blijft:

- **Return** = procentuele prijsverandering. "De beurs deed +1%" is een return.
- **Basispunt (bp)** = een honderdste van een procent. 100 bp = 1%. Handig om kleine bewegingen netjes uit te drukken.
- **Model trainen** = de computer voorbeelden laten zien tot hij een patroon herkent, zoals je een kind leert appels van peren te onderscheiden door er veel te tonen.
- **Train/test split** = je leert de computer op de helft van de gegevens en test hem daarna op de andere helft, die hij nog nooit gezien heeft. Anders weet je niet of hij écht iets geleerd heeft of gewoon antwoorden uit zijn hoofd heeft geleerd.

### Notebook 01 — De berichten verzamelen

Hier bouw ik de verzameling van Trump's posts op. Ik haal ze uit drie mogelijke bronnen, in volgorde van betrouwbaarheid: een stabiel archief (van Kaggle, een bekende dataplatform), een live-scraper die de nieuwste berichten ophaalt, en als laatste redmiddel nep-data om de code te testen als het internet plat ligt.

Het resultaat: **26.819 berichten met tekst**, van 14 februari 2022 tot nu. Er waren oorspronkelijk 32.754 berichten, maar bijna 6.000 daarvan waren alleen een foto of video zonder tekst — die kan ik niet analyseren, dus die gooi ik eruit. Daarna doe ik controles: zitten er dubbele berichten in? Kloppen de datums? Staan ze op volgorde? Dat soort huishoudelijke checks voorkomt fouten verderop.

### Notebook 02 — De marktdata verzamelen

Hetzelfde, maar nu voor de financiële markten. Ik download de dagelijkse koersen van vier dingen: de S&P 500 (de brede Amerikaanse beursindex), WTI (ruwe olie), de VIX ("angstindex" van de beurs) en de DXY (de waarde van de dollar). De data loopt van februari 2022 tot **8 juni 2026** (mijn laatste update).

Dan controleer ik de kwaliteit: ontbreken er dagen, zitten er gaten in? Ik bereken de dagelijkse koersbewegingen en bekijk hoe ze verdeeld zijn. Een leuke sanity-check: de VIX (angst) beweegt sterk tegengesteld aan de S&P 500 — als de beurs daalt, schiet de angst omhoog. Dat klopt met de theorie en bevestigt dat mijn data deugt.

### Notebook 03 — Berichten en markt aan elkaar koppelen

Nu komt het samen. Voor elk bericht wil ik weten: wat deed de markt erna? Maar dat is niet zo simpel als "kijk naar de koers de volgende dag", want de markt beweegt ook gewoon vanzelf. Daarom bereken ik de **abnormale return**: hoeveel de markt bewoog *bovenop* wat normaal zou zijn. Het "normale" schat ik uit het gemiddelde van de 30 dagen ervoor — en cruciaal: ik kijk nooit vooruit, alleen naar het verleden, anders zou ik vals spelen.

Een bericht in het weekend koppel ik aan de eerstvolgende handelsdag (maandag). Daarna doe ik een belangrijke basistest: is de markt op dagen mét een Trump-bericht gemiddeld anders dan op dagen zónder? Het antwoord is: nauwelijks. Dat is geen slecht nieuws — het betekent gewoon dat niet *elk* bericht de markt beweegt, alleen specifieke over specifieke onderwerpen. Precies dat ga ik later uitpluizen.

### Notebook 04 — Tekst omzetten naar getallen

Een computer kan niet rekenen met woorden, alleen met getallen. In deze notebook zet ik elk bericht om in een lange rij cijfers die aangeeft welke woorden erin voorkomen (een techniek die "TF-IDF" heet — je hoeft de naam niet te onthouden). Zo ontstaan ongeveer 5.000 woord-kenmerken per bericht.

Het belangrijkste hier is iets wat makkelijk fout gaat: ik splits de data **op tijd**, niet willekeurig. De computer leert op de oude berichten en wordt getest op de nieuwere. Zou ik willekeurig splitsen, dan zou hij stiekem "de toekomst" mogen zien tijdens het leren — dat geeft mooie maar nepresultaten. Op tijd splitsen is eerlijker en realistischer.

### Notebook 05 — De computer laten voorspellen

Hier probeer ik de oorspronkelijke vraag te beantwoorden: kun je uit de wóórden van een bericht voorspellen wat de markt doet? Ik train verschillende soorten modellen (waaronder een "Random Forest", een verzameling beslisbomen) en vergelijk ze met simpele gok-modellen als ondergrens.

De uitkomst is eerlijk en een beetje teleurstellend: **de modellen voorspellen nauwelijks beter dan gokken.** De richting van de markt raden ze ongeveer in de helft van de gevallen goed — net als kop of munt. Dit is een echt resultaat, geen mislukking: het laat zien dat Trump's berichten in het algemeen géén betrouwbaar voorspellend signaal bevatten. Dít was het moment waarop ik mijn onderzoek heb bijgestuurd naar de gerichtere vragen (Iran, tarieven, sentiment).

### Notebook 06 — Welke woorden tellen eigenlijk mee?

Voor de volledigheid kijk ik welke woorden de modellen het belangrijkst vonden. Ik gebruik twee technieken die als het ware aan het model vragen "welke woorden maken voor jou het verschil?". Omdat het signaal zwak was (notebook 05), zijn ook de belangrijkste woorden weinig overtuigend. Dat bevestigt netjes het vorige resultaat: er zit geen sterk, woord-gebaseerd voorspellend patroon in. Ik bespreek hier ook waarom je voorzichtig moet zijn als je honderden woorden tegelijk test — dan vind je per ongeluk altijd wel "iets" dat toeval is.

### Notebook 07 — Een nieuwe richting: stemming en toon

Omdat het voorspellen van de markt weinig opleverde, verschuift mijn focus. In plaats van *"wat doet de markt?"* ga ik kijken naar *"wat zit er eigenlijk in die berichten?"*. Het Kaggle-archief bevat al kant-en-klare labels voor de stemming (positief/negatief/neutraal) en de toxiciteit van elk bericht. Ik verken die: hoe is de stemming verdeeld, verandert ze door de tijd, welke onderwerpen zijn het negatiefst, en krijgen boze berichten meer of minder likes? Dit is de opstap naar de twee classifiers in de volgende notebooks.

### Notebook 08 — Een eigen stemmings-herkenner bouwen

Hier train ik de computer om zelf de stemming van een bericht te bepalen, op basis van de Kaggle-labels als "juiste antwoorden". Ik probeer drie methodes, van simpel tot geavanceerd, waaronder een groot, kant-en-klaar taalmodel (Twitter-RoBERTa).

Het verrassende resultaat: mijn **simpele model wint** met 83% nauwkeurigheid, terwijl het zware kant-en-klare taalmodel maar 69% haalt. De reden is leerzaam: dat grote model was getraind met een ándere definitie van "positief/negatief" dan die in mijn data, terwijl mijn eigen model precies op de juiste labels leert. Les: een groot model is niet automatisch beter dan een goed afgestemd eenvoudig model.

### Notebook 09 — Een toxiciteits-herkenner bouwen

Dezelfde aanpak, maar nu voor de vraag: is een bericht aanvallend ("toxic") of niet? Dit is een ja/nee-vraag, dus iets makkelijker. Omdat maar zo'n kwart van de berichten echt toxic is, moet ik het model expliciet leren niet lui "altijd niet-toxic" te gokken. Resultaat: **86% nauwkeurigheid**. De woorden die het model als meest aanvallend aanmerkt — *hell, racist, stupid, loser, corrupt, disgrace, crooked, deranged* — vormen herkenbaar Trump's aanvalswoordenschat. Een mooie controle dat het model echt iets zinnigs heeft geleerd.

### Notebook 10 — De Iran-olie vraag (per dag)

Nu de kernvraag. Sinds de Iran-oorlog op 28 februari 2026: beweegt Trump met zijn berichten de olieprijs? Ik filter alle Iran-gerelateerde berichten eruit en zet ze naast de olieprijs. Ik markeer de grote gebeurtenissen ("anchor events"), maak een tijdlijn, en vergelijk per bericht en in totaal de marktbeweging na Iran-posts met die na gewone posts.

Conclusie: **geen statistisch betrouwbaar effect.** Alleen de dollar verzwakt een heel klein beetje na Iran-berichten. De grote olieprijs-sprongen blijken telkens vast te hangen aan concrete gebeurtenissen (een aanval, een aankondiging), niet aan Trump's berichten op zich. Ik doe ook een robuustheidstest: als ik de heftigste week (de Hormuz-blokkade in april) eruit haal, blijft de conclusie overeind.

### Notebook 11 — De importtarieven van Liberation Day (per dag)

Dezelfde methode, maar nu voor Trump's handelstarieven rond "Liberation Day" (2 april 2025). Dit verhaal is dramatischer: op Liberation Day kelderde de S&P 500 ruim 10% in drie dagen; toen Trump op 9 april een pauze van 90 dagen aankondigde, sprong de beurs fors terug. Ik filter de tarief-berichten, bekijk de tijdlijn, test het gemiddelde effect, doe een Granger-test (die kijkt wat eerst beweegt) en een volume-test.

Twee dingen springen eruit: het gemiddelde effect over álle tarief-berichten is statistisch niet significant (de grote bewegingen zitten in een paar losse momenten), maar het **handelsvolume stijgt met 50%** na een tarief-bericht. Dat betekent dat handelaars wel degelijk reageren — ze letten op wat Trump schrijft, ook al is de gemiddelde koersbeweging klein.

### Notebook 12 — Hoe snel reageert de markt? (per minuut)

Tot nu toe keek ik per dag. Hier gebruik ik voor het eerst data **per minuut**, om te zien of de markt al binnen enkele minuten na een bericht reageert. Ik bereken de "cumulatieve abnormale return": hoeveel beweegt de koers op- of neerwaarts in de 5, 15, 30, 60 en 120 minuten na een post, vergeleken met de rust ervoor.

Bevindingen: bij tarief-berichten zie ik vooral een verhoogd handelsvolume (50% meer). Bij Iran-berichten dalen de aandelen van oliebedrijven (XLE) gestaag tot zo'n 238 basispunten (bijna 2,4%) over twee uur — en die daling keert niet terug. Dat "niet terugkeren" is belangrijk: het wijst erop dat de markt echte informatie verwerkt, geen tijdelijke paniek. Ik test ook of escalatie- en de-escalatieberichten verschillen, maar dat onderscheid is te grof om iets hards over te zeggen.

### Notebook 13 — Het sterkste bewijs: wie was er eerst, het nieuws of Trump?

Dit is methodologisch mijn beste stuk. Het grote probleem in al het voorgaande is: misschien reageren zowel de markt als Trump op hetzelfde onderliggende nieuws ("common cause"). Om dat uit te zoeken gebruik ik GDELT, een internationaal project dat wereldwijd nieuwsberichten registreert met tijdstempel. Voor elk Trump-bericht zoek ik op: wanneer verscheen het eerste relevante nieuwsartikel?

Het resultaat is glashelder: van de 128 onderzochte berichten vond ik bij 90 een bijpassend nieuwsartikel, en in **alle 90 gevallen postte Trump pas nádat het nieuws al online stond** — gemiddeld zo'n 3 uur later. De overige 38 berichten (geen matchend nieuws gevonden) leverden géén grotere marktbeweging op. Ook de vertraging en de toon van het nieuws hebben geen verband met de marktreactie. Kortom: Trump is een *nieuwslezer met een groot platform*, geen marktbeweger.

> *Technisch detail: in deze notebook zat een subtiele bug. De kolom die aangeeft of Trump na het nieuws postte, stond opgeslagen als getal (1,0) maar werd vergeleken met "waar/onwaar". Daardoor vielen alle berichten weg en bleven grafieken leeg ("geen data"). Na de fix verschenen de 90 reactieve posts netjes. Het soort foutje dat je eraan herinnert om je tussenresultaten altijd te controleren.*

---

### Notebook 14 — Kijken naar losse aandelen in plaats van de hele beurs

Tot nu toe keek ik steeds naar de héle beurs (de S&P 500) of naar de olieprijs. Maar een index is een gemiddelde van honderden bedrijven — als Trump één bedrijf noemt, verdwijnt dat effect in dat gemiddelde. Dus draaide ik de vraag om: wat gebeurt er met het *aandeel van dat ene bedrijf* op de dag dat Trump het noemt?

Ik liet de computer alle 26.819 berichten doorzoeken op bedrijfsnamen (Apple, Tesla, Boeing, enzovoort) en koppelde elke vermelding aan de koers van dat bedrijf. Belangrijk trucje: ik trek eerst de algemene beursbeweging van die dag eraf, zodat ik alleen het *bedrijfseigen* effect overhoud.

Het resultaat is opvallender dan op beursniveau. **Tesla** springt eruit: op dagen dat Trump Tesla of Elon Musk noemt, daalt het aandeel gemiddeld stevig — en dat blijft staan ook als ik de extreemste dag (5 juni 2025, de publieke ruzie tussen Trump en Musk) weglaat. Ook **Trump's eigen mediabedrijf (DJT)** zakt na zo'n bericht. De effecten zijn groot, maar ik heb per bedrijf weinig dagen, dus statistisch blijven ze "net niet hard bewezen". De les is mooi: op individuele aandelen zie je wél een richting waar de brede index niets liet zien.

---

## Wat ik heb gevonden — het hoofdverhaal

### Nee, Trump beweegt de olieprijs niet

Het lijkt eerst alsof er een verband is. Maar als ik strenger ga rekenen, valt dat verband uiteen. De tijdsrichting klopt niet (de olieprijs beweegt eerst, Trump tweet erna), er zijn geen tekenen van marktmanipulatie, en — het sterkste bewijs — in alle gevallen waarbij ik een bijpassend nieuwsartikel vond, postte Trump pas ná het nieuws. De meest logische uitleg: zowel de markt als Trump reageren op hetzelfde onderliggende nieuws, maar Trump *bestuurt* de markt niet.

### De importtarieven: een duidelijker verhaal

Bij de handelstarieven is het effect groter en zichtbaarder. Op Liberation Day daalde de S&P 500 ruim 10% in drie dagen; bij de aankondiging van de 90-daagse pauze veerde de beurs fors op. De dollar verzwakte bij élke tarief-aankondiging. En het handelsvolume steeg met 50% na een tarief-bericht — de markt *let op*. De richting van de beweging volgde de inhoud: deal-signalen ("massive amount of requests for negotiations") gingen samen met stijgingen, harde aankondigingen ("IT'S LIBERATION DAY IN AMERICA!") met dalingen.

### Een paar leuke bij-vondsten

**1. Trump werd vrolijker na de verkiezingen.** Zijn gemiddelde stemming lag tijdens de campagne- en rechtszaak-jaren (2022–2024) net rond neutraal, en sprong na zijn inauguratie in januari 2025 zichtbaar omhoog naar duidelijk positief. Meetbaar in zijn taalgebruik.

**2. Negatieve berichten krijgen meer likes.** Zijn negatieve berichten krijgen mediaan 14.874 likes, zijn positieve maar 13.633 — een statistisch zeker verschil van ongeveer 9%. Dat geeft hem een prikkel om kwaad te schrijven. Een schoolvoorbeeld van de "negativity bias" op sociale media.

**3. Olie-aandelen vallen wel een beetje na Iran-tweets.** Niet de olieprijs zelf, maar de aandelen van olie-bedrijven (XLE) dalen licht en aanhoudend na Iran-berichten. Trump's Iran-berichten gaan vaak over de-escalatie en nucleaire onderhandelingen, wat de olie-risicopremie verlaagt.

**4. Losse aandelen reageren wél, vooral Tesla.** Waar de brede beurs niets liet zien, daalt het Tesla-aandeel duidelijk op dagen dat Trump Tesla of Elon Musk noemt — gemiddeld zo'n 80 à 110 basispunten meer dan op gewone dagen, en dat blijft staan ook zonder de extreme ruzie-dag. Een index verbergt zulke bedrijfseigen effecten; pas als je inzoomt op het losse aandeel worden ze zichtbaar.

## Wat ik er niet over kan zeggen

Wetenschap moet eerlijk zijn over wat de data **niet** kunnen vertellen:

- **Wat Trump zelf koopt of verkoopt.** Daar zou ik zijn bankgegevens voor moeten zien — niet beschikbaar voor een student.
- **Of escalatie- en de-escalatieberichten echt anders zijn.** De twee groepen zijn statistisch niet goed te onderscheiden — te veel berichten bevatten beide soorten woorden.
- **Of een specifieke tweet wel of niet een specifiek event veroorzaakte.** Voor de 38 posts zonder matchend nieuws weet ik niet zeker of dat echt "originele" informatie was, of dat ik het artikel gewoon gemist heb (GDELT dekt niet alle bronnen).
- **Reacties binnen seconden.** Zelfs met minuutdata kan ik supersnelle, geautomatiseerde reacties niet zien. Daarvoor zou ik nóg fijnere data nodig hebben.

## Wat dit project is geworden

Het is geen sensationeel verhaal "Trump bestuurt de oliemarkt". Het is een **eerlijk onderzoek** dat een populaire claim toetst en zegt: "de data ondersteunt dit verhaal niet — wat we zien is meer consistent met Trump als reageerder, niet als aanjager". En als bonus heb ik tools gebouwd die zijn berichten automatisch op stemming en toxiciteit kunnen scoren, die je live zou kunnen toepassen op alles wat hij vandaag of morgen schrijft.

Mijn eindwerk is geen Nobel Prize, maar het is wel echt werk: data verzameld, nieuwsarchieven doorzocht, ML-modellen getraind, statistische tests gedaan, eerlijke conclusies getrokken. En misschien is dat wel het allerbelangrijkste lesje: **goede data science vertelt je vooral wat je *niet* weet**, niet alleen wat je hoopte te bewijzen.

---

**Code en data:** https://github.com/QuintenFritz/truthsocial-marketimpact
