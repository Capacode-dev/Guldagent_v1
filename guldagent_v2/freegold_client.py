from datetime import date

import requests


class FreeGoldClient:
    URL = "https://freegoldapi.com/data/latest.json"
    DAILY_SOURCE = "yahoo_finance"

    def __init__(self, session=None, timeout=30):
        self.session = session or requests.Session()
        self.timeout = timeout

    def hent_daglige_priser(self, startdato="2025-01-01", slutdato=None):
        """Hent den daglige del af FreeGoldAPI-datasættet i USD pr. troy ounce."""
        slutdato = slutdato or date.today().isoformat()
        response = self.session.get(self.URL, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()

        priser = []
        for row in payload:
            dato = row.get("date")
            source = row.get("source", "")
            price = row.get("price")
            if not dato or price in (None, ""):
                continue
            if not startdato <= dato <= slutdato:
                continue
            if source != self.DAILY_SOURCE:
                continue
            priser.append((dato, float(price), source))

        return sorted(priser)
