# Importation des types de colonnes SQLAlchemy
from sqlalchemy import Column, Integer, Float, Enum, Date

# Importation des relations ORM
from sqlalchemy.orm import relationship

# Accès à l'instance SQLAlchemy
from app.extension import db

# Importation de l'énumération définissant les types de capteurs
from .enums import TypeCapteur

# Modèle représentant un capteur biomédical
class Capteur(db.Model):
    __tablename__ = 'capteur'  # Table des capteurs

    # Identifiant unique du capteur
    id = Column(Integer, primary_key=True)

    # Type de capteur (ex : température, tension, fréquence cardiaque)
    type = Column(Enum(TypeCapteur), nullable=False)

    # Relation avec les données médicales collectées par ce capteur
    donnees_mesures = relationship('DonneesMedicale', back_populates='capteur')
    
# -------------------------------------------------------------
# Classe Capteur : modèle représentant un capteur biomédical
# -------------------------------------------------------------
# - Sert à identifier les capteurs utilisés pour collecter des données médicales
# - Contient le type de capteur (défini via une énumération)
# - Stocke la dernière valeur mesurée et sa date
# - Établit une relation avec les données médicales associées
# - Permet de tracer l’origine des mesures dans le système
