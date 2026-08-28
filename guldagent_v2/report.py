import json
from dataclasses import asdict
from pathlib import Path

from guldagent_v2.features import FEATURES
from guldagent_v2.data_sources import MVP_COLUMNS
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
        "signalstyrke": resultat.signalstyrke,
        "datadaekning_fuld_model": resultat.datadaekning,
        "mvp_signaler_brugt": len(set(resultat.bidrag) & set(MVP_COLUMNS)),
        "mvp_signaler_total": len(MVP_COLUMNS),
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
        f"**Signalstyrke:** {rapport['signalstyrke']}%",
        f"**MVP-dækning:** {rapport['mvp_signaler_brugt']}/{rapport['mvp_signaler_total']}",
        f"**Fuld modeldækning:** {rapport['datadaekning_fuld_model']}%",
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
            antal = backtest["retningssignaler"][horisont]
            lines.append(
                f"- {horisont} observationer: {accuracy:.2f}% træfsikkerhed "
                f"({antal} OP/NED-signaler)"
            )
        lines.extend(["", "Sammenligningsbaseline (altid OP på de samme datoer):", ""])
        for horisont, baseline in backtest["altid_op_baseline"].items():
            lines.append(f"- {horisont} observationer: {baseline:.2f}%")
        lines.extend(["", f"Signalfordeling: {backtest['signalfordeling']}"])

    gold = rapport.get("gulddata")
    if gold:
        lines.extend(
            [
                "",
                "## Historiske backtestdata",
                "",
                f"- Guldkilde: {gold['kilde']}",
                f"- Rolle: {gold['rolle']}",
                f"- Periode: {gold['foerste_dato']} til {gold['seneste_dato']}",
                f"- Observationer: {gold['antal_observationer']}",
                "- Serien bruges ikke som aktuel guldpris.",
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
