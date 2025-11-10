from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required
from app.utils.validation import validate_fields
from app.models.enums import TypeCapteur
from app.services.capteur_service import (
    create_capteur,
    get_all_capteurs,
    get_capteur_by_id,
    delete_capteur,
)

capteur_bp = Blueprint("capteur_bp", __name__, url_prefix="/v1")

# -------------------------------------------------------------
# POST /capteurs : créer un capteur
# -------------------------------------------------------------
@capteur_bp.route("/capteurs", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Capteurs'],
    'summary': 'Créer un capteur',
    'description': 'Crée un nouveau capteur biomédical (température, tension, etc.)',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'type': {'type': 'string', 'example': 'temperature'}
            },
            'required': ['type']
        }
    }],
    'responses': {
        201: {'description': 'Capteur créé avec succès'},
        400: {'description': 'Champs manquants'},
        500: {'description': 'Erreur serveur'}
    }
})
def create_capteur_route():
    data = request.get_json()
    required = ["type"]

    if not validate_fields(data, required):
        return jsonify({"error": "Le type du capteur est requis"}), 400

    try:
        capteur = create_capteur(data)
        return jsonify({
            "message": "Capteur créé avec succès",
            "capteur": {"id": capteur.id, "type": capteur.type.value}
        }), 201
    except Exception as e:
        print(e)
        return jsonify({"error": "Erreur serveur"}), 500


# -------------------------------------------------------------
# GET /capteurs : lister tous les capteurs
# -------------------------------------------------------------
@capteur_bp.route("/capteurs", methods=["GET"])
@jwt_required()
def get_all_capteurs_route():
    capteurs = get_all_capteurs()
    result = [{"id": c.id, "type": c.type.value} for c in capteurs]
    return jsonify(result), 200


# -------------------------------------------------------------
# GET /capteurs/types : liste des types de capteurs
# -------------------------------------------------------------
@capteur_bp.route("/capteurs/types", methods=["GET"])
@jwt_required()
def get_capteur_types():
    types = [t.name for t in TypeCapteur]
    return jsonify(types), 200


# -------------------------------------------------------------
# GET /capteurs/<id> : récupérer un capteur par ID
# -------------------------------------------------------------
@capteur_bp.route("/capteurs/<int:id>", methods=["GET"])
@jwt_required()
def get_capteur_route(id):
    capteur = get_capteur_by_id(id)
    if not capteur:
        return jsonify({"error": "Capteur introuvable"}), 404
    return jsonify({"id": capteur.id, "type": capteur.type.value}), 200


# -------------------------------------------------------------
# DELETE /capteurs/<id> : supprimer un capteur
# -------------------------------------------------------------
@capteur_bp.route("/capteurs/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_capteur_route(id):
    capteur = get_capteur_by_id(id)
    if not capteur:
        return jsonify({"error": "Capteur introuvable"}), 404

    delete_capteur(capteur)
    return jsonify({"message": "Capteur supprimé"}), 200
