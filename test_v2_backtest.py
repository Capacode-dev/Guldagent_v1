import csv
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from guldagent_v2.backtest import koer_backtest


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
        self.assertEqual(summary.signalfordeling, {"OP": 1})

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


if __name__ == "__main__":
    unittest.main()
