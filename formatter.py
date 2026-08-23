def format_text(pris, karat_priser):
    """
    Simpel formatter til Guldagent v1.
    Returnerer ren tekst uden HTML, LLM eller rapport.
    """

    tekst = (
        f"Dagens guldpris: {pris} kr/gram\n\n"
        f"- 20 % 18 karat: {karat_priser.get('18k')} kr\n"
        f"- 20 % 14 karat: {karat_priser.get('14k')} kr\n"
        f"- 20 % 8 karat: {karat_priser.get('8k')} kr\n"
    )

    return tekst
