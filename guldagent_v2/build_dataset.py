import argparse
import os

from dotenv import load_dotenv

from guldagent_v2.dataset import byg_mvp_dataset
from guldagent_v2.fred_client import FredClient


def main():
    parser = argparse.ArgumentParser(description="Byg Guldagent v2's makrodatasæt.")
    parser.add_argument("--start", default="2020-01-01", help="Startdato: YYYY-MM-DD")
    parser.add_argument("--slut", help="Slutdato: YYYY-MM-DD; standard er i dag")
    parser.add_argument("--output", default="data", help="Mappe til rå og behandlede data")
    args = parser.parse_args()

    load_dotenv()
    client = FredClient(os.getenv("FRED_API_KEY"))
    path = byg_mvp_dataset(client, args.start, args.slut, args.output)
    print(f"Datasæt gemt: {path}")


if __name__ == "__main__":
    main()

