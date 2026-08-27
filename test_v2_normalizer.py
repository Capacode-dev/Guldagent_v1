import csv
import tempfile
import unittest
from pathlib import Path

from guldagent_v2.analyze_latest import analyser_seneste
from guldagent_v2.normalizer import _beregn_signal, normaliser_dataset


class NormalizerTests(unittest.TestCase):
    def test_stigende_serie_giver_positivt_signal(self):
        signal = _beregn_signal([1, 2, 4, 5, 7], lookback=2, volatilitet_vindue=4)
        self.assertGreater(signal, 0)

    def test_faldende_serie_giver_negativt_signal(self):
        signal = _beregn_signal([7, 5, 4, 2, 1], lookback=2, volatilitet_vindue=4)
        self.assertLess(signal, 0)

    def test_signal_begrænses_til_interval(self):
        signal = _beregn_signal([0, 0.01, 0.02, 0.03, 100], lookback=1, volatilitet_vindue=2)
        self.assertLessEqual(signal, 1)

    def test_fil_bevarer_datoer_og_manglende_vaerdier(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "macro.csv"
            output_path = Path(directory) / "signals.csv"
            with input_path.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "vix"])
                writer.writerow(["2026-01-01", 10])
                writer.writerow(["2026-01-02", ""])
                writer.writerow(["2026-01-03", 12])
                writer.writerow(["2026-01-04", 15])

            normaliser_dataset(input_path, output_path, lookback=1, volatilitet_vindue=2)
            with output_path.open(encoding="utf-8") as fil:
                rows = list(csv.DictReader(fil))

        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[1]["vix"], "")
        self.assertGreater(float(rows[-1]["vix"]), 0)

    def test_seneste_signaler_sendes_til_modellen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "signals.csv"
            with path.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow(["date", "realrente_10aar", "vix"])
                writer.writerow(["2026-01-01", "", ""])
                writer.writerow(["2026-01-02", -1, 1])

            dato, resultat = analyser_seneste(
                path,
                required_features=("realrente_10aar", "vix"),
            )

        self.assertEqual(dato, "2026-01-02")
        self.assertEqual(resultat.retning, "OP")

    def test_live_analyse_vaelger_seneste_dato_med_alle_fem_signaler(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "signals.csv"
            with path.open("w", newline="", encoding="utf-8") as fil:
                writer = csv.writer(fil)
                writer.writerow([
                    "date",
                    "realrente_10aar",
                    "dollarindeks",
                    "inflationsforventning",
                    "vix",
                    "fed_forventning",
                ])
                writer.writerow(["2026-01-02", -0.2, -0.2, 0.2, 0.2, -0.2])
                writer.writerow(["2026-01-03", "", "", 0.3, 0.3, ""])

            dato, resultat = analyser_seneste(path)

        self.assertEqual(dato, "2026-01-02")
        self.assertEqual(len(resultat.bidrag), 5)


if __name__ == "__main__":
    unittest.main()
