import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from guldagent_v2.goldapi_spot_client import GoldApiSpotClient, SpotPrice
from guldagent_v2.paper_journal import PaperJournal


def main():
    parser = argparse.ArgumentParser(description="Guldagent v2 paper trading-journal")
    parser.add_argument("--journal-dir", default="paper_trading")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record", help="Gem månedens signal")
    record.add_argument("--report", default="data/processed/latest_report.json")
    record.add_argument("--dry-run", action="store_true")
    record.add_argument("--test-price", type=float)

    evaluate = subparsers.add_parser("evaluate", help="Evaluer et modent signal")
    evaluate.add_argument("signal_id")
    evaluate.add_argument("--dry-run", action="store_true")
    evaluate.add_argument("--test-price", type=float)

    subparsers.add_parser("status", help="Vis journalens signaler og status")
    args = parser.parse_args()

    journal = PaperJournal(args.journal_dir)
    if args.command == "status":
        _print_status(journal)
        return

    if args.test_price is not None and not args.dry_run:
        raise ValueError("--test-price må kun bruges sammen med --dry-run")

    load_dotenv()
    spot = _hent_spot(args.test_price)
    now = datetime.now(timezone.utc)

    if args.command == "record":
        report = json.loads(Path(args.report).read_text(encoding="utf-8"))
        row = journal.registrer_signal(
            report,
            spot,
            _git_commit(),
            recorded_at=now,
            save=not args.dry_run,
        )
        prefix = "DRY RUN – ville registrere" if args.dry_run else "Registrerede"
        print(f"{prefix} signal {row['signal_id']}")
        print(f"Retning: {row['direction']} | Score: {float(row['score']):+.3f}")
        print(f"Startpris: {float(row['gold_price_start_usd_oz']):.2f} USD/oz")
        print(f"Evalueres tidligst: {row['evaluation_due_date']}")
        return

    row = journal.registrer_resultat(
        args.signal_id,
        spot,
        evaluated_at=now,
        save=not args.dry_run,
    )
    prefix = "DRY RUN – ville evaluere" if args.dry_run else "Evaluerede"
    print(f"{prefix} signal {row['signal_id']}")
    print(f"Afkast: {float(row['return_percent']):+.4f}%")
    print(f"Retning korrekt: {row['direction_correct']}")


def _hent_spot(test_price):
    if test_price is not None:
        if test_price <= 0:
            raise ValueError("--test-price skal være større end nul")
        return SpotPrice(
            test_price,
            datetime.now(timezone.utc).isoformat(),
            source="TESTPRIS",
        )
    return GoldApiSpotClient(os.getenv("GOLD_API_KEY")).hent_spotpris()


def _git_commit():
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "ukendt"


def _print_status(journal):
    rows = journal.status()
    if not rows:
        print("Signaljournalen er tom.")
        return
    for row in rows:
        print(
            f"{row['signal_id']}: {row['direction']} {float(row['score']):+.3f} "
            f"| {row['status']} | evaluering {row['evaluation_due_date']}"
        )


if __name__ == "__main__":
    main()
