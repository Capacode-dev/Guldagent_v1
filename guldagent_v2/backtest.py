import csv
from collections import Counter
from dataclasses import dataclass
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
    signalfordeling: dict[str, int]


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


def opsummer_backtest(rows, horisonter=(5, 20, 60)):
    traefsikkerhed = {}
    gennemsnitligt_afkast = {}
    altid_op_baseline = {}
    vurderbare_signaler = {}
    retningssignaler_antal = {}

    for horisont in horisonter:
        kolonne = f"return_{horisont}d"
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
        vurderbare_signaler[horisont] = len(vurderbare)
        retningssignaler_antal[horisont] = len(retningssignaler)

    signalfordeling = dict(Counter(row["direction"] for row in rows))
    return BacktestSummary(
        len(rows),
        traefsikkerhed,
        gennemsnitligt_afkast,
        altid_op_baseline,
        vurderbare_signaler,
        retningssignaler_antal,
        signalfordeling,
    )


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


def _skriv_resultater(path, rows, horisonter):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["date", "score", "direction", "coverage", *[f"return_{h}d" for h in horisonter]]
    with path.open("w", newline="", encoding="utf-8") as fil:
        writer = csv.DictWriter(fil, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
