import unittest
from unittest.mock import Mock

from guldagent_v2.worldbank_gold_client import WorldBankGoldClient


class WorldBankGoldClientTests(unittest.TestCase):
    def test_beholder_kun_worldbank_i_perioden(self):
        response = Mock()
        response.json.return_value = [
            {"date": "2009-12-01", "price": 1100, "source": "worldbank"},
            {"date": "2010-01-01", "price": 1120, "source": "worldbank"},
            {"date": "2010-02-01", "price": 1115, "source": "worldbank"},
            {"date": "2010-01-04", "price": 1121, "source": "yahoo_finance"},
        ]
        session = Mock()
        session.get.return_value = response

        client = WorldBankGoldClient(session=session)
        priser = client.hent_maanedlige_priser("2010-01-01", "2010-02-28")

        self.assertEqual(
            priser,
            [
                ("2010-01-01", 1120.0, "worldbank"),
                ("2010-02-01", 1115.0, "worldbank"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
