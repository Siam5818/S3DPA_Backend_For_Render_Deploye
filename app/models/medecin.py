# Importation des types de colonnes et des clés étrangères
from sqlalchemy import Column, Integer, String, ForeignKey

# Importation des relations ORM
from sqlalchemy.orm import relationship

# Accès à l'instance SQLAlchemy
from app.extension import db

# Importation de la classe mère Personne (héritage)
from .personne import Personne

# Modèle représentant un médecin, héritant des attributs de Personne
class Medecin(Personne):
    __tablename__ = 'medecin'  # Table spécifique aux médecins

    # Clé primaire liée à la table 'personne' (héritage par jointure)
    id = Column(Integer, ForeignKey('personne.id'), primary_key=True)

    # Champ spécifique au médecin : sa spécialité médicale
    specialite = Column(String(100))

    # Configuration de l’héritage polymorphique : identifie cette classe comme 'medecin'
    __mapper_args__ = {
        'polymorphic_identity': 'medecin',
    }

    # Relation avec les analyses médicales effectuées par ce médecin
    analyses = relationship('Analyseur', back_populates='medecin')

    # Relation avec les alertes générées ou gérées par ce médecin
    alertes = relationship('Alerte', back_populates='medecin')
    
# -------------------------------------------------------------
# Classe Medecin : modèle représentant un professionnel de santé
# -------------------------------------------------------------
# - Hérite de tous les champs du modèle Personne (nom, email, etc.)
# - Ajoute un champ spécifique : 'specialite'
# - Utilise l’héritage polymorphique pour être identifié comme 'medecin'
# - Établit des relations avec les entités Analyseur et Alerte
# - Permet de retrouver toutes les analyses et alertes liées à ce médecin