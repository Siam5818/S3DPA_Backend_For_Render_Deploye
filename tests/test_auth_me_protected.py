# Test pour verifier que l'acces a l'endpoint protege /v1/auth/me sans authentification renvoie une erreur 401.

def test_me_requires_auth(client):
    """Test que l'accès à /v1/auth/me sans authentification retourne 401"""
    response = client.get("/v1/auth/me")

    assert response.status_code == 401
