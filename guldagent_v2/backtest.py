import csv
import math
from collections import Counter
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from guldagent_v2.signal_model import beregn_signal


@dataclass(frozen=True)
class BacktestSummary:
    antal_signaler: int
    traefsikkerhed: dict[int, float]
    gennemsnitligt_afkast: dict[int, float]
    altid_op_baseline: dict[int, float]
    vurderbare_signaler: dict[int, int]
    retningssignaler: dict[int, int]
    konfidensinterval_95: dict[int, tuple[float, float]]
    baseline_konfidensinterval_95: dict[int, tuple[float, float]]
    traefsikkerhed_pr_retning: dict[int, dict[str, float]]
    konfidensinterval_pr_retning: dict[int, dict[str, tuple[float, float]]]
    antal_pr_retning: dict[int, dict[str, int]]
    signalfordeling: dict[str, int]
    horisont_enhed: str
    delperioder: dict[str, dict] = field(default_factory=dict)
    primaer_horisont: int | None = None


def koer_backtest(
    signal_path,
    gold_path,
    output_path=None,
    horisonter=(5, 20, 60),
    required_features=(),
):
    """Sammenlign historiske signaler med senere guldafkast."""
    signal_rows = _laes_csv(signal_path)
    gold_rows = _laes_guld(gold_path)
    gold_index = {dato: index for index, (dato, _) in enumerate(gold_rows)}
    output_rows = []

    for row in signal_rows:
        dato = row["date"]
        if dato not in gold_index:
            continue

        signaler = {
            key: float(value)
            for key, value in row.items()
            if key != "date" and value not in (None, "")
        }
        if not signaler or not all(feature in signaler for feature in required_features):
            continue

        resultat = beregn_signal(signaler)
        start_index = gold_index[dato]
        start_price = gold_rows[start_index][1]
        output_row = {
            "date": dato,
            "score": resultat.score,
            "direction": resultat.retning,
            "coverage": len(signaler),
        }

        for horisont in horisonter:
            target_index = start_index + horisont
            kolonne = f"return_{horisont}d"
            if target_index >= len(gold_rows):
                output_row[kolonne] = ""
            else:
                target_price = gold_rows[target_index][1]
                output_row[kolonne] = round((target_price / start_price - 1) * 100, 4)
        output_rows.append(output_row)

    if output_path:
        _skriv_resultater(output_path, output_rows, horisonter)

    return output_rows, opsummer_backtest(output_rows, horisonter)


def koer_maanedsbacktest(
    signal_path,
    gold_path,
    output_path=None,
    horisonter=(1, 3, 12),
    required_features=(),
    test_startdato=None,
):
    """Test månedsguld mod månedens sidste komplette makrosignal."""
    signal_rows = _laes_csv(signal_path)
    gold_rows = _laes_guld(gold_path)
    seneste_signal_i_maaned = {}

    for row in signal_rows:
        signaler = {
            key: float(value)
            for key, value in row.items()
            if key != "date" and value not in (None, "")
        }
        if not signaler or not all(feature in signaler for feature in required_features):
            continue
        seneste_signal_i_maaned[row["date"][:7]] = (
            row["date"],
            beregn_signal(signaler),
            len(signaler),
        )

    output_rows = []
    for start_index, (gold_date, start_price) in enumerate(gold_rows):
        signal = seneste_signal_i_maaned.get(gold_date[:7])
        if not signal:
            continue
        signal_date, resultat, coverage = signal
        output_row = {
            "date": signal_date,
            "gold_month": gold_date,
            "score": resultat.score,
            "direction": resultat.retning,
            "coverage": coverage,
        }
        for horisont in horisonter:
            target_index = start_index + horisont
            kolonne = f"return_{horisont}m"
            if target_index >= len(gold_rows):
                output_row[kolonne] = ""
            else:
                target_price = gold_rows[target_index][1]
                output_row[kolonne] = round((target_price / start_price - 1) * 100, 4)
        output_rows.append(output_row)

    if output_path:
        _skriv_resultater(
            output_path,
            output_rows,
            horisonter,
            suffix="m",
            ekstra_felter=("gold_month",),
        )

    summary = opsummer_backtest(
        output_rows,
        horisonter,
        suffix="m",
        horisont_enhed="måneder",
    )
    summary = replace(summary, primaer_horisont=1)
    if test_startdato:
        reference_rows = [
            row for row in output_rows
            if row["gold_month"] < test_startdato
        ]
        reference_rows = _afgraens_fremtidige_targets(
            reference_rows,
            horisonter,
            test_startdato,
        )
        test_rows = [
            row for row in output_rows
            if row["gold_month"] >= test_startdato
        ]
        delperioder = {
            "reference": _opsummer_delperiode(
                "Referenceperiode",
                reference_rows,
                horisonter,
            ),
            "senere_test": _opsummer_delperiode(
                "Senere testperiode",
                test_rows,
                horisonter,
            ),
        }
        summary = replace(summary, delperioder=delperioder)

    return output_rows, summary


def opsummer_backtest(
    rows,
    horisonter=(5, 20, 60),
    suffix="d",
    horisont_enhed="guldobservationer",
):
    traefsikkerhed = {}
    gennemsnitligt_afkast = {}
    altid_op_baseline = {}
    vurderbare_signaler = {}
    retningssignaler_antal = {}
    konfidensinterval_95 = {}
    baseline_konfidensinterval_95 = {}
    traefsikkerhed_pr_retning = {}
    konfidensinterval_pr_retning = {}
    antal_pr_retning = {}

    for horisont in horisonter:
        kolonne = f"return_{horisont}{suffix}"
        vurderbare = [row for row in rows if row.get(kolonne) not in (None, "")]
        retningssignaler = [row for row in vurderbare if row["direction"] in ("OP", "NED")]
        korrekte = [
            row for row in retningssignaler
            if (row["direction"] == "OP" and row[kolonne] > 0)
            or (row["direction"] == "NED" and row[kolonne] < 0)
        ]
        traefsikkerhed[horisont] = round(len(korrekte) / len(retningssignaler) * 100, 2) if retningssignaler else 0.0
        gennemsnitligt_afkast[horisont] = (
            round(sum(row[kolonne] for row in vurderbare) / len(vurderbare), 4)
            if vurderbare else 0.0
        )
        # Baseline skal måles på præcis de datoer, hvor modellen afgav
        # et retningssignal. Ellers sammenlignes to forskellige stikprøver.
        altid_op_baseline[horisont] = (
            round(sum(row[kolonne] > 0 for row in retningssignaler) / len(retningssignaler) * 100, 2)
            if retningssignaler else 0.0
        )
        konfidensinterval_95[horisont] = _wilson_interval_95(
            len(korrekte),
            len(retningssignaler),
        )
        baseline_korrekte = sum(row[kolonne] > 0 for row in retningssignaler)
        baseline_konfidensinterval_95[horisont] = _wilson_interval_95(
            baseline_korrekte,
            len(retningssignaler),
        )
        vurderbare_signaler[horisont] = len(vurderbare)
        retningssignaler_antal[horisont] = len(retningssignaler)
        traefsikkerhed_pr_retning[horisont] = {}
        konfidensinterval_pr_retning[horisont] = {}
        antal_pr_retning[horisont] = {}
        for retning in ("OP", "NED"):
            valgte = [row for row in retningssignaler if row["direction"] == retning]
            retning_korrekte = [
                row for row in valgte
                if (retning == "OP" and row[kolonne] > 0)
                or (retning == "NED" and row[kolonne] < 0)
            ]
            traefsikkerhed_pr_retning[horisont][retning] = (
                round(len(retning_korrekte) / len(valgte) * 100, 2)
                if valgte else 0.0
            )
            konfidensinterval_pr_retning[horisont][retning] = _wilson_interval_95(
                len(retning_korrekte),
                len(valgte),
            )
            antal_pr_retning[horisont][retning] = len(valgte)

    signalfordeling = dict(Counter(row["direction"] for row in rows))
    return BacktestSummary(
        antal_signaler=len(rows),
        traefsikkerhed=traefsikkerhed,
        gennemsnitligt_afkast=gennemsnitligt_afkast,
        altid_op_baseline=altid_op_baseline,
        vurderbare_signaler=vurderbare_signaler,
        retningssignaler=retningssignaler_antal,
        konfidensinterval_95=konfidensinterval_95,
        baseline_konfidensinterval_95=baseline_konfidensinterval_95,
        traefsikkerhed_pr_retning=traefsikkerhed_pr_retning,
        konfidensinterval_pr_retning=konfidensinterval_pr_retning,
        antal_pr_retning=antal_pr_retning,
        signalfordeling=signalfordeling,
        horisont_enhed=horisont_enhed,
    )


def _opsummer_delperiode(navn, rows, horisonter):
    summary = opsummer_backtest(
        rows,
        horisonter,
        suffix="m",
        horisont_enhed="måneder",
    )
    data = asdict(summary)
    data.pop("delperioder")
    data["navn"] = navn
    data["periode"] = (
        f"{rows[0]['gold_month'][:7]} til {rows[-1]['gold_month'][:7]}"
        if rows else "ingen observationer"
    )
    return data


def _wilson_interval_95(antal_korrekte, antal):
    if antal == 0:
        return (0.0, 0.0)
    z = 1.96
    andel = antal_korrekte / antal
    naevner = 1 + z**2 / antal
    centrum = (andel + z**2 / (2 * antal)) / naevner
    margen = (
        z
        * math.sqrt(
            andel * (1 - andel) / antal
            + z**2 / (4 * antal**2)
        )
        / naevner
    )
    return (
        round(max(0.0, centrum - margen) * 100, 2),
        round(min(1.0, centrum + margen) * 100, 2),
    )


def _afgraens_fremtidige_targets(rows, horisonter, slut_foer):
    resultat = []
    for original in rows:
        row = dict(original)
        for horisont in horisonter:
            target_maaned = _tilfoej_maaneder(row["gold_month"], horisont)
            if target_maaned >= slut_foer:
                row[f"return_{horisont}m"] = ""
        resultat.append(row)
    return resultat


def _tilfoej_maaneder(dato, antal):
    aar, maaned, _ = (int(dato_del) for dato_del in dato.split("-"))
    nulbaseret = aar * 12 + maaned - 1 + antal
    nyt_aar, ny_maaned = divmod(nulbaseret, 12)
    return f"{nyt_aar:04d}-{ny_maaned + 1:02d}-01"


def _laes_csv(path):
    with Path(path).open(encoding="utf-8") as fil:
        return list(csv.DictReader(fil))


def _laes_guld(path):
    rows = _laes_csv(path)
    resultat = []
    for row in rows:
        if not row.get("date") or not row.get("gold_price"):
            continue
        resultat.append((row["date"], float(row["gold_price"])))
    return sorted(resultat)


def _skriv_resultater(path, rows, horisonter, suffix="d", ekstra_felter=()):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "date",
        *ekstra_felter,
        "score",
        "direction",
        "coverage",
        *[f"return_{h}{suffix}" for h in horisonter],
    ]
    with path.open("w", newline="", encoding="utf-8") as fil:
        writer = csv.DictWriter(fil, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
