# Test pour verifier que la tentative de connexion sans les champs requis renvoie une erreur 400.

from app import create_app

def test_login_missing_fields():
    app = create_app()
    client = app.test_client()

    response = client.post("/v1/auth/login", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()
