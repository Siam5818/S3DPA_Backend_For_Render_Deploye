from app import db
from app.models import Analyseur, Patient, Medecin, DonneesMedicale, Alerte
from app.utils.seuils import SEUILS_CAPTEURS

def create_analyse(patient, medecin, donnee):
    """
    Analyse automatique d'une donnée médicale déjà instanciée
    """

    capteur = donnee.capteur
    valeur = donnee.valeur_mesuree

    seuil = SEUILS_CAPTEURS.get(capteur.type_capteur)

    # Valeur par défaut
    resultat = "Analyse non effectuée : seuil non défini pour ce capteur"

    if seuil:
        if valeur < seuil["min"] or valeur > seuil["max"]:
            resultat = (
                f"Anomalie détectée : valeur {valeur} "
                f"hors seuil [{seuil['min']} - {seuil['max']}]"
            )

            # Création d’alerte
            alerte = Alerte(
                patient_id=patient.id,
                medecin_id=medecin.id,
                niveau_urgence=seuil["niveau_urgence"],
                type_alerte=seuil["type_alerte"],
                description=resultat,
                etat_traitement=False
            )
            db.session.add(alerte)

        else:
            resultat = "Résultat normal : valeur dans les seuils"

    analyse = Analyseur(
        patient_id=patient.id,
        medecin_id=medecin.id,
        donnee_medicale_id=donnee.id,
        resultat=resultat
    )

    db.session.add(analyse)

    return analyse

def get_all_analyses():
    """Récupère toutes les analyses."""
    return Analyseur.query.order_by(Analyseur.date_analyse.desc()).all()


def get_analyses_by_medecin(medecin_id):
    """Récupère toutes les analyses effectuées par un médecin."""
    return (
        Analyseur.query
        .filter_by(medecin_id=medecin_id)
        .order_by(Analyseur.date_analyse.desc())
        .all()
    )


def get_analyse_by_id(analyse_id):
    """Récupère une analyse par son ID."""
    return Analyseur.query.get(analyse_id)


def delete_analyse(analyse):
    """Supprime une analyse."""
    db.session.delete(analyse)
    db.session.commit()