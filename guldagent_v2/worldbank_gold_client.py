from datetime import date

import requests


class WorldBankGoldClient:
    """Hent månedlige World Bank-guldpriser via FreeGoldAPI."""

    URL = "https://freegoldapi.com/data/latest.json"
    SOURCE = "worldbank"
    SOURCE_NAME = "FreeGoldAPI / World Bank (månedligt guldgennemsnit i USD)"

    def __init__(self, session=None, timeout=30):
        self.session = session or requests.Session()
        self.timeout = timeout

    def hent_maanedlige_priser(self, startdato="2010-01-01", slutdato=None):
        slutdato = slutdato or date.today().isoformat()
        response = self.session.get(self.URL, timeout=self.timeout)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise RuntimeError(
                f"FreeGoldAPI kunne ikke hente World Bank-data "
                f"(HTTP {response.status_code})"
            ) from None

        priser = []
        for row in response.json():
            dato = row.get("date")
            price = row.get("price")
            if row.get("source") != self.SOURCE:
                continue
            if not dato or price in (None, ""):
                continue
            if startdato <= dato <= slutdato:
                priser.append((dato, float(price), self.SOURCE))

        return sorted(priser)
