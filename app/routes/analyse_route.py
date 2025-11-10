# app/routes/analyse_route.py

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required
from app.services.analyse_service import (
    create_analyse, get_all_analyses, get_analyses_by_medecin,
    get_analyse_by_id, delete_analyse
)
from app.utils.serializers import serialize_analyse
from app.utils.validation import validate_fields

analyse_bp = Blueprint("analyse_bp", __name__, url_prefix="/v1")


# POST /analyses — créer une analyse
@analyse_bp.route("/analyses", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Analyses'],
    'summary': 'Créer une analyse médicale',
    'description': 'Crée une analyse liée à une donnée médicale, un patient et un médecin.',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'patient_id': {'type': 'integer'},
                'medecin_id': {'type': 'integer'},
                'donnee_medicale_id': {'type': 'integer'},
                'resultat': {'type': 'string', 'example': 'Analyse normale, aucune anomalie détectée'}
            },
            'required': ['patient_id', 'medecin_id', 'donnee_medicale_id']
        }
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': 'Analyse créée'},
        400: {'description': 'Champs requis manquants'},
        500: {'description': 'Erreur serveur'}
    }
})
def create_analyse_route():
    data = request.get_json()
    required = ["patient_id", "medecin_id", "donnee_medicale_id"]

    if not validate_fields(data, required):
        return jsonify({"error": "Champs requis manquants"}), 400

    analyse = create_analyse(data)
    return jsonify(serialize_analyse(analyse)), 201


# GET /analyses — liste des analyses
@analyse_bp.route("/analyses", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Analyses'],
    'summary': 'Lister toutes les analyses',
    'description': 'Retourne toutes les analyses enregistrées dans le système.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Liste des analyses'}
    }
})
def get_all_analyses_route():
    analyses = get_all_analyses()
    return jsonify([serialize_analyse(a) for a in analyses]), 200


# GET /medecins/<id>/analyses — analyses faites par un médecin
@analyse_bp.route("/medecins/<int:medecin_id>/analyses", methods=["GET", "OPTIONS"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Analyses'],
    'summary': 'Lister les analyses effectuées par un médecin',
    'description': 'Retourne toutes les analyses créées par le médecin spécifié.',
    'parameters': [{
        'name': 'medecin_id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du médecin'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Liste des analyses du médecin'},
        404: {'description': 'Médecin introuvable'}
    }
})
def get_analyses_by_medecin_route(medecin_id):
    analyses = get_analyses_by_medecin(medecin_id)
    return jsonify([serialize_analyse(a) for a in analyses]), 200


# GET /analyses/<id> — détail d’une analyse
@analyse_bp.route("/analyses/<int:id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Analyses'],
    'summary': 'Obtenir les détails d’une analyse',
    'description': 'Retourne les informations détaillées d’une analyse spécifique.',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID de l’analyse'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Analyse trouvée'},
        404: {'description': 'Analyse introuvable'}
    }
})
def get_analyse_by_id_route(id):
    analyse = get_analyse_by_id(id)
    if not analyse:
        return jsonify({"error": "Analyse introuvable"}), 404
    return jsonify(serialize_analyse(analyse)), 200


# DELETE /analyses/<id> — supprimer une analyse
@analyse_bp.route("/analyses/<int:id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Analyses'],
    'summary': 'Supprimer une analyse',
    'description': 'Supprime une analyse médicale existante.',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID de l’analyse à supprimer'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Analyse supprimée'},
        404: {'description': 'Analyse introuvable'}
    }
})
def delete_analyse_route(id):
    analyse = get_analyse_by_id(id)
    if not analyse:
        return jsonify({"error": "Analyse introuvable"}), 404
    delete_analyse(analyse)
    return jsonify({"message": "Analyse supprimée"}), 200
