from dataclasses import dataclass


@dataclass(frozen=True)
class Feature:
    navn: str
    forklaring: str
    forventet_effekt: int
    vaegt: float


# forventet_effekt:
#  1 = variablen og guld bevæger sig typisk samme vej
# -1 = variablen og guld bevæger sig typisk modsat
FEATURES = {
    "realrente_10aar": Feature("Amerikansk 10-årig realrente", "Højere realrente gør guld mindre attraktivt", -1, 1.00),
    "dollarindeks": Feature("Dollarindeks (DXY)", "En stærkere dollar presser ofte guld", -1, 0.90),
    "fed_forventning": Feature("Forventet Fed-rente", "Højere forventet rente presser ofte guld", -1, 0.75),
    "inflationsforventning": Feature("10-årig inflationsforventning", "Stigende inflationsfrygt kan støtte guld", 1, 0.65),
    "vix": Feature("VIX", "Markedsuro kan øge efterspørgslen efter sikre aktiver", 1, 0.60),
    "geopolitisk_risiko": Feature("Geopolitisk risiko", "Øget risiko kan støtte guld", 1, 0.65),
    "centralbank_koeb": Feature("Centralbankers guldkøb", "Større køb øger efterspørgslen", 1, 0.80),
    "etf_flow": Feature("Guld-ETF-flow", "Indstrømning viser investorinteresse", 1, 0.70),
    "comex_positionering": Feature("COMEX-positionering", "Flere spekulative long-positioner støtter momentum", 1, 0.45),
    "guld_momentum_20d": Feature("Guldmomentum, 20 dage", "Positivt momentum kan fortsætte på kort sigt", 1, 0.55),
    "guld_momentum_200d": Feature("Guld mod 200-dages gennemsnit", "Viser den langsigtede trend", 1, 0.65),
    "sp500_momentum": Feature("S&P 500-momentum", "Stærk risikoappetit kan mindske safe-haven-efterspørgsel", -1, 0.30),
    "kreditspraend": Feature("Kreditspænd", "Stigende spænd signalerer finansiel uro", 1, 0.45),
    "oliepris": Feature("Oliepris", "Stigende olie kan øge inflationspresset", 1, 0.30),
    "kobberpris": Feature("Kobberpris", "Kan afspejle global vækst og råvareefterspørgsel", 1, 0.20),
    "us_geld_vaekst": Feature("Vækst i amerikansk statsgæld", "Finanspolitisk bekymring kan støtte guld", 1, 0.35),
    "realiseret_inflation": Feature("Amerikansk kerneinflation", "Vedvarende inflation kan støtte guld", 1, 0.40),
    "arbejdsmarked": Feature("Amerikansk arbejdsmarked", "Et stærkt arbejdsmarked kan holde renterne høje", -1, 0.30),
    "recession_risiko": Feature("Recessionsrisiko", "Øget risiko kan støtte safe-haven-efterspørgsel", 1, 0.45),
    "usd_likviditet": Feature("Dollar-likviditet", "Mere likviditet kan støtte aktiv- og guldpriser", 1, 0.40),
}

