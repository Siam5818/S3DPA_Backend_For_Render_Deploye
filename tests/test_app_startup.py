# Test de sante de demarrage de l'application sans erreur.
def test_app_startup(client):
    """Test que l'application démarre sans erreur"""
    assert client is not None