from guldagent_v2.features import FEATURES
from guldagent_v2.signal_model import beregn_signal, vigtigste_drivere


def main():
    # Eksempel: renten stiger, men uro og investorefterspørgsel trækker op.
    signaler = {
        "realrente_10aar": 0.50,
        "dollarindeks": -0.30,
        "vix": 0.70,
        "geopolitisk_risiko": 0.80,
        "etf_flow": 0.60,
        "guld_momentum_20d": 0.50,
    }
    resultat = beregn_signal(signaler)

    print(f"Retning: {resultat.retning}")
    print(f"Score: {resultat.score:+.3f}")
    print(f"Signalstyrke: {resultat.signalstyrke}%")
    print(f"Fuld modeldækning: {resultat.datadaekning}%")
    print("Vigtigste drivere:")
    for noegle, bidrag in vigtigste_drivere(resultat):
        print(f"- {FEATURES[noegle].navn}: {bidrag:+.3f}")
    print(f"Manglende variable: {len(resultat.mangler)}")


if __name__ == "__main__":
    main()
