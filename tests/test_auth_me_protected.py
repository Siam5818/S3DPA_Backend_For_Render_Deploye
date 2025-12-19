# Test pour verifier que l'acces a l'endpoint protege /v1/auth/me sans authentification renvoie une erreur 401.
from app.__init__ import create_app

def test_me_requires_auth():
    app = create_app()
    client = app.test_client()

    response = client.get("/v1/auth/me")

    assert response.status_code == 401
