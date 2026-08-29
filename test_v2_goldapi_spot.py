import unittest
from unittest.mock import Mock

import requests

from guldagent_v2.goldapi_spot_client import GoldApiSpotClient


class GoldApiSpotClientTests(unittest.TestCase):
    def test_henter_usd_pr_troy_ounce(self):
        response = Mock()
        response.json.return_value = {"price": 3456.78, "timestamp": 1788000000}
        session = Mock()
        session.get.return_value = response

        spot = GoldApiSpotClient("hemmelig", session=session).hent_spotpris()

        self.assertEqual(spot.price_usd_oz, 3456.78)
        self.assertEqual(spot.source, "GoldAPI XAU/USD")
        headers = session.get.call_args.kwargs["headers"]
        self.assertEqual(headers["x-access-token"], "hemmelig")

    def test_http_fejl_skjuler_noeglen(self):
        session = Mock()
        session.get.side_effect = requests.ConnectionError(
            "forbindelsesfejl med hemmelig"
        )

        with self.assertRaises(RuntimeError) as context:
            GoldApiSpotClient("hemmelig", session=session).hent_spotpris()

        self.assertNotIn("hemmelig", str(context.exception))


if __name__ == "__main__":
    unittest.main()
