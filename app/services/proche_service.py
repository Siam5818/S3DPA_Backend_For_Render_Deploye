from app import db
from app.models.proche import Proche

# -------------------------------------------------------------
# Fonction create_proche : crée un nouveau proche
# -------------------------------------------------------------
def create_proche(data):
    proche = Proche(
        lien_parente=data["lien_parente"],
        patient_id=data["patient_id"]
    )
    db.session.add(proche)
    db.session.commit()
    return proche

# -------------------------------------------------------------
# Fonction get_all_proches : liste tous les proches
# -------------------------------------------------------------
def get_all_proches():
    return Proche.query.all()

# -------------------------------------------------------------
# Fonction get_proche_by_id : récupère un proche par ID
# -------------------------------------------------------------
def get_proche_by_id(id):
    return Proche.query.get(id)

# -------------------------------------------------------------
# Fonction update_proche : met à jour un proche existant
# -------------------------------------------------------------
def update_proche(proche, data):
    proche.lien_parente = data.get("lien_parente", proche.lien_parente)
    proche.patient_id = data.get("patient_id", proche.patient_id)
    db.session.commit()
    return proche

# -------------------------------------------------------------
# Fonction delete_proche : supprime un proche
# -------------------------------------------------------------
def delete_proche(proche):
    db.session.delete(proche)
    db.session.commit()

# -------------------------------------------------------------
# proche_service.py : logique métier liée aux proches
# -------------------------------------------------------------
# - Crée, lit, met à jour et supprime des proches
# - Centralise les opérations sur le modèle Proche
# - Facilite la réutilisation et la testabilité