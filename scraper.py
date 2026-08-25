import os

import requests
from dotenv import load_dotenv

load_dotenv()


def hent_guldpris_dkk_pr_gram(api_key=None):
    """Hent guldprisen i DKK pr. gram fra GoldAPI."""
    api_key = api_key or os.getenv("GOLD_API_KEY")
    if not api_key:
        print("GOLD_API_KEY mangler i miljøvariablerne.")
        return None

    url = "https://www.goldapi.io/api/XAU/DKK"
    headers = {
        "x-access-token": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "price" not in data:
            print("API returnerede ingen guldpris.")
            return None

        pris_dkk_pr_ounce = float(data["price"])
        pris_dkk_pr_gram = pris_dkk_pr_ounce / 31.1035
        return round(pris_dkk_pr_gram, 2)

    except requests.RequestException as error:
        print(f"Netværksfejl ved hentning af guldpris: {error}")
        return None
    except (ValueError, TypeError, KeyError) as error:
        print(f"Ugyldigt API-svar: {error}")
        return None
