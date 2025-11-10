# Importation des types de colonnes et des clés étrangères
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey

# Importation des relations ORM
from sqlalchemy.orm import relationship

# Importation de la date/heure actuelle pour les mesures
from datetime import datetime

# Accès à l'instance SQLAlchemy
from app.extension import db

# Modèle représentant une donnée médicale mesurée par un capteur
class DonneesMedicale(db.Model):
    __tablename__ = 'donnees_medicales'  # Table des mesures médicales

    # Identifiant unique de la donnée
    id = Column(Integer, primary_key=True)

    # Référence au patient concerné
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)

    # Référence au capteur ayant effectué la mesure
    capteur_id = Column(Integer, ForeignKey('capteur.id'), nullable=False)

    # Valeur mesurée (ex : tension, température, etc.)
    valeur_mesuree = Column(Float, nullable=False)

    # Date et heure de la mesure (défaut : maintenant)
    date_heure_mesure = Column(DateTime, default=datetime.utcnow)

    # Relation vers le patient concerné
    patient = relationship('Patient', back_populates='donnees_phys')

    # Relation vers le capteur ayant effectué la mesure
    capteur = relationship('Capteur', back_populates='donnees_mesures')

    # Relation vers les analyses effectuées sur cette donnée
    analyses = relationship('Analyseur', back_populates='donnee_medicale')

    def __repr__(self):
        return f"<DonneeMedicale(patient={self.patient_id}, capteur={self.capteur_id}, valeur={self.valeur_mesuree})>"
    
# -------------------------------------------------------------
# Classe DonneesMedicale : mesure captée liée à un patient
# -------------------------------------------------------------
# - Représente une donnée médicale enregistrée par un capteur
# - Reliée à un patient et à un capteur via des clés étrangères
# - Contient la valeur mesurée et la date/heure de la mesure
# - Permet de retrouver les analyses associées à cette donnée
# - Sert de base pour le suivi médical automatisé ou manuel