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

git clone https://github.com/Capacode-dev/Guldagent_v1.git
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

GOLD_API_KEY=<goldapi-nøgle>
BRIDGE_USERNAME=<bridge-email>
BRIDGE_PASSWORD=<bridge-password>
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

Test hele beregningen uden live API og uden at sende mail:

```bash
python agent_v1.py --dry-run --test-pris 750
```

Kontrollér at miljøvariablerne findes uden at vise deres indhold:

```bash
python check_env.py
```

---

## 6. Push til Git

git add .
git commit -m "Tilføjet README og HTML-layout"
git push
