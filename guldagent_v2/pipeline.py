from dataclasses import dataclass
from datetime import date
from pathlib import Path

from guldagent_v2.analyze_latest import analyser_seneste
from guldagent_v2.backtest import koer_backtest
from guldagent_v2.build_gold_history import gem_guldhistorik
from guldagent_v2.dataset import byg_mvp_dataset
from guldagent_v2.llm_analysis import lav_llm_analyse
from guldagent_v2.normalizer import normaliser_dataset
from guldagent_v2.report import byg_rapport, gem_rapport


@dataclass(frozen=True)
class PipelineResultat:
    dato: str
    retning: str
    score: float
    rapport_json: Path
    rapport_markdown: Path
    backtest_signaler: int
    llm_brugt: bool


def koer_mvp_pipeline(
    fred_client,
    gold_client,
    startdato="2025-01-01",
    slutdato=None,
    output_dir="data",
    llm_client=None,
    llm_model="gpt-5.4-mini",
):
    output_dir = Path(output_dir)
    processed_dir = output_dir / "processed"
    input_dir = output_dir / "input"

    macro_path = byg_mvp_dataset(fred_client, startdato, slutdato, output_dir)
    signal_path = normaliser_dataset(macro_path, processed_dir / "macro_signals.csv")

    guldpriser = gold_client.hent_daglige_priser(startdato, slutdato)
    if not guldpriser:
        raise RuntimeError("Guldkilden returnerede ingen daglige priser")
    gold_path = gem_guldhistorik(guldpriser, input_dir / "gold_history.csv")

    _, backtest = koer_backtest(
        signal_path,
        gold_path,
        processed_dir / "backtest_results.csv",
    )
    dato, signal_resultat = analyser_seneste(signal_path)

    llm_analyse = None
    if llm_client:
        llm_analyse = lav_llm_analyse(signal_resultat, dato, llm_client, llm_model)

    seneste_gulddato = guldpriser[-1][0]
    alder = (date.today() - date.fromisoformat(seneste_gulddato)).days
    gold_status = {
        "kilde": "FreeGoldAPI / yahoo_finance",
        "antal_observationer": len(guldpriser),
        "seneste_dato": seneste_gulddato,
        "alder_dage": alder,
        "foraeldet": alder > 7,
    }
    rapport = byg_rapport(dato, signal_resultat, backtest, llm_analyse, gold_status)
    json_path, md_path = gem_rapport(rapport, processed_dir)

    return PipelineResultat(
        dato=dato,
        retning=signal_resultat.retning,
        score=signal_resultat.score,
        rapport_json=json_path,
        rapport_markdown=md_path,
        backtest_signaler=backtest.antal_signaler,
        llm_brugt=llm_analyse is not None,
    )

