# Importation de la fonction pour générer un token JWT
from flask_jwt_extended import create_access_token

# Importation du modèle Personne (classe mère des utilisateurs)
from app.models.personne import Personne
import json


# -------------------------------------------------------------
# Fonction authenticate_user : vérifie les identifiants
# -------------------------------------------------------------
# - Recherche l'utilisateur par email
# - Vérifie que le mot de passe correspond via la méthode check_password
# - Retourne l'objet utilisateur si les identifiants sont valides, sinon None
def authenticate_user(email, mot_de_passe):
    user = Personne.query.filter_by(email=email).first()
    if user and user.check_password(mot_de_passe):
        return user
    return None

# -------------------------------------------------------------
# Fonction generate_token : génère un JWT pour l'utilisateur
# -------------------------------------------------------------
# - Crée un token contenant l'identité (id + rôle)
# - Sert à authentifier l'utilisateur dans les requêtes futures
def generate_token(user):
    identity = json.dumps({"id": user.id, "role": user.role})
    return create_access_token(identity=identity)


# -------------------------------------------------------------
# Fonction format_user_response : structure les infos du user
# -------------------------------------------------------------
# - Prépare un dictionnaire avec les données essentielles du user
# - Sert à renvoyer une réponse claire au frontend après login
def format_user_response(user):
    base = {
        "id": user.id,
        "nom": user.nom,
        "prenom": user.prenom,
        "email": user.email,
        "role": user.role
    }

    if user.role == "medecin":
        base["specialite"] = getattr(user, "specialite", None)

    elif user.role == "patient":
        base["date_naissance"] = (
            user.date_naissance.isoformat() if user.date_naissance else None
        )
        base["adresse"] = getattr(user, "adresse", None)

    return base

def get_user_by_id(user_id):
    return Personne.query.get(user_id)
    

# -------------------------------------------------------------
# auth_service.py : logique métier liée à l'authentification
# -------------------------------------------------------------
# - Vérifie les identifiants
# - Génère le token JWT
# - Prépare les données utilisateur à renvoyer