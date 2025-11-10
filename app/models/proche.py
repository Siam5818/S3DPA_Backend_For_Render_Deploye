# Importation des types de colonnes et des clés étrangères
from sqlalchemy import Column, Integer, String, ForeignKey

# Importation des relations ORM
from sqlalchemy.orm import relationship

# Accès à l'instance SQLAlchemy
from app.extension import db
from .personne import Personne

# Modèle représentant un proche d’un patient
class Proche(Personne):
    __tablename__ = 'proche'  # Table spécifique aux proches

    # Clé primaire liée à la table 'personne' (héritage par jointure)
    id = Column(Integer, ForeignKey('personne.id'), primary_key=True) 

    # Type de lien avec le patient (ex : mère, frère, ami)
    lien_parente = Column(String(100))

    # Clé étrangère vers le patient concerné
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)

    # Relation bidirectionnelle avec le modèle Patient
    patient = relationship('Patient', back_populates='proches', foreign_keys=[patient_id])

    # Identité polymorphique (inutile ici si Proche n’hérite pas de Personne)
    __mapper_args__ = {
        'polymorphic_identity': 'proche',
    }
    
# -------------------------------------------------------------
# Classe Proche : modèle représentant un proche lié à un patient
# -------------------------------------------------------------
# - Hérite de Personne → possède nom, prénom, email, mot de passe, etc.
# - Peut être authentifié (si tu le souhaites)
# - Contient un champ 'lien_parente' pour définir la relation (ex : père, sœur)
# - Relié à un patient via une clé étrangère 'patient_id'
# - Utilise une relation bidirectionnelle avec le modèle Patient
# - Identifié comme 'proche' via héritage polymorphique