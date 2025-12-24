# -------------------------------------------------------------
# app/routes/donnee_medical_route.py
# -------------------------------------------------------------
# Routes REST liées aux données médicales :
# - CRUD
# - Statistiques
# - Capteurs d’un patient
# -------------------------------------------------------------

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from app.services.auth_service import get_user_by_id
from app.services.proche_service import get_proche_by_id
from app.services.donnee_medical_service import (
    create_donnee_medicale,
    get_all_donnees,
    get_donnees_by_patient,
    get_stats_by_patient,
    delete_donnee,
    get_capteurs_by_patient,
    get_donnee_by_id
)
from app.utils.validation import validate_fields
from app.utils.serializers import (
    serialize_donnee_medicale,
    serialize_capteur
)

donnees_bp = Blueprint("donnees_bp", __name__, url_prefix="/v1")


# -------------------------------------------------------------
# POST /donnees → ajouter une donnée médicale
# -------------------------------------------------------------
@donnees_bp.route("/donnees", methods=["POST"])
@swag_from({
    'tags': ['v1 - Données Médicales'],
    'summary': 'Créer une nouvelle donnée médicale',
    'description': 'Cette route permet d’enregistrer une nouvelle mesure biomédicale captée par un capteur pour un patient donné.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'example': {
                    "patient_id": 1,
                    "capteur_id": 2,
                    "valeur_mesuree": 36.7
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Donnée médicale enregistrée avec succès',
            'examples': {
                'application/json': {
                    "message": "Donnée médicale enregistrée avec succès",
                    "donnee": {
                        "id": 1,
                        "patient_id": 1,
                        "capteur_id": 2,
                        "valeur_mesuree": 36.7,
                        "date_heure_mesure": "2025-10-06T18:45:00Z"
                    }
                }
            }
        },
        400: {'description': 'Champs manquants ou invalides'},
        500: {'description': 'Erreur interne du serveur'}
    }
})
def create_donnee_route():
    data = request.get_json()

    # Si c’est une liste → plusieurs mesures d’un coup
    if isinstance(data, list):
        saved_donnees = []
        for item in data:
            try:
                donnee = create_donnee_medicale(item)
                saved_donnees.append(serialize_donnee_medicale(donnee))
            except Exception as e:
                print(f"Erreur sur {item}: {e}")
                continue

        return jsonify({
            "message": f"{len(saved_donnees)} données enregistrées avec succès",
            "donnees": saved_donnees
        }), 201

    # Sinon → une seule donnée
    elif isinstance(data, dict):
        required = ["patient_id", "capteur_id", "valeur_mesuree"]
        if not validate_fields(data, required):
            return jsonify({"error": "Champs manquants"}), 400

        try:
            donnee = create_donnee_medicale(data)
            return jsonify({
                "message": "Donnée médicale enregistrée avec succès",
                "donnee": serialize_donnee_medicale(donnee)
            }), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            print(e)
            return jsonify({"error": "Erreur interne du serveur"}), 500

    else:
        return jsonify({"error": "Format JSON invalide"}), 400


# -------------------------------------------------------------
# GET /donnees → liste de toutes les données médicales
# -------------------------------------------------------------
@donnees_bp.route("/donnees", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Données Médicales'],
    'summary': 'Obtenir toutes les données médicales',
    'description': 'Retourne la liste complète des mesures médicales enregistrées dans le système.',
    'responses': {
        200: {
            'description': 'Liste des données médicales',
            'examples': {
                'application/json': [
                    {
                        "id": 1,
                        "patient_id": 1,
                        "capteur_id": 2,
                        "valeur_mesuree": 36.5,
                        "date_heure_mesure": "2025-10-06T18:45:00Z"
                    }
                ]
            }
        }
    }
})
def get_all_donnees_route():
    donnees = get_all_donnees()
    return jsonify([serialize_donnee_medicale(d) for d in donnees]), 200


# -------------------------------------------------------------
# GET /donnees/patient/<id> → données d’un patient
# -------------------------------------------------------------
@donnees_bp.route("/donnees/patient/<int:patient_id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Données Médicales'],
    'summary': 'Obtenir les données médicales d’un patient',
    'description': 'Retourne toutes les mesures collectées pour un patient donné.',
    'parameters': [
        {
            'name': 'patient_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant du patient'
        }
    ],
    'responses': {
        200: {'description': 'Liste des données du patient'},
        404: {'description': 'Aucune donnée trouvée'}
    }
})
def get_donnees_by_patient_route(patient_id):
    # Autorisation : patient lui-même, medecin, ou proche lié
    identity_raw = get_jwt_identity()
    try:
        identity = json.loads(identity_raw)
    except Exception:
        identity = {"id": None, "role": None}

    user_role = identity.get("role")
    user_id = identity.get("id")

    allowed = False
    if user_role == 'medecin':
        allowed = True
    elif user_role == 'patient' and user_id == patient_id:
        allowed = True
    elif user_role == 'proche':
        proche = get_proche_by_id(user_id)
        if proche and proche.patient_id == patient_id:
            allowed = True

    if not allowed:
        return jsonify({"error": "Accès non autorisé"}), 403

    donnees = get_donnees_by_patient(patient_id)
    if not donnees:
        return jsonify({"message": "Aucune donnée trouvée"}), 404
    return jsonify([serialize_donnee_medicale(d) for d in donnees]), 200


# -------------------------------------------------------------
# GET /donnees/patient/<id>/stats → statistiques du patient
# -------------------------------------------------------------
@donnees_bp.route("/donnees/patient/<int:patient_id>/stats", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Données Médicales'],
    'summary': 'Obtenir les statistiques médicales d’un patient',
    'description': 'Retourne les valeurs minimales, maximales et moyennes par capteur pour un patient.',
    'parameters': [
        {
            'name': 'patient_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant du patient'
        }
    ],
    'responses': {
        200: {
            'description': 'Statistiques par capteur',
            'examples': {
                'application/json': [
                    {"capteur": "Température", "min": 35.9, "max": 38.2, "moyenne": 36.8}
                ]
            }
        },
        404: {'description': 'Aucune statistique trouvée'}
    }
})
def get_stats_by_patient_route(patient_id):
    # Autorisation identique à get_donnees_by_patient
    identity_raw = get_jwt_identity()
    try:
        identity = json.loads(identity_raw)
    except Exception:
        identity = {"id": None, "role": None}

    user_role = identity.get("role")
    user_id = identity.get("id")

    allowed = False
    if user_role == 'medecin':
        allowed = True
    elif user_role == 'patient' and user_id == patient_id:
        allowed = True
    elif user_role == 'proche':
        proche = get_proche_by_id(user_id)
        if proche and proche.patient_id == patient_id:
            allowed = True

    if not allowed:
        return jsonify({"error": "Accès non autorisé"}), 403

    stats = get_stats_by_patient(patient_id)
    if not stats:
        return jsonify({"message": "Aucune statistique trouvée"}), 404
    return jsonify(stats), 200


# -------------------------------------------------------------
# DELETE /donnees/<id> → supprimer une donnée
# -------------------------------------------------------------
@donnees_bp.route("/donnees/<int:donnee_id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Données Médicales'],
    'summary': 'Supprimer une donnée médicale',
    'description': 'Permet de supprimer une donnée médicale spécifique par son ID.',
    'parameters': [
        {
            'name': 'donnee_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant de la donnée médicale'
        }
    ],
    'responses': {
        200: {'description': 'Donnée supprimée avec succès'},
        404: {'description': 'Donnée introuvable'}
    }
})
def delete_donnee_route(donnee_id):
    if not delete_donnee(donnee_id):
        return jsonify({"error": "Donnée introuvable"}), 404
    return jsonify({"message": "Donnée supprimée avec succès"}), 200


# -------------------------------------------------------------
# GET /patients/<id>/capteurs → capteurs associés au patient
# -------------------------------------------------------------
@donnees_bp.route("/patients/<int:patient_id>/capteurs", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Données Médicales'],
    'summary': 'Lister les capteurs associés à un patient',
    'description': 'Retourne tous les capteurs ayant déjà envoyé des mesures pour un patient donné.',
    'parameters': [
        {
            'name': 'patient_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant du patient'
        }
    ],
    'responses': {
        200: {'description': 'Liste des capteurs du patient'},
        404: {'description': 'Aucun capteur trouvé'}
    }
})
def get_capteurs_by_patient_route(patient_id):
    capteurs = get_capteurs_by_patient(patient_id)
    if not capteurs:
        return jsonify({"error": "Aucun capteur trouvé"}), 404
    return jsonify([serialize_capteur(c) for c in capteurs]), 200

# -------------------------------------------------------------
# GET /donnees/<id> → obtenir une donnée médicale précise
# -------------------------------------------------------------
@donnees_bp.route("/donnees/<int:donnee_id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['v1 - Données Médicales'],
    'summary': 'Obtenir une donnée médicale par ID',
    'description': 'Retourne une donnée médicale spécifique avec son patient et son capteur.',
    'parameters': [
        {
            'name': 'donnee_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant de la donnée médicale'
        }
    ],
    'responses': {
        200: {'description': 'Donnée médicale trouvée'},
        404: {'description': 'Donnée introuvable'}
    }
})
def get_donnee_by_id_route(donnee_id):
    donnee = get_donnee_by_id(donnee_id)
    if not donnee:
        return jsonify({"error": "Donnée introuvable"}), 404
    return jsonify(serialize_donnee_medicale(donnee)), 200
