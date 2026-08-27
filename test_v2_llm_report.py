import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from guldagent_v2.llm_analysis import lav_llm_analyse
from guldagent_v2.report import byg_rapport, gem_rapport
from guldagent_v2.signal_model import beregn_signal


class LlmAnalysisTests(unittest.TestCase):
    def test_llm_faar_beregnet_resultat_og_stramt_schema(self):
        client = Mock()
        client.responses.create.return_value.output_text = json.dumps(
            {
                "opsummering": "Realrenten trækker ned, mens VIX trækker op.",
                "positive_faktorer": ["VIX"],
                "negative_faktorer": ["Realrente"],
                "usikkerheder": ["Mange variable mangler"],
                "konklusion": "Dette er et modelsignal og ikke en garanti.",
            }
        )
        resultat = beregn_signal({"realrente_10aar": 0.5, "vix": 1.0})

        analyse = lav_llm_analyse(resultat, "2026-01-02", client)

        self.assertIn("modelsignal", analyse.konklusion)
        kwargs = client.responses.create.call_args.kwargs
        self.assertFalse(kwargs["store"])
        self.assertTrue(kwargs["text"]["format"]["strict"])
        self.assertIn('"beregnet_retning": "NEUTRAL"', kwargs["input"])


class ReportTests(unittest.TestCase):
    def test_gemmer_json_og_markdown(self):
        resultat = beregn_signal({"dollarindeks": -1.0})
        rapport = byg_rapport("2026-01-02", resultat)

        with tempfile.TemporaryDirectory() as directory:
            json_path, md_path = gem_rapport(rapport, directory)
            data = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = md_path.read_text(encoding="utf-8")

        self.assertEqual(data["retning"], "OP")
        self.assertIn("Guldagent v2", markdown)
        self.assertIn("ikke en garanti", markdown)


if __name__ == "__main__":
    unittest.main()
