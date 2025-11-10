from app import db
from app.models.capteur import Capteur

# -------------------------------------------------------------
# Fonction create_capteur : crée un nouveau capteur
# -------------------------------------------------------------
def create_capteur(data):
    capteur = Capteur(
        type=data["type"],
        valeur=data.get("valeur"),
        date_mesure=data.get("date_mesure")
    )
    db.session.add(capteur)
    db.session.commit()
    return capteur

# -------------------------------------------------------------
# Fonction get_all_capteurs : liste tous les capteurs
# -------------------------------------------------------------
def get_all_capteurs():
    return Capteur.query.all()

# -------------------------------------------------------------
# Fonction get_capteur_by_id : récupère un capteur par ID
# -------------------------------------------------------------
def get_capteur_by_id(id):
    return Capteur.query.get(id)

# -------------------------------------------------------------
# Fonction update_capteur : met à jour un capteur existant
# -------------------------------------------------------------
def update_capteur(capteur, data):
    capteur.type = data.get("type", capteur.type)
    capteur.valeur = data.get("valeur", capteur.valeur)
    capteur.date_mesure = data.get("date_mesure", capteur.date_mesure)
    db.session.commit()
    return capteur

# -------------------------------------------------------------
# Fonction delete_capteur : supprime un capteur
# -------------------------------------------------------------
def delete_capteur(capteur):
    db.session.delete(capteur)
    db.session.commit()

# -------------------------------------------------------------
# Fonction get_capteur_stats : statistiques des capteurs
# -------------------------------------------------------------
def get_capteur_stats():
    from sqlalchemy import func
    return db.session.query(
        Capteur.type,
        func.min(Capteur.valeur),
        func.max(Capteur.valeur),
        func.avg(Capteur.valeur)
    ).group_by(Capteur.type).all()