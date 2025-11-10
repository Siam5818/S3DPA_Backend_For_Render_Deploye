from app import db
from app.models.medecin import Medecin

# -------------------------------------------------------------
# Fonction create_medecin : crée un nouveau médecin
# -------------------------------------------------------------
# - Initialise un objet Medecin avec les données reçues
# - Hash le mot de passe
# - Enregistre le médecin en base
def create_medecin(data):
    medecin = Medecin(
        nom=data["nom"],
        prenom=data["prenom"],
        email=data["email"],
        adresse=data.get("adresse"),
        date_naissance=data.get("date_naissance"),
        specialite=data["specialite"],
        type="medecin"
    )
    medecin.set_password(data["mot_de_passe"])
    db.session.add(medecin)
    db.session.commit()
    return medecin

# -------------------------------------------------------------
# Fonction get_all_medecins : liste tous les médecins
# -------------------------------------------------------------
# - Retourne tous les objets Medecin présents en base
def get_all_medecins():
    return Medecin.query.all()

# -------------------------------------------------------------
# Fonction get_medecin_by_id : récupère un médecin par ID
# -------------------------------------------------------------
# - Retourne l’objet Medecin correspondant à l’ID donné
def get_medecin_by_id(id):
    return Medecin.query.get(id)

# -------------------------------------------------------------
# Fonction get_medecin_by_email : récupère un médecin par son Email
# -------------------------------------------------------------
# - Retourne l’objet Medecin correspondant à l’Email donné
def get_medecin_by_email(email):
    return Medecin.query.filter_by(email=email).first()

# -------------------------------------------------------------
# Fonction update_medecin : met à jour un médecin existant
# -------------------------------------------------------------
# - Modifie les champs du médecin avec les données reçues
# - Commit les changements en base
def update_medecin(medecin, data):
    medecin.nom = data.get("nom", medecin.nom)
    medecin.prenom = data.get("prenom", medecin.prenom)
    medecin.email = data.get("email", medecin.email)
    medecin.adresse = data.get("adresse", medecin.adresse)
    medecin.specialite = data.get("specialite", medecin.specialite)
    db.session.commit()
    return medecin

# -------------------------------------------------------------
# Fonction delete_medecin : supprime un médecin
# -------------------------------------------------------------
# - Supprime l’objet Medecin de la base
def delete_medecin(medecin):
    db.session.delete(medecin)
    db.session.commit()

# -------------------------------------------------------------
# medecin_service.py : logique métier liée aux médecins
# -------------------------------------------------------------
# - Crée, lit, met à jour et supprime des médecins
# - Centralise les opérations sur le modèle Medecin
# - Facilite la réutilisation et la testabilité