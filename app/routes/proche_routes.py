from app.extension import db
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from sqlalchemy import or_, func
from app.models import Proche
from app.utils.validation import validate_fields
from app.utils.serializers import serialize_proche
from flask_jwt_extended import jwt_required
from app.services.proche_service import (
    create_proche,
    get_all_proches,
    get_proche_by_id,
    update_proche,
    delete_proche
)

proche_bp = Blueprint("proche_bp", __name__, url_prefix="/v1")

# -------------------------------------------------------------
# Route POST /proches : créer un proche
# -------------------------------------------------------------
@proche_bp.route("/proches", methods=["POST"])
@swag_from({
    'tags': ['v1 - Proches'],
    'summary': 'Créer un proche',
    'description': 'Crée un proche lié à un patient existant.',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'lien_parente': {'type': 'string', 'example': 'Frère'},
                'patient_id': {'type': 'integer', 'example': 1}
            },
            'required': ['lien_parente', 'patient_id']
        }
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': 'Proche créé avec succès'},
        400: {'description': 'Champs manquants'},
        500: {'description': 'Erreur serveur'}
    }
})
@jwt_required()
def create_proche_route():
    data = request.get_json()
    required = ["lien_parente", "patient_id"]

    if not validate_fields(data, required):
        return jsonify({"error": "Tous les champs sont requis"}), 400

    try:
        proche = create_proche(data)
        return jsonify({"message": "Proche créé avec succès"}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": "Erreur serveur"}), 500

# -------------------------------------------------------------
# Route GET /proches : lister tous les proches
# -------------------------------------------------------------
@proche_bp.route("/proches", methods=["GET"])
@swag_from({
    'tags': ['v1 - Proches'],
    'summary': 'Lister tous les proches',
    'description': 'Retourne la liste complète des proches enregistrés.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Liste des proches',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'lien_parente': {'type': 'string'},
                        'patient_id': {'type': 'integer'}
                    }
                }
            }
        }
    }
})
@jwt_required()
def get_all_proches_route():
    proches = get_all_proches()
    result = [serialize_proche(p) for p in proches]
    return jsonify(result), 200

# -------------------------------------------------------------
# Route GET /proches/search : rechercher des proches
# -------------------------------------------------------------
@proche_bp.route("/proches/search", methods=["GET"])
@swag_from({
    'tags': ['v1 - Proches'],
    'summary': 'Rechercher des proches',
    'description': 'Recherche un proche par lien de parenté ou identifiant patient.',
    'parameters': [{
        'name': 'q',
        'in': 'query',
        'type': 'string',
        'required': True,
        'description': 'Mot-clé à rechercher (lien de parenté ou ID patient)'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Proches correspondants'}
    }
})
@jwt_required()
def search_proches_route():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify([]), 200

    proches = Proche.query.filter(
        or_(
            func.lower(Proche.lien_parente).like(f"%{q}%"),
            func.cast(Proche.patient_id, db.String).like(f"%{q}%")
        )
    ).all()
    return jsonify([serialize_proche(p) for p in proches]), 200

# -------------------------------------------------------------
# Route GET /proches/<id> : récupérer un proche par ID
# -------------------------------------------------------------
@proche_bp.route("/proches/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['v1 - Proches'],
    'summary': 'Récupérer un proche par ID',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du proche'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Proche trouvé'},
        404: {'description': 'Proche introuvable'}
    }
})
@jwt_required()
def get_proche_route(id):
    proche = get_proche_by_id(id)
    if not proche:
        return jsonify({"error": "Proche introuvable"}), 404
    return jsonify(serialize_proche(proche)), 200

# -------------------------------------------------------------
# Route PUT /proches/<id> : mettre à jour un proche
# -------------------------------------------------------------
@proche_bp.route("/proches/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['v1 - Proches'],
    'summary': 'Mettre à jour un proche',
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'lien_parente': {'type': 'string'},
                    'patient_id': {'type': 'integer'}
                }
            }
        }
    ],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Proche mis à jour'},
        404: {'description': 'Proche introuvable'}
    }
})
@jwt_required()
def update_proche_route(id):
    proche = get_proche_by_id(id)
    if not proche:
        return jsonify({"error": "Proche introuvable"}), 404

    data = request.get_json()
    update_proche(proche, data)
    return jsonify({"message": "Proche mis à jour"}), 200

# -------------------------------------------------------------
# Route DELETE /proches/<id> : supprimer un proche
# -------------------------------------------------------------
@proche_bp.route("/proches/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['v1 - Proches'],
    'summary': 'Supprimer un proche',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du proche à supprimer'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Proche supprimé'},
        404: {'description': 'Proche introuvable'}
    }
})
@jwt_required()
def delete_proche_route(id):
    proche = get_proche_by_id(id)
    if not proche:
        return jsonify({"error": "Proche introuvable"}), 404

    delete_proche(proche)
    return jsonify({"message": "Proche supprimé"}), 200