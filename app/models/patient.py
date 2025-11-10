# Importation des types de colonnes et des clés étrangères
from sqlalchemy import Column, Integer, ForeignKey

# Importation des relations ORM
from sqlalchemy.orm import relationship

# Accès à l'instance SQLAlchemy
from app.extension import db

# Importation de la classe mère Personne
from .personne import Personne

# Modèle représentant un patient, héritant des attributs de Personne
class Patient(Personne):
    __tablename__ = 'patient'  # Table spécifique aux patients

    # Clé primaire liée à la table 'personne' (héritage par jointure)
    id = Column(Integer, ForeignKey('personne.id'), primary_key=True)

    # Configuration de l’héritage polymorphique : identifie cette classe comme 'patient'
    __mapper_args__ = {
        'polymorphic_identity': 'patient',
    }

    # Relation avec les données médicales du patient
    donnees_phys = relationship('DonneesMedicale', back_populates='patient')

    # Relation avec les proches associés à ce patient
    proches = relationship('Proche', back_populates='patient', foreign_keys='Proche.patient_id')

    # Relation avec les analyses médicales du patient
    analyses = relationship('Analyseur', back_populates='patient')

    # Relation avec les alertes générées pour ce patient
    alertes = relationship('Alerte', back_populates='patient')
    
    
# -------------------------------------------------------------
# Classe Patient : modèle représentant un patient du système
# -------------------------------------------------------------
# - Hérite de tous les champs du modèle Personne (nom, email, etc.)
# - Identifié comme 'patient' via héritage polymorphique
# - Relié à plusieurs entités : données médicales, proches, analyses, alertes
# - Permet de naviguer facilement vers toutes les informations liées au patient