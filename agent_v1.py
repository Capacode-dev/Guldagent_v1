from dotenv import load_dotenv
load_dotenv()
import os
import argparse

from scraper import hent_guldpris_dkk_pr_gram
from validator import validate_price
from calculator import beregn_priser
from formatter import format_text
from mailer import send_mail
from logger import log_price

def run_guldagent_v1(dry_run=False, test_pris=None):
    print("Guldagent v1 kører…")

    # 1. Hent guldpris
    pris = test_pris if test_pris is not None else hent_guldpris_dkk_pr_gram()

    # 2. Valider pris
    if not validate_price(pris):
        print("Ugyldig pris hentet – afbryder.")
        return

    # 3. Beregn karatpriser
    karat_priser = beregn_priser(pris)

    # 4. Formatér HTML-tekst til mail
    body_html = format_text(pris, karat_priser)

    # 5. Send mail
    subject = "Dagens guldpriser"
    receiver = os.getenv("HEMMELIG_MODTAGER")

    if dry_run:
        print("DRY RUN: Mail blev ikke sendt.")
        print(body_html)
    else:
        if not receiver:
            print("HEMMELIG_MODTAGER mangler – afbryder før mailafsendelse.")
            return
        send_mail(subject, body_html, receiver)

    # 6. Log kun rigtige kørsler
    if not dry_run:
        log_price(pris)

    if not dry_run:
        print("Mail sendt!")
    print("Guldagent v1 afsluttet.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hent og beregn dagens guldpriser.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Kør uden at sende mail.",
    )
    parser.add_argument(
        "--test-pris",
        type=float,
        help="Brug en lokal testpris i stedet for GoldAPI.",
    )
    args = parser.parse_args()
    run_guldagent_v1(dry_run=args.dry_run, test_pris=args.test_pris)
