from app import db
from app.models import Analyseur

def create_analyse(data):
    """Créer une nouvelle analyse médicale."""
    analyse = Analyseur(
        patient_id=data["patient_id"],
        medecin_id=data["medecin_id"],
        donnee_medicale_id=data["donnee_medicale_id"],
        resultat=data.get("resultat")
    )
    db.session.add(analyse)
    db.session.commit()
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