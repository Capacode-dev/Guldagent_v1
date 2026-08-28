# Guldagent v2 MVP

Guldagent v2 vurderer den sandsynlige retning for guld som `OP`, `NEUTRAL`
eller `NED`. Talmodellen beregner signalet; LLM'en forklarer resultatet uden
at kunne ændre score eller retning.

## Hvad MVP'en indeholder

- fem automatiske makroserier fra FRED
- månedligt historisk guldgennemsnit fra World Bank via FreeGoldAPI
- normalisering til sammenlignelige signaler mellem `-1` og `1`
- vægtet og forklarlig signalmodel
- backtest efter 1, 3 og 12 måneder
- valgfri LLM-forklaring via OpenAI Responses API
- JSON- og Markdown-rapport
- dry-run uden LLM og 22 automatiske tests

## 1. Åbn projektet i VS Code

Åbn en terminal i projektmappen og opret et virtuelt miljø.

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Installer pakkerne:

```bash
python -m pip install -r requirements.txt
```

## 2. Opret lokal konfiguration

Kopiér `.env.example` til `.env`. Minimum for data-pipelinen er:

```env
FRED_API_KEY=din_fred_noegle
```

LLM-forklaringen er valgfri og kræver separat OpenAI API-adgang:

```env
OPENAI_API_KEY=din_openai_noegle
OPENAI_MODEL=gpt-5.4-mini
```

ChatGPT Plus og OpenAI API-fakturering er separate. Del aldrig nøgler i chat,
og commit aldrig `.env`.

## 3. Kør først alle tests

```bash
python -m unittest -v
```

## 4. Kør hele MVP'en

Sikker første kørsel uden LLM-omkostning:

```bash
python -m guldagent_v2.run_mvp --start 2010-01-01 --no-llm
```

Med LLM-forklaring, når `OPENAI_API_KEY` er sat:

```bash
python -m guldagent_v2.run_mvp --start 2010-01-01
```

## Output

Pipelinen opretter blandt andet:

| Fil | Indhold |
|---|---|
| `data/processed/macro_mvp.csv` | Samlede rå FRED-data |
| `data/processed/macro_signals.csv` | Normaliserede signaler |
| `data/input/gold_history.csv` | Historiske guldpriser |
| `data/processed/backtest_results.csv` | Resultat for hvert historisk signal |
| `data/processed/latest_report.json` | Maskinlæsbar rapport |
| `data/processed/latest_report.md` | Læsbar rapport |

CSV- og rapportfilerne genereres lokalt og ignoreres af Git.

## Sådan skal resultatet læses

- `OP`: vægtet score er mindst `+0.20`
- `NED`: vægtet score er højst `-0.20`
- `NEUTRAL`: score ligger mellem grænserne
- signalstyrken er den absolutte score; den er ikke en statistisk sandsynlighed
- MVP-dækningen skal være 5/5, mens fuld modeldækning foreløbig er 5/20
- backtesten er en teknisk validering, ikke et løfte om fremtidigt afkast

## Kendte MVP-begrænsninger

- kun fem af de planlagte cirka 20 variable hentes automatisk
- den 2-årige amerikanske rente er en proxy for Fed-forventninger
- hovedpipelinen bruger World Banks månedlige guldgennemsnit fra 1960 til
  2024 som historisk reference; fællesperioden bestemmes af makroserierne
- månedsprisen er en afsluttet periodes gennemsnit og ikke Guldagent v1's
  aktuelle GoldAPI-spotpris
- månedsbacktesten bruger månedens sidste komplette makrosignal og måler
  udviklingen i de efterfølgende 1, 3 og 12 månedsgennemsnit
- FRED-guldserien er udfaset, Stooq kræver browserkontrol, og Yahoo
  ratebegrænser automatiske kald; de bruges derfor ikke i hovedpipelinen
- FreeGoldAPI-klienten er bevaret som et separat eksperiment, men dens
  daglige `yahoo_finance`-del dækker ikke en lang markedscyklus
- historisk London-fix og GoldAPI-spotprisen i v1 er forskellige dataserier
- vægte og grænser er hypoteser, indtil backtesten har tilstrækkelige observationer
- 3- og 12-måneders backtestsignaler overlapper og er derfor ikke fuldt
  uafhængige observationer
- træfsikkerheden sammenlignes med altid-OP-baseline på præcis de samme
  datoer, hvor modellen afgiver OP eller NED
- LLM'en forklarer kun modellen og må ikke skabe eller ændre tal

Guldagent v2 er et analyse- og læringsprojekt, ikke personlig
investeringsrådgivning.
