import os
import requests
from dotenv import load_dotenv

# Indlæs .env filen
load_dotenv()

API_KEY = os.getenv("GOLD_API_KEY")

def hent_guldpris_dkk_pr_gram():
    """
    Sikker scraper til Guldagent.
    Henter guldpris i DKK pr gram fra GoldAPI.
    API-nøglen hentes fra .env og ligger ikke i koden.
    """

    if not API_KEY:
        print("FEJL: GOLD_API_KEY mangler i .env")
        return None

    url = "https://www.goldapi.io/api/XAU/DKK"
    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        if "price" not in data:
            print("API returnerede ingen guldpris.")
            return None

        pris_dkk_pr_ounce = data["price"]
        pris_dkk_pr_gram = pris_dkk_pr_ounce / 31.1035

        return round(pris_dkk_pr_gram, 2)

    except Exception as e:
        print("SCRAPER FEJL:", e)
        return None
