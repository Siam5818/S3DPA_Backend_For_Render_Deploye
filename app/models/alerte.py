# Importation des types de colonnes et des clés étrangères
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum

# Importation des relations ORM
from sqlalchemy.orm import relationship

# Importation de la date/heure actuelle pour l’alerte
from datetime import datetime

# Accès à l'instance SQLAlchemy
from app.extension import db

# Importation des énumérations pour le type et le niveau d'urgence
from .enums import UrgenceEnum, TypeAlerte

# Modèle représentant une alerte médicale déclenchée pour un patient
class Alerte(db.Model):
    __tablename__ = 'alerte'  # Table des alertes médicales

    # Identifiant unique de l’alerte
    id = Column(Integer, primary_key=True)

    # Référence au patient concerné
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)

    # Référence au médecin responsable ou notifié
    medecin_id = Column(Integer, ForeignKey('medecin.id'), nullable=False)

    # Date et heure de déclenchement de l’alerte
    date_heure_alerte = Column(DateTime, default=datetime.utcnow)

    # Niveau d’urgence (ex : faible, modéré, critique)
    niveau_urgence = Column(Enum(UrgenceEnum), nullable=False)

    # Type d’alerte (ex : tension élevée, température anormale)
    type_alerte = Column(Enum(TypeAlerte), nullable=False)

    # Description libre de l’alerte (contexte, observations)
    description = Column(String(255))

    # État de traitement : False = non traitée, True = résolue
    etat_traitement = Column(Boolean, default=False)

    # Relation vers le patient concerné
    patient = relationship('Patient', back_populates='alertes')

    # Relation vers le médecin responsable
    medecin = relationship('Medecin', back_populates='alertes')
    
# -------------------------------------------------------------
# Classe Alerte : modèle représentant une alerte médicale
# -------------------------------------------------------------
# - Déclenchée lorsqu'une donnée médicale dépasse un seuil critique
# - Reliée à un patient et au médecin responsable
# - Contient le niveau d'urgence et le type d'alerte (via des enums)
# - Stocke une description et l'état de traitement (résolue ou non)
# - Permet de suivre les événements critiques dans le système