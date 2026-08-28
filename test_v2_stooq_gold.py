import unittest
from unittest.mock import Mock

from guldagent_v2.stooq_gold_client import StooqGoldClient


class StooqGoldClientTests(unittest.TestCase):
    def test_henter_lukkepriser_i_standardformat(self):
        response = Mock()
        response.text = (
            "Date,Open,High,Low,Close\n"
            "2010-01-04,1096.5,1131.5,1096.0,1121.5\n"
            "2010-01-05,1121.5,1128.0,1115.0,1123.0\n"
        )
        session = Mock()
        session.get.return_value = response

        client = StooqGoldClient(session=session)
        priser = client.hent_daglige_priser("2010-01-01", "2010-01-31")

        self.assertEqual(
            priser,
            [
                ("2010-01-04", 1121.5, "stooq_xauusd"),
                ("2010-01-05", 1123.0, "stooq_xauusd"),
            ],
        )
        params = session.get.call_args.kwargs["params"]
        self.assertEqual(params["s"], "xauusd")
        self.assertEqual(params["d1"], "20100101")

    def test_afviser_tomt_svar(self):
        response = Mock()
        response.text = "No data"
        session = Mock()
        session.get.return_value = response

        client = StooqGoldClient(session=session)
        with self.assertRaisesRegex(RuntimeError, "ingen XAU/USD-priser"):
            client.hent_daglige_priser("2010-01-01", "2010-01-31")


if __name__ == "__main__":
    unittest.main()
