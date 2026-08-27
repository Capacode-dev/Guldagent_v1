import argparse
import csv

from guldagent_v2.features import FEATURES
from guldagent_v2.data_sources import MVP_COLUMNS
from guldagent_v2.signal_model import beregn_signal, vigtigste_drivere


def analyser_seneste(signal_path, required_features=MVP_COLUMNS):
    with open(signal_path, encoding="utf-8") as fil:
        rows = list(csv.DictReader(fil))

    for row in reversed(rows):
        signaler = {
            noegle: float(value)
            for noegle, value in row.items()
            if noegle != "date" and value not in (None, "")
        }
        if signaler and all(feature in signaler for feature in required_features):
            return row["date"], beregn_signal(signaler)

    raise ValueError("Signalfilen indeholder ingen dato med alle krævede MVP-signaler")


def main():
    parser = argparse.ArgumentParser(description="Analysér seneste Guldagent v2-signaler.")
    parser.add_argument("--input", default="data/processed/macro_signals.csv")
    args = parser.parse_args()

    dato, resultat = analyser_seneste(args.input)
    print(f"Dato: {dato}")
    print(f"Retning: {resultat.retning}")
    print(f"Score: {resultat.score:+.3f}")
    print(f"Signalstyrke: {resultat.signalstyrke}%")
    print(f"Fuld modeldækning: {resultat.datadaekning}%")
    print("Vigtigste drivere:")
    for noegle, bidrag in vigtigste_drivere(resultat):
        print(f"- {FEATURES[noegle].navn}: {bidrag:+.3f}")


if __name__ == "__main__":
    main()
