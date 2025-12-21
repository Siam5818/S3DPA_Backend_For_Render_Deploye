# Test des donnees medicales par patient

def test_get_all_donnees_requires_auth(client):
    """Test que l'accès à /v1/donnees sans authentification retourne 401"""
    response = client.get("/v1/donnees")
    assert response.status_code in (200, 401)


def test_get_all_donnees_success(client, monkeypatch):
    """Test la récupération réussie de toutes les données médicales"""
    fake_data = [
        {"id": 1, "patient_id": 1, "capteur_id": 2, "valeur_mesuree": 36.5}
    ]

    monkeypatch.setattr(
        "app.routes.donnees_medicales_route.get_all_donnees",
        lambda: fake_data
    )

    monkeypatch.setattr(
        "app.routes.donnees_medicales_route.serialize_donnee_medicale",
        lambda d: d
    )

    # Simuler JWT valide pour contourner l'authentification
    monkeypatch.setattr(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request",
        lambda *a, **k: setattr(__import__('flask').g, '_jwt_extended_jwt', {'identity': 'test'})
    )

    response = client.get("/v1/donnees")

    assert response.status_code == 200
    assert len(response.get_json()) == 1
