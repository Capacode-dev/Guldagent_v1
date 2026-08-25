from dataclasses import dataclass

from guldagent_v2.features import FEATURES


@dataclass(frozen=True)
class SignalResultat:
    score: float
    retning: str
    sikkerhed: int
    bidrag: dict[str, float]
    mangler: list[str]


def beregn_signal(signaler: dict[str, float]) -> SignalResultat:
    """Beregn en vægtet guldscore ud fra normaliserede signaler [-1, 1]."""
    ukendte = set(signaler) - set(FEATURES)
    if ukendte:
        raise ValueError(f"Ukendte variable: {', '.join(sorted(ukendte))}")

    bidrag = {}
    samlet_vaegt = 0.0
    for noegle, signal in signaler.items():
        if not -1 <= signal <= 1:
            raise ValueError(f"{noegle} skal være mellem -1 og 1")

        feature = FEATURES[noegle]
        bidrag[noegle] = signal * feature.forventet_effekt * feature.vaegt
        samlet_vaegt += feature.vaegt

    score = sum(bidrag.values()) / samlet_vaegt if samlet_vaegt else 0.0
    score = round(score, 3)

    if score >= 0.20:
        retning = "OP"
    elif score <= -0.20:
        retning = "NED"
    else:
        retning = "NEUTRAL"

    datadaekning = len(signaler) / len(FEATURES)
    sikkerhed = round(min(abs(score), 1.0) * datadaekning * 100)
    mangler = sorted(set(FEATURES) - set(signaler))

    return SignalResultat(score, retning, sikkerhed, bidrag, mangler)


def vigtigste_drivere(resultat: SignalResultat, antal=3):
    return sorted(resultat.bidrag.items(), key=lambda item: abs(item[1]), reverse=True)[:antal]

