import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from guldagent_v2.build_gold_history import gem_guldhistorik
from guldagent_v2.freegold_client import FreeGoldClient


class FreeGoldClientTests(unittest.TestCase):
    def test_beholder_kun_daglige_yahoo_futures(self):
        response = Mock()
        response.json.return_value = [
            {"date": "2024-12-01", "price": 2600, "source": "World Bank Pink Sheet"},
            {"date": "2025-01-02", "price": 2650, "source": "yahoo_finance"},
            {"date": "2025-01-03", "price": 2660, "source": "yahoo_finance"},
            {"date": "2025-01-04", "price": None, "source": "yahoo_finance"},
        ]
        session = Mock()
        session.get.return_value = response

        client = FreeGoldClient(session=session)
        priser = client.hent_daglige_priser("2025-01-01", "2025-01-03")

        self.assertEqual(len(priser), 2)
        self.assertEqual(priser[0][:2], ("2025-01-02", 2650.0))
        response.raise_for_status.assert_called_once()

    def test_gemmer_standardformat_til_backtest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gold.csv"
            gem_guldhistorik(
                [("2025-01-02", 2650.0, "yahoo_finance")],
                path,
            )
            with path.open(encoding="utf-8") as fil:
                rows = list(csv.DictReader(fil))

        self.assertEqual(rows[0]["gold_price"], "2650.0")
        self.assertEqual(rows[0]["source"], "yahoo_finance")


if __name__ == "__main__":
    unittest.main()
