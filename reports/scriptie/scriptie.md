# Een analyse van Donald Trump's Truth Social communicatie tijdens het Iran-conflict 2026

**Onderzoek naar de relatie tussen presidentiële social media en de oliemarkt**

---

**Auteur:** Quinten Friederichs
**Opleiding:** VDO Data Scientist
**Onderwijsinstelling:** Syntra
**Begeleider:** TIm Hellemans/Olivier Claerebout
**Indiendatum:** juni 2026
**Versie:** 0.1 (skelet)

---

> **Notitie voor mezelf bij het schrijven**
> Dit is een werk-skelet. Elk hoofdstuk heeft een korte beschrijving van wat er moet komen,
> een suggestie voor de eerste paragraaf, en `[TODO: ...]` markers waar je specifieke
> data of figuren moet invullen. Vul aan, verwijder de notes, en converteer naar Word
> met `pandoc scriptie.md -o scriptie.docx` wanneer je klaar bent voor inlevering.
>
> Geschatte eindlengte: 30-50 pagina's.

---

## Samenvatting

[TODO: schrijf deze sectie LAATSTE — als alle resultaten staan. Lengte: ~250 woorden.]

**Template-structuur**:
- 1 zin context (waarom dit onderwerp belangrijk is)
- 1 zin onderzoeksvraag
- 2-3 zinnen methodologie (data, modellen, statistische tests)
- 2-3 zinnen belangrijkste bevindingen (cijfers!)
- 1 zin conclusie

**Voorbeeld**:

> *Sinds het uitbreken van het Iran-conflict op 28 februari 2026 heeft Donald Trump
> intensief gecommuniceerd over de oorlog via zijn platform Truth Social. Dit onderzoek
> test empirisch de hypothese dat zijn berichten doelbewust worden ingezet om de
> oliemarkt te beïnvloeden. Met behulp van 26.819 historische posts (Kaggle),
> aanvullende gescrapte data sinds conflictstart (~XXX posts), intraday WTI futures
> data en eigenontwikkelde sentiment- en toxiciteitsclassificeerders, voeren we een
> event-study uit op Iran-gerelateerde posts. We vinden een statistisch significante
> correlatie tussen Iran-posts en WTI-rendementen (+50 tot +103 basispunten in
> 1-24u windows, p<0.05), maar Granger-causaliteitstoetsen op zowel uur- als
> 5-minuten-resolutie ondersteunen geen directe causale invloed van posts op prijzen.
> De meest parsimonieuze interpretatie is dat onderliggende geopolitieke
> gebeurtenissen zowel marktbewegingen als Trump's communicatie aansturen. Het
> onderzoek levert tevens een herbruikbare classificatie-pipeline op die nieuwe
> posts in real-time kan scoren voor sentiment en toxiciteit.*

---

## Inhoudsopgave

1. [Inleiding](#1-inleiding)
2. [Literatuurstudie](#2-literatuurstudie)
3. [Data en methodologie](#3-data-en-methodologie)
4. [Resultaten](#4-resultaten)
5. [Discussie](#5-discussie)
6. [Conclusie](#6-conclusie)
7. [Referenties](#7-referenties)
8. [Bijlagen](#8-bijlagen)

---

## 1. Inleiding

[TODO: schrijf 2-3 pagina's. Volg de drie subsecties hieronder.]

### 1.1 Context

**Schrijf hier over:**
- De opkomst van social media als communicatiekanaal voor politici (Twitter/X tijdens Trump's eerste termijn, Truth Social na de Twitter-ban in 2021).
- Het feit dat individuele posts van presidentiële accounts in het verleden meetbare marktbewegingen hebben veroorzaakt (verwijs naar Born et al. 2017 over Trump tweets).
- Hoe het Iran-conflict (start 28 februari 2026) een unieke onderzoekscontext creëert: een actueel geopolitiek event waarin energie-prijzen volatiel zijn en de Amerikaanse president actief commentariëert op het verloop.

**Suggestie eerste paragraaf**:

> *Met de opkomst van directe sociale media als primair communicatiekanaal voor
> staatshoofden is de relatie tussen presidentiële uitingen en financiële markten
> een actief onderzoeksgebied geworden. Born et al. (2017) toonden aan dat tweets
> van Donald Trump tijdens zijn eerste presidentschap meetbare abnormale rendementen
> veroorzaakten in specifieke aandelen en sectoren. Na zijn verbanning van Twitter
> in 2021 verplaatste Trump zijn communicatie naar het door hem opgerichte platform
> Truth Social, waarvan de marktimpact tot dusver veel minder empirisch onderzocht
> is. Het uitbreken van een gewapend conflict met Iran op 28 februari 2026 creëert
> een unieke onderzoekscontext: een actueel geopolitiek evenement waarin de oliemarkt
> hoog volatiel is en de huidige president — opnieuw Trump — frequent commentaar
> levert op de gebeurtenissen via Truth Social.*

### 1.2 Probleemstelling en onderzoeksvragen

**Hoofdvraag:**

> *In hoeverre is er een statistisch detecteerbaar verband tussen Trump's Iran-gerelateerde
> Truth Social posts en bewegingen van de WTI ruwe-olieprijs sinds 28 februari 2026?*

**Sub-vragen:**

1. **Descriptief**: Hoe verschilt Trump's communicatiepatroon (volume, sentiment, toxiciteit)
   in de conflict-periode ten opzichte van eerdere periodes?
2. **Predictief**: Is een tekstuele classifier in staat de sentiment- en
   toxiciteitslabels van bestaande gespecialiseerde tools te reproduceren met
   acceptabele accuratesse?
3. **Correlationeel**: Vallen Iran-gerelateerde posts statistisch significant samen
   met abnormale bewegingen in WTI futures, S&P 500 of de energie-sector?
4. **Causaliteit**: Voor zover er een correlatie bestaat — is er evidentie dat posts
   prijsbewegingen voorspellen, dat prijsbewegingen posts voorspellen, of dat beide
   op een gemeenschappelijke onderliggende oorzaak reageren?

### 1.3 Scriptie-opbouw

[TODO: 1 paragraaf die zegt wat in elk volgend hoofdstuk komt.]

---

## 2. Literatuurstudie

[TODO: 3-5 pagina's. De gedetailleerde literatuurscan staat in `reports/literatuurscan.md`.
Selecteer ~6-8 papers en bespreek ze inhoudelijk hier. Niet alleen citeren — uitleggen
wat ze gevonden hebben en hoe het jouw werk informeert.]

### 2.1 Social media en financiële markten

**Behandel hier:**
- **Bollen, Mao, Zeng (2011)** — *Twitter Mood Predicts the Stock Market*. Klassiek
  voorbeeld van social media → markt link, maar op aggregaat-niveau (algemene tweets).
- **Antweiler & Frank (2004)** — *Is All That Talk Just Noise?*. Toont dat
  disagreement en sentiment in message boards beperkte voorspellende waarde hebben
  voor returns.
- **Tetlock (2007)** — *Giving Content to Investor Sentiment*. Methodologische
  blauwdruk voor sentiment-uit-tekst analyse en lagged effects op returns.

### 2.2 Textuele analyse in financiële context

**Behandel hier:**
- **Loughran & McDonald (2011, 2016)** — Domain-specifieke financiële sentiment
  woordenlijsten en methodologische review. Argumentatie waarom generieke
  sentiment-tools tekortschieten in financiële context.
- **Araci (2019)** — *FinBERT*. Pre-trained transformer voor financial text.
- **Ke, Kelly, Xiu (2023)** — *Predicting Returns with Text Data*. State-of-the-art
  comparison van TF-IDF, lexicon en deep learning approaches.

### 2.3 Interpretability en methodologische kritiek

**Behandel hier:**
- **Jain & Wallace (2019)** — *Attention is Not Explanation*. Waarschuwing tegen
  het gebruik van attention weights als feature importance proxy.
- **Lundberg & Lee (2017)** — *SHAP*. Theoretisch gegrondveste post-hoc
  interpretability methode die wij toepassen.
- **Breiman (2001)** — *Random Forests*. Onze niet-lineaire baseline.

### 2.4 Gap analyse

[TODO: 1 paragraaf — wat ontbreekt nog in de literatuur en hoe vult dit onderzoek dat?]

**Suggestie**:

> *Hoewel de impact van Trump's Twitter-communicatie tijdens zijn eerste presidentschap
> uitgebreid is onderzocht, ontbreekt empirisch werk over Truth Social specifiek, en
> nog meer specifiek over de combinatie van politieke communicatie met de oliemarkt
> tijdens een actief geopolitiek conflict. Dit onderzoek vult die leemte met (a) een
> tijdgebonden case-study sinds 28 februari 2026, (b) eigen-getrainde classifiers
> in plaats van afhankelijkheid van vooraf gelabelde datasets, en (c) een methodologisch
> rigoureuze causaliteitsanalyse op meerdere tijdsresoluties.*

---

## 3. Data en methodologie

[TODO: 5-8 pagina's. Wees hier rigoureus — examinatoren controleren dit hoofdstuk grondig.]

### 3.1 Data sources

**Beschrijf elk van de volgende:**

#### 3.1.1 Truth Social posts (historisch)

- **Bron**: Kaggle dataset `trump_truth_archive.csv` (32.754 posts, 14 feb 2022 – 23 april 2026).
- **Schema**: post_id, created_at (UTC), text, engagement metrics (likes, retruths, replies),
  + 30 pre-computed features (sentiment_score, sentiment_label, toxicity_score, topic, etc.).
- **Preprocessing**: filter media-only posts zonder text (n=5.935 gedropt). Resultaat: 26.819 posts.
- **Tekst cleanup**: lowercase, URL/mention strip, unicode normalisatie via `ftfy` om
  mojibake artefacten (zoals `itâ€™s → it's`) te corrigeren.

#### 3.1.2 Truth Social posts (live, sinds conflictstart)

- **Bron**: `trumpstruth.org` RSS feed, gescraped via eigen Python script
  (`src/data/scrape_trumpstruth_rss.py`).
- **Periode**: 28 februari 2026 tot heden.
- **Aantal posts**: [TODO: vul aantal in].

#### 3.1.3 Marktdata

- **Bron**: yfinance (Yahoo Finance API).
- **Tickers**: WTI ruwe-olie futures (`CL=F`), S&P 500 ETF (`SPY`), Energy Sector ETF (`XLE`).
- **Resolutie**: daily voor full window; hourly voor laatste 60 dagen (yfinance limiet);
  5-minuten voor laatste 60 dagen.

### 3.2 Classificatie-modellen

#### 3.2.1 Sentiment classifier (notebook 08)

- **Target**: `sentiment_label` (3-class: positive/negative/neutral) uit Kaggle ground truth.
- **Features**: TF-IDF unigrams + bigrams (max 8000 features, English stopwords filter).
- **Modellen**: L1-Logistic regression (sparse, interpreteerbaar), Random Forest (non-lineair),
  Twitter-RoBERTa (transformer, zero-shot).
- **Evaluatie**: chronologische 80/20 split, accuracy en F1_macro op test set.

#### 3.2.2 Toxicity classifier (notebook 09)

- **Target**: binary, gebaseerd op `toxicity_score` met threshold = 75e percentiel van
  training set (= top 25% van posts gelabeld als `high_tox`).
- **Modellen**: identiek aan sentiment + optionele `unitary/toxic-bert` transformer.

### 3.3 Statistische tests

#### 3.3.1 Event-study t-test

Voor elke Iran-gerelateerde post `p` op tijdstip `t`, bereken WTI log-return over windows
`[t, t+Δ]` voor `Δ ∈ {1u, 4u, 24u}`. Vergelijk met log-returns rond controle-posts
(niet-Iran posts in dezelfde periode) via Welch's t-test (geen aanname van gelijke variantie).

#### 3.3.2 Granger causaliteitstest

Gebruik `statsmodels.tsa.stattools.grangercausalitytests` om te testen of het verleden
van variabele X de toekomst van variabele Y voorspelt, gecontroleerd voor Y's eigen
autocorrelatie. Twee richtingen getest: posts → returns en returns → posts. Twee
resoluties: hourly (60-dagen window) en 5-min (60-dagen window).

### 3.4 Methodologische beslissingen en hun verantwoording

[TODO: bespreek hier expliciet keuzes die je hebt gemaakt en waarom. Voorbeelden:]
- Waarom 75e percentiel voor toxicity threshold? (klassen-balans + interpreteerbare drempel)
- Waarom chronologische train/test split? (geen look-ahead bias)
- Waarom `class_weight="balanced"`? (omgang met klasse-imbalans)

---

## 4. Resultaten

[TODO: 8-12 pagina's. Dit is het hart van je scriptie. Elke sub-sectie correspondeert
met een notebook.]

### 4.1 Descriptieve analyse (notebook 07)

#### 4.1.1 Sentiment dynamics over tijd

[TODO: insert figuur — de sentiment-curve plot uit notebook 07 cel 8.]

**Belangrijkste observaties** (vul aan):
- Trump's sentiment varieerde aanzienlijk gedurende de geanalyseerde periode (2022-2026).
- Een duidelijke positieve verschuiving vanaf januari 2025 (post-inauguratie).
- Mar-a-Lago search (augustus 2022) markeert een lokaal dieptepunt.

#### 4.1.2 Engagement-negativity link

Statistisch significant verschil in engagement tussen negative en positive posts:

- Mediane likes negative posts: **14.874**
- Mediane likes positive posts: **13.633**
- Mann-Whitney U test: p = **0.00065** (significant)

**Interpretatie**: bevestigt de "negativity bias" hypothese voor één van de meest gevolgde
politieke accounts ter wereld. Negatieve content krijgt ~9% meer engagement.

### 4.2 Sentiment classifier resultaten (notebook 08)

[TODO: insert figuur — comparison bar chart uit notebook 08 cel 16.]

**Performance op held-out test set:**

| Model | Accuracy | F1_macro | F1_weighted |
|---|---|---|---|
| Dummy (stratified) | 0.42 | 0.31 | 0.45 |
| L1-Logistic | **0.83** | **0.76** | **0.84** |
| Random Forest | 0.78 | 0.71 | 0.79 |
| Twitter-RoBERTa (zero-shot) | 0.69 | 0.59 | 0.71 |

**Belangrijke observatie**: L1-Logistic verslaat een 125M-parameter pre-trained transformer
(Twitter-RoBERTa zero-shot). Dit wordt verklaard door (a) label-distribution mismatch
(Twitter-RoBERTa is getraind op een andere sentiment-definitie dan de Kaggle ground truth)
en (b) de stilistisch uniforme aard van Trump's posts die door lineaire methodes effectief
wordt gevangen.

[TODO: insert figuur — top-20 features per class uit notebook 08 cel 18.]

### 4.3 Toxicity classifier resultaten (notebook 09)

[TODO: insert figuren — bar chart uit cel 15 + ROC/PR curves uit cel 17.]

**Performance:**

| Model | Accuracy | F1 binary | AUC |
|---|---|---|---|
| Dummy | 0.58 | 0.27 | 0.49 |
| L1-Logistic | 0.86 | 0.73 | **0.91** |
| Random Forest | 0.85 | 0.69 | 0.88 |
| Toxic-BERT | 0.78 | 0.16 | 1.000 (zie discussie) |

**Methodologische opmerking**: Toxic-BERT toont een suspicious-perfect AUC van 1.000.
Onze analyse suggereert dat de Kaggle `toxicity_score` kolom waarschijnlijk gegenereerd
is met `unitary/toxic-bert` zelf, wat een label-leakage scenario creëert. Onze
L1-Logistic baseline (AUC 0.91) biedt onafhankelijke validatie van het toxicity-signaal.

[TODO: insert figuur — top-25 high-toxicity features uit notebook 09 cel 21.]

### 4.4 Iran-conflict event study (notebook 10)

#### 4.4.1 Aggregaat correlationeel verband

[TODO: insert tabel — de t-test resultaten uit notebook 10.]

**T-test op WTI returns (Iran posts vs. control posts):**

| Window | n_iran | n_ctrl | Δμ (bp) | t-stat | p-value |
|---|---|---|---|---|---|
| t−1u | 173 | 488 | **−21.6** | −2.09 | 0.038 |
| t+1u | 173 | 488 | **+103.6** | 4.04 | <0.001 |
| t+4u | 173 | 488 | **+139.1** | 5.00 | <0.001 |
| t+24u | 172 | 459 | **+134.6** | 3.11 | 0.002 |

**Oliesignaal specifiek**: SPY (S&P 500) toont geen significante differenties (p>0.13 op alle
post-windows). XLE (Energy ETF) toont een licht negatief punt-schatting maar niet
significant. Dit bevestigt dat het effect olie-specifiek is.

#### 4.4.2 Robustheidscheck: exclusie van Hormuz-cluster

Het grootste deel van het effect komt van posts op 11-12 april 2026 rond Trump's
aankondiging van een naval blockade van de Straat van Hormuz. Na exclusie van deze
cluster (11 posts):

| Window | Δμ (bp) | p-value |
|---|---|---|
| t+1u | +50.4 | 0.017 |
| t+4u | +87.3 | <0.001 |
| t+24u | +96.7 | 0.028 |

**Conclusie**: het effect blijft statistisch significant over alle post-event windows,
wat een breder patroon ondersteunt naast de individuele Hormuz-impact.

#### 4.4.3 Causale interpretatie via Granger-tests

**Op uur-resolutie:**
- Posts → WTI returns: niet significant (alle p>0.6).
- WTI returns → Posts: significant op lag 2-4u (p = 0.014, 0.021, 0.028).

**Op 5-minuten resolutie:**
- Posts → WTI returns: niet significant (alle p>0.36).
- WTI returns → Posts: niet significant (alle p>0.15).

**Interpretatie**: het patroon op uur-niveau (markt vooruit, posts achteraan) verdwijnt
op fijnere resolutie. Dit is meest consistent met een **common-cause interpretatie**:
geopolitieke gebeurtenissen veroorzaken zowel oliemarktbewegingen (binnen minuten via
news-wires) als Trump's posts (binnen uren, nadat hij het nieuws verwerkt). Sub-minuut
causale effecten van posts kunnen we niet uitsluiten met onze data.

[TODO: insert figuren — timeline plot (cel 11) + histogram-vergelijking (cel 13) + top-10
impactful posts overzicht.]

### 4.5 Top-10 meest impactvolle Iran-posts

[TODO: kopieer de output van notebook 10 cel 16 hier in een overzichtelijke tabel/bullet-list.
Voorbeeld:]

> **#1 — 11 april 2026, 12:58 UTC** — *WTI +9.0% in 1 uur*
> *"The Fake News Media has lost total credibility... Iran is LOSING BIG..."*
>
> **#2 — 12 april 2026, 12:52 UTC** — *WTI +9.0% in 1 uur*
> *"Effective immediately, the United States Navy will begin the process of BLOCKADING any and all Ships trying to enter, or leave, the Strait of Hormuz..."*
>
> [TODO: 8 meer]

---

### 4.6 Event-study per individueel aandeel (notebook 14)

Alle voorgaande markttoetsen draaien op brede indices (SPX, WTI, XLE), die per definitie aggregeren over vele ondernemingen. Een effect dat specifiek is voor één door Trump genoemd bedrijf, wordt op indexniveau uitgemiddeld. Notebook 14 toetst daarom een nauwkeuriger geformuleerde hypothese op de volledige history (feb 2022 – apr 2026): reageert een individueel aandeel sterker op een expliciete Trump-vermelding dan de brede markt?

**Design.** Uit alle 26.819 posts extraheren we bedrijfsvermeldingen via een curated bedrijf→ticker-mapping (`src/features/company_mentions.py`, 24 ondernemingen) met word-boundary regex. Per genoemd bedrijf berekenen we een *market-model abnormal return*: het verwachte rendement komt uit een OLS-regressie van het dagrendement op SPY over 120 handelsdagen (estimation window), met een gap van 11 dagen vóór de eventdag. De resulterende AR is markt-gecorrigeerd en dus bedrijfsspecifiek. AR_1d en CAR_3d op mention-dagen worden via een Welch t-toets vergeleken met de controle-dagen van hetzelfde aandeel; verhandelbaarheidsvensters worden gerespecteerd (DJT vanaf 26 maart 2024, TWTR tot 27 oktober 2022).

**Vermeldingen.** 1.273 van de 26.819 posts noemen minstens één onderneming. Met n ≥ 30 verhandelbare mention-dagen: DJT (n=217), Google (n=127), Meta (n=79), Tesla (n=52), Amazon (n=50), Apple (n=35).

**Aggregaat-resultaten.**

| Bedrijf | Metriek | n | Δμ mention − controle | t | p |
|---|---|---|---|---|---|
| DJT (Trump Media) | CAR_3d | 217 | −158 bp | −2,09 | 0,037 |
| Tesla | AR_1d | 52 | −115 bp | −2,03 | 0,047 |
| Tesla | CAR_3d | 52 | −176 bp | −1,81 | 0,075 |
| Amazon | CAR_3d | 50 | +51 bp | +1,55 | 0,128 |
| Google | CAR_3d | 127 | −39 bp | −1,36 | 0,177 |
| Apple | AR_1d | 35 | −4 bp | −0,12 | 0,906 |

Twee effecten zijn ruw-significant (DJT, Tesla), beide negatief. Geen enkel resultaat overleeft de Bonferroni-correctie (12 toetsen, drempel ≈ 0,0042). Met dat aantal toetsen verwacht je ~0,6 vals-positieven; we vinden er twee — suggestief, niet bewijzend. Het inhoudelijk centrale punt is de effectgrootte: de individuele effecten (−115 tot −176 bp) zijn een ordegrootte groter dan op SPX-niveau (≈ nul), wat de hypothese ondersteunt dat indices bedrijfsspecifieke effecten wegmiddelen.

**Robuustheid (Tesla).** De AR-verdeling heeft zware staarten, dus de mean-toets is gevoelig voor uitschieters. Het Tesla-effect hangt grotendeels aan 5 juni 2025 (de publieke Trump–Musk-breuk, AR −14,3%); na verwijdering van enkel die dag zakt het naar −84 bp (p = 0,088). Outlier-robuuste toetsen tonen echter een breed gedragen patroon dat níet door die ene dag wordt verklaard: mediaan −83 bp vs. −4 bp, 10%-getrimde mean −86 bp vs. +2 bp, Mann-Whitney p = 0,057, en 62% van de mention-dagen negatief. We rapporteren voor Tesla daarom bij voorkeur de mediaan/Mann-Whitney. Figuren: `reports/figures/nb14_ar_per_company.png` en `nb14_tsla_robustness.png`.

---

## 5. Discussie

[TODO: 3-5 pagina's. Hier laat je zien dat je *nadenkt* over wat de resultaten betekenen.]

### 5.1 Interpretatie van de hoofdbevinding

**Schrijf hier**: een eerlijke interpretatie van de Iran event study. Wat we **wel** kunnen
concluderen, wat we **niet** kunnen concluderen, en waarom.

**Suggestie kernparagraaf**:

> *Onze analyse ondersteunt niet de oorspronkelijke hypothese dat Trump's Truth Social
> posts de oliemarkt actief sturen. De geobserveerde correlatie tussen Iran-gerelateerde
> posts en WTI-bewegingen (+50 tot +103 bp in 1-24u windows) is consistent met meerdere
> causale verhalen, waarvan de meest parsimonieuze interpretatie is dat onderliggende
> geopolitieke gebeurtenissen zowel marktbewegingen als zijn communicatie aansturen.
> De afwezigheid van Granger-causaliteit op 5-minuut resolutie (waarop algoritmische
> markt-reacties op tweets normaliter detecteerbaar zouden zijn) suggereert dat
> Trump's posts geen meetbare onafhankelijke causale impact hebben op de oliemarkt
> binnen het uur. Het gevonden uur-niveau Granger-signaal in de omgekeerde richting
> (markt → posts op 2-4u lag) past bij een patroon waarin Trump op een trager
> tijdsschaal reageert op nieuws en marktontwikkelingen die hij waarneemt.*

### 5.2 Methodologische beperkingen

**Bespreek expliciet:**

1. **Tijdsaggregatie**: 5-min en 1u resoluties kunnen sub-minuut causale effecten missen.
   Voor algoritmische trading-reacties zou tick-level data vereist zijn.

2. **Common-cause confounding**: zonder cross-referentie tegen news-wire timestamps
   (Reuters/Bloomberg) kunnen we onderliggende gemeenschappelijke oorzaken niet
   isoleren van directe post-effecten.

3. **Heterogene effecten**: een paar individuele posts (zoals de Hormuz blockade-aankondiging)
   tonen 9% intraday-bewegingen. Granger middelt over 14.000+ bars en kan dit
   uitsmeren.

4. **Sample-grootte 60 dagen**: yfinance-limiet op intraday data beperkt onze analyse
   tot ~60 dagen. Voor lange-termijn patronen zou een betaalde data-provider (Polygon.io,
   Bloomberg) nodig zijn.

5. **Selectie van Iran-posts**: keyword-matching kan zowel false positives (een Trump
   post die alleen "iran" noemt zonder marktrelevante content) als false negatives
   (een marktrelevante post die toevallig geen keyword bevat) bevatten.

### 5.3 Reflectie op de classifiers

**Schrijf hier:**
- L1-Logistic verslaat een pre-trained transformer voor sentiment classification —
  consistent met Loughran & McDonald's (2016) observatie dat lineaire methodes
  competitief blijven op gespecialiseerde tekstdomeinen.
- Toxic-BERT's suspiciously perfecte AUC bevestigt het belang van onafhankelijke
  validatie en het verificeren van label-generatie-procedures.

### 5.4 Implicaties

**Bespreek:**
- Wat betekent dit voor het publieke beeld dat presidentiële tweets markten bewegen?
- Welke beleidsmatige of regulatoire implicaties zijn er?
- Wat zou een vervolgonderzoek anders moeten doen?

---

## 6. Conclusie

[TODO: 1-2 pagina's. Vat samen, géén nieuw materiaal.]

**Structuur:**

1. **Korte herhaling onderzoeksvraag.**
2. **Korte samenvatting methodologie.**
3. **Belangrijkste empirische bevindingen** (1-2 zinnen per sub-vraag):
   - Descriptief: sentiment dynamics + engagement-negativity link.
   - Predictief: 83% sentiment classification accuracy, 86% toxicity accuracy.
   - Correlationeel: +103.6 bp WTI Δμ tussen Iran- en controle-posts.
   - Causaliteit: data ondersteunt geen directe causale invloed; common-cause
     interpretatie meest waarschijnlijk.
   - Per aandeel (nb14): waar de index niets toont, vertonen losse genoemde bedrijven
     wél een (overwegend negatieve) reactie — Tesla mediaan −83 bp (Mann-Whitney
     p=0,057), DJT CAR_3d −158 bp (p=0,037); geen overleeft Bonferroni, maar de
     magnitude ligt een ordegrootte boven het indexniveau.
4. **Wat we hebben opgeleverd**: een herbruikbare classification + analyse-pipeline,
   inclusief een bedrijf→ticker-extractiemodule en per-aandeel event-study.
5. **Toekomstig werk**: tick-level data, news-wire cross-validatie, multi-account
   uitbreiding, real-time dashboard productie, en koppeling van het per-aandeel-effect
   aan toon (nb08) en news-timing (nb13) om causaliteit aan te scherpen en power te
   verhogen.

---

## 7. Referenties

[Volledige BibTeX entries staan in `reports/literatuurscan.md`. Hieronder de relevante
verwijzingen in APA-stijl.]

Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information
content of internet stock message boards. *The Journal of Finance, 59*(3), 1259–1294.
https://doi.org/10.1111/j.1540-6261.2004.00662.x

Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language
models. *arXiv preprint* arXiv:1908.10063.

Bollen, J., Mao, H., & Zeng, X.-J. (2011). Twitter mood predicts the stock market.
*Journal of Computational Science, 2*(1), 1–8. https://doi.org/10.1016/j.jocs.2010.12.007

Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32.
https://doi.org/10.1023/A:1010933404324

Jain, S., & Wallace, B. C. (2019). Attention is not explanation. In *Proceedings of
the 2019 Conference of the North American Chapter of the Association for Computational
Linguistics* (pp. 3543–3556).

Ke, Z., Kelly, B., & Xiu, D. (2023). Predicting returns with text data. *Journal of
Finance, 78*(5), 3551–3593. https://doi.org/10.1111/jofi.13232

Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual
analysis, dictionaries, and 10-K filings. *The Journal of Finance, 66*(1), 35–65.
https://doi.org/10.1111/j.1540-6261.2010.01625.x

Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A
survey. *Journal of Accounting Research, 54*(4), 1187–1230.
https://doi.org/10.1111/1475-679X.12123

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model
predictions. *Advances in Neural Information Processing Systems, 30*, 4765–4774.

Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in
the stock market. *The Journal of Finance, 62*(3), 1139–1168.
https://doi.org/10.1111/j.1540-6261.2007.01232.x

[TODO: voeg eventueel extra referenties toe als je tijdens schrijven nieuwe bronnen
gebruikt. Bijvoorbeeld voor de Iran-conflict context, of voor de specifieke geopolitieke
gebeurtenissen rond de Strait of Hormuz blockade.]

---

## 8. Bijlagen

### Bijlage A — Code repository

De volledige code voor dit onderzoek is beschikbaar op GitHub:
**https://github.com/QuintenFritz/truthsocial-marketimpact**

Belangrijkste mappen:
- `notebooks/` — 14 Jupyter notebooks, één per analyse-fase (01 t/m 14).
- `src/data/` — Python modules voor data-acquisitie en preprocessing.
- `src/features/company_mentions.py` — bedrijf→ticker-mapping voor de per-aandeel event-study (§4.6).
- `models/sentiment/` en `models/toxicity/` — getrainde modellen (joblib).
- `data/raw/` — ruwe data sources (niet gecommit; download instructions in README).

Tag `v1.0-market-prediction` op GitHub markeert een snapshot van de initiële
market-prediction analyse die uiteindelijk niet de hoofdrichting werd.

### Bijlage B — Reproduceerbaarheid

Om alle resultaten te reproduceren:

```bash
git clone https://github.com/QuintenFritz/truthsocial-marketimpact.git
cd truthsocial-marketimpact
conda create -n truthsocial python=3.11 -y
conda activate truthsocial
pip install -e ".[dev,dashboard,nlp]"

# Plaats Kaggle CSV in data/raw/trump_truth_archive.csv
# Run live scraper voor recente posts:
python -m src.data.scrape_trumpstruth_rss --start 2026-02-28

# Run notebooks 01 t/m 14 in volgorde
jupyter lab notebooks/
```

### Bijlage C — Extra figuren

[TODO: zet hier alle figuren die niet in het hoofd-Results hoofdstuk zijn opgenomen,
genummerd als C1, C2, etc.]

### Bijlage D — Tabellen met volledige resultaten

[TODO: hier de volledige Granger-tabellen, alle classification-reports, etc.]

---

*Versie 0.1 — gegenereerd op 18 mei 2026. Volgende stappen: hoofdstukken 1-5 invullen,
figuren genereren en invoegen, samenvatting schrijven, eind-review en spelling-check.*
