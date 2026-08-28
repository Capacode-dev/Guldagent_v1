class FredGoldClient:
    """Tilpas FREDs historiske London-guldserie til backtestformatet."""

    SERIES_ID = "GOLDAMGBD228NLBM"
    SOURCE_NAME = "FRED / LBMA London AM Fix (USD pr. troy ounce)"

    def __init__(self, fred_client):
        self.fred_client = fred_client

    def hent_daglige_priser(self, startdato="2010-01-01", slutdato=None):
        observationer = self.fred_client.hent_serie(
            self.SERIES_ID,
            startdato,
            slutdato,
        )
        return [
            (dato, pris, self.SERIES_ID)
            for dato, pris in observationer
            if pris > 0
        ]
