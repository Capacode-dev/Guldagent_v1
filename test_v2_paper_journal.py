import tempfile
import unittest
from datetime import datetime, timezone

from guldagent_v2.goldapi_spot_client import SpotPrice
from guldagent_v2.paper_journal import PaperJournal


def _report():
    return {
        "dato": "2026-01-30",
        "retning": "OP",
        "score": 0.31,
        "signalstyrke": 31,
        "mvp_signaler_brugt": 5,
        "mvp_signaler_total": 5,
        "drivere": [{"navn": "Dollarindeks", "bidrag": 0.84}],
        "backtest": {"primaer_horisont": 1},
    }


class PaperJournalTests(unittest.TestCase):
    def test_signal_og_resultat_gemmes_separat_uden_dubletter(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = PaperJournal(directory)
            start_spot = SpotPrice(3000.0, "2026-01-31T10:00:00+00:00")
            recorded_at = datetime(2026, 1, 31, 10, tzinfo=timezone.utc)
            signal = journal.registrer_signal(
                _report(),
                start_spot,
                "abc1234",
                recorded_at,
            )

            self.assertEqual(signal["evaluation_due_date"], "2026-02-28")
            self.assertEqual(journal.status()[0]["status"], "PENDING")
            with self.assertRaisesRegex(ValueError, "allerede registreret"):
                journal.registrer_signal(
                    _report(),
                    start_spot,
                    "abc1234",
                    recorded_at,
                )

            with self.assertRaisesRegex(ValueError, "først evalueres"):
                journal.registrer_resultat(
                    signal["signal_id"],
                    SpotPrice(3300.0, "2026-02-27T10:00:00+00:00"),
                    datetime(2026, 2, 27, 10, tzinfo=timezone.utc),
                )

            outcome = journal.registrer_resultat(
                signal["signal_id"],
                SpotPrice(3300.0, "2026-02-28T10:00:00+00:00"),
                datetime(2026, 2, 28, 10, tzinfo=timezone.utc),
            )
            self.assertEqual(outcome["return_percent"], 10.0)
            self.assertEqual(outcome["direction_correct"], "JA")
            self.assertEqual(journal.status()[0]["status"], "EVALUATED")
            with self.assertRaisesRegex(ValueError, "allerede evalueret"):
                journal.registrer_resultat(
                    signal["signal_id"],
                    SpotPrice(3300.0, "2026-02-28T10:00:00+00:00"),
                    datetime(2026, 2, 28, 10, tzinfo=timezone.utc),
                )

    def test_dry_run_skriver_ikke_signal(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = PaperJournal(directory)
            journal.registrer_signal(
                _report(),
                SpotPrice(3000.0, "2026-01-31T10:00:00+00:00"),
                "abc1234",
                datetime(2026, 1, 31, 10, tzinfo=timezone.utc),
                save=False,
            )

            self.assertEqual(journal.laes_signaler(), [])

    def test_afviser_for_gammel_rapport(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = PaperJournal(directory)
            with self.assertRaisesRegex(ValueError, "ikke aktuel"):
                journal.registrer_signal(
                    _report(),
                    SpotPrice(3000.0, "2026-03-31T10:00:00+00:00"),
                    "abc1234",
                    datetime(2026, 3, 31, 10, tzinfo=timezone.utc),
                )

    def test_afviser_signal_foer_maanedens_25(self):
        report = _report()
        report["dato"] = "2026-01-19"
        with tempfile.TemporaryDirectory() as directory:
            journal = PaperJournal(directory)
            with self.assertRaisesRegex(ValueError, "fra den 25"):
                journal.registrer_signal(
                    report,
                    SpotPrice(3000.0, "2026-01-20T10:00:00+00:00"),
                    "abc1234",
                    datetime(2026, 1, 20, 10, tzinfo=timezone.utc),
                )


if __name__ == "__main__":
    unittest.main()
