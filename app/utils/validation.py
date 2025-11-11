def validate_fields(data, required_fields):
    """
    Vérifie que tous les champs requis sont présents et non vides.
    Compatible avec les types str, int, float, bool.
    """
    if not isinstance(data, dict):
        return False

    for field in required_fields:
        if field not in data:
            return False

        value = data[field]

        # Cas None
        if value is None:
            return False

        # Cas string vide
        if isinstance(value, str) and not value.strip():
            return False

        # Cas numérique : on accepte 0, mais pas un champ absent
        if isinstance(value, (int, float)) and str(value).strip() == "":
            return False

        # Cas booléen : False est accepté, mais pas None
        if isinstance(value, bool):
            continue

    return True
