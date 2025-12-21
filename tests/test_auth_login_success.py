# Test pour verifier qu'une connexion reussie retourne le token et les informations utilisateur correctes.

def test_login_success(client, monkeypatch):
    """Test qu'une connexion réussie retourne le token et les infos utilisateur"""
    fake_user = {"id": 1, "email": "test@test.com"}

    # Patch where the functions are used, not where they're defined
    monkeypatch.setattr(
        "app.routes.auth_routes.authenticate_user",
        lambda email, password: fake_user
    )

    monkeypatch.setattr(
        "app.routes.auth_routes.generate_token",
        lambda user: "fake-jwt-token"
    )

    monkeypatch.setattr(
        "app.routes.auth_routes.format_user_response",
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
