from app import create_app
from app.extension import db, bcrypt
from app.models import Medecin, Patient, Proche, Capteur, TypeCapteur, DonneesMedicale, Alerte, TypeAlerte, UrgenceEnum
from app.services.donnee_medical_service import create_donnee_medicale
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Création des utilisateurs
    medecin1 = Medecin(
        nom="Anzize",
        prenom="Mohamed",
        email="anzize@gmedical.sn",
        phone="770000001",
        mot_de_passe=bcrypt.generate_password_hash("Passer123").decode("utf-8"),
        role="medecin",
        date_naissance="2000-12-28",
        specialite="Cardiologie",
        adresse="Dakar"
    )

    medecin2 = Medecin(
        nom="Aichatou",
        prenom="Djamila",
        email="adjamila@gmedical.sn",
        phone="780000002",
        mot_de_passe=bcrypt.generate_password_hash("Passer123").decode("utf-8"),
        role="medecin",
        date_naissance="2002-02-28",
        specialite="Pediatre",
        adresse="Dakar"
    )

    patient = Patient(
        nom="Darkam",
        prenom="Aliyane",
        email="adarkam@gmail.com",
        phone="770000002",
        mot_de_passe=bcrypt.generate_password_hash("Passer123").decode("utf-8"),
        role="patient",
        date_naissance="1976-05-15",
        adresse="Mbour",
    )

    proche = Proche(
        nom="Aliyane",
        prenom="Awa",
        email="aaliyane05@gmail.com",
        phone="770000003",
        mot_de_passe=bcrypt.generate_password_hash("Passer123").decode("utf-8"),
        role="proche",
        adresse="Dakar",
        date_naissance="1995-10-20",
        lien_parente="Fille",
        patient=patient
    )

    capteurs = [
            Capteur(type=TypeCapteur.temperature),
            Capteur(type=TypeCapteur.pression),
            Capteur(type=TypeCapteur.rythme)
        ]
    
    # Ajout des objets principaux
    #db.session.add_all([medecin1, medecin2, patient, proche, *capteurs])
    #db.session.commit()

    # CORRECTION: Utiliser create_donnee_medicale pour déclencher l'analyse
    # Les données doivent passer par le service pour générer les analyses et alertes
    
    # 1. Température anormale (< 36.0) → ALERTE CRITIQUE
    donnee1 = create_donnee_medicale({
        "patient_id": 6,
        "capteur_id": 1,
        "valeur_mesuree": 35.0,  # ANOMALIE: < 36.0
        "medecin_id": 1
    })
    print(f"✓ Donnée 1 créée: Température={donnee1.valeur_mesuree}°C → Analyse générée + Alerte")
    
    # 2. Rythme cardiaque anormal (< 60) → ALERTE MOYENNE
    donnee2 = create_donnee_medicale({
        "patient_id": 6,
        "capteur_id": 3,
        "valeur_mesuree": 55,  # ANOMALIE: < 60
        "medecin_id": 1
    })
    print(f"✓ Donnée 2 créée: Rythme={donnee2.valeur_mesuree} bpm → Analyse générée + Alerte")
    
    # 3. Rythme cardiaque normal (60-100) → NORMAL
    donnee3 = create_donnee_medicale({
        "patient_id": 6,
        "capteur_id": 3,
        "valeur_mesuree": 80,  # NORMAL: 60-100
        "medecin_id": 1
    })
    print(f"✓ Donnée 3 créée: Rythme={donnee3.valeur_mesuree} bpm → Analyse générée (normal)")

    print("\n Toutes les données ont été insérées avec analyses automatiques et alertes!")