import csv
import math
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import Mock

from guldagent_v2.pipeline import koer_mvp_pipeline


class PipelineTests(unittest.TestCase):
    def test_hele_mvp_pipeline_uden_netvaerk_eller_noegler(self):
        start = date(2025, 1, 1)
        datoer = [(start + timedelta(days=index)).isoformat() for index in range(100)]

        fred_client = Mock()
        fred_client.hent_serie.side_effect = lambda series_id, startdato, slutdato: [
            (dato, 100 + index * 0.1 + math.sin(index / 3))
            for index, dato in enumerate(datoer)
        ]
        gold_client = Mock()
        gold_client.hent_daglige_priser.return_value = [
            (dato, 2600 + index * 2, "yahoo_finance")
            for index, dato in enumerate(datoer)
        ]

        with tempfile.TemporaryDirectory() as directory:
            resultat = koer_mvp_pipeline(
                fred_client,
                gold_client,
                startdato=datoer[0],
                slutdato=datoer[-1],
                output_dir=directory,
            )
            rapport_path = Path(resultat.rapport_markdown)
            backtest_path = Path(directory) / "processed" / "backtest_results.csv"
            with backtest_path.open(encoding="utf-8") as fil:
                backtest_rows = list(csv.DictReader(fil))
            rapport = rapport_path.read_text(encoding="utf-8")

            self.assertTrue(rapport_path.exists())
            self.assertTrue(backtest_path.exists())
            self.assertGreater(len(backtest_rows), 0)
            self.assertIn("samme datoer", rapport)
            self.assertIn("Historiske backtestdata", rapport)

        self.assertFalse(resultat.llm_brugt)
        self.assertIn(resultat.retning, {"OP", "NEUTRAL", "NED"})


if __name__ == "__main__":
    unittest.main()
