import os

def beregn_priser(finguld_pris):
    """
    Guldagent v1 karatberegner.
    - 24 kt = finguld (ingen beregning)
    - 18, 14, 8 kt beregnes via:
        (finguld / 999.9 * promille) * faktor_arbejde * faktor_avance * 0.8
    """

    faktor_arbejde = float(os.getenv("HEMMELIG_FAKTOR_ARBEJDE", "2.5"))
    faktor_avance = 1.25

    priser = {
        "24kt": round(float(finguld_pris), 2)
    }

    promiller = {
        "18kt": 750,
        "14kt": 585,
        "8kt": 333
    }

    for karat, promille in promiller.items():
        pris = (finguld_pris / 999.9 * promille)
        pris = pris * faktor_arbejde * faktor_avance
        pris = pris * 0.8  # 20% fradrag
        priser[karat] = round(pris, 2)

    return priser
