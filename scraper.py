import requests

API_KEY = "goldapi-96b34b737fd3c9d9c180ad12a06be94a-io"

def hent_guldpris_dkk_pr_gram():
    """
    Simpel scraper til Guldagent v1.
    Henter kun guldpris i DKK pr gram fra GoldAPI.
    """

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
        print(f"Fejl ved hentning af guldpris: {e}")
        return None
