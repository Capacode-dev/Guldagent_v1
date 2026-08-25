import unittest

from guldagent_v2.signal_model import beregn_signal, vigtigste_drivere


class SignalModelTests(unittest.TestCase):
    def test_stigende_realrente_traekker_ned(self):
        resultat = beregn_signal({"realrente_10aar": 1.0})
        self.assertEqual(resultat.retning, "NED")

    def test_faldende_dollar_traekker_op(self):
        resultat = beregn_signal({"dollarindeks": -1.0})
        self.assertEqual(resultat.retning, "OP")

    def test_modsatrettede_faktorer_samles(self):
        resultat = beregn_signal({"realrente_10aar": 0.5, "vix": 1.0})
        self.assertEqual(resultat.retning, "NEUTRAL")

    def test_afviser_signal_uden_for_interval(self):
        with self.assertRaises(ValueError):
            beregn_signal({"vix": 1.1})

    def test_vigtigste_driver(self):
        resultat = beregn_signal({"vix": 0.2, "centralbank_koeb": 1.0})
        self.assertEqual(vigtigste_drivere(resultat, antal=1)[0][0], "centralbank_koeb")


if __name__ == "__main__":
    unittest.main()
