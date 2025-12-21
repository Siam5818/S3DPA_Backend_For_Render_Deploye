# Test des donnees medicales par patient

def test_get_donnees_by_patient_not_found(client, monkeypatch):
    """Test que la récupération des données médicales pour un patient inexistant retourne 404"""
    monkeypatch.setattr(
        "app.routes.donnees_medicales_route.get_donnees_by_patient",
        lambda patient_id: []
    )

    # Simuler JWT valide pour contourner l'authentification
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **k: setattr(__import__('flask').g, '_jwt_extended_jwt', {'identity': 'test'})
    )

    response = client.get("/v1/donnees/patient/99")
    assert response.status_code == 404


def test_get_stats_by_patient_success(client, monkeypatch):
    """Test que la récupération des statistiques des données médicales pour un patient retourne 200"""
    fake_stats = [
        {"capteur": "Température", "min": 35.9, "max": 38.2, "moyenne": 36.8}
    ]

    monkeypatch.setattr(
        "app.routes.donnees_medicales_route.get_stats_by_patient",
        lambda patient_id: fake_stats
    )

    # Simuler JWT valide pour contourner l'authentification
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **k: setattr(__import__('flask').g, '_jwt_extended_jwt', {'identity': 'test'})
    )

    response = client.get("/v1/donnees/patient/1/stats")

    assert response.status_code == 200
    assert response.get_json()[0]["capteur"] == "Température"
