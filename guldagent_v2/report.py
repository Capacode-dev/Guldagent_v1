import json
from dataclasses import asdict
from pathlib import Path

from guldagent_v2.features import FEATURES
from guldagent_v2.signal_model import vigtigste_drivere


def byg_rapport(dato, resultat, backtest=None, llm_analyse=None, gold_status=None):
    drivere = [
        {
            "noegle": noegle,
            "navn": FEATURES[noegle].navn,
            "bidrag": round(bidrag, 4),
        }
        for noegle, bidrag in vigtigste_drivere(resultat, antal=5)
    ]
    rapport = {
        "dato": dato,
        "retning": resultat.retning,
        "score": resultat.score,
        "sikkerhed": resultat.sikkerhed,
        "drivere": drivere,
        "manglende_variable": resultat.mangler,
        "backtest": asdict(backtest) if backtest else None,
        "gulddata": gold_status,
        "llm_analyse": asdict(llm_analyse) if llm_analyse else None,
        "disclaimer": "Modelsignal til analyse og læring; ikke en garanti eller personlig investeringsrådgivning.",
    }
    return rapport


def gem_rapport(rapport, output_dir="data/processed"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "latest_report.json"
    md_path = output_dir / "latest_report.md"

    json_path.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_til_markdown(rapport), encoding="utf-8")
    return json_path, md_path


def _til_markdown(rapport):
    lines = [
        "# Guldagent v2 – analyserapport",
        "",
        f"**Dato:** {rapport['dato']}",
        f"**Retning:** {rapport['retning']}",
        f"**Score:** {rapport['score']:+.3f}",
        f"**Foreløbig sikkerhed:** {rapport['sikkerhed']}%",
        "",
        "## Vigtigste drivere",
        "",
    ]
    for driver in rapport["drivere"]:
        lines.append(f"- {driver['navn']}: {driver['bidrag']:+.3f}")

    backtest = rapport.get("backtest")
    if backtest:
        lines.extend(["", "## Backtest", "", f"Antal signaler: {backtest['antal_signaler']}", ""])
        for horisont, accuracy in backtest["traefsikkerhed"].items():
            lines.append(f"- {horisont} observationer: {accuracy:.2f}% træfsikkerhed")

    gold = rapport.get("gulddata")
    if gold:
        status = "forældet" if gold["foraeldet"] else "aktuel"
        lines.extend(
            [
                "",
                "## Datakvalitet",
                "",
                f"- Guldkilde: {gold['kilde']}",
                f"- Seneste guldobservation: {gold['seneste_dato']}",
                f"- Status: {status} ({gold['alder_dage']} dage gammel)",
            ]
        )

    llm = rapport.get("llm_analyse")
    if llm:
        lines.extend(["", "## LLM-forklaring", "", llm["opsummering"]])
        lines.extend(["", "### Positive faktorer", ""])
        lines.extend(f"- {item}" for item in llm["positive_faktorer"])
        lines.extend(["", "### Negative faktorer", ""])
        lines.extend(f"- {item}" for item in llm["negative_faktorer"])
        lines.extend(["", "### Usikkerheder", ""])
        lines.extend(f"- {item}" for item in llm["usikkerheder"])
        lines.extend(["", "### Konklusion", "", llm["konklusion"]])

    lines.extend(["", "---", "", rapport["disclaimer"], ""])
    return "\n".join(lines)
