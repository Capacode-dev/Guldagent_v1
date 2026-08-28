import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import requests

from guldagent_v2.dataset import byg_mvp_dataset
from guldagent_v2.fred_client import FredClient


class FredClientTests(unittest.TestCase):
    def test_overspringer_manglende_fred_vaerdier(self):
        response = Mock()
        response.json.return_value = {
            "observations": [
                {"date": "2026-01-01", "value": "."},
                {"date": "2026-01-02", "value": "2.50"},
            ]
        }
        session = Mock()
        session.get.return_value = response

        client = FredClient("test-key", session=session)
        result = client.hent_serie("DFII10", "2026-01-01", "2026-01-02")

        self.assertEqual(result, [("2026-01-02", 2.5)])
        response.raise_for_status.assert_called_once()

    def test_http_fejl_skjuler_api_noeglen(self):
        response = Mock()
        response.status_code = 400
        response.raise_for_status.side_effect = requests.HTTPError(
            "400 for url: https://example.test?api_key=hemmelig"
        )
        response.json.return_value = {"error_message": "Serien findes ikke"}
        session = Mock()
        session.get.return_value = response

        client = FredClient("hemmelig", session=session)
        with self.assertRaises(RuntimeError) as context:
            client.hent_serie("UKENDT", "2026-01-01", "2026-01-02")

        self.assertNotIn("hemmelig", str(context.exception))
        self.assertIn("UKENDT", str(context.exception))

    def test_forbindelsesfejl_skjuler_api_noeglen(self):
        session = Mock()
        session.get.side_effect = requests.ConnectionError(
            "fejl ved https://example.test?api_key=hemmelig"
        )

        client = FredClient("hemmelig", session=session)
        with self.assertRaises(RuntimeError) as context:
            client.hent_serie("DFII10", "2026-01-01", "2026-01-02")

        self.assertNotIn("hemmelig", str(context.exception))
        self.assertIn("DFII10", str(context.exception))


class DatasetTests(unittest.TestCase):
    def test_bygger_raa_og_samlet_dataset(self):
        client = Mock()
        client.hent_serie.return_value = [("2026-01-02", 2.5)]

        with tempfile.TemporaryDirectory() as directory:
            path = byg_mvp_dataset(client, "2026-01-01", "2026-01-02", directory)
            self.assertTrue(path.exists())
            self.assertEqual(len(list((Path(directory) / "raw").glob("*.csv"))), 5)

            with path.open(encoding="utf-8") as fil:
                rows = list(csv.DictReader(fil))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["realrente_10aar"], "2.5")
        self.assertEqual(client.hent_serie.call_count, 5)


if __name__ == "__main__":
    unittest.main()
