# -------------------------------------------------------------
# app/services/donnee_medical_service.py
# -------------------------------------------------------------
# Gère la logique métier liée aux données médicales :
# - Création de mesure
# - Suppression
# - Statistiques
# - Récupération par patient
# -------------------------------------------------------------

from app import db
from app.models.donnees_medicales import DonneesMedicale
from app.models.patient import Patient
from app.models.capteur import Capteur
from datetime import datetime
from sqlalchemy import func

# -------------------------------------------------------------
# SERVICE : Données Médicales
# -------------------------------------------------------------

def create_donnee_medicale(data):
    """Crée et enregistre une nouvelle donnée médicale."""
    required_fields = ["patient_id", "capteur_id", "valeur_mesuree"]
    if not all(field in data for field in required_fields):
        raise ValueError("Certains champs obligatoires sont manquants")

    patient = Patient.query.get(data["patient_id"])
    capteur = Capteur.query.get(data["capteur_id"])

    if not patient or not capteur:
        raise ValueError("Patient ou capteur introuvable")

    donnee = DonneesMedicale(
        patient_id=data["patient_id"],
        capteur_id=data["capteur_id"],
        valeur_mesuree=data["valeur_mesuree"],
        date_heure_mesure=datetime.utcnow()
    )

    db.session.add(donnee)
    db.session.commit()
    return donnee


def get_all_donnees():
    """Récupère toutes les données médicales enregistrées."""
    return DonneesMedicale.query.order_by(DonneesMedicale.date_heure_mesure.desc()).all()


def get_donnees_by_patient(patient_id):
    """Retourne toutes les mesures d’un patient donné."""
    return DonneesMedicale.query.filter_by(patient_id=patient_id).order_by(DonneesMedicale.date_heure_mesure.desc()).all()


def get_donnee_by_id(donnee_id):
    """Récupère une donnée médicale spécifique via son ID."""
    return DonneesMedicale.query.get(donnee_id)


def delete_donnee(donnee_id):
    """Supprime une donnée médicale spécifique."""
    donnee = DonneesMedicale.query.get(donnee_id)
    if not donnee:
        return False
    db.session.delete(donnee)
    db.session.commit()
    return True


def get_stats_by_patient(patient_id):
    """Retourne les statistiques (min, max, moyenne) par capteur pour un patient donné."""
    resultats = db.session.query(
        DonneesMedicale.capteur_id,
        func.min(DonneesMedicale.valeur_mesuree).label("min"),
        func.max(DonneesMedicale.valeur_mesuree).label("max"),
        func.avg(DonneesMedicale.valeur_mesuree).label("avg")
    ).filter(
        DonneesMedicale.patient_id == patient_id
    ).group_by(
        DonneesMedicale.capteur_id
    ).all()

    # Structuration propre des résultats
    stats = []
    for r in resultats:
        capteur = Capteur.query.get(r.capteur_id)
        stats.append({
            "capteur": capteur.type.value if capteur and capteur.type else "Inconnu",
            "min": round(r.min, 2) if r.min is not None else None,
            "max": round(r.max, 2) if r.max is not None else None,
            "moyenne": round(r.avg, 2) if r.avg is not None else None
        })
    return stats


def get_capteurs_by_patient(patient_id):
    """Retourne les capteurs ayant enregistré des données pour un patient."""
    return (
        db.session.query(Capteur)
        .join(DonneesMedicale)
        .filter(DonneesMedicale.patient_id == patient_id)
        .distinct()
        .all()
    )
