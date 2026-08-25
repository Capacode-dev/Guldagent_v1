import argparse
import csv

from guldagent_v2.features import FEATURES
from guldagent_v2.signal_model import beregn_signal, vigtigste_drivere


def analyser_seneste(signal_path):
    with open(signal_path, encoding="utf-8") as fil:
        rows = list(csv.DictReader(fil))

    for row in reversed(rows):
        signaler = {
            noegle: float(value)
            for noegle, value in row.items()
            if noegle != "date" and value not in (None, "")
        }
        if signaler:
            return row["date"], beregn_signal(signaler)

    raise ValueError("Signalfilen indeholder ingen beregnede signaler")


def main():
    parser = argparse.ArgumentParser(description="Analysér seneste Guldagent v2-signaler.")
    parser.add_argument("--input", default="data/processed/macro_signals.csv")
    args = parser.parse_args()

    dato, resultat = analyser_seneste(args.input)
    print(f"Dato: {dato}")
    print(f"Retning: {resultat.retning}")
    print(f"Score: {resultat.score:+.3f}")
    print(f"Foreløbig sikkerhed: {resultat.sikkerhed}%")
    print("Vigtigste drivere:")
    for noegle, bidrag in vigtigste_drivere(resultat):
        print(f"- {FEATURES[noegle].navn}: {bidrag:+.3f}")


if __name__ == "__main__":
    main()

