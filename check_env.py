from dotenv import load_dotenv
import os

load_dotenv()

VARIABLES = (
    "GOLD_API_KEY",
    "FRED_API_KEY",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "HEMMELIG_MODTAGER",
    "BRIDGE_USERNAME",
    "BRIDGE_PASSWORD",
    "HEMMELIG_FAKTOR_ARBEJDE",
)

for navn in VARIABLES:
    status = "sat" if os.getenv(navn) else "mangler"
    print(f"{navn}: {status}")
