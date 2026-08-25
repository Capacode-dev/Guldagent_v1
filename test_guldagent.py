import os
import unittest
from unittest.mock import Mock, patch

from calculator import beregn_priser
from scraper import hent_guldpris_dkk_pr_gram
from validator import validate_price


class GuldagentTests(unittest.TestCase):
    def test_validator(self):
        self.assertTrue(validate_price(750))
        self.assertFalse(validate_price(None))
        self.assertFalse(validate_price(0))
        self.assertFalse(validate_price("ikke et tal"))

    def test_beregner_karatpriser(self):
        with patch.dict(os.environ, {"HEMMELIG_FAKTOR_ARBEJDE": "2.5"}):
            priser = beregn_priser(750)

        self.assertEqual(priser["24kt"], 750.0)
        self.assertEqual(set(priser), {"24kt", "18kt", "14kt", "8kt"})

    @patch("scraper.requests.get")
    def test_scraper_omregner_ounce_til_gram(self, mock_get):
        response = Mock()
        response.json.return_value = {"price": 31_103.5}
        mock_get.return_value = response

        pris = hent_guldpris_dkk_pr_gram(api_key="test-noegle")

        self.assertEqual(pris, 1000.0)
        response.raise_for_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
