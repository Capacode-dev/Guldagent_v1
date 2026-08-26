import argparse
import csv
from datetime import date
from pathlib import Path

from guldagent_v2.freegold_client import FreeGoldClient


def gem_guldhistorik(priser, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fil:
        writer = csv.writer(fil)
        writer.writerow(["date", "gold_price", "source"])
        writer.writerows(priser)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Hent daglig guldhistorik fra FreeGoldAPI.")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--slut")
    parser.add_argument("--output", default="data/input/gold_history.csv")
    args = parser.parse_args()

    client = FreeGoldClient()
    priser = client.hent_daglige_priser(args.start, args.slut)
    if not priser:
        raise RuntimeError("FreeGoldAPI returnerede ingen daglige guldpriser i perioden")
    path = gem_guldhistorik(priser, args.output)
    print(f"Gemte {len(priser)} guldpriser i {path}")
    seneste = date.fromisoformat(priser[-1][0])
    alder = (date.today() - seneste).days
    if alder > 7:
        print(f"ADVARSEL: Seneste FreeGoldAPI-pris er {alder} dage gammel ({seneste}).")


if __name__ == "__main__":
    main()
