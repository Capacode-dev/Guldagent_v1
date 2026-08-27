import argparse
import os

from dotenv import load_dotenv

from guldagent_v2.fred_client import FredClient
from guldagent_v2.freegold_client import FreeGoldClient
from guldagent_v2.pipeline import koer_mvp_pipeline


def main():
    parser = argparse.ArgumentParser(description="Kør hele Guldagent v2 MVP-pipelinen.")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--slut")
    parser.add_argument("--output", default="data")
    parser.add_argument("--no-llm", action="store_true", help="Kør uden OpenAI API-kald")
    args = parser.parse_args()

    load_dotenv()
    fred_client = FredClient(os.getenv("FRED_API_KEY"))
    gold_client = FreeGoldClient()

    llm_client = None
    openai_key = os.getenv("OPENAI_API_KEY")
    if not args.no_llm and openai_key:
        from openai import OpenAI

        llm_client = OpenAI(api_key=openai_key)
    elif not args.no_llm:
        print("INFO: OPENAI_API_KEY mangler; fortsætter med rapport uden LLM-forklaring.")

    resultat = koer_mvp_pipeline(
        fred_client=fred_client,
        gold_client=gold_client,
        startdato=args.start,
        slutdato=args.slut,
        output_dir=args.output,
        llm_client=llm_client,
        llm_model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
    )
    print(f"Dato: {resultat.dato}")
    print(f"Retning: {resultat.retning}")
    print(f"Score: {resultat.score:+.3f}")
    print(f"Backtest-signaler: {resultat.backtest_signaler}")
    print(f"LLM-analyse: {'ja' if resultat.llm_brugt else 'nej'}")
    print(f"Rapport: {resultat.rapport_markdown}")


if __name__ == "__main__":
    main()

