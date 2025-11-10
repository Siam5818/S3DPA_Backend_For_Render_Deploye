# Importation des types de colonnes et des clés étrangères
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

# Importation des relations ORM
from sqlalchemy.orm import relationship

# Importation de la date/heure actuelle pour l’analyse
from datetime import datetime

# Accès à l'instance SQLAlchemy
from app.extension import db

# Modèle représentant une analyse médicale effectuée par un médecin
class Analyseur(db.Model):
    __tablename__ = 'analyseur'  # Table des analyses médicales

    # Identifiant unique de l’analyse
    id = Column(Integer, primary_key=True)

    # Référence au patient concerné
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)

    # Référence au médecin ayant effectué l’analyse
    medecin_id = Column(Integer, ForeignKey('medecin.id'), nullable=False)

    # Référence à la donnée médicale analysée
    donnee_medicale_id = Column(Integer, ForeignKey('donnees_medicales.id'), nullable=False)

    # Résultat de l’analyse (ex : "normal", "anomalie détectée")
    resultat = Column(String(255))

    # Date et heure de l’analyse (défaut : maintenant)
    date_analyse = Column(DateTime, default=datetime.utcnow)

    # Relation vers le patient concerné
    patient = relationship('Patient', back_populates='analyses')

    # Relation vers le médecin ayant effectué l’analyse
    medecin = relationship('Medecin', back_populates='analyses')

    # Relation vers la donnée médicale analysée
    donnee_medicale = relationship('DonneesMedicale', back_populates='analyses')
    
# -------------------------------------------------------------
# Classe Analyseur : modèle représentant une analyse médicale
# -------------------------------------------------------------
# - Relie un patient, un médecin et une donnée médicale spécifique
# - Stocke le résultat de l’analyse et sa date d’exécution
# - Permet de tracer qui a analysé quoi, quand, et avec quel résultat
# - Sert de base pour le suivi médical, les alertes ou les diagnostics