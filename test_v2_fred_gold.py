import unittest
from unittest.mock import Mock

from guldagent_v2.fred_gold_client import FredGoldClient


class FredGoldClientTests(unittest.TestCase):
    def test_henter_fred_guld_og_udelader_ugyldige_priser(self):
        fred_client = Mock()
        fred_client.hent_serie.return_value = [
            ("2010-01-04", 1121.5),
            ("2010-01-05", 0.0),
        ]

        client = FredGoldClient(fred_client)
        priser = client.hent_daglige_priser("2010-01-01", "2010-01-31")

        self.assertEqual(
            priser,
            [("2010-01-04", 1121.5, "GOLDAMGBD228NLBM")],
        )
        fred_client.hent_serie.assert_called_once_with(
            "GOLDAMGBD228NLBM",
            "2010-01-01",
            "2010-01-31",
        )


if __name__ == "__main__":
    unittest.main()
