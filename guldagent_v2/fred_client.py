from datetime import date

import requests


class FredClient:
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key, session=None, timeout=20):
        if not api_key:
            raise ValueError("FRED_API_KEY mangler")
        self.api_key = api_key
        self.session = session or requests.Session()
        self.timeout = timeout

    def hent_serie(self, series_id, startdato, slutdato=None):
        slutdato = slutdato or date.today().isoformat()
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": startdato,
            "observation_end": slutdato,
            "sort_order": "asc",
        }
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
        except requests.RequestException:
            raise RuntimeError(
                f"FRED-forbindelsen fejlede for serien {series_id}"
            ) from None
        try:
            response.raise_for_status()
        except requests.HTTPError:
            # requests' standardfejl indeholder hele URL'en og dermed
            # api_key. Giv en brugbar fejl uden at lække hemmeligheden.
            try:
                fejl = response.json().get("error_message", "Ukendt FRED-fejl")
            except (ValueError, AttributeError):
                fejl = "Ukendt FRED-fejl"
            raise RuntimeError(
                f"FRED kunne ikke hente serien {series_id} "
                f"(HTTP {response.status_code}): {fejl}"
            ) from None
        payload = response.json()

        resultat = []
        for observation in payload.get("observations", []):
            value = observation.get("value")
            if value in (None, "."):
                continue
            resultat.append((observation["date"], float(value)))
        return resultat
