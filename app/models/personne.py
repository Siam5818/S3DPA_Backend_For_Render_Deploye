# Importation des types de colonnes SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy import Column, Integer, String, Date  # doublon à fusionner

# Importation de l'instance SQLAlchemy et du module de hachage bcrypt
from app.extension import db, bcrypt

# Modèle de base représentant une personne (classe mère abstraite)
class Personne(db.Model):
    __tablename__ = 'personne'  # Nom de la table en base

    # Identifiant unique
    id = Column(Integer, primary_key=True)

    # Informations personnelles obligatoires
    prenom = Column(String(50), nullable=False)
    nom = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)  # Email unique pour l'authentification
    phone = Column(String(20), unique=True, nullable=False)  # Numéro de téléphone unique
    
    # Informations facultatives
    adresse = Column(String(255))
    date_naissance = Column(Date)

    # Mot de passe haché
    mot_de_passe = Column(String(255), nullable=False)

    # Rôle fonctionnel (medecin, patient, proche)
    role = Column(String(50))

    # Champ technique utilisé pour l’héritage polymorphique
    type = db.Column(db.String(50))

    # Configuration de l’héritage : permet à SQLAlchemy de distinguer les sous-classes
    __mapper_args__ = {
        'polymorphic_identity': 'personne',  # Identité par défaut
        'polymorphic_on': type               # Champ utilisé pour différencier les enfants
    }

    # Méthode pour hacher et stocker un mot de passe
    def set_password(self, password):
        self.mot_de_passe = bcrypt.generate_password_hash(password).decode('utf-8')

    # Méthode pour vérifier si un mot de passe correspond au mot de passe haché
    def check_password(self, password):
        return bcrypt.check_password_hash(self.mot_de_passe, password)
    
# -------------------------------------------------------------
# Classe Personne : modèle abstrait pour tous les types d'usagers
# -------------------------------------------------------------
# - Sert de base commune pour les rôles : Medecin, Patient, Proche
# - Contient les champs partagés (nom, email, mot de passe, etc.)
# - Utilise l’héritage polymorphique pour différencier les sous-classes
# - Ne doit pas être instanciée directement sauf cas générique
# - Le champ 'type' permet à SQLAlchemy de router vers la bonne table enfant
# - Les méthodes de hachage assurent la sécurité des mots de passe