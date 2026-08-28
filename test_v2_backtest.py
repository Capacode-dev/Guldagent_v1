import csv
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from guldagent_v2.backtest import koer_backtest, koer_maanedsbacktest


class BacktestTests(unittest.TestCase):
    def test_maaler_fremtidigt_afkast_uden_fremtidsdata_i_signalet(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            signals = directory / "signals.csv"
            gold = directory / "gold.csv"
            output = directory / "results.csv"

            with signals.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "realrente_10aar", "vix"])
                writer.writerow(["2026-01-01", -1, 1])

            with gold.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "gold_price"])
                start = date(2026, 1, 1)
                for index in range(62):
                    writer.writerow([(start + timedelta(days=index)).isoformat(), 100 + index])

            rows, summary = koer_backtest(signals, gold, output)

            self.assertTrue(output.exists())

        self.assertEqual(rows[0]["direction"], "OP")
        self.assertEqual(rows[0]["return_5d"], 5.0)
        self.assertEqual(rows[0]["return_20d"], 20.0)
        self.assertEqual(rows[0]["return_60d"], 60.0)
        self.assertEqual(summary.traefsikkerhed[20], 100.0)
        self.assertEqual(summary.altid_op_baseline[20], 100.0)
        self.assertEqual(summary.retningssignaler[20], 1)
        self.assertEqual(summary.signalfordeling, {"OP": 1})

    def test_baseline_bruger_samme_datoer_som_modellens_retningssignaler(self):
        rows = [
            {"direction": "NEUTRAL", "return_5d": 1.0},
            {"direction": "NEUTRAL", "return_5d": 1.0},
            {"direction": "OP", "return_5d": -1.0},
            {"direction": "NED", "return_5d": -1.0},
        ]

        from guldagent_v2.backtest import opsummer_backtest

        summary = opsummer_backtest(rows, horisonter=(5,))

        self.assertEqual(summary.traefsikkerhed[5], 50.0)
        self.assertEqual(summary.altid_op_baseline[5], 0.0)
        self.assertEqual(summary.vurderbare_signaler[5], 4)
        self.assertEqual(summary.retningssignaler[5], 2)

    def test_udelader_horisont_uden_nok_senere_priser(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            signals = directory / "signals.csv"
            gold = directory / "gold.csv"
            with signals.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "vix"])
                writer.writerow(["2026-01-01", 1])
            with gold.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "gold_price"])
                writer.writerow(["2026-01-01", 100])

            rows, summary = koer_backtest(signals, gold)

        self.assertEqual(rows[0]["return_5d"], "")
        self.assertEqual(summary.traefsikkerhed[5], 0.0)

    def test_maanedsbacktest_bruger_maanedens_sidste_komplette_signal(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            signals = directory / "signals.csv"
            gold = directory / "gold.csv"

            with signals.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "vix"])
                writer.writerow(["2026-01-10", -1])
                writer.writerow(["2026-01-30", 1])
                writer.writerow(["2026-02-27", 1])

            with gold.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "gold_price"])
                writer.writerow(["2026-01-01", 100])
                writer.writerow(["2026-02-01", 110])

            rows, summary = koer_maanedsbacktest(
                signals,
                gold,
                horisonter=(1,),
                required_features=("vix",),
            )

        self.assertEqual(rows[0]["date"], "2026-01-30")
        self.assertEqual(rows[0]["gold_month"], "2026-01-01")
        self.assertEqual(rows[0]["direction"], "OP")
        self.assertEqual(rows[0]["return_1m"], 10.0)
        self.assertEqual(summary.horisont_enhed, "måneder")


if __name__ == "__main__":
    unittest.main()
