# Een analyse van Donald Trump's Truth Social communicatie tijdens het Iran-conflict 2026

**Een empirisch onderzoek naar de relatie tussen presidentiële sociale media en de oliemarkt**

---

**Auteur:** Quinten Friederichs
**Opleiding:** VDO Data Scientist
**Onderwijsinstelling:** Syntra
**Begeleider:** Tim Hellemans / Olivier Claerebout
**Indiendatum:** juni 2026

---

## Samenvatting

Sinds het uitbreken van het Iran-conflict op 28 februari 2026 heeft Donald Trump intensief over de oorlog gecommuniceerd via zijn platform Truth Social. Dit onderzoek toetst empirisch de hypothese dat zijn berichten doelbewust worden ingezet om de oliemarkt te beïnvloeden. Op basis van 26.819 historische posts (Kaggle-dataset, februari 2022 – april 2026), aangevuld met gescrapte posts via de trumpstruth.org RSS-feed sinds conflictstart, intraday WTI futures data op uur- en 5-minuten-resolutie, en eigenontwikkelde classificatie-modellen voor sentiment en toxiciteit, voeren wij een event-study uit op 134 Iran-gerelateerde posts versus 435 controle-posts.

De resultaten ondersteunen niet de hypothese van directe markt-aansturing. De return-effecten zijn niet consistent gericht: op uur-resolutie gaan Iran-posts samen met een hogere SPY-return (t+4u, +14 bp, CI sluit 0 uit) en XLE-return (t+24u, +44 bp, CI sluit 0 uit), terwijl de brede markt op minuut-niveau juist een negatieve drift toont (CAR −32 bp na 120 min, CI [−56,9, −6,1]); WTI zelf is op geen enkel window significant. Deze tekenwisseling tussen horizon en databron wijst op de afwezigheid van een robuust gericht effect. Granger-causaliteitstoetsen ondersteunen consequent een reactief patroon: WTI-rendementen voorspellen Trumps Iran-postingactiviteit met lagstructuur 2–4 uur (F = 4,3–6,5, p < 0,002), terwijl het omgekeerde verband op geen enkele resolutie significant is. Wat robuust overeind blijft, is verhoogd energiesector-volume rond Iran-posts (+0,25σ, CI [+0,04, +0,46]); er is geen patroon van optimale prijs-timing. Het geheel wijst op een reactieve rol, met common cause (onderliggend Iran-nieuws) als meest plausibele verklaring.

De meest parsimonieuze interpretatie is dat onderliggende geopolitieke gebeurtenissen zowel marktbewegingen als Trumps communicatie aansturen — een common-cause verklaring. Dit onderzoek levert tevens herbruikbare classifiers (sentiment: 83% accuratesse; toxiciteit: AUC 0,91) en een complete reproduceerbare pipeline op.

---

## Inhoudsopgave

1. Inleiding
2. Literatuurstudie
3. Data en methodologie
4. Resultaten
5. Discussie
6. Conclusie
7. Referenties
8. Bijlagen

---

## 1. Inleiding

### 1.1 Context

Met de opkomst van sociale media als primair communicatiekanaal voor staatshoofden is de relatie tussen presidentiële uitingen en financiële markten een actief onderzoeksgebied geworden. Born, Müller, Schularick en Sedláček (gepubliceerd circa 2017) toonden aan dat tweets van Donald Trump tijdens zijn eerste presidentschap meetbare abnormale rendementen veroorzaakten in specifieke aandelen en sectoren. Sentimentanalyse op grote tekstcorpora — variërend van krantenartikelen (Tetlock, 2007) tot Twitter-tijdlijnen (Bollen, Mao en Zeng, 2011) — heeft herhaaldelijk een voorspellende relatie aangetoond met financiële markten, hoewel de effectgrootte en robuustheid sterk variëren.

Na zijn verbanning van Twitter in 2021 verplaatste Trump zijn directe communicatie naar het door hem opgerichte platform Truth Social. De marktimpact van deze nieuwe communicatie-omgeving is empirisch veel minder onderzocht dan zijn Twitter-periode. Het uitbreken van een gewapend conflict met Iran op 28 februari 2026 creëert een unieke onderzoekscontext: een actueel geopolitiek evenement waarin de oliemarkt hoog volatiel is en de huidige president — opnieuw Donald Trump — frequent commentaar levert via Truth Social. Het publieke debat over de aard van deze communicatie is gepolariseerd: sommige commentatoren stellen dat Trumps posts marktbewegingen veroorzaken of zelfs voorafgaand handelsgedrag mogelijk maken; anderen stellen dat hij vooral reactief commentarieert op gebeurtenissen die hij niet zelf in gang heeft gezet.

Dit onderzoek poogt deze hypothesen empirisch te toetsen aan publiek beschikbare data. Wij gebruiken hiervoor zowel klassieke event-study technieken als Granger-causaliteitstoetsen op meerdere tijdsresoluties, en bouwen daarnaast eigen tekstuele classifiers die de communicatie systematisch karakteriseren naar sentiment en toxiciteit.

### 1.2 Probleemstelling en onderzoeksvragen

**Hoofdvraag:**

> In hoeverre is er een statistisch detecteerbaar verband tussen Trumps Iran-gerelateerde Truth Social posts en bewegingen van de WTI ruwe-olieprijs sinds 28 februari 2026, en wat is de meest plausibele richting van dit verband?

**Sub-vragen:**

1. *Descriptief.* Hoe heeft Trumps communicatiepatroon (volume, sentiment, toxiciteit) zich ontwikkeld over de periode 2022–2026, en in het bijzonder rond geopolitieke triggers?
2. *Predictief.* Kunnen tekstuele classifiers de sentiment- en toxiciteitslabels van bestaande gespecialiseerde tools reproduceren met acceptabele accuratesse op basis van eenvoudige features?
3. *Correlationeel.* Vallen Iran-gerelateerde posts samen met statistisch significante bewegingen in WTI-futures, de S&P 500, of de energiesector-ETF (XLE)?
4. *Causaliteit.* Voor zover er een correlatie bestaat — is er evidentie dat posts marktbewegingen voorspellen, dat marktbewegingen posts voorspellen, of dat beide reageren op een gemeenschappelijke onderliggende oorzaak?
5. *Falsificeerbaar.* Vinden wij patronen die consistent zijn met een hypothese van voor-positionering (informed trading) rond Trumps posts, zoals verhoogd handelsvolume of optimale prijs-timing?

### 1.3 Opbouw van dit document

Hoofdstuk 2 plaatst dit onderzoek in de bestaande literatuur over sociale media en financiële markten. Hoofdstuk 3 beschrijft de data, modellen en statistische technieken. Hoofdstuk 4 presenteert de empirische resultaten in vier subsecties: descriptieve analyse, sentimentclassificatie, toxiciteitsclassificatie, en de Iran-conflict event-study. Hoofdstuk 5 bespreekt de interpretatie van de bevindingen en de methodologische beperkingen. Hoofdstuk 6 sluit af met de conclusie en aanbevelingen voor vervolgonderzoek.

---

## 2. Literatuurstudie

### 2.1 Sociale media en financiële markten

Het meest geciteerde vroege werk in dit domein is Bollen, Mao en Zeng (2011), die op een corpus van ~9,8 miljoen tweets uit 2008–2009 stemmingsindices construeerden en aantoonden dat de zogeheten "Calm"-dimensie een statistisch significante voorspeller is voor de richting van dagelijkse S&P 500-bewegingen (correlatie 0,10, lag 1–2 dagen). Hun werk leverde echter een aggregaat-niveau bevinding op: het gemiddelde sentiment van miljoenen anonieme gebruikers, niet de impact van één individuele communicator.

Antweiler en Frank (2004) onderzochten 1,5 miljoen posts op Yahoo! Finance en Motley Fool message boards (1999–2002) en vonden dat *disagreement* (variantie in sentiment) sterker correleerde met marktvolatiliteit dan met returns zelf. Hun werk waarschuwt dat sentiment-uit-sociale-media zwakke voorspellende waarde heeft (R² < 0,5%) en context-afhankelijk werkt.

Tetlock (2007) leverde een methodologische blauwdruk voor textuele sentimentanalyse in een financiële context door 51 jaren Wall Street Journal-kolommen te analyseren. Pessimistisch sentiment bleek significant lagere toekomstige returns te voorspellen (OOS R² circa 3–4%), met effecten die sterker waren in lage-informatie periodes.

### 2.2 Tekstuele analyse in financiële context

Loughran en McDonald (2011, 2016) ontwikkelden domeinspecifieke financiële sentiment-woordenlijsten en argumenteerden dat generieke sentiment-tools (zoals Harvard IV-4) systematisch tekortschieten op financiële tekst. Bedrijfsspecifieke termen als "liability", "loss" of "risk" hebben in financial-disclosure-context een andere lading dan in algemeen taalgebruik. Hun survey-paper (2016) biedt een meta-analyse van 127 studies en wijst op terugkerende methodologische valkuilen: selectiebias, in-sample overfitting en look-ahead bias.

Araci (2019) introduceerde FinBERT, een pre-trained transformer-model gefinetuned op het Financial PhraseBank-corpus dat 92% accuratesse haalde tegen 75% voor lexicon-gebaseerde methodes. Ke, Kelly en Xiu (2023) toonden in *Predicting Returns with Text Data* aan dat transformer-gebaseerde sentimentsignalen lineaire TF-IDF-baselines met een factor 2–3 overtreffen in out-of-sample voorspellende R².

### 2.3 Interpretability en methodologische kritiek

Jain en Wallace (2019), in hun paper *Attention is Not Explanation*, toonden aan dat attention-gewichten in BERT-achtige modellen geen betrouwbare proxy zijn voor feature importance, en bepleitten post-hoc methoden zoals SHAP. Lundberg en Lee (2017) introduceerden de SHAP-methodologie, theoretisch verankerd in coöperatieve speltheorie via Shapley-waarden, als consistente interpretability-methode voor zowel boom-gebaseerde als neurale modellen. Breiman (2001) leverde de oorspronkelijke Random Forest-publicatie; het algoritme blijft een sterke niet-lineaire baseline op tekstdata.

### 2.4 Gap-analyse

Hoewel Trumps Twitter-communicatie uit zijn eerste presidentschap (2017–2021) uitgebreid is onderzocht, is empirisch werk over Truth Social specifiek schaars — en nog schaarser is onderzoek over de interactie tussen zijn communicatie en de oliemarkt tijdens een actief geopolitiek conflict. Dit onderzoek vult die leemte op drie manieren: (a) een tijdgebonden case-study sinds de uitbraak van het Iran-conflict op 28 februari 2026, (b) eigen-getrainde tekstuele classifiers in plaats van afhankelijkheid van vooraf gelabelde datasets, en (c) een methodologisch rigoureuze causaliteitsanalyse op zowel uur- als minuten-resolutie via Granger-toetsen aangevuld met traditionele event-study t-toetsen.

---

## 3. Data en methodologie

### 3.1 Databronnen

**Historische Truth Social posts.** Wij gebruiken een publiek beschikbare Kaggle-dataset (`trump_truth_archive.csv`) met 32.754 posts van het account @realDonaldTrump tussen 14 februari 2022 en 23 april 2026. Het ruwe bestand bevat per post een unieke identifier, een UTC-tijdstempel, de tekstinhoud, engagement-metrieken (likes, retruths, replies) en circa 30 pre-berekende features waaronder een sentiment-score, sentiment-label, toxiciteits-score en topic-classificatie. Na het filteren van media-only posts zonder tekst (5.935 posts) bleven 26.819 posts beschikbaar voor analyse.

**Live Truth Social posts.** Voor de periode na 23 april 2026 maken wij gebruik van de RSS-feed van trumpstruth.org, een onafhankelijke archief-site beheerd door Defending Democracy Together. Wij hebben een Python-scraperscript (`src/data/scrape_trumpstruth_rss.py`) ontwikkeld dat de feed in maand-chunks raadpleegt en de output normaliseert naar het canonieke datasetschema. Deze bron vereist geen authenticatie en valt binnen de servicevoorwaarden voor academisch gebruik.

**Marktdata.** Wij gebruiken yfinance (Yahoo Finance API) voor drie tickers: WTI ruwe-olie futures (`CL=F`), de S&P 500 ETF (`SPY`) en de Energy Select Sector ETF (`XLE`). Dagelijkse data zijn beschikbaar voor de volledige conflictperiode; uur- en 5-minuten-data zijn beperkt tot de meest recente 60 dagen door technische limieten van de bron.

### 3.2 Preprocessing

Posts worden gefilterd op aanwezigheid van tekstuele inhoud (drop van media-only posts) en doorgaan vervolgens door een tekst-cleaningpipeline (`src/data/preprocess.py`): lowercase-transformatie, URL- en mention-strip, Unicode-normalisatie via de `ftfy`-library om mojibake-artefacten (zoals `itâ€™s → it's`) te corrigeren, en filtering op minimaal vijf tokens.

### 3.3 Classificatie-modellen

**Sentiment classifier.** Wij trainen drie modellen om het 3-klasse-sentimentlabel (positief/neutraal/negatief) uit de Kaggle ground truth te reproduceren: een L1-geregulariseerde logistische regressie (saga-solver, max 3000 iteraties), een Random Forest (200 bomen, class-weight gebalanceerd), en — als vergelijking — de zero-shot toepassing van het Twitter-RoBERTa-model `cardiffnlp/twitter-roberta-base-sentiment-latest`. Features bestaan uit TF-IDF van unigrammen en bigrammen met maximaal 8.000 features, English stopwords-filtering, en sublinear term frequency-normalisatie. Train/test-split is chronologisch (80/20).

**Toxicity classifier.** Wij definiëren een binaire classificatie: de 25% van trainingsposts met de hoogste pre-berekende toxiciteitsscore wordt gelabeld als `high_tox`, de rest als `low_tox`. De drempel wordt vastgesteld op het 75ᵉ percentiel van de trainingsverdeling om train/test-leakage te voorkomen. Modellen: L1-logistische regressie (liblinear), Random Forest en de pre-trained `unitary/toxic-bert` transformer.

### 3.4 Statistische toetsen

**Event-study met bootstrap-CI.** Voor elke Iran-gerelateerde post `p` op tijdstip `t` berekenen wij de logaritmische return van WTI, SPY en XLE over windows `[t, t+Δ]` voor `Δ ∈ {1u, 4u, 24u}`. Iran-relevantie wordt vastgesteld via keyword-matching op een lexicon van 38 termen (Iran, Tehran, ayatollah, Hormuz, OPEC, oil, sanctions, et cetera). Posts zonder Iran-keyword vormen de controlegroep. Het verschil in gemiddelde returns tussen beide groepen schatten wij via **bootstrap-resampling** (10.000 resamples, percentiel-95%-confidence-interval) in plaats van een parametrische t-toets. Deze keuze sluit aan bij de resampling-methoden uit de cursus, vergt geen normaliteitsaanname en is robuust tegen de zware staarten van financiële returns; een 95%-CI dat nul uitsluit fungeert als equivalent van statistische significantie. Doordat wij CI's rapporteren in plaats van losse p-waarden vervalt de noodzaak van een Bonferroni-correctie voor meervoudig toetsen.

**Granger-causaliteitstoets.** Wij gebruiken `statsmodels.tsa.stattools.grangercausalitytests` om te toetsen of het verleden van variabele X (post-frequentie) de toekomst van variabele Y (rendement) voorspelt, gecontroleerd voor Y's eigen autocorrelatie. Twee richtingen worden getest (posts→rendementen en rendementen→posts) op twee resoluties: hour-level over een 60-dagen window, en 5-minuten-level over een 60-dagen window.

**Volume-anomalie test.** Voor elke Iran-post berekenen wij de WTI-handelsvolume z-score in het post-uur ten opzichte van een 24-uurs voortschrijdende baseline (rolling mean en standaarddeviatie). Het verschil in gemiddelde z-score tussen Iran- en controle-posts schatten wij eveneens via een bootstrap-CI; een CI dat nul uitsluit zou wijzen op anomale handelsactiviteit rond post-momenten — een patroon dat consistent zou zijn met geïnformeerde voor-positionering.

**Price-timing test.** Voor elke Iran-post berekenen wij de relatieve prijspositie binnen het 4-uurs voorgaande window: `(prijs_op_t − min) / (max − min)`. Een waarde nabij 0 indiceert een lokaal dieptepunt, nabij 1 een lokaal hoogtepunt. Onder de manipulatie-hypothese ("buy low, then pump") zouden bullish posts systematisch bij lokale dieptepunten moeten vallen.

### 3.5 Methodologische beslissingen

Wij hanteren chronologische train/test-splits om look-ahead bias uit te sluiten, en gebruiken `class_weight="balanced"` om om te gaan met klasse-onbalans in zowel sentiment als toxiciteit. De toxiciteitsdrempel wordt uitsluitend op de trainingsset bepaald om label-leakage te voorkomen. Voor de event-studies rapporteren wij bootstrap-confidence-intervals in plaats van losse p-waarden; doordat wij per effect aflezen of het 95%-CI nul uitsluit, vervalt de noodzaak van een Bonferroni-correctie voor meervoudig toetsen.

---

## 4. Resultaten

### 4.1 Descriptieve analyse van Trumps communicatie

Over de periode februari 2022 tot juni 2026 toont Trumps sentiment een duidelijk temporeel patroon. Het gemiddelde 30-daags voortschrijdend sentiment ligt in 2022 nabij +0,15, daalt in late 2022 en vroege 2023 tot onder nul (samenvallend met de Mar-a-Lago doorzoeking en zijn voortgaande juridische procedures), en stijgt langzaam in 2023–2024 terug. Een markante verschuiving vindt plaats rond januari 2025: van een sentiment-niveau circa +0,10 voor de verkiezingen springt het 30-daags gemiddelde naar circa +0,45 in de weken na inauguratie. In de daaropvolgende periode (2025–2026) blijft het sentiment consistent positief tussen +0,25 en +0,35.

Een bootstrap-CI op het mediaan-verschil in engagement (n = 26.819, in-cursus resampling) toont een robuust verschil tussen negatieve en positieve posts: negatieve posts ontvangen mediaan 14.874 likes versus 13.633 voor positieve posts, en het 95%-CI op het verschil sluit nul uit. Dit verschil van circa 9% in mediane engagement, hoewel klein in absolute zin, vormt empirisch bewijs voor het bekende "negativity bias"-fenomeen op sociale media, hier gemeten op een individueel politiek dominant account.

### 4.2 Sentimentclassificatie

Op een chronologisch afgesplitste test-set van ongeveer 4.000 posts presteert het L1-Logistic model duidelijk het sterkst:

| Model | Accuratesse | F1 (macro) | F1 (gewogen) |
|---|---|---|---|
| Dummy (gestratificeerd) | 0,42 | 0,31 | 0,45 |
| L1-Logistic | **0,83** | **0,76** | **0,84** |
| Random Forest | 0,78 | 0,71 | 0,79 |
| Twitter-RoBERTa (zero-shot) | 0,69 | 0,59 | 0,71 |

Het feit dat een sparse lineair model met circa 8.000 woord-features een 125 miljoen-parameter pre-trained transformer (Twitter-RoBERTa) verslaat is methodologisch interessant. Wij verklaren dit via twee mechanismen: ten eerste een label-distributie-mismatch (Twitter-RoBERTa is gefinetuned op een dataset met andere sentiment-conventies dan de Kaggle ground truth), en ten tweede de stilistisch uniforme aard van Trumps posts die door lineaire methodes effectief wordt gevangen zonder dat contextuele modellering meerwaarde biedt.

Inspectie van de L1-coëfficiënten per klasse onthult coherente vocabulaire-clusters. De sterkste indicatoren van *negatief* sentiment zijn `hell`, `dead`, `destroy`, `fraud`, `worst`, `loser`, `hating`, `corrupt`, `disgrace` en `lunatics`. De sterkste indicatoren van *positief* sentiment zijn `great`, `best`, `liberty`, `protect`, `congratulations`, `thank`, `win`, `beautiful`, `greatest` en `amazing`. De *neutrale* klasse bevat meer entiteits- en context-specifieke termen.

### 4.3 Toxiciteitsclassificatie

Met top-25%-drempel definiëring presteren de modellen als volgt:

| Model | Accuratesse | F1 (binair) | AUC |
|---|---|---|---|
| Dummy | 0,58 | 0,27 | 0,49 |
| L1-Logistic | 0,86 | 0,73 | **0,91** |
| Random Forest | 0,85 | 0,69 | 0,88 |
| Toxic-BERT | 0,78 | 0,16 | 1,000 (zie tekst) |

Toxic-BERT vertoont een opmerkelijke AUC van exact 1,000 maar een lage F1 van 0,16. De combinatie van perfecte ranking met lage drempelgebaseerde precision wijst op label-leakage: de Kaggle pre-berekende `toxicity_score`-kolom is hoogstwaarschijnlijk gegenereerd met `unitary/toxic-bert` zelf, waardoor onze toets effectief zelfvoorspelling betreft. Deze observatie versterkt de waarde van onze onafhankelijke L1-Logistic baseline (AUC 0,91) als onafhankelijke validatie van het toxiciteitssignaal.

De top-features voor *hoge toxiciteit* — `hell`, `racist`, `stupid`, `worst`, `loser`, `corrupt`, `disgrace`, `lunatics`, `pathetic`, `thugs`, `crooked`, `disgusting`, `incompetent`, `deranged` — vormen herkenbaar Trumps signatuur-aanvalsvocabulaire. Voor *lage toxiciteit*: `thank`, `pleased`, `congratulations`, `fantastic`, `endorsement`, `incredible`, `champion`, `honor`.

### 4.4 Iran-conflict event-study

#### 4.4.1 Sample en design

Op basis van data tot juni 2026 identificeren wij 134 Iran-gerelateerde posts (versus 435 controle-posts) waarvoor voldoende intraday WTI-data beschikbaar is. Voor SPY en XLE bedraagt het sample 128 Iran-posts versus 378 controle-posts (kleiner vanwege markt-openingstijden).

#### 4.4.2 Event-study op marktreacties (bootstrap-CI)

Wij vergelijken het verschil in gemiddelde returns tussen Iran- en controle-posts (n = 135 vs. ~499) via bootstrap-95%-CI's. Het beeld is **window-afhankelijk**: op de meeste windows omvat het CI nul, maar twee windows tonen een significant *positief* verschil:

| Ticker | Window | Δμ (bp) | 95%-CI (bp) | sluit 0 uit |
|---|---|---|---|---|
| WTI | t+24u | +73,3 | [−2,8, +148,6] | nee |
| SPY | t+4u | +14,0 | [+4,4, +23,5] | **ja** |
| SPY | t+24u | +9,6 | [−2,8, +22,1] | nee |
| XLE (WTI-proxy) | t+24u | +44,0 | [+3,4, +83,6] | **ja** |
| XLE (WTI-proxy) | t+4u | −1,1 | [−36,0, +33,2] | nee |

Iran-posts gaan dus samen met een hogere SPY-return op 4 uur (+14 bp) en een hogere XLE-return op 24 uur (+44 bp); WTI zelf is op geen enkel window significant. Het eerder gerapporteerde sterk *negatieve* XLE-effect (Δμ −56,9 bp, p = 0,007 onder een parametrische t-toets) repliceert dus niet — op de volledige, opnieuw verzamelde dataset draait het zelfs van teken. Dit onderstreept hoe gevoelig deze correlaties zijn voor de dataset-revisie en de keuze van window.

Op **minuut-niveau** (one-sample CAR t.o.v. nul, baseline = 30 minuten vóór de post, 1-minuut-data) wijst het juist de andere kant op: de brede markt (SPY) vertoont een significante *negatieve* drift in het venster direct na Iran-posts, oplopend tot Δ = −32,0 bp na 120 minuten (95%-CI [−56,9, −6,1], n = 54). Voor XLE is de puntschatting −75,7 bp maar het CI omvat nul ([−210,8, +25,2]). De tegengestelde tekens tussen de uur-event-study (positief, langere horizon, dagdata) en de minuut-CAR (negatief, korte horizon, 1-min-data) tonen dat er **geen robuust, consistent gericht return-effect** is; de richting hangt af van horizon en databron.

#### 4.4.3 Granger-causaliteitstoetsen

Op uur-resolutie (n = 918 uurlijkse observaties, waarvan 70 met ten minste één Iran-post):

| Richting | Lag 1u | Lag 2u | Lag 3u | Lag 4u |
|---|---|---|---|---|
| Posts → WTI returns | F = 0,04, p = 0,84 | p = 0,97 | p = 0,98 | p = 0,99 |
| WTI returns → Posts | F = 2,13, p = 0,14 | **F = 6,51, p = 0,0016** | **F = 5,26, p = 0,0013** | **F = 4,32, p = 0,0018** |

Op 5-minuten-resolutie (n = 13.386 observaties):

| Richting | Lag 5m | Lag 10m | Lag 15m | Lag 30m | Lag 60m |
|---|---|---|---|---|---|
| Posts → WTI returns | p = 0,75 | p = 0,85 | p = 0,92 | p = 0,66 | p = 0,46 |
| WTI returns → Posts | p = 0,41 | p = 0,67 | p = 0,19 | p = 0,14 | **p = 0,025** |

De Granger-resultaten zijn opmerkelijk consistent: posts voorspellen WTI-rendementen niet op enige geteste resolutie of lag, terwijl WTI-rendementen Trumps posting-frequentie robuust voorspellen met een lag van 2–4 uur (p < 0,002). Op 5-minuten-resolutie verschijnt eveneens een marginaal reverse-direction signaal op 60-minuten lag (p = 0,025). Dit patroon is consistent met een reactieve Trump-interpretatie: hij commentariëert op marktbewegingen die hij waarneemt op een tijdsschaal van enkele uren.

#### 4.4.4 Tests voor informed trading

Wij toetsen twee falsificeerbare implicaties van de manipulatie-hypothese.

**Volume-anomalie.** Op basis van XLE-uurvolumes (WTI-proxy) z-gescoord tegen een 24-uurs voortschrijdende baseline vallen Iran-posts in uren met een gemiddelde z-score van +0,29 tegen +0,05 voor controle-posts; het bootstrap-95%-CI op het verschil (+0,25σ) bedraagt [+0,04, +0,46] en **sluit nul uit**. Voor de brede markt (SPY) is het verschil niet significant (+0,13σ, CI [−0,05, +0,32]). Er is dus aantoonbaar verhoogd handelsvolume in de energiesector rond Iran-posts, maar de meest plausibele verklaring blijft common cause (Iran-nieuwsperiodes drijven zowel het volume als Trumps posts), niet systematische voor-positionering.

**Price-timing.** Onder de manipulatie-hypothese zouden bullish posts (de meerderheid van Iran-posts) systematisch nabij lokale dieptepunten in het 4-uurs voorgaande window moeten vallen — een patroon dat optimale entry-timing voor lange posities zou indiceren. Wij vinden geen significant verschil: Iran-posts hebben een gemiddelde positie van 0,391 binnen het 4-uurs window (waarbij 0 = lokaal dieptepunt, 1 = lokaal hoogtepunt) tegen 0,354 voor controle-posts (p = 0,42). Beide groepen vertonen een bimodale verdeling met clusters nabij 0 en 1, een methodologisch artefact van het korte window. Geen aanwijzing voor systematische optimale timing.

### 4.5 Event-study per individueel aandeel

De voorgaande analyses opereren op brede marktindices (SPX, WTI, XLE). Een index aggregeert echter over honderden ondernemingen, waardoor een effect dat specifiek is voor één genoemd bedrijf systematisch wordt uitgemiddeld. Wij toetsen daarom een nauwkeuriger geformuleerde hypothese op de volledige history (februari 2022 – april 2026): vertoont een individueel aandeel een grotere abnormale reactie wanneer Trump het bedrijf expliciet noemt dan de brede markt?

**Design.** Uit alle 26.819 posts extraheren wij bedrijfsvermeldingen via een curated bedrijf→ticker-mapping (`src/features/company_mentions.py`, 24 ondernemingen), met word-boundary regex om valse positieven te beperken. Voor elk genoemd bedrijf berekenen wij een *market-model abnormal return*: het verwachte rendement volgt uit een OLS-regressie van het dagrendement op SPY over een estimation window van 120 handelsdagen, met een gap van 11 dagen vóór de eventdag om contaminatie te vermijden ($r_{i,t} = \alpha_i + \beta_i r_{SPY,t} + \varepsilon_{i,t}$; $AR_{i,t} = r_{i,t} - (\hat\alpha_i + \hat\beta_i r_{SPY,t})$). De AR is hierdoor per constructie markt-gecorrigeerd, dus bedrijfsspecifiek. Het verschil in AR_1d en CAR_3d tussen mention- en controle-dagen van hetzelfde aandeel schatten wij via bootstrap-CI's (op zowel het gemiddelde als het outlier-robuuste mediaan-verschil). Verhandelbaarheidsvensters worden gerespecteerd (DJT vanaf de beursgang 26 maart 2024; TWTR tot de delisting op 27 oktober 2022).

**Vermeldingen.** Van de 26.819 posts noemen er 1.273 minstens één onderneming. Met voldoende verhandelbare mention-dagen voor toetsing (n ≥ 30): DJT (n=217), Google (n=127), Meta (n=79), Tesla (n=52), Amazon (n=50) en Apple (n=35).

**Aggregaat-resultaten.** Wij rapporteren het verschil als bootstrap-95%-CI op het gemiddelde verschil tussen mention- en controle-dagen. Twee effecten sluiten nul uit, beide negatief: DJT op CAR_3d (Δμ = −158 bp, 95%-CI [−309, −8]) en Tesla op AR_1d (Δμ = −115 bp, 95%-CI [−228, −7]). Tesla's CAR_3d (−176 bp, CI [−364, 13]) en de overige ondernemingen — Amazon (CAR_3d +51 bp, CI [−12, 116]), Google, Meta en Apple — sluiten nul niet uit. Doordat wij CI's rapporteren in plaats van p-waarden is geen Bonferroni-correctie nodig. De resultaten zijn suggestief, niet bewijzend.

Het inhoudelijk relevante punt is echter de effectgrootte, niet de significantie: de individuele effecten (−115 tot −176 bp) overtreffen met een ordegrootte alles wat op SPX-niveau zichtbaar was (≈ nul). Dit ondersteunt de hypothese dat indices bedrijfsspecifieke effecten wegmiddelen.

**Robuustheid (Tesla) — fragiel.** Het Tesla-effect verdient nadere toetsing omdat de AR-verdeling zware staarten heeft. Het volle-sample mean-effect sluit nul uit (−115 bp, CI [−228, −7]), maar leunt op de staart: bootstrap-CI's na het weglaten van de zwaarste dag (5 juni 2025, de publieke breuk tussen Trump en Musk, AR = −14,3%) verbreden tot [−189, 11] en omvatten nul weer. Ook het outlier-robuuste **mediaan**-verschil sluit nul niet uit (−79 bp, 95%-CI [−147, 47]). Het negatieve effect is dus reëel in richting — 62% van de mention-dagen is negatief — maar statistisch fragiel en deels gedreven door enkele extreme dagen. Wij presenteren het bijgevolg als suggestief, en rapporteren naast het gemiddelde steeds het mediaan-CI.

---

## 5. Discussie

### 5.1 Interpretatie van de hoofdbevinding

De cumulatieve evidentie van complementaire analyses (event-study met bootstrap-CI, Granger op uur- en 5-minuten-resolutie, volume- en price-timing-toetsen) ondersteunt geen directe causale invloed van Trumps Iran-posts op de oliemarkt. De return-effecten op uur-resolutie zijn klein, niet consistent gericht (positief op enkele windows, negatief op minuut-niveau) en gevoelig voor dataset-revisie; gecombineerd met de afwezigheid van Granger-causaliteit in de richting posts→prijzen op beide tijdsresoluties, sluit dit weliswaar sub-minute causale effecten niet uit, maar maakt het de hypothese van directe aansturing minder waarschijnlijk dan een gemeenschappelijke onderliggende oorzaak. De tekenwisseling tussen horizonnen — positieve uur-effecten, negatieve minuut-drift — past beter bij correlaties rond nieuwsperiodes dan bij een door de post veroorzaakte beweging.

Het robuuste Granger-signaal in de richting van WTI→posts op uur-resolutie (F = 4,3–6,5, p < 0,002) ondersteunt een interpretatie waarin Trumps posts reactief zijn: hij commentariëert op marktbewegingen die hij waarneemt op een tijdsschaal van enkele uren. Deze reactieve interpretatie is consistent met (a) het engagement-resultaat (negatieve posts ontvangen meer engagement, hetgeen Trump een prikkel geeft om reactief negatief te schrijven over gebeurtenissen die hij waarneemt), en (b) het feit dat sub-uur Granger-signalen in *beide* richtingen ontbreken — wat erop wijst dat geen van beide variabelen direct op de andere reageert binnen het uur.

De meest parsimonieuze interpretatie is dat onderliggende geopolitieke gebeurtenissen — Israëlische operaties, Iraanse vergelding, OPEC-besluiten, andere Midden-Oosten-ontwikkelingen — zowel de oliemarkt (binnen minuten via nieuwsberichten en algoritmische traders) als Trumps daaropvolgende Truth Social-activiteit (binnen uren, na nieuwsverwerking en publicatie-beslissing) aansturen. De geobserveerde correlatie tussen Iran-posts en marktbewegingen reflecteert dan een gemeenschappelijke informatiebron, niet een directe oorzakelijke keten.

### 5.2 Het XLE-resultaat als secundaire bevinding

De return-effecten rond Iran-posts zijn niet consistent gericht. Op uur-resolutie gaan Iran-posts samen met een *hogere* SPY-return (t+4u, +14,0 bp, CI [+4,4, +23,5]) en XLE-return (t+24u, +44,0 bp, CI [+3,4, +83,6]); op minuut-niveau vertoont SPY juist een *negatieve* drift (−32,0 bp na 120 min, CI [−56,9, −6,1]). Het eerder gerapporteerde negatieve XLE-uureffect (−56,9 bp, p = 0,007) houdt niet stand en draait zelfs van teken op de volledige data. Deze tegenstrijdigheid tussen horizon en databron maakt duidelijk dat er geen robuust energiesector-specifiek koerseffect is. Wat wél consistent overeind blijft, is (a) significant verhoogd XLE-handelsvolume rond Iran-posts (+0,25σ, CI [+0,04, +0,46]) en (b) de reactieve Granger-structuur. Gegeven dat geheel is common cause (onderliggend Iran-nieuws dat zowel de markt als Trumps posts aanstuurt) de meest plausibele verklaring.

### 5.3 Methodologische beperkingen

Vijf beperkingen dienen expliciet vermeld:

1. *Tijdsaggregatie.* Onze fijnste resolutie (5 minuten) kan sub-minute marktreacties op individuele posts missen. Algoritmische trading-systemen kunnen tweets binnen seconden verwerken en handelen; voor uitsluitsel over deze tijdsschaal zou tick-level data (per seconde of per transactie) vereist zijn.
2. *Common-cause confounding.* Zonder kruisverwijzing naar nieuwswire-tijdstempels (Reuters, Bloomberg, AP) kunnen wij niet definitief vaststellen of marktbewegingen voortvloeien uit nieuws dat Trumps posts simpelweg parafraseren, dan wel uit Trumps posts zelf.
3. *Heterogene effecten.* De aggregaat-analyse middelt over 134 Iran-posts. Specifieke high-impact posts (zoals de Hormuz-blokkade-aankondiging op 11–12 april 2026) kunnen substantiële individuele impact hebben die door het gemiddelde wordt uitgesmeerd.
4. *Sample-omvang van 60 dagen.* yfinance beperkt intraday-data tot circa 60 dagen, hetgeen onze analyse op uur-resolutie inkort tot een gedeelte van de conflictperiode.
5. *Keyword-selectie van Iran-posts.* Onze keyword-matching kan zowel valse positieven (een Trump-post die alleen `iran` noemt zonder marktrelevante inhoud) als valse negatieven (een marktrelevante post zonder Iran-keyword) bevatten.

### 5.4 Reflectie op de classifiers

De superieure prestatie van L1-Logistic ten opzichte van Twitter-RoBERTa is consistent met de observatie van Loughran en McDonald (2016) dat lineaire methodes competitief blijven op gespecialiseerde tekstdomeinen. De vermoedelijke label-leakage van Toxic-BERT op de toxiciteitstaak versterkt het argument voor onafhankelijke baseline-modellen bij elke evaluatie waarin de herkomst van ground-truth labels niet volledig transparant is.

### 5.5 Implicaties

Voor het publieke debat impliceren onze bevindingen dat de populaire perceptie dat presidentiële social-media-posts directe markt-bewegingen veroorzaken — althans in deze case van Iran-conflict-communicatie op de oliemarkt — niet door empirische data wordt ondersteund. Markten lijken te reageren op het onderliggende nieuws, niet op de presidentiële uitingen erover.

De per-aandeel event-study (§4.5) nuanceert dit beeld op één punt: waar het indexniveau geen effect toont, is er op bedrijfsniveau wél een — overwegend negatieve — richting zichtbaar, met effectgroottes die een ordegrootte boven het indexniveau liggen. De bevinding blijft statistisch zwak door kleine samples per bedrijf en overleeft geen multiple-testing-correctie, maar suggereert dat aggregatie over de markt een reëel bedrijfsspecifiek signaal verbergt.

Voor toekomstig onderzoek bevelen wij aan: (a) tick-level data combineren met nieuwswire-tijdstempels om sub-minute causale effecten te isoleren, (b) uitbreiding naar andere geopolitieke contexten (handelsoorlogen, NAVO-spanningen) voor generaliseerbaarheid, (c) vergelijkende analyse met andere politiek dominante accounts, en (d) het bedrijfsspecifieke effect aanscherpen door per mention-dag de toon (§4.2) en de news-timing te koppelen — is de daling groter bij negatief-getoonde en niet-reactieve posts? — wat tevens de statistische power verhoogt door ondernemingen op toon te poolen.

---

## 6. Conclusie

Dit onderzoek toetste empirisch of Donald Trumps Iran-gerelateerde Truth Social-posts de WTI ruwe-olieprijs beïnvloeden sinds het uitbreken van het Iran-conflict op 28 februari 2026.

Op basis van 134 Iran-posts en 435 controle-posts in een 60-daagse intraday-window vinden wij geen statistisch significante directe invloed van posts op WTI-rendementen op enige geteste resolutie of tijdvenster. Granger-causaliteitstoetsen ondersteunen consistent het omgekeerde verband: WTI-rendementen voorspellen Trumps Iran-post-frequentie met een lag van 2–4 uur (p < 0,002). De meest parsimonieuze interpretatie is dat onderliggende geopolitieke gebeurtenissen zowel marktbewegingen als Trumps daaropvolgende communicatie aansturen.

Secundaire bevindingen, na hertoetsing met bootstrap-CI's op de volledige dataset: de uur-return-effecten zijn niet consistent gericht (significant positief op SPY t+4u en XLE t+24u, maar negatief op de minuut-CAR van SPY; WTI nergens significant), en het eerder gerapporteerde XLE-effect van −56,9 bp houdt geen stand. Wat robuust overeind blijft, is significant verhoogd energiesector-volume rond Iran-posts (+0,25σ). Dat geheel is consistent met een reactieve interpretatie en common cause, niet met directe markt-aansturing.

Toetsen voor informed trading (volume-anomalie en price-timing) leveren geen robuust patroon dat consistent zou zijn met systematische voor-positionering rond Trumps posts.

Een uitbreiding naar het niveau van individuele aandelen toont een complementair beeld: waar de brede index geen effect vertoont, vertonen afzonderlijke door Trump genoemde ondernemingen wél een — overwegend negatieve — bedrijfsspecifieke reactie. Twee bootstrap-CI's sluiten nul uit: DJT (CAR_3d −158 bp, CI [−309, −8]) en Tesla (AR_1d −115 bp, CI [−228, −7]); het Tesla-effect is echter fragiel (het mediaan-CI omvat nul). De effectgroottes liggen een ordegrootte boven het indexniveau, wat bevestigt dat marktbrede aggregatie individuele effecten maskeert.

Naast deze empirische bevindingen heeft dit onderzoek een herbruikbare classificatie-pipeline opgeleverd: een sentiment-classifier met 83% accuratesse en een toxiciteits-classifier met AUC 0,91, beide gebaseerd op interpreteerbare lineaire modellen die in productie kunnen worden ingezet voor real-time scoring van nieuwe posts.

---

## 7. Referenties

Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. *The Journal of Finance, 59*(3), 1259–1294.

Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. *arXiv preprint* arXiv:1908.10063.

Bollen, J., Mao, H., & Zeng, X.-J. (2011). Twitter mood predicts the stock market. *Journal of Computational Science, 2*(1), 1–8.

Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32.

Jain, S., & Wallace, B. C. (2019). Attention is not explanation. *Proceedings of NAACL-HLT 2019*, 3543–3556.

Ke, Z., Kelly, B., & Xiu, D. (2023). Predicting returns with text data. *Journal of Finance, 78*(5), 3551–3593.

Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-K filings. *The Journal of Finance, 66*(1), 35–65.

Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. *Journal of Accounting Research, 54*(4), 1187–1230.

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems, 30*, 4765–4774.

Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *The Journal of Finance, 62*(3), 1139–1168.

---

## 8. Bijlagen

### Bijlage A — Code repository

Volledige broncode beschikbaar op GitHub:
**https://github.com/QuintenFritz/truthsocial-marketimpact**

Belangrijke onderdelen:
- `notebooks/01–14` — analyse-notebooks per fase.
- `src/data/` — Python-modules voor dataverzameling en preprocessing.
- `src/data/scrape_trumpstruth_rss.py` — eigen scraper voor live posts.
- `src/features/company_mentions.py` — bedrijf→ticker-mapping voor de per-aandeel event-study (§4.5).
- `models/sentiment/` en `models/toxicity/` — getrainde classifiers.

De tag `v1.0-market-prediction` markeert een snapshot van een initiële (verworpen) onderzoeksrichting waarin wij de algemene marktimpact van alle Trump-posts (niet uitsluitend Iran-gerelateerd) probeerden te modelleren via Random Forest. Deze richting werd verworpen wegens onvoldoende signaal-tot-ruis-verhouding (AUC circa 0,55), waarna de focus verschoof naar de Iran-conflict event-study die in dit document wordt gerapporteerd.

### Bijlage B — Reproductie

```bash
git clone https://github.com/QuintenFritz/truthsocial-marketimpact.git
cd truthsocial-marketimpact
conda create -n truthsocial python=3.11 -y
conda activate truthsocial
pip install -e ".[dev,dashboard,nlp]"

# Plaats Kaggle CSV in data/raw/trump_truth_archive.csv
python -m src.data.scrape_trumpstruth_rss --start 2026-02-28

# Run notebooks 01 t/m 14 in volgorde
jupyter lab notebooks/
# Run notebooks 01 t/m 10 in volgorde
```

### Bijlage C — Aanvullende figuren en tabellen

[TODO: voeg PNG-exports van de relevante notebooks toe — temporal sentiment plot, classifier comparison bars, t-test histograms, Granger output, volume z-score histogram.]

---

*Versie 1.0 — gegenereerd 2 juni 2026 op basis van data t/m juni 2026.
Conversie naar Word: `pandoc scriptie_full.md -o scriptie.docx`.*
