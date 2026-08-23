from dotenv import load_dotenv
load_dotenv()
import os

from scraper import hent_guldpris_dkk_pr_gram
from validator import validate_price
from calculator import beregn_priser
from formatter import format_text
from mailer import send_mail
from logger import log_price

def run_guldagent_v1():
    print("Guldagent v1 kører…")

    # 1. Hent guldpris
    pris = hent_guldpris_dkk_pr_gram()

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

    send_mail(subject, body_html, receiver)

    # 6. Log pris
    log_price(pris)

    print("Mail sendt!")
    print("Guldagent v1 afsluttet.")

if __name__ == "__main__":
    run_guldagent_v1()
