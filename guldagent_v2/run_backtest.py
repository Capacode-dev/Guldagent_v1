import argparse

from guldagent_v2.backtest import koer_backtest
from guldagent_v2.data_sources import MVP_COLUMNS


def main():
    parser = argparse.ArgumentParser(description="Backtest Guldagent v2 mod historiske guldpriser.")
    parser.add_argument("--signals", default="data/processed/macro_signals.csv")
    parser.add_argument("--gold", default="data/input/gold_history.csv")
    parser.add_argument("--output", default="data/processed/backtest_results.csv")
    args = parser.parse_args()

    _, summary = koer_backtest(
        args.signals,
        args.gold,
        args.output,
        required_features=MVP_COLUMNS,
    )
    print(f"Antal signaler: {summary.antal_signaler}")
    for horisont, accuracy in summary.traefsikkerhed.items():
        print(f"Træfsikkerhed efter {horisont} dage: {accuracy:.2f}%")
        print(f"Altid-OP baseline efter {horisont} dage: {summary.altid_op_baseline[horisont]:.2f}%")
    print(f"Detaljer gemt: {args.output}")


if __name__ == "__main__":
    main()
