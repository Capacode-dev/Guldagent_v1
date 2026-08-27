import json
from dataclasses import dataclass

from guldagent_v2.features import FEATURES
from guldagent_v2.signal_model import vigtigste_drivere


ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "opsummering": {"type": "string"},
        "positive_faktorer": {"type": "array", "items": {"type": "string"}},
        "negative_faktorer": {"type": "array", "items": {"type": "string"}},
        "usikkerheder": {"type": "array", "items": {"type": "string"}},
        "konklusion": {"type": "string"},
    },
    "required": [
        "opsummering",
        "positive_faktorer",
        "negative_faktorer",
        "usikkerheder",
        "konklusion",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class LlmAnalyse:
    opsummering: str
    positive_faktorer: list[str]
    negative_faktorer: list[str]
    usikkerheder: list[str]
    konklusion: str


def lav_llm_analyse(resultat, dato, client, model="gpt-5.4-mini"):
    """Forklar et beregnet signal uden at lade LLM'en ændre resultatet."""
    drivere = [
        {
            "variabel": FEATURES[noegle].navn,
            "bidrag": round(bidrag, 4),
            "forklaring": FEATURES[noegle].forklaring,
        }
        for noegle, bidrag in vigtigste_drivere(resultat, antal=5)
    ]
    input_data = {
        "dato": dato,
        "beregnet_retning": resultat.retning,
        "score": resultat.score,
        "foreloebig_sikkerhed_procent": resultat.sikkerhed,
        "antal_manglende_variable": len(resultat.mangler),
        "drivere": drivere,
    }
    instructions = (
        "Du er forklaringslaget i Guldagent v2. Forklar kun de leverede tal på dansk. "
        "Du må ikke ændre beregnet retning eller score, opfinde markedsdata eller give "
        "personlig investeringsrådgivning. Fremhæv datamangler og modstridende faktorer. "
        "Konklusionen skal udtrykkeligt sige, at analysen er et modelsignal og ikke en garanti."
    )
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=json.dumps(input_data, ensure_ascii=False),
        text={
            "format": {
                "type": "json_schema",
                "name": "guldagent_analyse",
                "strict": True,
                "schema": ANALYSIS_SCHEMA,
            }
        },
        store=False,
    )
    data = json.loads(response.output_text)
    return LlmAnalyse(**data)

