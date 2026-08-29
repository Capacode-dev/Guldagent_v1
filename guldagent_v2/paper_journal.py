import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path


MODEL_VERSION = "2.0.0-mvp"
SIGNAL_FIELDS = (
    "signal_id",
    "recorded_at_utc",
    "analysis_date",
    "evaluation_due_date",
    "direction",
    "score",
    "signal_strength",
    "primary_horizon_months",
    "gold_price_start_usd_oz",
    "gold_price_observed_at_utc",
    "gold_source",
    "model_version",
    "git_commit",
    "mvp_coverage",
    "drivers_json",
)
OUTCOME_FIELDS = (
    "signal_id",
    "evaluated_at_utc",
    "gold_price_end_usd_oz",
    "gold_price_observed_at_utc",
    "gold_source",
    "return_percent",
    "direction_correct",
)


@dataclass(frozen=True)
class JournalPaths:
    signals: Path
    outcomes: Path


class PaperJournal:
    """Append-only journal: signalet og det senere udfald gemmes separat."""

    def __init__(self, directory="paper_trading"):
        directory = Path(directory)
        self.paths = JournalPaths(
            signals=directory / "paper_signals.csv",
            outcomes=directory / "paper_outcomes.csv",
        )

    def registrer_signal(
        self,
        report,
        spot,
        git_commit,
        recorded_at=None,
        save=True,
        max_analysis_age_days=14,
    ):
        recorded_at = recorded_at or datetime.now(timezone.utc)
        recorded_date = recorded_at.date()
        if recorded_date.day < 25:
            raise ValueError("Månedssignalet kan først registreres fra den 25.")
        analysis_date = date.fromisoformat(report["dato"])
        analysis_age = (recorded_date - analysis_date).days
        if analysis_age < 0 or analysis_age > max_analysis_age_days:
            raise ValueError(
                f"Analyserapporten er ikke aktuel ({analysis_age} dage)"
            )
        primary_horizon = report.get("backtest", {}).get("primaer_horisont")
        if primary_horizon != 1:
            raise ValueError("Rapportens primære horisont skal være 1 måned")

        signal_id = f"{recorded_date:%Y-%m}__{MODEL_VERSION}"
        if signal_id in {row["signal_id"] for row in self.laes_signaler()}:
            raise ValueError(f"Signalet {signal_id} er allerede registreret")

        row = {
            "signal_id": signal_id,
            "recorded_at_utc": recorded_at.isoformat(),
            "analysis_date": report["dato"],
            "evaluation_due_date": _tilfoej_maaned(recorded_date).isoformat(),
            "direction": report["retning"],
            "score": report["score"],
            "signal_strength": report["signalstyrke"],
            "primary_horizon_months": primary_horizon,
            "gold_price_start_usd_oz": spot.price_usd_oz,
            "gold_price_observed_at_utc": spot.observed_at_utc,
            "gold_source": spot.source,
            "model_version": MODEL_VERSION,
            "git_commit": git_commit,
            "mvp_coverage": (
                f"{report['mvp_signaler_brugt']}/{report['mvp_signaler_total']}"
            ),
            "drivers_json": json.dumps(
                report.get("drivere", []),
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        }
        if save:
            _append_row(self.paths.signals, SIGNAL_FIELDS, row)
        return row

    def registrer_resultat(self, signal_id, spot, evaluated_at=None, save=True):
        evaluated_at = evaluated_at or datetime.now(timezone.utc)
        signals = {row["signal_id"]: row for row in self.laes_signaler()}
        if signal_id not in signals:
            raise ValueError(f"Ukendt signal-id: {signal_id}")
        if signal_id in {row["signal_id"] for row in self.laes_resultater()}:
            raise ValueError(f"Signalet {signal_id} er allerede evalueret")

        signal = signals[signal_id]
        due_date = date.fromisoformat(signal["evaluation_due_date"])
        if evaluated_at.date() < due_date:
            raise ValueError(
                f"Signalet kan først evalueres {due_date.isoformat()}"
            )

        start_price = float(signal["gold_price_start_usd_oz"])
        return_percent = round((spot.price_usd_oz / start_price - 1) * 100, 4)
        direction = signal["direction"]
        if direction == "OP":
            correct = return_percent > 0
        elif direction == "NED":
            correct = return_percent < 0
        else:
            correct = None

        row = {
            "signal_id": signal_id,
            "evaluated_at_utc": evaluated_at.isoformat(),
            "gold_price_end_usd_oz": spot.price_usd_oz,
            "gold_price_observed_at_utc": spot.observed_at_utc,
            "gold_source": spot.source,
            "return_percent": return_percent,
            "direction_correct": (
                "JA"
                if correct is True
                else "NEJ"
                if correct is False
                else "IKKE_RETNING"
            ),
        }
        if save:
            _append_row(self.paths.outcomes, OUTCOME_FIELDS, row)
        return row

    def laes_signaler(self):
        return _read_rows(self.paths.signals)

    def laes_resultater(self):
        return _read_rows(self.paths.outcomes)

    def status(self):
        evaluated = {row["signal_id"] for row in self.laes_resultater()}
        return [
            {**row, "status": "EVALUATED" if row["signal_id"] in evaluated else "PENDING"}
            for row in self.laes_signaler()
        ]


def _append_row(path, fieldnames, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def _read_rows(path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _tilfoej_maaned(value):
    zero_based = value.year * 12 + value.month
    year, month_zero = divmod(zero_based, 12)
    month = month_zero + 1
    day = min(value.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year, month):
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - date(year, month, 1)).days
