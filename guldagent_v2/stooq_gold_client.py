import csv
from datetime import date
from io import StringIO

import requests


class StooqGoldClient:
    """Hent daglige historiske XAU/USD-lukkepriser fra Stooq."""

    URL = "https://stooq.com/q/d/l/"
    SOURCE_NAME = "Stooq XAU/USD (daglig lukkepris)"

    def __init__(self, session=None, timeout=30):
        self.session = session or requests.Session()
        self.timeout = timeout

    def hent_daglige_priser(self, startdato="2010-01-01", slutdato=None):
        slutdato = slutdato or date.today().isoformat()
        params = {
            "s": "xauusd",
            "i": "d",
            "d1": startdato.replace("-", ""),
            "d2": slutdato.replace("-", ""),
        }
        response = self.session.get(self.URL, params=params, timeout=self.timeout)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise RuntimeError(
                f"Stooq kunne ikke hente XAU/USD (HTTP {response.status_code})"
            ) from None

        priser = {}
        for row in csv.DictReader(StringIO(response.text)):
            dato = row.get("Date")
            close = row.get("Close")
            if not dato or close in (None, "", "N/D"):
                continue
            if startdato <= dato <= slutdato:
                priser[dato] = float(close)

        if not priser:
            raise RuntimeError("Stooq returnerede ingen XAU/USD-priser i perioden")

        return [
            (dato, pris, "stooq_xauusd")
            for dato, pris in sorted(priser.items())
        ]
