def is_fragment_quote(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True

    if len(t) < 25:
        return True

    tl = t.lower()

    if tl.startswith((
        "and ", "but ", "or ", "so ", "because ", "then ", "when ", "while ",
        "as ", "if ", "that ", "which ", "who ", "whom ", "with ", "without ",
        "to ", "of ", "for ", "in ", "on ", "at ", "from ", "by ", "into ",
        "over ", "under ", "after ", "before "
    )):
        return True

    if t[0] in ",.;:)]}»”’—-":
        return True

    if t[0].islower():
        return True

    return False


def is_valid_highlight(text: str, final_type: int) -> bool:
    """
    Regra única de aceitação de highlights
    (usada por Quotes e Vocabulary).
    """

    # Quote sem NOTE / TYPE continua válida.
    # Fragmentação é heurística de qualidade, não critério de exclusão.
    if not (text or "").strip():
        return False

    return True
