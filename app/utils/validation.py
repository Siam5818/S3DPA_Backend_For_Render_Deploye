def validate_fields(data, required_fields):
    """
    Vérifie que tous les champs requis sont présents et non vides.
    :param data: dictionnaire (ex: request.form ou request.json)
    :param required_fields: liste des clés attendues
    :return: True si tous les champs sont valides, False sinon
    """
    return all(field in data and data[field].strip() != "" for field in required_fields)

