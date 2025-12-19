# Test pour verifier qu'une connexion reussie retourne le token et les informations utilisateur correctes.
from app.__init__ import create_app

def test_login_success(monkeypatch):
    app = create_app()
    client = app.test_client()

    fake_user = {"id": 1, "email": "test@test.com"}

    monkeypatch.setattr(
        "app.services.auth_service.authenticate_user",
        lambda email, password: fake_user
    )

    monkeypatch.setattr(
        "app.services.auth_service.generate_token",
        lambda user: "fake-jwt-token"
    )

    monkeypatch.setattr(
        "app.services.auth_service.format_user_response",
        lambda user: user
    )

    response = client.post(
        "/v1/auth/login",
        json={"email": "test@test.com", "password": "1234"}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["token"] == "fake-jwt-token"
    assert data["user"]["email"] == "test@test.com"
