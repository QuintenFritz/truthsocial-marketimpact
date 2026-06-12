# Voortgang & Pistes — Trump's Truth Social & Financiële Markten

**Laatste update:** 11 juni 2026  
**Status:** Kernanalyse afgerond, Prioriteit-1 vervolgpiste (individuele aandelen) in uitvoering

---

## ✅ Wat is afgerond

### Data & infrastructuur
- [x] Kaggle-archief geladen en verwerkt (26.819 posts, feb 2022 – apr 2026)
- [x] Live RSS-scraper gebouwd voor posts vanaf feb 2026 (Iran-periode)
- [x] Dagelijkse marktdata via yfinance (SPX, WTI, DXY, VIX)
- [x] Intraday 1-minuutdata via Twelve Data API (SPY + XLE, 534 API-calls)
- [x] GDELT news-timing pipeline (128 posts, 14 nieuwsbronnen)

### Modellering & analyse
- [x] **nb01** Data collection & kwaliteitschecks
- [x] **nb02** EDA — marktdata en posts (met event-markeringen op alle tijdlijn-grafieken)
- [x] **nb03** Alignment & abnormal returns berekenen
- [x] **nb04** Feature engineering (TF-IDF)
- [x] **nb05** Random Forest modeling
- [x] **nb06** Interpretability (SHAP + permutation importance)
- [x] **nb07** Sentiment exploratie over tijd
- [x] **nb08** Sentiment-classifier (L1-Logistic: 83% acc, F1 0.76)
- [x] **nb09** Toxicity-classifier (86% acc, AUC 0.91)
- [x] **nb10** Iran event study dagelijks
- [x] **nb11** Liberation Day tariff event study dagelijks
- [x] **nb12** Intraday CAR-analyse (minuutdata)
- [x] **nb13** GDELT news-timing analyse

### Rapporten & documentatie
- [x] `reports/rapport_normaal.md` — volledig onderzoeksverslag
- [x] `reports/rapport_eenvoudig.md` — toegankelijke samenvatting
- [x] `reports/notebook_gids.docx` — per-notebook uitleg met grafieken en resultaten
- [x] `README.md` — projectdocumentatie voor GitHub
- [x] `.gitignore` bijgewerkt (figures + kleine databestanden worden gecommit)

---

## 📊 Kernresultaten

| Analyse | Resultaat |
|---|---|
| ML-model marktrichting voorspellen | ❌ Niet beter dan baseline |
| Bulk event-study Iran (dagelijks) | ❌ Geen significant effect (p > 0.05) |
| Bulk event-study tariffs (dagelijks) | ❌ Geen significant effect (p > 0.05) |
| Granger-causaliteit | ❌ Geen causaliteit in beide richtingen |
| Volume-effect tariff-posts | ✅ **Ratio = 1.50** (sterkste significante bevinding) |
| Intraday CAR Iran/XLE | ⚠️ -238 bp na 120 min, geen mean reversion (kleine n) |
| GDELT news-timing | ✅ **100% reactief**, mediaan lag ~3 uur |
| Marktmanipulatie-hypothese | ❌ Geen bewijs |

**Hoofdconclusie:** Trump is een nieuwsreageerder, niet een marktbeweger. De correlaties reflecteren een gemeenschappelijke oorzaak (onderliggend nieuws), geen directe causaliteit.

---

## 🔭 Mogelijke vervolgpistes

### 🥇 Prioriteit 1 — Individuele aandelen die Trump noemt
**Kans op significant resultaat: hoog**

Brede indices (SPY, SPX) middelen individuele effecten weg. Als Trump expliciet "Boeing", "Apple" of "ExxonMobil" noemt, verwacht je een groter effect op die individuele aandelen dan op de brede markt. Dit is een specifiekere hypothese en methodologisch sterker.

**Aanpak:**
1. spaCy NER op posts → extraheer bedrijfsnamen (PRODUCT, ORG entities)
2. Match bedrijfsnamen aan ticker-symbolen (handmatige mapping of lookup API)
3. Download koersen per bedrijf via yfinance
4. Zelfde event-study methodiek als nb10/nb11 maar per bedrijf
5. Vergelijk: individuele stock return vs. sector-ETF return (isoleer bedrijfsspecifiek effect)

**Wat nodig is:** ~1-2 dagen werk, geen nieuwe API-kosten  
**Status:** ✅ Afgerond — notebook 14 gedraaid, bevindingen geschreven

**Resultaat:** anders dan op index-niveau (nb10/nb11) is er op bedrijfsniveau wél een richting zichtbaar. Inferentie via **bootstrap-95%-CI** (in-cursus resampling, geen Bonferroni nodig). Twee effecten sluiten 0 uit, beide negatief: **DJT CAR_3d −158 bp, CI [−309,−8] (n=217)** en **TSLA AR_1d −115 bp, CI [−228,−7] (n=52)**. AMZN is het enige positieve effect (+51 bp, CI [−12,116] → omvat 0). De effectgroottes (−115 tot −176 bp) zijn een ordegrootte groter dan op SPX — de hypothese dat indices individuele effecten wegmiddelen wordt ondersteund.

**TSLA outlier-check (sectie 8b/8c) — fragiel:** het volle-sample mean-effect sluit 0 uit (−115 bp, CI [−228,−7]), maar leunt op de staart: drop 5 juni 2025 (Trump-Musk-breuk, AR −14,3%) → CI [−189,11] omvat 0. Ook het mediaan-verschil sluit 0 niet uit (−79 bp, CI [−147,47]). Richting negatief (62% mention-dagen), maar statistisch fragiel → suggestief, niet bewijzend.

**Methodewissel (i.v.m. cursus-bestek):** alle out-of-scope toetsen project-breed vervangen door bootstrap-CI's (`src/evaluation/bootstrap.py`, sluit aan bij cursusmodule 04 "Resampling"). Omgezet: nb03 (AR post-dag vs geen-post), nb07 (engagement/negativity-bias, mediaan), nb10/nb11 (Welch event-study + volume + price-timing), nb12 (one-sample CAR + volume-ratio + escalatie/de-escalatie), nb13 (GDELT reactief vs geen_nieuws), nb14 (per-aandeel). Geen `ttest_ind`/`ttest_1samp`/`mannwhitneyu` meer in de notebooks; lineaire regressie/correlatie (linregress in nb13) blijft, want dat valt binnen de cursus. Reëel herberekend (data lokaal): nb14, nb03 (alle CI's omvatten 0), engagement (mediaan-verschil +1.608 likes, CI [1.056, 2.042] → sluit 0 uit). nb10/nb11/nb12/nb13 lokaal opnieuw draaien om hun exacte CI-cijfers in de reports te vullen.

**Volgende stap (optioneel):** koppel toon/sentiment (nb08) + GDELT news-timing (nb13) per mention-dag → grotere daling bij negatief-getoonde en niet-reactieve posts? Poolt bedrijven op toon → hogere power.

---

## 🔁 Data-herziening juni 2026: scraper + intraday op lokale parquets

- **posts_live opnieuw gescrapet** met kleinere chunks (`--chunk-days 3`): RSS-feed capt op ~100 items/request, dus maand-chunks kapten af. Nu **2.161 posts (28 feb → 12 jun), 271 Iran-matches** (was 100 posts / 2 Iran). Scraper kreeg een `--chunk-days` optie.
- **Intraday-analyses (nb10/nb11) gevoed uit lokale Twelve Data 1-min parquets** i.p.v. yfinance-uurdata (die maar ~60 dagen terug gaat). XLE = WTI-proxy op intraday (gratis tier, gedocumenteerde beperking).
- **Herberekende Iran/tariff-bevindingen (bootstrap-CI, volledige data):**
  - Tariff SPY volume-z: **+0,30σ [+0,11, +0,49]** ✅
  - Iran XLE volume-z (WTI-proxy): **+0,23σ [+0,02, +0,44]** ✅ | Iran SPY volume-z: +0,13σ [−0,05, +0,32] ❌
  - Iran minuut-CAR SPY: **−33,2 bp/120m [−57,7, −8,5]** ✅ | XLE: −73,9 bp [−205, +24] ❌ (te ruisig)
  - Iran uur-event-study (Iran vs controle): geen significant verschil (SPY/XLE CI's omvatten 0)
- **Kernverhaal bijgesteld (eerlijker):** het oude "XLE −238 bp / −56,9 bp significant" houdt op de volledige data + bootstrap géén stand. Wat robuust is: een **significante negatieve brede-markt-drift (SPY)** na Iran-posts + **verhoogd energiesector-volume**. Reports (scriptie, scriptie_full, rapport_normaal, rapport_eenvoudig) hierop bijgewerkt.

**Wat al klaar is:**
- `src/features/company_mentions.py`: curated bedrijf→ticker→sector-ETF mapping (24 bedrijven) + word-boundary extractie. Bewust geen kale NER (interpreteerbaar, hoge precisie); spaCy beschikbaar als optionele recall-uitbreiding (`discover_org_candidates`).
- `notebooks/14_individual_stocks_event_study.ipynb`: volledige event-study per aandeel met **market-model abnormal returns** (regressie op SPY) i.p.v. simpele baseline → isoleert bedrijfsspecifiek effect. Welch t-toets mention- vs controle-dagen + Bonferroni.
- Extractie al gedraaid op alle 26.819 posts: **1.273 posts** noemen ≥1 bedrijf. Bruikbare kandidaten met genoeg volume: Google (173), Meta (106), Tesla (94), Amazon (66), Apple (49). DJT (573) alleen vanaf 2024-03-26, TWTR (206) alleen tot 2022-10-27 (verhandelbaarheids-filter zit in de notebook).
- Kernlogica offline gevalideerd op synthetische data (effect-recovery + weekend→handelsdag-alignment OK).

**Nog te doen (lokaal, yfinance vereist internettoegang):** notebook draaien → koersen downloaden, resultaten + plot genereren, sectie 9 invullen met echte bevindingen.

---

### 🥈 Prioriteit 2 — VIX als doelvariabele (onzekerheidseffect)
**Kans op significant resultaat: gemiddeld-hoog**

Hypothese wijzigen: niet "posts voorspellen returns" maar "posts verhogen marktangst (VIX)". Dit is een andere en misschien verdedigbaardere claim — Trump's communicatie creëert onzekerheid, ook als de gemiddelde koersbeweging nul is.

**Aanpak:**
1. VIX data is al beschikbaar in market.parquet
2. Bereken VIX-change t+1d en t+5d na posts (net als huidige AR-berekening)
3. Test: zijn VIX-stijgingen significant groter na escalatie-posts vs. controle?
4. Split op escalatie vs. de-escalatie (hogere kans op significant resultaat dan bij returns)

**Wat nodig is:** ~halve dag, alle data al beschikbaar  
**Status:** ⬜ Niet gestart

---

### 🥉 Prioriteit 3 — Crypto (Bitcoin/Ethereum)
**Kans op significant resultaat: gemiddeld**

Crypto handelt 24/7 — het "posts buiten beurstijden" probleem verdwijnt. Bitcoin is gevoelig voor retail sentiment en Trumps achterban is oververtegenwoordigd in crypto. Trump heeft zelf ook uitspraken gedaan over Bitcoin en crypto-wetgeving.

**Aanpak:**
1. Download BTC/ETH minuutdata via CoinGecko of Binance API (gratis)
2. Zelfde intraday CAR-methodiek als nb12
3. Filter op posts die crypto/bitcoin expliciet noemen + algemene tariff/Iran posts
4. Vergelijk crypto-reactie vs. aandelenmarkt-reactie

**Wat nodig is:** ~1 dag, gratis API  
**Status:** ⬜ Niet gestart

---

### Prioriteit 4 — Lagsnelheid als moderator (binnen GDELT)
**Kans op significant resultaat: onzeker**

Binnen de reactieve posts (n=90): posts waarbij Trump snel reageerde (< 60 min na nieuws) zijn mogelijk meer originele informatie of signaleren dat hij goed geïnformeerd is. Test of deze subgroep een grotere marktimpact heeft dan trage-reactie posts.

**Aanpak:**
1. Data al beschikbaar in gdelt_news_timing.parquet
2. Split: lag < 60 min (n=?) vs. lag > 180 min (n=?)
3. Vergelijk SPX/WTI return t+1d tussen de twee groepen
4. Interpretatie: versterkt of weerlegt de common-cause verklaring

**Wat nodig is:** ~2 uur, alle data al beschikbaar  
**Status:** ⬜ Niet gestart

---

### Prioriteit 5 — Na-sluitingsuren posts → opening gap
**Kans op significant resultaat: gemiddeld**

Posts na 21:00 UTC (na beurssluiting) kunnen niet direct verwerkt worden. De markt kan pas reageren bij opening de volgende dag. Test of er een opening gap ontstaat in de verwachte richting, en of deze gap groter is dan op dagen zonder post.

**Aanpak:**
1. Filter posts op tijdstip: 21:00 UTC - 13:30 UTC (buiten markturen)
2. Bereken opening gap = open(t+1d) / close(t) - 1
3. Vergelijk gap-grootte en -richting voor post-days vs. no-post-days
4. Combineer met sentiment-score voor richting

**Wat nodig is:** ~halve dag, yfinance open/close data al beschikbaar  
**Status:** ⬜ Niet gestart

---

## 📝 Open methodologische vragen

- [ ] **Twee databronnen**: Kaggle (40 kolommen, tot apr 2026) en RSS (8 kolommen, feb 2026+) hebben overlappende periode (feb–apr 2026). Dubbelchecken dat Iran-posts niet dubbel geteld worden.
- [ ] **Toon-classifier**: keyword-gebaseerde escalatie/de-escalatie split werkt niet (p=0.733). Een getrainde toon-classifier op tariff-specifieke inhoud zou de intraday split kunnen verbeteren.
- [ ] **XLE als WTI-proxy**: bij betaalde Twelve Data tier direct WTI-futures (CL=F) gebruiken.
- [ ] **Kleine steekproef Iran**: 37 posts, waarvan slechts ~15 tijdens markturen. Meer posts scrapen (of wachten tot conflict verder evolueert) voor robuustere intraday resultaten.

---

## 🔧 Technische TODO's

- [ ] Alle notebooks draaien met outputs en committen naar GitHub
- [ ] Kaggle dataset-link toevoegen in README.md (regel 48: `[DATASET-LINK-HIER]`)
- [ ] requirements.txt aanmaken in de root van de repo

---

*Dit bestand bijhouden naarmate het onderzoek vordert.*
