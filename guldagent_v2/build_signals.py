import argparse

from guldagent_v2.normalizer import normaliser_dataset


def main():
    parser = argparse.ArgumentParser(description="Normalisér Guldagent v2's makrodata.")
    parser.add_argument("--input", default="data/processed/macro_mvp.csv")
    parser.add_argument("--output", default="data/processed/macro_signals.csv")
    parser.add_argument("--lookback", type=int, default=20)
    parser.add_argument("--volatilitet", type=int, default=60)
    args = parser.parse_args()

    path = normaliser_dataset(
        args.input,
        args.output,
        lookback=args.lookback,
        volatilitet_vindue=args.volatilitet,
    )
    print(f"Signaler gemt: {path}")


if __name__ == "__main__":
    main()

