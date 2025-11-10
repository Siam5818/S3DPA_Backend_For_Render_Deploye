from app import db
from sqlalchemy import or_, func
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from app.utils.validation import validate_fields
from app.utils.serializers import serialize_patient, serialize_statistique, serialize_capteur, serialize_donnee_medicale
from flask_jwt_extended import jwt_required
from app.models import Capteur, Patient, Proche, Alerte, DonneesMedicale, Analyseur
from app.services.donnee_medical_service import get_stats_by_patient
from app.services.patient_service import (
    create_patient,
    get_all_patients,
    get_patient_by_id,
    update_patient,
    delete_patient
)

patient_bp = Blueprint("patient_bp", __name__, url_prefix="/v1")

# -------------------------------------------------------------
# Route POST /patients : créer un patient
# -------------------------------------------------------------
@patient_bp.route("/patients", methods=["POST"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Créer un patient avec ses proches',
    'description': 'Crée un patient et ses proches en héritant du modèle Personne.',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'nom': {'type': 'string'},
                'prenom': {'type': 'string'},
                'email': {'type': 'string'},
                'phone': {'type': 'string'},
                'mot_de_passe': {'type': 'string'},
                'adresse': {'type': 'string'},
                'date_naissance': {'type': 'string', 'format': 'date'},
                'proches': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'nom': {'type': 'string'},
                            'prenom': {'type': 'string'},
                            'email': {'type': 'string'},
                            'phone': {'type': 'string'},
                            'mot_de_passe': {'type': 'string'},
                            'adresse': {'type': 'string'},
                            'date_naissance': {'type': 'string', 'format': 'date'},
                            'lien_parente': {'type': 'string'}
                        },
                        'required': ['nom', 'prenom', 'email', 'phone', 'mot_de_passe', 'lien_parente']
                    }
                }
            },
            'required': ['nom', 'prenom', 'email', 'phone', 'mot_de_passe']
        }
    }],
    'responses': {
        201: {'description': 'Patient et proches créés avec succès'},
        400: {'description': 'Champs manquants ou invalides'},
        409: {'description': 'Email déjà utilisé'},
        500: {'description': 'Erreur serveur'}
    }
})
@jwt_required()
def create_patient_route():
    data = request.get_json()

    try:
        patient = create_patient(data)
        return jsonify({"message": "Patient et proches créés avec succès", "patient_id": patient.id}), 201

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400 if "manquants" in str(ve) else 409

    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    
# -------------------------------------------------------------
# Route GET /patients : Lister tous les patients
# -------------------------------------------------------------
@patient_bp.route("/patients", methods=["GET"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Lister tous les patients (avec relations)',
    'description': 'Retourne la liste complète des patients, incluant les informations personnelles, les proches et les alertes associées.',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Liste détaillée des patients',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 3},
                        'nom': {'type': 'string', 'example': 'Darkam'},
                        'prenom': {'type': 'string', 'example': 'Aliyane'},
                        'email': {'type': 'string', 'example': 'adarkam@gmail.com'},
                        'date_naissance': {'type': 'string', 'example': '1985-04-12'},
                        'proches': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer', 'example': 5},
                                    'lien_parente': {'type': 'string', 'example': 'Fils'}
                                }
                            }
                        },
                        'alertes': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'integer', 'example': 12},
                                    'type_alerte': {'type': 'string', 'example': 'Urgence'},
                                    'niveau_urgence': {'type': 'string', 'example': 'Critique'},
                                    'description': {'type': 'string', 'example': 'Température très élevée'},
                                    'etat_traitement': {'type': 'boolean', 'example': False},
                                    'date_heure_alerte': {'type': 'string', 'example': '2025-10-12T14:45:00Z'}
                                }
                            }
                        }
                    }
                }
            }
        },
        401: {'description': 'Token manquant ou invalide'}
    }
})
@jwt_required()
def get_all_patients_route():
    patients = get_all_patients()
    return jsonify([serialize_patient(p) for p in patients]), 200

# -------------------------------------------------------------
# Route GET /patients/search : rechercher des patients
# -------------------------------------------------------------
@patient_bp.route("/patients/search", methods=["GET"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Rechercher des patients',
    'description': 'Recherche un patient par nom, prénom, email, ou urgence associée.',
    'parameters': [
        {
            'name': 'q',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Mot-clé à rechercher (nom, prénom ou email)'
        },
        {
            'name': 'urgence',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filtrer les patients par niveau d’urgence de leur dernière alerte'
        }
    ],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Liste des patients correspondants'}
    }
})
@jwt_required()
def search_patients_route():
    q = request.args.get("q", "").lower().strip()
    urgence = request.args.get("urgence", "").strip()

    query = Patient.query

    # Filtre par mot-clé (nom, prénom, email)
    if q:
        query = query.filter(
            or_(
                func.lower(Patient.nom).like(f"%{q}%"),
                func.lower(Patient.prenom).like(f"%{q}%"),
                func.lower(Patient.email).like(f"%{q}%")
            )
        )

    patients = query.all()

    # Si un niveau d’urgence est précisé → filtrer via les alertes du patient
    if urgence:
        filtered_patients = []
        for patient in patients:
            # récupérer la dernière alerte (par date)
            last_alert = (
                Alerte.query.filter_by(patient_id=patient.id)
                .order_by(Alerte.date_heure_alerte.desc())
                .first()
            )
            if last_alert and last_alert.niveau_urgence.value.lower() == urgence.lower():
                filtered_patients.append(patient)
        patients = filtered_patients

    return jsonify([serialize_patient(p) for p in patients]), 200

# -------------------------------------------------------------
# Route GET /patients/<id> : Détails d’un patient
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Récupérer un patient par ID',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du patient'
    }],
    'responses': {
        200: {'description': 'Patient trouvé'},
        404: {'description': 'Patient introuvable'}
    }
})
@jwt_required()
def get_patient_route(id):
    patient = get_patient_by_id(id)
    if not patient:
        return jsonify({"error": "Patient introuvable"}), 404
    return jsonify(serialize_patient(patient)), 200

# -------------------------------------------------------------
# Route PUT /patients/<id> : Mettre à jour un patient
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Mettre à jour un patient',
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
                    'adresse': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Patient mis à jour'},
        404: {'description': 'Patient introuvable'}
    }
})
@jwt_required()
def update_patient_route(id):
    patient = get_patient_by_id(id)
    if not patient:
        return jsonify({"error": "Patient introuvable"}), 404

    data = request.get_json()
    update_patient(patient, data)
    return jsonify({"message": "Patient mis à jour"}), 200

# -------------------------------------------------------------
# Route DELETE /patients/<id> : supprimer un patient
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Supprimer un patient',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True
    }],
    'responses': {
        200: {'description': 'Patient supprimé'},
        404: {'description': 'Patient introuvable'}
    }
})
@jwt_required()
def delete_patient_route(id):
    patient = get_patient_by_id(id)
    if not patient:
        return jsonify({"error": "Patient introuvable"}), 404

    delete_patient(patient)
    return jsonify({"message": "Patient supprimé"}), 200

# -------------------------------------------------------------
# Route GET /patients/<id>/capteurs : capteurs d'un patient
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>/capteurs", methods=["GET"])
@jwt_required()
def get_capteurs_by_patient(id):
    capteurs = db.session.query(Capteur).join(DonneesMedicale).filter(DonneesMedicale.patient_id == id).distinct().all()
    
    if not capteurs:
        return jsonify({"error": "Aucun capteur trouvé"}), 404

    return jsonify([serialize_capteur(c) for c in capteurs]), 200

# -------------------------------------------------------------
# Route GET /patients/<id>/capteurs/disponibles : capteurs libres
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>/capteurs/disponibles", methods=["GET"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Lister les capteurs non associés à un patient',
    'description': 'Retourne la liste des capteurs disponibles (non encore liés à ce patient).',
    'parameters': [{
        'name': 'id',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'ID du patient'
    }],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Liste des capteurs non associés',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'example': 1},
                        'type': {'type': 'string', 'example': 'TEMPERATURE'},
                    }
                }
            }
        },
        401: {'description': 'Token JWT invalide ou manquant'},
        404: {'description': 'Aucun capteur disponible trouvé'}
    }
})
@jwt_required()
def get_capteurs_non_associes(id):
    """Retourne la liste des capteurs non encore associés à ce patient"""

    capteurs_associes = db.session.query(Capteur.id).join(DonneesMedicale).filter(DonneesMedicale.patient_id == id)
    capteurs_non_associes = db.session.query(Capteur).filter(~Capteur.id.in_(capteurs_associes)).all()

    return jsonify([serialize_capteur(c) for c in capteurs_non_associes]), 200

# -------------------------------------------------------------
# Route POST /patients/<id>/capteurs/<capteur_id> → associer
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>/capteurs/<int:capteur_id>", methods=["POST"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Associer un capteur à un patient',
    'description': 'Crée une relation entre un patient et un capteur afin de permettre la collecte de données médicales.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant du patient'
        },
        {
            'name': 'capteur_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant du capteur à associer'
        }
    ],
    'security': [{'BearerAuth': []}],
    'responses': {
        201: {'description': 'Capteur associé avec succès'},
        400: {'description': 'Le capteur est déjà associé à ce patient'},
        401: {'description': 'Authentification requise'}
    }
})
@jwt_required()
def associer_capteur(id, capteur_id):
    """Associe un capteur à un patient (prépare la collecte de données)"""

    existe = DonneesMedicale.query.filter_by(patient_id=id, capteur_id=capteur_id).first()
    if existe:
        return jsonify({"message": "Ce capteur est déjà associé à ce patient"}), 400

    nouvelle = DonneesMedicale(patient_id=id, capteur_id=capteur_id, valeur_mesuree=0.0)
    db.session.add(nouvelle)
    db.session.commit()

    return jsonify({"message": "Capteur associé au patient avec succès"}), 201

# -------------------------------------------------------------
# Route DELETE /patients/<id>/capteurs/<capteur_id> → dissocier
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>/capteurs/<int:capteur_id>", methods=["DELETE"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Dissocier un capteur d’un patient',
    'description': 'Supprime le lien entre un patient et un capteur, effaçant les données associées si nécessaire.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant du patient'
        },
        {
            'name': 'capteur_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Identifiant du capteur à dissocier'
        }
    ],
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {'description': 'Capteur dissocié avec succès'},
        404: {'description': 'Capteur non associé à ce patient'},
        401: {'description': 'Authentification requise'}
    }
})
@jwt_required()
def dissocier_capteur(id, capteur_id):
    """Dissocie un capteur d’un patient (supprime le lien historique)"""

    donnees = DonneesMedicale.query.filter_by(patient_id=id, capteur_id=capteur_id).all()
    if not donnees:
        return jsonify({"error": "Ce capteur n’est pas associé à ce patient"}), 404

    for d in donnees:
        db.session.delete(d)
    db.session.commit()

    return jsonify({"message": "Capteur dissocié avec succès"}), 200

# -------------------------------------------------------------
# Route GET /patients/<id>/mesures : dernières données médicales
# -------------------------------------------------------------
@patient_bp.route("/patients/<int:id>/mesures", methods=["GET"])
@swag_from({
    'tags': ['v1 - Patients'],
    'summary': 'Récupérer les dernières mesures d’un patient',
    'description': 'Retourne les données médicales récentes du patient (température, tension, rythme).',
    'responses': {
        200: {'description': 'Mesures récupérées avec succès'},
        404: {'description': 'Aucune mesure trouvée pour ce patient'}
    }
})
@jwt_required()
def get_mesures_patient(id):
    mesures = DonneesMedicale.query.filter_by(patient_id=id)\
        .order_by(DonneesMedicale.date_heure_mesure.desc())\
        .limit(20).all()

    return jsonify([serialize_donnee_medicale(m) for m in mesures]), 200
