import csv
from pathlib import Path

from guldagent_v2.data_sources import MVP_SERIES


def byg_mvp_dataset(client, startdato, slutdato=None, output_dir="data"):
    """Hent rå FRED-serier og gem både rå og sammenflettede CSV-filer."""
    output_dir = Path(output_dir)
    raw_dir = output_dir / "raw"
    processed_dir = output_dir / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    alle_datoer = set()
    serier = {}

    for source in MVP_SERIES:
        observationer = client.hent_serie(source.series_id, startdato, slutdato)
        serier[source.kolonne] = dict(observationer)
        alle_datoer.update(dato for dato, _ in observationer)
        _skriv_raa_csv(raw_dir / f"{source.series_id}.csv", observationer)

    output_path = processed_dir / "macro_mvp.csv"
    kolonner = [source.kolonne for source in MVP_SERIES]
    with output_path.open("w", newline="", encoding="utf-8") as fil:
        writer = csv.DictWriter(fil, fieldnames=["date", *kolonner])
        writer.writeheader()
        for dato in sorted(alle_datoer):
            row = {"date": dato}
            row.update({kolonne: serier[kolonne].get(dato, "") for kolonne in kolonner})
            writer.writerow(row)

    return output_path


def _skriv_raa_csv(path, observationer):
    with path.open("w", newline="", encoding="utf-8") as fil:
        writer = csv.writer(fil)
        writer.writerow(["date", "value"])
        writer.writerows(observationer)

