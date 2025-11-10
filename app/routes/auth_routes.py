from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.auth_service import (
    authenticate_user,
    generate_token,
    format_user_response,
    get_user_by_id
)
from app.extension import blacklist # Pour la gestion de la blacklist des tokens
import json

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/v1/auth")

# -------------------------------------------------------------
# Route /login : authentifie l'utilisateur et renvoie un token
# -------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
@swag_from({
    'tags': ['v1 - Authentification'],
    'summary': 'Connexion utilisateur',
    'description': 'Permet à un médecin, un patient ou un proche de se connecter avec email et mot de passe.',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'example': 'user@example.com'},
                'password': {'type': 'string', 'example': 'Passer123'}
            },
            'required': ['email', 'password']
        }
    }],
    'responses': {
        200: {
            'description': 'Connexion réussie',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'token': {'type': 'string'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'nom': {'type': 'string'},
                            'prenom': {'type': 'string'},
                            'email': {'type': 'string'},
                            'role': {'type': 'string', 'enum': ['medecin', 'patient', 'proche']}
                        }
                    }
                }
            }
        },
        400: {'description': 'Champs manquants'},
        401: {'description': 'Identifiants invalides'}
    }
})
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    user = authenticate_user(email, password)
    if not user:
        return jsonify({"error": "Identifiants invalides"}), 401

    token = generate_token(user)
    return jsonify({
        "message": "Connexion réussie",
        "token": token,
        "user": format_user_response(user)
    }), 200

# -------------------------------------------------------------
# Route /me : renvoie les infos du user connecté via JWT
# -------------------------------------------------------------
@swag_from({
    'tags': ['v1 - Authentification'],
    'summary': 'Profil utilisateur connecté',
    'description': 'Renvoie les informations du médecin, patient ou proche actuellement connecté via le token JWT.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Informations du user connecté',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'example': 1},
                    'nom': {'type': 'string', 'example': 'Anzize'},
                    'prenom': {'type': 'string', 'example': 'Mohamed'},
                    'email': {'type': 'string', 'example': 'anzize@gmedical.sn'},
                    'role': {'type': 'string', 'enum': ['medecin', 'patient', 'proche'], 'example': 'medecin'}
                }
            }
        },
        401: {'description': 'Token manquant ou invalide'},
        404: {'description': 'Utilisateur introuvable'}
    }
})
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    identity_raw = get_jwt_identity()
    identity = json.loads(identity_raw) 
    
    user = get_user_by_id(identity["id"])

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify(format_user_response(user)), 200

# -------------------------------------------------------------
# Route /logout : déconnexion (invalide le token courant)
# -------------------------------------------------------------
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Authentification'],
    'summary': 'Déconnexion utilisateur',
    'description': 'Invalide le token JWT en cours en l’ajoutant à la blacklist.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Déconnexion réussie'},
        401: {'description': 'Token manquant ou invalide'}
    }
})
def logout():
    jti = get_jwt()["jti"]   # identifiant unique du token
    blacklist.add(jti)       # ajout dans la blacklist
    return jsonify({"message": "Déconnexion réussie"}), 200

# -------------------------------------------------------------
# auth_routes.py : routes liées à l'authentification
# -------------------------------------------------------------
# - /login : connexion utilisateur avec JWT
# - /me : récupération des infos du user connecté via le token
# - /logout : déconnexion et invalidation du token JWT
