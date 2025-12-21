# Test des donnees medicales create

def test_create_donnee_missing_fields(client):
    """Test que la creation de donnee medicale sans champs requis retourne une erreur 400"""
    response = client.post("/v1/donnees", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_donnee_success(client, monkeypatch):
    """Test que la creation de donnee medicale avec des champs valides retourne 201"""
    fake_donnee = {
        "id": 1,
        "patient_id": 1,
        "capteur_id": 2,
        "valeur_mesuree": 36.7
    }

    monkeypatch.setattr(
        "app.routes.donnee_medical_route.create_donnee_medicale",
        lambda data: fake_donnee
    )

    monkeypatch.setattr(
        "app.routes.donnee_medical_route.serialize_donnee_medicale",
        lambda d: d
    )

    response = client.post(
        "/v1/donnees",
        json={"patient_id": 1, "capteur_id": 2, "valeur_mesuree": 36.7}
    )

    assert response.status_code == 201
    assert response.get_json()["donnee"]["valeur_mesuree"] == 36.7
