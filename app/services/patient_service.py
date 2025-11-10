from app import db
from app.models import Patient, Proche, Personne
from sqlalchemy.exc import IntegrityError
import logging

from app.utils.validation import validate_fields

logger = logging.getLogger(__name__)

# -------------------------------------------------------------
# Fonction create_patient : crée un patient et ses proches
# -------------------------------------------------------------
def create_patient(data):
    required_fields = ["nom", "prenom", "email", "phone", "mot_de_passe"]

    # Vérification des champs du patient
    if not validate_fields(data, required_fields):
        raise ValueError("Champs obligatoires manquants pour le patient")

    if get_personne_by_email(data["email"]):
        raise ValueError("Email déjà utilisé pour le patient")

    try:
        # Création du patient
        patient = Patient(
            nom=data["nom"],
            prenom=data["prenom"],
            email=data["email"],
            phone=data["phone"],
            adresse=data.get("adresse"),
            date_naissance=data.get("date_naissance"),
            role="patient",
            type="patient"
        )
        patient.set_password(data["mot_de_passe"])
        db.session.add(patient)
        db.session.flush()  # pour récupérer patient.id

        # Création des proches
        proches_data = data.get("proches", [])
        for proche_data in proches_data:
            if not validate_fields(proche_data, required_fields + ["lien_parente"]):
                raise ValueError("Champs obligatoires manquants pour un proche")

            if get_personne_by_email(proche_data["email"]):
                raise ValueError(f"Email déjà utilisé pour le proche {proche_data['email']}")

            proche = create_proche(proche_data, patient.id)
            db.session.add(proche)

        db.session.commit()
        return patient

    except IntegrityError as e:
        db.session.rollback()
        logger.error("Conflit d'intégrité lors de la création du patient : %s", str(e))
        raise ValueError("Conflit d'intégrité en base")

    except Exception as e:
        db.session.rollback()
        logger.exception("Erreur inattendue lors de la création du patient")
        raise RuntimeError("Erreur serveur")

# -------------------------------------------------------------
# Fonction create_proche : crée un proche lié à un patient
# -------------------------------------------------------------
def create_proche(data, patient_id):
    proche = Proche(
        nom=data["nom"],
        prenom=data["prenom"],
        email=data["email"],
        phone=data["phone"],
        adresse=data.get("adresse"),
        date_naissance=data.get("date_naissance"),
        lien_parente=data["lien_parente"],
        role="proche",
        type="proche",
        patient_id=patient_id
    )
    proche.set_password(data["mot_de_passe"])
    return proche

# -------------------------------------------------------------
# Fonction get_all_patients : liste tous les patients
# -------------------------------------------------------------
# - Retourne tous les objets Patient présents en base
def get_all_patients():
    return Patient.query.all()

# -------------------------------------------------------------
# Fonction get_patient_by_id : récupère un patient par ID
# -------------------------------------------------------------
# - Retourne l’objet Patient correspondant à l’ID donné
def get_patient_by_id(id):
    return Patient.query.get(id)

# -------------------------------------------------------------
# Fonction get_patient_by_email : vérifie si un email est déjà utilisé
# -------------------------------------------------------------
# - Retourne le patient correspondant à l’email donné
def get_personne_by_email(email):
    return Personne.query.filter_by(email=email).first()


# -------------------------------------------------------------
# Fonction update_patient : met à jour un patient existant
# -------------------------------------------------------------
# - Modifie les champs du patient avec les données reçues
# - Commit les changements en base
def update_patient(patient, data):
    patient.nom = data.get("nom", patient.nom)
    patient.prenom = data.get("prenom", patient.prenom)
    patient.email = data.get("email", patient.email)
    patient.adresse = data.get("adresse", patient.adresse)
    db.session.commit()
    return patient

# -------------------------------------------------------------
# Fonction delete_patient : supprime un patient
# -------------------------------------------------------------
# - Supprime l’objet Patient de la base
def delete_patient(patient):
    db.session.delete(patient)
    db.session.commit()

# -------------------------------------------------------------
# patient_service.py : logique métier liée aux patients
# -------------------------------------------------------------
# - Crée, lit, met à jour et supprime des patients
# - Centralise les opérations sur le modèle Patient
# - Facilite la réutilisation et la testabilité