from dataclasses import dataclass
from datetime import datetime, timezone

import requests


@dataclass(frozen=True)
class SpotPrice:
    price_usd_oz: float
    observed_at_utc: str
    source: str = "GoldAPI XAU/USD"


class GoldApiSpotClient:
    URL = "https://www.goldapi.io/api/XAU/USD"

    def __init__(self, api_key, session=None, timeout=15):
        if not api_key:
            raise ValueError("GOLD_API_KEY mangler")
        self.api_key = api_key
        self.session = session or requests.Session()
        self.timeout = timeout

    def hent_spotpris(self):
        headers = {
            "x-access-token": self.api_key,
            "Content-Type": "application/json",
        }
        response = None
        try:
            response = self.session.get(
                self.URL,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException:
            status = response.status_code if response is not None else "ukendt"
            raise RuntimeError(
                f"GoldAPI kunne ikke hente XAU/USD (HTTP {status})"
            ) from None

        try:
            payload = response.json()
            price = float(payload["price"])
        except (ValueError, TypeError, KeyError):
            raise RuntimeError("GoldAPI returnerede ingen gyldig XAU/USD-pris") from None
        if price <= 0:
            raise RuntimeError("GoldAPI returnerede en ugyldig XAU/USD-pris")

        observed_at = _format_timestamp(payload.get("timestamp"))
        return SpotPrice(price, observed_at)


def _format_timestamp(timestamp):
    if timestamp in (None, ""):
        return datetime.now(timezone.utc).isoformat()
    try:
        return datetime.fromtimestamp(float(timestamp), timezone.utc).isoformat()
    except (ValueError, TypeError, OSError):
        return datetime.now(timezone.utc).isoformat()
