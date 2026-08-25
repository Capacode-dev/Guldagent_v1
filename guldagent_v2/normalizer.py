import csv
import math
import statistics
from collections import deque
from pathlib import Path


def normaliser_dataset(input_path, output_path=None, lookback=20, volatilitet_vindue=60):
    """Omsæt hver rå serie til et bagudskuende, volatilitetsjusteret signal."""
    input_path = Path(input_path)
    output_path = Path(output_path or input_path.with_name("macro_signals.csv"))

    with input_path.open(encoding="utf-8") as fil:
        reader = csv.DictReader(fil)
        rows = list(reader)
        kolonner = [kolonne for kolonne in reader.fieldnames if kolonne != "date"]

    historik = {kolonne: deque(maxlen=volatilitet_vindue + lookback + 1) for kolonne in kolonner}
    output_rows = []

    for row in rows:
        output_row = {"date": row["date"]}
        for kolonne in kolonner:
            raw_value = row.get(kolonne, "")
            if raw_value == "":
                output_row[kolonne] = ""
                continue

            value = float(raw_value)
            values = historik[kolonne]
            values.append(value)
            output_row[kolonne] = _beregn_signal(list(values), lookback, volatilitet_vindue)
        output_rows.append(output_row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fil:
        writer = csv.DictWriter(fil, fieldnames=["date", *kolonner])
        writer.writeheader()
        writer.writerows(output_rows)

    return output_path


def _beregn_signal(values, lookback, volatilitet_vindue):
    if len(values) <= lookback:
        return ""

    aendringer = [ny - gammel for gammel, ny in zip(values, values[1:])]
    relevante = aendringer[-volatilitet_vindue:]
    if len(relevante) < 2:
        return ""

    volatilitet = statistics.stdev(relevante)
    if volatilitet == 0:
        return 0.0

    periode_aendring = values[-1] - values[-1 - lookback]
    forventet_periode_volatilitet = volatilitet * math.sqrt(lookback)
    z_score = periode_aendring / forventet_periode_volatilitet
    return round(max(-1.0, min(1.0, z_score / 2)), 4)

