from app import db
from app.models.alerte import Alerte

# -------------------------------------------------------------
# Fonction create_alerte : crée une nouvelle alerte
# -------------------------------------------------------------
def create_alerte(data):
    alerte = Alerte(
        patient_id=data["patient_id"],
        medecin_id=data["medecin_id"],
        niveau_urgence=data["niveau_urgence"],
        type_alerte=data["type_alerte"],
        description=data.get("description"),
        etat_traitement=data.get("etat_traitement", False)
    )
    db.session.add(alerte)
    db.session.commit()
    return alerte

# -------------------------------------------------------------
# Fonction get_alertes_by_patient : alertes d’un patient
# -------------------------------------------------------------
def get_alertes_by_patient(patient_id):
    return Alerte.query.filter_by(patient_id=patient_id).all()

# -------------------------------------------------------------
# Fonction get_alertes_by_medecin : alertes d’un médecin
# -------------------------------------------------------------
def get_alertes_by_medecin(medecin_id):
    return Alerte.query.filter_by(medecin_id=medecin_id).all()

# -------------------------------------------------------------
# Fonction update_alerte_etat : marquer une alerte comme traitée
# -------------------------------------------------------------
def update_alerte_etat(alerte, etat):
    alerte.etat_traitement = etat
    db.session.commit()
    return alerte

# -------------------------------------------------------------
# Fonction delete_alerte : supprimer une alerte
# -------------------------------------------------------------
def delete_alerte(alerte):
    db.session.delete(alerte)
    db.session.commit()

# -------------------------------------------------------------
# Fonction get_all_alertes : lister toutes les alertes
# -------------------------------------------------------------
def get_all_alertes():
    return Alerte.query.all()

# -------------------------------------------------------------
# Fonction get_alerte_by_id : récupérer une alerte par ID
# -------------------------------------------------------------
def get_alerte_by_id(id):
    return Alerte.query.get(id)