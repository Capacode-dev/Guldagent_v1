import csv
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from guldagent_v2.backtest import (
    _eksakt_mcnemar_p,
    _wilson_interval_95,
    koer_backtest,
    koer_maanedsbacktest,
    opsummer_backtest,
)


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
        self.assertEqual(summary.traefsikkerhed_pr_retning[5]["OP"], 0.0)
        self.assertEqual(summary.traefsikkerhed_pr_retning[5]["NED"], 100.0)
        self.assertEqual(summary.antal_pr_retning[5], {"OP": 1, "NED": 1})
        self.assertEqual(summary.parret_sammenligning[5]["model_sejre"], 1)
        self.assertEqual(summary.parret_sammenligning[5]["baseline_sejre"], 0)
        self.assertIsNone(summary.parret_sammenligning[5]["signifikant_5pct"])

    def test_wilson_interval_viser_usikkerhed(self):
        self.assertEqual(_wilson_interval_95(27, 40), (52.02, 79.92))
        self.assertEqual(_wilson_interval_95(0, 0), (0.0, 0.0))

    def test_eksakt_mcnemar_sammenligner_parrede_udfald(self):
        self.assertEqual(_eksakt_mcnemar_p(14, 7), 0.1892)
        self.assertEqual(_eksakt_mcnemar_p(0, 0), 1.0)

    def test_overlappende_horisont_faar_ingen_formel_p_vaerdi(self):
        summary = opsummer_backtest(
            [{"direction": "NED", "return_3m": -1.0}],
            horisonter=(3,),
            suffix="m",
            formelle_parrede_horisonter=(1,),
        )

        self.assertFalse(summary.parret_sammenligning[3]["formel_test"])
        self.assertIsNone(summary.parret_sammenligning[3]["p_vaerdi"])

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
        self.assertEqual(summary.primaer_horisont, 1)

    def test_maanedsbacktest_deler_reference_og_senere_test(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            signals = directory / "signals.csv"
            gold = directory / "gold.csv"

            with signals.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "vix"])
                writer.writerow(["2018-12-28", 1])
                writer.writerow(["2019-01-31", 1])
                writer.writerow(["2019-02-28", 1])

            with gold.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "gold_price"])
                writer.writerow(["2018-12-01", 100])
                writer.writerow(["2019-01-01", 105])
                writer.writerow(["2019-02-01", 110])

            _, summary = koer_maanedsbacktest(
                signals,
                gold,
                horisonter=(1,),
                required_features=("vix",),
                test_startdato="2019-01-01",
            )

        self.assertEqual(summary.delperioder["reference"]["antal_signaler"], 1)
        self.assertEqual(summary.delperioder["senere_test"]["antal_signaler"], 2)
        self.assertEqual(
            summary.delperioder["reference"]["retningssignaler"][1],
            0,
        )
        self.assertEqual(
            summary.delperioder["senere_test"]["periode"],
            "2019-01 til 2019-02",
        )


if __name__ == "__main__":
    unittest.main()
