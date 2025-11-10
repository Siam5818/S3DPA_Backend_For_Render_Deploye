from flask import Blueprint, request, jsonify
from flasgger import swag_from
from sqlalchemy import or_, func
from app.models import Alerte
from flask_jwt_extended import jwt_required
from app.utils.validation import validate_fields
from app.utils.serializers import serialize_alerte
from app.services.alerte_service import (
    create_alerte,
    get_all_alertes,
    get_alertes_by_patient,
    get_alertes_by_medecin,
    get_alerte_by_id,
    update_alerte_etat,
    delete_alerte
)

alerte_bp = Blueprint("alerte_bp", __name__, url_prefix="/v1")

# -------------------------------------------------------------
# Route POST /alertes : créer une alerte
# -------------------------------------------------------------
@alerte_bp.route("/alertes", methods=["POST"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Créer une alerte médicale',
    'description': 'Crée une alerte liée à un patient et à un médecin.',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'patient_id': {'type': 'integer'},
                'medecin_id': {'type': 'integer'},
                'niveau_urgence': {'type': 'string', 'example': 'critique'},
                'type_alerte': {'type': 'string', 'example': 'tension_elevee'},
                'description': {'type': 'string', 'example': 'Tension à 180/120'},
                'etat_traitement': {'type': 'boolean', 'example': False}
            },
            'required': ['patient_id', 'medecin_id', 'niveau_urgence', 'type_alerte']
        }
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': 'Alerte créée'},
        400: {'description': 'Champs manquants'},
        500: {'description': 'Erreur serveur'}
    }
})
@jwt_required()
def create_alerte_route():
    data = request.get_json()
    required = ["patient_id", "medecin_id", "niveau_urgence", "type_alerte"]

    if not validate_fields(data, required):
        return jsonify({"error": "Champs requis manquants"}), 400

    alerte = create_alerte(data)
    return jsonify(serialize_alerte(alerte)), 201

# -------------------------------------------------------------
# Route GET /alertes : lister toutes les alertes
# -------------------------------------------------------------
@alerte_bp.route("/alertes", methods=["GET"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Lister toutes les alertes',
    'description': 'Retourne toutes les alertes enregistrées.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Liste des alertes'}
    }
})
@jwt_required()
def get_all_alertes_route():
    alertes = get_all_alertes()
    return jsonify([serialize_alerte(a) for a in alertes]), 200

# -------------------------------------------------------------
# Route GET /alertes/search : rechercher des alertes
# -------------------------------------------------------------
@alerte_bp.route("/alertes/search", methods=["GET"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Rechercher des alertes',
    'description': 'Recherche des alertes par type, niveau d’urgence ou description.',
    'parameters': [{
        'name': 'q',
        'in': 'query',
        'type': 'string',
        'required': True,
        'description': 'Mot-clé à rechercher (type, urgence ou description)'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Alertes correspondantes'}
    }
})
@jwt_required()
def search_alertes_route():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify([]), 200

    alertes = Alerte.query.filter(
        or_(
            func.lower(Alerte.type_alerte).like(f"%{q}%"),
            func.lower(Alerte.niveau_urgence).like(f"%{q}%"),
            func.lower(Alerte.description).like(f"%{q}%")
        )
    ).all()
    return jsonify([serialize_alerte(a) for a in alertes]), 200


# -------------------------------------------------------------
# Route GET /alertes/<id> : récupérer une alerte par ID
# -------------------------------------------------------------
@alerte_bp.route("/alertes/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Récupérer une alerte par ID',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Alerte trouvée'},
        404: {'description': 'Alerte introuvable'}
    }
})
@jwt_required()
def get_alerte_by_id_route(id):
    alerte = get_alerte_by_id(id)
    if not alerte:
        return jsonify({"error": "Alerte introuvable"}), 404
    return jsonify(serialize_alerte(alerte)), 200

# -------------------------------------------------------------
# Route PUT /alertes/<id>/etat : marquer une alerte comme traitée
# -------------------------------------------------------------
@alerte_bp.route("/alertes/<int:id>/etat", methods=["PUT"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Mettre à jour l’état de traitement d’une alerte',
    'parameters': [
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'etat_traitement': {'type': 'boolean', 'example': True}
                },
                'required': ['etat_traitement']
            }
        }
    ],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'État mis à jour'},
        404: {'description': 'Alerte introuvable'}
    }
})
@jwt_required()
def update_alerte_etat_route(id):
    alerte = get_alerte_by_id(id)
    if not alerte:
        return jsonify({"error": "Alerte introuvable"}), 404

    data = request.get_json()
    update_alerte_etat(alerte, data["etat_traitement"])
    return jsonify({"message": "État de l’alerte mis à jour"}), 200

# -------------------------------------------------------------
# Route GET /patients/<id>/alertes : alertes d’un patient
# -------------------------------------------------------------
@alerte_bp.route("/patients/<int:id>/alertes", methods=["GET"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Alertes d’un patient',
    'description': 'Retourne toutes les alertes associées à un patient donné.',
    'parameters': [{'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Liste des alertes'},
        404: {'description': 'Aucune alerte trouvée'}
    }
})
@jwt_required()
def get_alertes_by_patient_route(id):
    alertes = get_alertes_by_patient(id)
    result = [serialize_alerte(a) for a in alertes]
    return jsonify(result), 200


# -------------------------------------------------------------
# Route DELETE /alertes/<id> : supprimer une alerte
# -------------------------------------------------------------
@alerte_bp.route("/alertes/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Supprimer une alerte',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Alerte supprimée'},
        404: {'description': 'Alerte introuvable'}
    }
})
@jwt_required()
def delete_alerte_route(id):
    alerte = get_alerte_by_id(id)
    if not alerte:
        return jsonify({"error": "Alerte introuvable"}), 404

    delete_alerte(alerte)
    return jsonify({"message": "Alerte supprimée"}), 200

# -------------------------------------------------------------
# Route GET /medecins/<id>/alertes : alertes d’un médecin
# -------------------------------------------------------------
@alerte_bp.route("/medecins/<int:id>/alertes", methods=["GET"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Alertes d’un médecin',
    'description': 'Retourne toutes les alertes associées à un médecin donné.',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du médecin'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Liste des alertes du médecin',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'patient_id': {'type': 'integer'},
                        'niveau_urgence': {'type': 'string'},
                        'type_alerte': {'type': 'string'},
                        'description': {'type': 'string'},
                        'etat_traitement': {'type': 'boolean'},
                        'date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        404: {'description': 'Aucune alerte trouvée pour ce médecin'}
    }
})
@jwt_required()
def get_alertes_by_medecin_route(id):
    """Retourne toutes les alertes gérées par un médecin spécifique."""
    alertes = get_alertes_by_medecin(id)
    if not alertes:
        return jsonify({"error": "Aucune alerte trouvée pour ce médecin"}), 404

    result = [serialize_alerte(a) for a in alertes]
    return jsonify(result), 200

# -------------------------------------------------------------
# Route GET toutes les types d’alertes
# -------------------------------------------------------------
@alerte_bp.route("/alertes/types", methods=["GET"])
@swag_from({
    'tags': ['v1 - Alertes'],
    'summary': 'Lister tous les types d’alertes',
    'description': 'Retourne une liste de tous les types d’alertes disponibles.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Liste des types d’alertes',
            'schema': {
                'type': 'array',
                'items': {'type': 'string'}
            }
        }
    }
})
@jwt_required()
def get_alerte_types_route():
    from app.models.enums import TypeAlerte

    types = [t.name for t in TypeAlerte]
    return jsonify(types), 200