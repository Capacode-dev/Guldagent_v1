# Guldagent v1

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![Scraper](ca://s?q=Hvad_er_scraper_badge)
![Mail](ca://s?q=Hvad_er_mail_badge)
![Formatter](ca://s?q=Hvad_er_formatter_badge)
![Automation](ca://s?q=Hvad_er_cron_badge)

Automatiseret agent der henter guldpris, beregner karatpriser og sender dem som mail.

---

## 1. Klon projektet

git clone https://github.com/Capacode-dev/Guldagent_v1.git
cd Guldagent_v1

---

## 2. Opret og aktiver virtual environment

python3 -m venv venv312
source venv312/bin/activate

Windows:

python -m venv venv312
venv312\Scripts\activate

---

## 3. Installer afhængigheder

pip install -r requirements.txt

---

## 4. Opret .env fil

GOLD_API_KEY=<goldapi-nøgle>
BRIDGE_USERNAME=<bridge-email>
BRIDGE_PASSWORD=<bridge-password>
HEMMELIG_MODTAGER=<modtager-mail>
HEMMELIG_FAKTOR_ARBEJDE=2.5

---

## 5. Kør agenten

python agent_v1.py

Agenten gør:
- henter pris
- validerer pris
- beregner karatpriser
- laver HTML-layout
- sender mail
- logger pris

Test hele beregningen uden live API og uden at sende mail:

```bash
python agent_v1.py --dry-run --test-pris 750
```

Kontrollér at miljøvariablerne findes uden at vise deres indhold:

```bash
python check_env.py
```

---

## 6. Push til Git

git add .
git commit -m "Tilføjet README og HTML-layout"
git push

---

## Guldagent v2 – første signalmodel

Den komplette MVP-vejledning findes i [README_V2.md](README_V2.md).

V2 kombinerer 20 makro- og markedsvariable til en forklarlig retning:
`OP`, `NEUTRAL` eller `NED`. Hver variabel leverer senere et normaliseret
signal mellem `-1` og `1`. Modellen viser både samlet score, datadækning og
de vigtigste positive og negative drivere.

Kør den foreløbige demo:

```bash
python -m guldagent_v2.demo
```

### Byg makrodatasættet

Opret en gratis FRED API-nøgle, og sæt `FRED_API_KEY` i din lokale `.env`.
Byg derefter datasættet med:

```bash
python -m guldagent_v2.build_dataset --start 2020-01-01
```

Kommandoen gemmer fem rå serier i `data/raw/` og det samlede datasæt i
`data/processed/macro_mvp.csv`:

- amerikansk 10-årig realrente (`DFII10`)
- bredt dollarindeks (`DTWEXBGS`)
- 10-årig inflationsforventning (`T10YIE`)
- VIX (`VIXCLS`)
- amerikansk 2-årig rente (`DGS2`) som foreløbig Fed-proxy

De genererede CSV-filer ignoreres af Git, så repoet ikke vokser for hver
daglig opdatering.

Normalisér rådata til sammenlignelige signaler mellem `-1` og `1`:

```bash
python -m guldagent_v2.build_signals
```

Beregn retningen fra den seneste række med signaler:

```bash
python -m guldagent_v2.analyze_latest
```

Normaliseringen bruger en 20-observations ændring og seriens bagudskuende
60-observations volatilitet. Den bruger aldrig observationer efter den dato,
der beregnes for.

### Backtest mod guldprisen

Hent den daglige del af FreeGoldAPI-datasættet:

```bash
python -m guldagent_v2.build_gold_history --start 2025-01-01
```

Der kræves ingen API-nøgle. Klienten beholder kun rækker med kilden
`yahoo_finance`, fordi ældre FreeGoldAPI-data har månedlig eller årlig
frekvens og derfor ikke kan bruges som handelsdage. Hvis seneste observation
er mere end syv dage gammel, vises en advarsel.

Filen gemmes i `data/input/gold_history.csv` med formatet:

```csv
date,gold_price
2026-01-02,2800.50
2026-01-05,2821.10
```

FreeGoldAPI-prisen er USD pr. troy ounce. Kør derefter:

```bash
python -m guldagent_v2.run_backtest
```

Backtesten måler, om `OP` og `NED` rammer den efterfølgende bevægelse efter
5, 20 og 60 guldobservationer. Det er normalt handelsdage, ikke kalenderdage.
Detaljerne gemmes i `data/processed/backtest_results.csv`.

Kør alle tests:

```bash
python -m unittest -v
```

FreeGoldAPI bruges til den foreløbige historiske MVP-test, mens GoldAPI fortsat
bruges til den aktuelle pris. LLM-laget tilføjes først, når talmodellen kan
forklare og teste sin egen score.
