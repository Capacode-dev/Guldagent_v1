# Guldagent v1
# Guldagent v1

![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![Scraper](ca://s?q=Hvad_er_scraper_badge)
![Mail](ca://s?q=Hvad_er_mail_badge)
![Formatter](ca://s?q=Hvad_er_formatter_badge)
![Automation](ca://s?q=Hvad_er_cron_badge)

Automatiseret agent der henter guldpris, beregner karatpriser og sender dem som mail.

---

## 1. Klon projektet

git clone <repo-url>
cd Guldagent_v1

---

## 2. Opret og aktiver virtual environment

python3 -m venv venv312
source venv312/bin/activate

Windows:

python -m venv venv312
venv312\Scripts\activate

---

## 3. Installer afhængigheder

pip install -r requirements.txt

---

## 4. Opret .env fil

SMTP_USER=<bridge-email>
SMTP_PASS=<bridge-password>
HEMMELIG_MODTAGER=<modtager-mail>
HEMMELIG_FAKTOR_ARBEJDE=2.5

---

## 5. Kør agenten

python agent_v1.py

Agenten gør:
- henter pris
- validerer pris
- beregner karatpriser
- laver HTML-layout
- sender mail
- logger pris

---

## 6. Push til Git

git add .
git commit -m "Tilføjet README og HTML-layout"
git push
