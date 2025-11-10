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
def get_all_analyses_route():
    analyses = get_all_analyses()
    return jsonify([serialize_analyse(a) for a in analyses]), 200


# GET /medecins/<id>/analyses — analyses faites par un médecin
@analyse_bp.route("/medecins/<int:medecin_id>/analyses", methods=["GET", "OPTIONS"])
@jwt_required()
def get_analyses_by_medecin_route(medecin_id):
    analyses = get_analyses_by_medecin(medecin_id)
    return jsonify([serialize_analyse(a) for a in analyses]), 200


# GET /analyses/<id> — détail d’une analyse
@analyse_bp.route("/analyses/<int:id>", methods=["GET"])
@jwt_required()
def get_analyse_by_id_route(id):
    analyse = get_analyse_by_id(id)
    if not analyse:
        return jsonify({"error": "Analyse introuvable"}), 404
    return jsonify(serialize_analyse(analyse)), 200


# DELETE /analyses/<id> — supprimer une analyse
@analyse_bp.route("/analyses/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_analyse_route(id):
    analyse = get_analyse_by_id(id)
    if not analyse:
        return jsonify({"error": "Analyse introuvable"}), 404
    delete_analyse(analyse)
    return jsonify({"message": "Analyse supprimée"}), 200
