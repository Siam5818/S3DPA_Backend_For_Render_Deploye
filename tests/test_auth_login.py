# Test pour verifier que la tentative de connexion sans les champs requis renvoie une erreur 400.

def test_login_missing_fields(client):
    """Test que la connexion sans champs requis retourne une erreur 400"""
    response = client.post("/v1/auth/login", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()
