import os
from dotenv import load_dotenv
from urllib.parse import quote
from ast import literal_eval
from datetime import timedelta

# Chargement des variables d'environnement
load_dotenv()

# Fonction utilitaire pour convertir les booléens
def strtobool(value):
    try:
        return bool(literal_eval(value.capitalize()))
    except (ValueError, SyntaxError):
        return False

# Vérification des variables critiques
REQUIRED_ENV_VARS = [
    "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME",
    "JWT_SECRET_KEY", "MAIL_USERNAME", "MAIL_PASSWORD"
]

for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise RuntimeError(f"Variable d'environnement manquante : {var}")

# Configuration principale
class Config:
    """Configuration générale de l'application"""

    # Base de données PostgreSQL
    password = quote(os.getenv('DB_PASSWORD', ''))
    try:
        password.encode('utf-8')
    except UnicodeEncodeError:
        raise RuntimeError("Le mot de passe PostgreSQL contient des caractères non UTF-8.")
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER')}:{password}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # print(" URI PostgreSQL →", SQLALCHEMY_DATABASE_URI)

    # Clés de sécurité
    SECRET_KEY = os.getenv('SESSION_SECRET_KEY')  # utilisée par Flask pour les sessions
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # utilisée pour signer les tokens JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")))
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')  # utilisée pour le chiffrement des données sensibles

    # Configuration Mail (Mailtrap ou autre)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 2525))
    MAIL_USE_TLS = strtobool(os.getenv("MAIL_USE_TLS", "True"))
    MAIL_USE_SSL = strtobool(os.getenv("MAIL_USE_SSL", "False"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_FROM_ADDRESS", "noreply@example.com"),
        os.getenv("MAIL_FROM_NAME", "e-Santé Platform")
    )

    # Environnement Flask
    # Environnement Flask
    DEBUG = strtobool(os.getenv('FLASK_DEBUG', 'False'))
    ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", "5000"))

    # Déterminer l'URL dynamique
    PRIMARY_URL = os.getenv("RENDER_EXTERNAL_URL", f"http://{FLASK_RUN_HOST}:{FLASK_RUN_PORT}")

    #print(f"Backend de S3DPA vient d'être démarré en mode {ENV} sur {PRIMARY_URL}")
    #print(f"Voici l'Url de la documentation Swagger --> {PRIMARY_URL}/apidocs")

# Configuration spécifique au développement
class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

# Configuration spécifique à la production
class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False