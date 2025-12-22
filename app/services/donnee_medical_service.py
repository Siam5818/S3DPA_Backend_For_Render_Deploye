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
from app.models import Patient, Medecin, Capteur, DonneesMedicale
from datetime import datetime
from sqlalchemy import func
from app.services.analyse_service import create_analyse

# -------------------------------------------------------------
# SERVICE : Données Médicales
# -------------------------------------------------------------

def create_donnee_medicale(data):
    """
    Création d'une donnée médicale AVEC analyse automatique obligatoire
    """

    required_fields = [
        "patient_id",
        "capteur_id",
        "valeur_mesuree",
        "medecin_id"
    ]

    if not all(field in data for field in required_fields):
        raise ValueError("Champs obligatoires manquants")

    patient = Patient.query.get(data["patient_id"])
    capteur = Capteur.query.get(data["capteur_id"])
    medecin = Medecin.query.get(data["medecin_id"])

    if not patient or not capteur or not medecin:
        raise ValueError("Patient, capteur ou médecin introuvable")

    # Création de la donnée
    donnee = DonneesMedicale(
        patient_id=patient.id,
        capteur_id=capteur.id,
        valeur_mesuree=data["valeur_mesuree"],
        date_heure_mesure=datetime.utcnow()
    )

    db.session.add(donnee)
    db.session.flush()  # Génère donnee.id

    # Analyse automatique
    create_analyse(
        patient=patient,
        medecin=medecin,
        donnee=donnee
    )

    # Commit global (donnée + analyse + alerte)
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
