# Importation des extensions Flask utilisées dans le projet
from flask_sqlalchemy import SQLAlchemy         # ORM pour la base de données
from flask_migrate import Migrate               # Gestion des migrations Alembic
from flask_bcrypt import Bcrypt                 # Hachage sécurisé des mots de passe
from flask_jwt_extended import JWTManager       # Gestion des tokens JWT
from flask_mail import Mail                     # Envoi d’e-mails via SMTP
from flasgger import Swagger                    # Documentation Swagger pour l’API

# -------------------------------------------------------------
# Configuration Swagger : définition du template
# -------------------------------------------------------------
# - Active le bouton "Authorize" dans Swagger UI
# - Permet de tester les routes protégées par JWT
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API S3DPA",
        "description": "Documentation des endpoints sécurisés",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Token JWT au format: Bearer <votre_token>"
        }
    },
    "security": [{"BearerAuth": []}]
}

# -------------------------------------------------------------
# Instanciation des extensions (à l’état global, sans app encore)
# -------------------------------------------------------------
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()
swagger = Swagger(template=swagger_template)
blacklist = set()

# -------------------------------------------------------------
# Fonction d’initialisation des extensions avec l’application Flask
# -------------------------------------------------------------
# - Appelée dans create_app() pour lier les modules à l’instance Flask
def init_extension(app):
    db.init_app(app)             # Liaison de SQLAlchemy à l’app
    migrate.init_app(app, db)    # Liaison de Migrate avec SQLAlchemy
    bcrypt.init_app(app)         # Activation du hachage sécurisé
    jwt.init_app(app)            # Activation du gestionnaire JWT
    mail.init_app(app)           # Activation du module d’envoi d’e-mails
    swagger.init_app(app)        # Activation de la documentation Swagger
    # Vérification si le token est dans la blacklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in blacklist
    
# -------------------------------------------------------------
# extension.py : initialisation des extensions Flask
# -------------------------------------------------------------
# - Centralise l’instanciation des modules utilisés dans l’application
# - Facilite l’importation et la configuration dans create_app()
# - Permet une architecture modulaire et maintenable