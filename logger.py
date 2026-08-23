import csv
from datetime import datetime

def log_price(pris):
    """
    Simpel logger til Guldagent v1.
    Logger kun dato og pris i en CSV-fil.
    Ingen HTML, ingen rapport, ingen trend.
    """

    dato = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open("guld_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([dato, pris])
    except Exception as e:
        print(f"Fejl ved logning: {e}")
