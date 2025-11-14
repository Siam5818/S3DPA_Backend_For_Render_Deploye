def validate_fields(data, required_fields):
    """
    Vérifie que tous les champs requis sont présents et non vides.
    Compatible: string, int, float, bool.
    """
    for field in required_fields:
        if field not in data:
            return False

        value = data[field]

        # Cas None
        if value is None:
            return False

        # Cas string : vérifier non vide
        if isinstance(value, str):
            if value.strip() == "":
                return False

        # Cas int / float : juste vérifier que c'est bien un nombre
        if isinstance(value, (int, float)):
            continue  # OK automatiquement

        # Autres types, on accepte aussi (bool, obj, etc.)
    return True
