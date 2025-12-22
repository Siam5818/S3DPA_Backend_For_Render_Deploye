# S3DPA Backend

Plateforme de gestion de santé numérique pour le suivi des patients, la gestion des données médicales et les alertes en temps réel via capteurs IoT.

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage](#démarrage)
- [Structure du projet](#structure-du-projet)
- [API Endpoints](#api-endpoints)
- [Authentification](#authentification)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Contribution](#contribution)

## 🎯 Aperçu

S3DPA Backend est une API REST construite avec Flask qui gère une plateforme complète de santé numérique. Elle permet de :

- Gérer les patients et leurs données personnelles
- Suivre les données médicales en temps réel
- Gérer les capteurs IoT pour le suivi des patients
- Automatiser les alertes basées sur les seuils médicaux
- Assurer la communication entre médecins, patients et proches
- Analyser les données médicales pour les tendances et rapports

## ✨ Fonctionnalités

### 🔐 Authentification & Autorisation
- Authentification par email/mot de passe avec JWT
- Rôles utilisateur (Patient, Médecin, Proche, Administrateur)
- Tokens JWT sécurisés avec expiration configurable
- Protection des routes avec authentification

### 👥 Gestion des utilisateurs
- **Patients** : Profils personnels et gestion des données médicales
- **Médecins** : Suivi des patients assignés et consultation des dossiers
- **Proches** : Accès limité aux données du patient autorisé
- **Administrateurs** : Gestion complète du système

### 📊 Gestion des données médicales
- Enregistrement des mesures de santé (tension, glycémie, etc.)
- Historique des données avec timestamps
- Groupage et analyse des données par patient
- Support des différents types de mesures

### 📡 Gestion des capteurs IoT
- Enregistrement et configuration des capteurs
- Suivi de l'état des capteurs (actif/inactif)
- Réception des données en temps réel
- Gestion du cycle de vie des capteurs

### ⚠️ Système d'alertes
- Génération automatique d'alertes basées sur les seuils
- Alertes pour valeurs anormales (tension, glycémie, etc.)
- Escalade automatique des alertes
- Historique complet des alertes
- Statuts d'alerte (En attente, Traitée, Fermée)

### 📈 Analyses et rapports
- Analyse des tendances des données médicales
- Génération de rapports de santé
- Statistiques par patient
- Export des données

### 💌 Communications
- Notifications par email
- Système de messages entre utilisateurs
- Alertes aux proches en cas d'urgence

## 🏗️ Architecture

```
S3DPA_Backend/
├── app/
│   ├── models/          # Modèles de données SQLAlchemy
│   ├── routes/          # Endpoints API
│   ├── services/        # Logique métier
│   ├── utils/           # Utilitaires (serializers, validation)
│   ├── extension.py     # Extensions Flask
│   └── __init__.py      # Factory Flask
├── migrations/          # Migrations de base de données (Alembic)
├── tests/               # Suite de tests
├── config.py            # Configuration de l'application
├── run.py               # Point d'entrée principal
├── requirements.txt     # Dépendances Python
├── Procfile             # Configuration Heroku/Render
└── seed.py              # Script de données de test
```

### Stack technologique

| Composant | Technology |
|-----------|-----------|
| Framework | Flask 3.1.2 |
| Base de données | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Authentification | Flask-JWT-Extended |
| Documentation API | Flasgger (Swagger) |
| Migrations | Alembic |
| Hash de mots de passe | bcrypt |
| CORS | Flask-CORS |
| Email | Flask-Mail |
| Serveur | Gunicorn |
| Tests | pytest |

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :

- **Python 3.8+** installé
- **PostgreSQL** (version 12+)
- **Git** pour les contrôles de version
- **pip** gestionnaire de paquets Python

## 💻 Installation

### 1. Cloner le projet

```bash
git clone <repository-url>
cd S3DPA_Backend
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv santevenv
santevenv\Scripts\activate

# macOS/Linux
python3 -m venv santevenv
source santevenv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Créer la base de données PostgreSQL

```sql
CREATE DATABASE s3dpa_db;
CREATE USER s3dpa_user WITH PASSWORD 'votre_mot_de_passe';
ALTER ROLE s3dpa_user SET client_encoding TO 'utf8';
ALTER ROLE s3dpa_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE s3dpa_db TO s3dpa_user;
```

## ⚙️ Configuration

### 1. Créer un fichier `.env`

À la racine du projet, créer un fichier `.env` avec les variables suivantes :

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_RUN_HOST=127.0.0.1
FLASK_RUN_PORT=5000

# Base de données PostgreSQL
DB_USER=s3dpa_user
DB_PASSWORD=votre_mot_de_passe_securise
DB_HOST=localhost
DB_PORT=5432
DB_NAME=s3dpa_db

# Sécurité - JWT
JWT_SECRET_KEY=votre_clé_secrète_très_longue_et_aléatoire
SESSION_SECRET_KEY=votre_session_secret_key
JWT_ACCESS_TOKEN_EXPIRES=3600

# Chiffrement des données sensibles
ENCRYPTION_KEY=votre_clé_chiffrement_base64

# Configuration Mail (Mailtrap ou autre service)
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=votre_mailtrap_username
MAIL_PASSWORD=votre_mailtrap_password
MAIL_FROM_ADDRESS=noreply@s3dpa.com
MAIL_FROM_NAME=S3DPA Platform

# URLs
RENDER_EXTERNAL_URL=http://localhost:5000
```

**⚠️ Sécurité** : 
- Générer des clés secrètes longues et aléatoires
- Ne jamais commiter le fichier `.env`
- Utiliser des services de gestion de secrets en production (Render, Heroku, AWS Secrets Manager)

### 2. Initialiser les migrations de base de données

```bash
# Créer les migrations
flask db upgrade

# Ou avec Alembic directement
alembic upgrade head
```

### 3. Charger les données de test (optionnel)

```bash
python seed.py
```

## 🚀 Démarrage

### Démarrage en développement

```bash
python run.py
```

L'application démarre sur `http://localhost:5000`

### Documentation API Swagger

Une fois l'application lancée, accédez à la documentation interactive :

```
http://localhost:5000/apidocs
```

### Démarrage en production

```bash
gunicorn run:app --bind 0.0.0.0:8000 --workers 4
```

## 📁 Structure du projet

### `app/models/`
Modèles de données SQLAlchemy :
- `personne.py` - Classe de base pour tous les utilisateurs
- `patient.py` - Profil patient
- `medecin.py` - Profil médecin
- `proche.py` - Proches du patient
- `capteur.py` - Configuration des capteurs IoT
- `donnees_medicales.py` - Mesures de santé
- `alerte.py` - Alertes générées
- `analyseur.py` - Analyses de données
- `enums.py` - Énumérations (rôles, statuts, etc.)

### `app/routes/`
Endpoints API par ressource :
- `auth_routes.py` - Authentification (login, register, logout)
- `patient_routes.py` - Gestion des profils patients
- `medecin_routes.py` - Gestion des profils médecins
- `proche_routes.py` - Gestion des proches
- `capteur_routes.py` - Configuration des capteurs
- `donnees_medicales_route.py` - Enregistrement des mesures
- `alerte_routes.py` - Gestion des alertes
- `analyse_route.py` - Analyses et rapports

### `app/services/`
Logique métier isolée :
- `auth_service.py` - Authentification et tokens JWT
- `patient_service.py` - Gestion des patients
- `medecin_service.py` - Gestion des médecins
- `capteur_service.py` - Gestion des capteurs
- `donnee_medical_service.py` - Logique des données médicales
- `alerte_service.py` - Génération et gestion des alertes
- `analyse_service.py` - Analyses et statistiques

### `app/utils/`
Utilitaires réutilisables :
- `serializers.py` - Conversion modèles → JSON
- `validation.py` - Validation des données

### `migrations/`
Historique des migrations de base de données avec Alembic

### `tests/`
Suite de tests automatisés (pytest)

## 🔌 API Endpoints

### 🔐 Authentification
```
POST   /v1/auth/register    # Créer un compte
POST   /v1/auth/login       # Connexion
POST   /v1/auth/logout      # Déconnexion
GET    /v1/auth/me          # Profil utilisateur actuel (protégé)
```

### 👤 Patients
```
GET    /v1/patients         # Liste des patients
GET    /v1/patients/<id>    # Détails d'un patient
POST   /v1/patients         # Créer un patient
PUT    /v1/patients/<id>    # Modifier un patient
DELETE /v1/patients/<id>    # Supprimer un patient
```

### 🏥 Médecins
```
GET    /v1/medecins         # Liste des médecins
GET    /v1/medecins/<id>    # Détails d'un médecin
POST   /v1/medecins         # Créer un médecin
PUT    /v1/medecins/<id>    # Modifier un médecin
```

### 👨‍👩‍👧 Proches
```
GET    /v1/proches          # Mes proches
POST   /v1/proches          # Ajouter un proche
DELETE /v1/proches/<id>     # Supprimer un proche
```

### 📡 Capteurs
```
GET    /v1/capteurs         # Liste des capteurs
POST   /v1/capteurs         # Enregistrer un capteur
PUT    /v1/capteurs/<id>    # Modifier configuration du capteur
DELETE /v1/capteurs/<id>    # Supprimer un capteur
```

### 📊 Données Médicales
```
POST   /v1/donnees-medicales              # Enregistrer une mesure
GET    /v1/donnees-medicales/<patient_id> # Historique des mesures
GET    /v1/donnees-medicales/<id>         # Détails d'une mesure
```

### ⚠️ Alertes
```
GET    /v1/alertes          # Liste des alertes
GET    /v1/alertes/<id>     # Détails d'une alerte
PUT    /v1/alertes/<id>     # Mettre à jour statut d'alerte
GET    /v1/alertes/patient/<patient_id>  # Alertes d'un patient
```

### 📈 Analyses
```
GET    /v1/analyses/patient/<patient_id>  # Analyses d'un patient
GET    /v1/analyses/tendances/<patient_id> # Tendances des données
```

## 🔐 Authentification

### Flux d'authentification

1. **Inscription** : POST `/v1/auth/register`
   ```json
   {
     "email": "user@example.com",
     "password": "SecurePassword123!",
     "nom": "Dupont",
     "prenom": "Jean"
   }
   ```

2. **Connexion** : POST `/v1/auth/login`
   ```json
   {
     "email": "user@example.com",
     "password": "SecurePassword123!"
   }
   ```

3. **Réponse** : Reçoit un JWT token
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "user": {
       "id": 1,
       "email": "user@example.com",
       "role": "patient"
     }
   }
   ```

4. **Utilisation du token** : Ajouter à chaque requête protégée
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Rôles et permissions

| Rôle | Permissions |
|------|-----------|
| **Patient** | Voir ses données, ajouter médecins/proches, consultation |
| **Médecin** | Consulter patients assignés, ajouter données, générer rapports |
| **Proche** | Accès limité aux données autorisées du patient |
| **Admin** | Accès complet au système |

## 🧪 Tests

### Exécuter tous les tests

```bash
pytest
```

### Exécuter des tests spécifiques

```bash
# Tests d'authentification
pytest tests/test_auth_login.py -v

# Tests de démarrage
pytest tests/test_app_startup.py -v

# Afficher les sorties print
pytest -s
```

### Couverture des tests

```bash
pytest --cov=app --cov-report=html
```

Le rapport HTML est généré dans `htmlcov/index.html`

### Fichiers de tests inclus

- `test_app_startup.py` - Vérification du démarrage de l'application
- `test_auth_login.py` - Tests de connexion
- `test_auth_login_success.py` - Tests de connexion réussie
- `test_auth_me_protected.py` - Tests de route protégée
- `test_donnee_medicale_create.py` - Tests de création de données
- `test_donnee_medicale_get.py` - Tests de récupération de données
- `test_donnee_medicale_patient.py` - Tests d'accès patient

## 🚢 Déploiement

### Déploiement sur Render

1. **Connecter le repository Git à Render**
   - Se connecter à [render.com](https://render.com)
   - Créer un nouveau "Web Service"
   - Connecter votre GitHub repository

2. **Configuration Render**
   - Build command : `pip install -r requirements.txt && alembic upgrade head`
   - Start command : `gunicorn run:app --bind 0.0.0.0:$PORT`

3. **Variables d'environnement**
   - Ajouter tous les variables du `.env` dans la section "Environment"

4. **Déploiement**
   - Chaque push sur `main` déclenche le déploiement automatique

### Déploiement sur Heroku

```bash
# Se connecter à Heroku
heroku login

# Créer une nouvelle application
heroku create s3dpa-backend

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Définir les variables d'environnement
heroku config:set FLASK_ENV=production
heroku config:set JWT_SECRET_KEY=votre_clé_secrète

# Déployer
git push heroku main
```

### Checklist de déploiement

- [ ] Tester en mode production localement : `FLASK_ENV=production python run.py`
- [ ] Vérifier tous les tests : `pytest`
- [ ] Mettre à jour les migrations : `alembic upgrade head`
- [ ] Configurer les variables d'environnement
- [ ] Configurer la sauvegarde de base de données
- [ ] Mettre en place la surveillance/logging
- [ ] Configurer les certificats HTTPS/SSL
- [ ] Tester les endpoints critiques en production

## 🤝 Contribution

### Guidelines de contribution

1. **Fork le repository**
2. **Créer une branche feature** : `git checkout -b feature/nom-feature`
3. **Commit vos changements** : `git commit -m "Add: description de la feature"`
4. **Push vers la branche** : `git push origin feature/nom-feature`
5. **Ouvrir une Pull Request**

### Conventions de code

- Suivre PEP 8
- Ajouter des docstrings aux fonctions
- Écrire des tests pour les nouvelles features
- Mettre à jour la documentation
- Commits descriptifs et atomiques

### Commit Messages

```
[Type]: Description brève

Type: Add, Fix, Update, Refactor, Remove, Docs
Exemple: "Add: endpoint pour récupérer alertes du patient"
```

## 📝 License

[Définir votre license ici - MIT, Apache 2.0, etc.]

## 📞 Support

Pour des questions ou issues :
- Ouvrir une Issue sur GitHub
- Contacter : [email de support]

## 🔄 Changelog

### Version 1.0.0 (Initial Release)
- ✅ Système d'authentification JWT
- ✅ Gestion des patients et médecins
- ✅ Système de données médicales
- ✅ Gestion des capteurs IoT
- ✅ Système d'alertes automatiques
- ✅ Analyses et rapports
- ✅ Documentation Swagger/OpenAPI

---

**Dernière mise à jour** : Décembre 2025

Pour rester à jour, consultez régulièrement ce README et la documentation API à `/apidocs`
