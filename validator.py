def validate_price(pris):
    """
    Simpel validator til Guldagent v1.
    Tjekker kun om prisen er gyldig.
    Ingen trend, ingen JSON-checks, ingen rapportlogik.
    """

    if pris is None:
        return False

    try:
        pris_float = float(pris)
    except (TypeError, ValueError):
        return False

    if pris_float <= 0:
        return False

    return True
