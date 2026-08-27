from dataclasses import dataclass


@dataclass(frozen=True)
class FredSeries:
    series_id: str
    kolonne: str
    beskrivelse: str
    er_proxy: bool = False


MVP_SERIES = (
    FredSeries("DFII10", "realrente_10aar", "10-årig amerikansk realrente"),
    FredSeries("DTWEXBGS", "dollarindeks", "Bredt nominelt amerikansk dollarindeks"),
    FredSeries("T10YIE", "inflationsforventning", "10-årig breakeven-inflation"),
    FredSeries("VIXCLS", "vix", "CBOE Volatility Index"),
    FredSeries(
        "DGS2",
        "fed_forventning",
        "2-årig amerikansk statsrente; foreløbig proxy for Fed-forventninger",
        er_proxy=True,
    ),
)

MVP_COLUMNS = tuple(source.kolonne for source in MVP_SERIES)
