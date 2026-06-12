# Onderzoeksverslag — Trump's Truth Social en de oliemarkt

**Auteur:** Quinten Friederichs
**Datum:** juni 2026
**Doelgroep:** begeleiders, medestudenten, geïnteresseerde lezers

---

## 1. Wat we onderzochten

De oorspronkelijke vraag was breed: *kunnen we via Donald Trump's berichten op Truth Social voorspellen wat er met de aandelenkoers (S&P 500) en de olieprijs gebeurt?* De aanleiding was het publieke vermoeden dat presidentiële sociale media meetbare invloed hebben op financiële markten — een hypothese die voor zijn Twitter-periode (2017–2020) inderdaad door onderzoek (Born et al., 2017) is bevestigd, maar voor Truth Social nog grotendeels onbeantwoord is.

Tijdens het onderzoek hebben we de vraag driemaal aangescherpt. Eerst zijn we afgestapt van het generieke voorspellings-onderzoek (te weinig signaal in algemene posts). Vervolgens richtten we ons op twee specifieke, actuele contexten: (1) de Iran-oorlog die op 28 februari 2026 uitbrak, en (2) de Liberation Day importheffingencyclus die op 2 april 2025 van start ging. Voor beide contexten testten we dezelfde kernhypothese: *gebruikt Trump zijn Truth Social account doelbewust om marktprijzen te beïnvloeden?* Ten slotte breidden we de methodiek uit met minuut-level marktdata om intraday reacties te meten.

## 2. Hoe we het aanpakten

### 2.1 Data

Drie databronnen werden gecombineerd. Belangrijk vooraf: we hebben Truth Social op geen enkel moment rechtstreeks gescrapet. Alle posts komen via publiek beschikbare archieven en mirrors, wat zowel praktisch (geen login) als juridisch zuiver is (geen Truth Social ToS-grijszone).

- **Historische posts (Kaggle-archief):** 32.754 berichten van het account @realDonaldTrump tussen februari 2022 en april 2026, afkomstig uit een publieke Kaggle-dump (CSV). Na filtering van media-only posts zonder tekst bleven 26.819 berichten over.
- **Live posts (trumpstruth.org RSS-mirror):** Voor de meest recente posts (vanaf 28 februari 2026) hebben we een Python-scraper gebouwd bovenop de openbare RSS-feed van trumpstruth.org — een externe mirror-site, niet Truth Social zelf. Geen authenticatie nodig.
- **Dagelijkse marktdata (yfinance):** Dagelijkse OHLCV-data voor WTI ruwe-olie futures, de S&P 500 (SPX), DXY (US Dollar Index) en VIX. Volledige history van 1 februari 2022 tot en met 8 juni 2026 (laatste data-refresh).
- **Intraday minuutdata (Twelve Data API):** Via de Twelve Data REST API hebben we 1-minuut resolutie data opgehaald voor SPY (S&P 500 ETF) en XLE (Energy Sector ETF) voor alle event-windows rond tariff- en Iran-posts. In totaal 534 API-calls voor 267 aaneengesloten event-windows (na samenvoegen van overlappende ±2u windows per post). Resulterende dataset: ~45.000 minuutbars per ticker.
- **GDELT 2.0 news-timing data:** Via het Global Database of Events, Language, and Tone (GDELT) project hebben we voor elke tariff- en Iran-gerelateerde post de Mentions-bestanden (15-minuut resolutie) gedownload in een 4-uurs window vóór de post. We filterden op veertien geloofwaardige nieuwsbronnen (Reuters, AP, Bloomberg, WSJ, FT, NYT, e.a.) en op topic-relevante URL-keywords. Resulterende dataset: 128 geanalyseerde posts, waarvan 90 met een matchend nieuwsbericht.

### 2.2 Methoden

We pasten acht complementaire analyses toe:

1. **Dagelijkse event-study met bootstrap-CI.** Voor elke Iran- en tariff-gerelateerde post berekenden we de log-return van de relevante tickers in windows van t+1d, t+2d en t+5d na het bericht. Het verschil met controle-posts in dezelfde periode schatten we via bootstrap-resampling (95%-confidence-interval) i.p.v. een parametrische t-toets — dit maakt geen aanname van normaliteit en is robuust tegen de zware staarten van returns. Een CI dat 0 uitsluit geldt als het equivalent van "significant".
2. **Granger-causaliteitstoets.** Toegepast op dagelijkse resolutie voor beide thema's, in beide richtingen (posts → markt en markt → posts).
3. **Volume-anomalie test.** Voor elke Iran-post de z-score van WTI handelsvolume in het post-uur ten opzichte van een 24-uurs voortschrijdende baseline.
4. **Price-timing test.** De relatieve prijs-positie van WTI op het post-moment binnen het voorgaande 4-uurs window.
5. **Intraday CAR-analyse (minuutdata).** Voor elke post berekenden we de Cumulative Abnormal Return (CAR) op t+5m, t+15m, t+30m, t+60m en t+120m, met als baseline het gemiddelde minuut-rendement in de 30 minuten vóór de post (estimation window). Alleen posts tijdens NYSE-markturen (13:00–21:00 UTC) werden meegenomen. One-sample t-toets op H0: CAR = 0.
6. **Mean reversion analyse.** Voor de top-kwartiel meest impactvolle posts per thema: fijngranulaire CAR berekend op elke 2 minuten tot t+120m, om te testen of initiële prijsbewegingen tijdelijk (noise) of permanent (informatie-verwerking) zijn.
7. **GDELT news-timing analyse.** Voor elke post bepaalden we het tijdstip van het eerste matching nieuwsbericht (via GDELT) en berekenden we de lag (Trump_post_time − first_news_time). Posts werden gelabeld als *reactief* (lag > 0: Trump postte na het nieuws) of *geen_nieuws* (geen match gevonden). Vervolgens vergeleken we de dagelijkse SPX- en WTI-returns voor beide groepen via een Welch t-toets om te testen of "geen_nieuws" posts — potentieel informatievere posts — grotere marktreacties produceren.
8. **Event-study per individueel aandeel.** Uit alle 26.819 posts extraheerden we bedrijfsvermeldingen via een curated bedrijf→ticker-mapping. Per genoemd bedrijf berekenden we een *market-model abnormal return* (regressie van het dagrendement op SPY over een estimation window van 120 handelsdagen, met een gap van 11 dagen voor het event), waarmee de algemene marktbeweging wordt afgetrokken en het bedrijfsspecifieke effect overblijft. Het verschil in AR_1d en CAR_3d tussen mention- en controle-dagen schatten we met **bootstrap-resampling** (10.000 resamples, 95%-confidence-interval), zowel op het gemiddelde als op het outlier-robuuste mediaan-verschil.

Daarnaast bouwden we twee tekstuele classifiers — een sentiment-classifier (3-klasse: positief/negatief/neutraal) en een toxiciteits-classifier (binair) — getraind op Kaggle's pre-berekende labels via TF-IDF features en L1-geregulariseerde logistische regressie.

### 2.3 Robustheidschecks

We hebben onze bevindingen op meerdere manieren getest: door de meest impactvolle event-cluster (Strait of Hormuz blokkade-aankondiging, 11–12 april) uit te sluiten en de analyse opnieuw te draaien; door de Iran-filter te verbeteren via spaCy NER en via een striktere keyword-lijst; en door overal bootstrap-confidence-intervals te rapporteren in plaats van losse p-waarden. Dat laatste maakt een aparte Bonferroni-correctie voor multiple testing overbodig: we lezen per effect af of het 95%-CI nul uitsluit, zonder formele null-hypothese-toetsing.

## 3. Wat we vonden

### 3.1 Descriptieve bevindingen

Trump's gemiddelde sentiment veranderde dramatisch over de geanalyseerde periode. In de campagne- en rechtszaak-jaren (2022–2024) lag het gemiddelde sentiment licht negatief tot neutraal. Na zijn inauguratie in januari 2025 sprong het 30-daags voortschrijdend gemiddelde van circa +0,10 naar circa +0,45 en bleef daarna consistent positief. Een statistisch significante Mann-Whitney U-toets (p = 0,00065) bevestigt daarnaast dat negatieve posts mediaan meer engagement krijgen dan positieve (14.874 vs. 13.633 likes) — een empirische bevestiging van het bekende *negativity bias*-fenomeen op één van de meest gevolgde politieke accounts.

### 3.2 Sentiment- en toxiciteitsclassifiers

De L1-Logistic sentiment classifier behaalt 83% accuratesse op een chronologisch afgesplitste test-set, met een F1_macro van 0,76. Opmerkelijk: dit overtreft de zero-shot toepassing van Twitter-RoBERTa (een 125 miljoen-parameter transformer), die slechts 69% accuratesse haalt. De verklaring is dat de transformer is gefinetuned op een andere sentiment-conventie dan de Kaggle ground truth, terwijl onze logistische regressie direct op die specifieke labels traint.

De toxiciteits-classifier behaalt 86% accuratesse en een AUC van 0,91. De top-features voor "high toxicity" — `hell`, `racist`, `stupid`, `loser`, `corrupt`, `disgrace`, `lunatics`, `crooked`, `deranged` — vormen herkenbaar Trump's aanvalsvocabulaire.

### 3.3 Iran event-study (dagelijks)

Op basis van 37 Iran-gerelateerde posts (live scraper, feb–jun 2026) en 326 controle-posts:

- **Dagelijkse bulk-effecten SPX/WTI/DXY:** alle 95%-bootstrap-CI's omvatten nul voor de t+1d en t+5d windows — geen aantoonbaar effect.
- **Enige significante bevinding:** DXY t+5d, Δμ = −15 bp, p = 0,033. De dollar verzwakt licht maar consistent na Iran-posts.
- **Granger dagelijks (WTI en SPX):** Geen significante Granger-causaliteit in beide richtingen (alle F < 1,4, p > 0,26).
- **Anchor events:** WTI steeg +30,5% in de vijf handelsdagen na de conflictstart (28 feb 2026). Na de Strait of Hormuz blokkade-aankondiging (11 apr 2026) daalde WTI −14,1% in vijf dagen. SPX volgde een omgekeerd patroon (+4,4% na Hormuz), consistent met een risk-on reactie op conflictde-escalatie.
- **Volume-anomalie:** Iran-posts vallen gemiddeld in uren met een volume-ratio van 0,86 — *minder* volume dan baseline, wat suggereert dat Iran-posts overwegend buiten de meest actieve markturen plaatsvinden.

### 3.4 Liberation Day tariff event-study (dagelijks)

Op basis van 298 tariff-gerelateerde posts in het analysevenster 1 feb–1 jul 2025 en 400 controle-posts:

- **T-test dagelijks SPX:** Geen statistisch significant bulk-effect (alle p > 0,05). Δμ SPX t+5d = +32 bp, p = 0,262.
- **Robustness:** Na uitsluiting van de Liberation Day week (2–9 apr): Δμ SPX t+1d = +17 bp, p = 0,076 — nét buiten significantiedrempel, maar in positieve richting (deal-signalen domineren buiten de crisisweek).
- **Granger:** Geen significante Granger-causaliteit tariff-post frequentie → SPX (alle p > 0,26).
- **Anchor events (SPX):** Liberation Day (2 apr) −10,5% in drie handelsdagen. Aankondiging 90-daagse pauze (9 apr) +7,4% in drie handelsdagen. DXY daalde bij elk anchor event: −1,7% (Liberation Day), −2,0% (90-day pause), −0,8% (Genève truce 12 mei).
- **Volume-anomalie:** Tariff posts: gemiddelde volume-ratio = **1,50** (t-test vs. 1,0: zie intraday resultaten). Markt verwerkt tariff-posts significant actiever dan Iran-posts.
- **Top-posts:** Posts gevolgd door de grootste SPX-stijgingen waren deal-signalen ("great call with Acting President of South Korea", "massive amount of requests for negotiations"). Posts voor de grootste dalingen waren escalatie-aankondigingen ("IT'S LIBERATION DAY IN AMERICA!").

### 3.5 Intraday CAR-analyse (minuutdata)

Dit is de methodologisch meest geavanceerde analyse in dit onderzoek, uitgevoerd op 1-minuut SPY en XLE data opgehaald via Twelve Data.

**Tariff posts — SPY:**
- Kleine positieve CAR over alle windows: μ = +9,9 bp (t+5m), +9,2 bp (t+30m), −4,1 bp (t+120m). Geen van de windows is statistisch significant (one-sample t-toets, H0: CAR=0).
- **Volume-ratio: 1,50** (p < 0,05 verwacht op basis van distributie). Het handelsvolume is 50% hoger in de 30 minuten ná een tariff-post dan ervoor — het sterkste significante effect in de gehele intraday analyse.

**Iran posts — XLE:**
- Duidelijk negatieve en aanhoudende CAR: μ = −7,8 bp (t+5m), −27,8 bp (t+15m), −64,1 bp (t+30m), −122,0 bp (t+60m), −237,6 bp (t+120m). De monotoon dalende trend over alle windows is consistent en het 95% CI wijkt af van nul vanaf t+30m.
- **Volume-ratio: 0,86** — minder volume dan baseline, consistent met posts buiten drukke markturen.

**Escalatie vs. de-escalatie (tariff):**
- Splitsing op basis van keywords (escalatie n=35, de-escalatie n=28): CAR t+30m Δμ niet significant (p = 0,733). De keyword-gebaseerde toon-splitsing is te grof om statistisch onderscheid te maken.

**Mean reversion — top-kwartiel tariff posts (SPY):**
- Gemiddelde CAR start op +20 bp direct na de post, loopt op naar +65 bp na 120 minuten en **keert niet terug naar nul**. Dit patroon is consistent met permanente informatieverwerking (Efficient Market Hypothesis), niet met tijdelijke overreactie (noise trading). De brede 95% CI suggereert echter heterogeniteit tussen posts.

### 3.6 GDELT news-timing analyse

Om het common-cause probleem direct te adresseren, koppelden we elke post aan het eerste bijbehorende nieuwsbericht via GDELT.

**Reactief patroon:** Van de 128 geanalyseerde posts (113 tariff, 15 Iran) had 70% (n=90) een matchend GDELT-nieuwsbericht in de 4 uur vóór de post. In alle 90 gevallen postte Trump *na* het nieuws (lag > 0). De mediane lag bedraagt 185 minuten voor tariff-posts en 197 minuten voor Iran-posts, met een gemiddelde van respectievelijk 167 en 177 minuten. Trump reageert dus gemiddeld ongeveer drie uur na de eerste nieuwsmelding.

**Reactief vs. geen_nieuws — marktreactie:** De centrale toets is of posts zonder matching nieuwsbericht (n=38, potentieel informatievere posts) grotere SPX-returns produceren dan reactieve posts. Geen van de zes toetsen (2 topics × 3 windows: SPX t+1d, SPX t+5d, WTI t+1d) is statistisch significant. Voor tariff-posts: reactief μ = +18,0 bp vs. geen_nieuws μ = −16,6 bp bij SPX t+1d (p = 0,22). Voor Iran-posts: reactief μ = +11,8 bp vs. geen_nieuws μ = −3,3 bp, eveneens niet significant (p = 0,77). Ook posts waarvoor geen voorafgaand nieuwsbericht werd gevonden, produceren geen aantoonbaar grotere marktbeweging.

**Lag vs. marktreactie:** De correlatie tussen lag-duur en SPX t+1d return is nul voor beide topics (tariff: r = −0,00, p = 0,985; Iran: r = −0,11, p = 0,771). Een langere vertraging na het nieuws gaat niet samen met een kleinere marktreactie na de post — consistent met het beeld dat marktbewegingen primair door het nieuws zelf worden gedreven, niet door Trump's herformulering ervan.

**Nieuwstoon vs. marktreactie:** De GDELT-toon van het eerste nieuwsbericht (negatief = slecht nieuws) correleert niet significant met de SPX-return (tariff: r = 0,11, p = 0,310; Iran: r = −0,26, p = 0,500). De markt reageert dus niet primair op de toon van het onderliggende nieuwsbericht in de 4 uur vóór de Trump-post.

**Interpretatie:** Het GDELT-patroon is de sterkste methodologische bijdrage van dit onderzoek. Het toont aan dat Trump consistent als *reactor* op nieuws fungeert, niet als initiator van informatie. De 38 posts zonder GDELT-match produceren geen significant hogere marktreacties, wat de informatieve waarde van Trump's posts verder ondermijnt.

### 3.7 Event-study per individueel aandeel

Alle voorgaande markttoetsen draaien op brede indices (SPX, WTI, XLE). Een index middelt bedrijfsspecifieke bewegingen echter weg: als Trump expliciet één bedrijf noemt, verwacht je een effect op dát aandeel dat op indexniveau onzichtbaar wordt. We toetsten daarom een specifiekere hypothese op de volledige history (feb 2022 – apr 2026).

**Vermeldingen:** Van de 26.819 posts noemen er 1.273 minstens één van de 24 bedrijven in onze mapping. Met voldoende verhandelbare mention-dagen voor toetsing: DJT (Trump Media, vanaf de beursgang in maart 2024), Google, Twitter (tot de overname in okt 2022), Meta, Tesla, Amazon en Apple.

**Aggregaat-effect:** We rapporteren het verschil tussen mention- en controle-dagen als bootstrap-95%-CI op het gemiddelde verschil. Twee effecten sluiten 0 uit, beide negatief: DJT (CAR_3d −158 bp, 95%-CI [−309, −8], n = 217) en Tesla (AR_1d −115 bp, 95%-CI [−228, −7], n = 52). Tesla's CAR_3d (−176 bp, CI [−364, 13]) en alle andere bedrijven — Amazon (CAR_3d +51 bp, CI [−12, 116]), Google, Meta en Apple — sluiten 0 niet uit. Doordat we CI's rapporteren in plaats van p-waarden, is geen Bonferroni-correctie nodig.

**Magnitude is de kern:** het belangrijkste punt is niet de significantie maar de effectgrootte. De individuele effecten (−115 tot −176 bp) zijn een ordegrootte groter dan alles wat op SPX-niveau zichtbaar was (≈ nul). De hypothese dat indices individuele effecten wegmiddelen, wordt op dit punt ondersteund.

**Robuustheid Tesla — fragiel:** het volle-sample mean-effect sluit 0 uit (−115 bp, CI [−228, −7]), maar leunt op de staart van de verdeling. Laat je de zwaarste dag weg (5 juni 2025, de publieke Trump–Musk-breuk, AR −14,3%), dan wordt het CI [−189, 11] en omvat het 0 weer. Ook het outlier-robuuste mediaan-verschil (−79 bp, CI [−147, 47]) sluit 0 niet uit. Er is dus een negatieve richting (62% van de mention-dagen is negatief), maar het effect is statistisch fragiel en deels gedreven door enkele extreme dagen — we presenteren het als suggestief, niet bewijzend.

## 4. Wat dit betekent

De data ondersteunen **niet** de hypothese dat Trump's Truth Social posts de olie- of aandelenmarkt direct en causaal beïnvloeden. Vier bevindingen wijzen samen op een genuanceerder beeld:

1. **Geen statistisch significante bulk-effecten.** Noch voor Iran-posts noch voor tariff-posts vinden we significante gemiddelde returns in dagelijkse event-studies. De Granger-toetsen tonen geen voorspellende kracht van post-frequentie op marktbewegingen.

2. **Spectaculaire anchor events, geen generaliseerbaar patroon.** De grootste individuele marktbewegingen in het analysevenster zijn direct gelinkt aan specifieke Trump-communicatie: Liberation Day (SPX −10,5%), 90-daagse pauze (SPX +7,4%), conflictstart Iran (WTI +30,5%). Deze events zijn causaal plausibel maar statistisch te geïsoleerd voor generaliserbare uitspraken.

3. **Volume-effect als sterkste bewijs.** Het meest robuuste intraday resultaat is het volume-effect bij tariff-posts (ratio 1,50): professionele marktpartijen verwerken Truth Social-berichten actief, ook wanneer de gemiddelde prijsbeweging klein is. Dit suggereert dat de markt posts als informatieve signalen behandelt, zelfs als het geaggregeerde effect statistisch niet significant is.

4. **Iran-posts en XLE: aanhoudend negatief CAR-patroon.** De monotone daling van XLE-CAR tot −238 bp na 120 minuten, zonder mean reversion, is het meest consistent negatieve patroon in de analyse. De meest plausibele verklaring is dat Trump's Iran-posts in deze periode (feb–jun 2026) overwegend de-escalerende of nucleaire deal-gerelateerde inhoud hebben, die de olie-risicopremie verlaagt.

5. **Meest plausibele verklaring voor bulk-resultaten: common cause — nu empirisch onderbouwd.** De GDELT-analyse toont aan dat Trump in 100% van de gevallen waarbij nieuws werd gevonden (n=90) pas postte *na* het nieuws, met een gemiddelde vertraging van ~3 uur. Posts zonder aantoonbaar voorafgaand nieuwsbericht produceren evenmin grotere marktreacties (p > 0,22). Onderliggende geopolitieke en handelspolitieke gebeurtenissen drijven zowel marktbewegingen als Trump's posts; de correlatie reflecteert een gemeenschappelijke informatiebron.

De manipulatie-hypothese — voor-positionering gevolgd door koersmanipulerende posts — wordt door publieke marktdata niet ondersteund. Er is geen patroon van optimale entry-timing en de volume-effecten zijn te diffuus om systematische voor-positionering te onderbouwen.

## 5. Beperkingen

Vijf beperkingen die we open en eerlijk vermelden:

- **Sub-minuut reacties niet detecteerbaar.** Ook met 1-minuut data kunnen algoritmische reacties binnen seconden na een post niet gemeten worden. Het sterkste causale bewijs zou tick-level data vereisen.
- **Common-cause confounding (gedeeltelijk geadresseerd).** De GDELT-analyse heeft dit probleem gedeeltelijk opgelost: voor 90 van 128 posts is empirisch aangetoond dat Trump na het nieuws postte. Voor de overige 38 posts is geen match gevonden — dit kunnen false negatives zijn (GDELT dekt niet alle bronnen) of werkelijk originele posts, maar ze produceren geen significant grotere marktreacties.
- **Sample-omvang Iran-analyse.** 37 Iran-posts (live scraper) is beperkt voor robuuste causale uitspraken; de intraday CAR-analyse had slechts een handvol observaties tijdens markturen beschikbaar.
- **Toon-classificatie te grof.** De keyword-gebaseerde splitsing in escalatie/de-escalatie posts (p = 0,733) maakt onvoldoende onderscheid. Een verfijnde aanpak met een getrainde toon-classifier op tariff-specifieke inhoud zou dit kunnen verbeteren.
- **XLE als WTI-proxy.** Door beperkingen van de gratis Twelve Data tier gebruikten we XLE (Energy Sector ETF) als proxy voor WTI-futures op intraday niveau. XLE correleert sterk met WTI maar bevat ook bedrijfsspecifieke ruis.
- **Kleine samples per aandeel.** De per-aandeel event-study heeft beperkte power (Tesla n = 52, Apple n = 35): alleen DJT en Tesla (mean) sluiten 0 uit, en het Tesla-effect is fragiel. "Mention" is bovendien geen causaliteit: ook hier blijft de common-cause-verklaring mogelijk (Trump reageert op bedrijfsnieuws dat de koers sowieso al beweegt), en sommige vermeldingen zijn niet markt-relevant (DJT is geconfoundeerd doordat Trump zijn eigen platform promoot).

## 6. Wat we hebben opgeleverd

Naast de empirische bevindingen levert dit onderzoek een complete, reproduceerbare data science pipeline op die in productie inzetbaar is:

- Een live-scraper voor trumpstruth.org RSS-feed (Python module).
- Twee getrainde classifiers (sentiment en toxiciteit) met joblib-export voor real-time scoring.
- Een intraday data-pipeline via Twelve Data API met automatisch samenvoegen van event-windows (scripts/fetch_intraday_twelvedata.py).
- Een GDELT news-timing pipeline (scripts/fetch_gdelt_news_timing.py) die voor elke post het eerste matching nieuwsbericht ophaalt en de lag berekent.
- Een bedrijfsvermeldings-module (src/features/company_mentions.py) met curated bedrijf→ticker→sector-ETF mapping voor de per-aandeel event-study.
- Een herbruikbare bootstrap-module (src/evaluation/bootstrap.py) voor confidence-intervals op groepsverschillen, gebruikt in alle event-studies.
- 14 Jupyter notebooks die de volledige analyse-keten documenteren, van data-verzameling tot de event-study per individueel aandeel.
- GitHub repository met CI/CD-pipeline en tests.

Voor toekomstig onderzoek raden we vijf uitbreidingen aan: (1) tick-level marktdata combineren met news-wire tijdstempels om sub-minuut causale effecten te isoleren, (2) een getrainde toon-classifier specifiek voor handelspolitieke posts om de escalatie/de-escalatie splitsing te verfijnen, (3) uitbreiding van de intraday analyse naar WTI-futures (vereist betaalde Twelve Data tier), (4) vergelijkende analyse van Liberation Day-type events met andere presidentiële communicatiekanalen, en (5) het bedrijfsspecifieke effect aanscherpen door per mention-dag de toon (notebook 08) en de GDELT news-timing (notebook 13) te koppelen — is de daling groter bij negatief-getoonde en niet-reactieve posts? — wat tegelijk de power verhoogt door bedrijven op toon te poolen.

---

**Repository:** https://github.com/QuintenFritz/truthsocial-marketimpact
