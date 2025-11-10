from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func
from app.models import Medecin
from flasgger import swag_from
from app.utils.validation import validate_fields
from app.utils.serializers import serialize_medecin
from flask_jwt_extended import jwt_required
from app.services.medecin_service import (
    create_medecin,
    get_all_medecins,
    get_medecin_by_id,
    get_medecin_by_email,
    update_medecin,
    delete_medecin
)

medecin_bp = Blueprint("medecin_bp", __name__, url_prefix="/v1")

# -------------------------------------------------------------
# Route POST /medecins : créer un médecin
# -------------------------------------------------------------
@medecin_bp.route("/medecins", methods=["POST"])
@swag_from({
    'tags': ['v1 - Médecins'],
    'summary': 'Créer un médecin',
    'description': 'Crée un nouveau médecin en héritant du modèle Personne.',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'nom': {'type': 'string', 'example': 'Anzize'},
                'prenom': {'type': 'string', 'example': 'Mohamed'},
                'email': {'type': 'string', 'example': 'anzize@gmedical.sn'},
                'mot_de_passe': {'type': 'string', 'example': 'Passer123'},
                'adresse': {'type': 'string', 'example': 'Rue 12, Dakar'},
                'date_naissance': {'type': 'string', 'format': 'date', 'example': '1990-05-12'},
                'specialite': {'type': 'string', 'example': 'Cardiologie'}
            },
            'required': ['nom', 'prenom', 'email', 'mot_de_passe', 'specialite']
        }
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': 'Médecin créé avec succès'},
        400: {'description': 'Champs manquants'},
        409: {'description': 'Email déjà utilisé'},
        500: {'description': 'Erreur serveur'}
    }
})
@jwt_required()
def create_medecin_route():
    data = request.get_json()
    required = ["nom", "prenom", "email", "mot_de_passe", "specialite"]

    if not validate_fields(data, required):
        return jsonify({"error": "Tous les champs sont requis"}), 400

    if get_medecin_by_email(data["email"]):
        return jsonify({"error": "Email déjà utilisé"}), 409

    try:
        medecin = create_medecin(data)
        return jsonify({"message": "Médecin créé avec succès"}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": "Erreur serveur"}), 500

# -------------------------------------------------------------
# Route GET /medecins : lister tous les médecins
# -------------------------------------------------------------
@medecin_bp.route("/medecins", methods=["GET"])
@swag_from({
    'tags': ['v1 - Médecins'],
    'summary': 'Lister tous les médecins',
    'description': 'Retourne la liste complète des médecins enregistrés.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Liste des médecins',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'nom': {'type': 'string'},
                        'prenom': {'type': 'string'},
                        'email': {'type': 'string'},
                        'specialite': {'type': 'string'}
                    }
                }
            }
        }
    }
})
@jwt_required()
def get_all_medecins_route():
    medecins = get_all_medecins()
    return jsonify([serialize_medecin(m) for m in medecins]), 200

# -------------------------------------------------------------
# Route GET /medecins/search : rechercher des médecins
# -------------------------------------------------------------
@medecin_bp.route("/medecins/search", methods=["GET"])
@swag_from({
    'tags': ['v1 - Médecins'],
    'summary': 'Rechercher des médecins',
    'description': 'Recherche un médecin par nom, prénom, spécialité ou email.',
    'parameters': [{
        'name': 'q',
        'in': 'query',
        'type': 'string',
        'required': True,
        'description': 'Mot-clé à rechercher (nom, spécialité ou email)'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Médecins correspondants'}
    }
})
@jwt_required()
def search_medecins_route():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify([]), 200

    medecins = Medecin.query.filter(
        or_(
            func.lower(Medecin.nom).like(f"%{q}%"),
            func.lower(Medecin.prenom).like(f"%{q}%"),
            func.lower(Medecin.email).like(f"%{q}%"),
            func.lower(Medecin.specialite).like(f"%{q}%")
        )
    ).all()
    return jsonify([serialize_medecin(m) for m in medecins]), 200

# -------------------------------------------------------------
# Route GET /medecins/<id> : récupérer un médecin par ID
# -------------------------------------------------------------
@medecin_bp.route("/medecins/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['v1 - Médecins'],
    'summary': 'Récupérer un médecin par ID',
    'description': 'Retourne les informations d’un médecin spécifique.',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du médecin'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Médecin trouvé'},
        404: {'description': 'Médecin introuvable'}
    }
})
@jwt_required()
def get_medecin_route(id):
    medecin = get_medecin_by_id(id)
    if not medecin:
        return jsonify({"error": "Médecin introuvable"}), 404
    return jsonify(serialize_medecin(medecin)), 200

# -------------------------------------------------------------
# Route PUT /medecins/<id> : mettre à jour un médecin
# -------------------------------------------------------------
@medecin_bp.route("/medecins/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['v1 - Médecins'],
    'summary': 'Mettre à jour un médecin',
    'description': 'Modifie les informations d’un médecin existant.',
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'nom': {'type': 'string'},
                    'prenom': {'type': 'string'},
                    'email': {'type': 'string'},
                    'adresse': {'type': 'string'},
                    'specialite': {'type': 'string'}
                }
            }
        }
    ],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Médecin mis à jour'},
        404: {'description': 'Médecin introuvable'}
    }
})
@jwt_required()
def update_medecin_route(id):
    medecin = get_medecin_by_id(id)
    if not medecin:
        return jsonify({"error": "Médecin introuvable"}), 404

    data = request.get_json()
    update_medecin(medecin, data)
    return jsonify({"message": "Médecin mis à jour"}), 200

# -------------------------------------------------------------
# Route DELETE /medecins/<id> : supprimer un médecin
# -------------------------------------------------------------
@medecin_bp.route("/medecins/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['v1 - Médecins'],
    'summary': 'Supprimer un médecin',
    'description': 'Supprime un médecin de la base de données.',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du médecin à supprimer'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Médecin supprimé'},
        404: {'description': 'Médecin introuvable'}
    }
})
@jwt_required()
def delete_medecin_route(id):
    medecin = get_medecin_by_id(id)
    if not medecin:
        return jsonify({"error": "Médecin introuvable"}), 404

    delete_medecin(medecin)
    return jsonify({"message": "Médecin supprimé"}), 200