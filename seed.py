from app import create_app
from app.extension import db, bcrypt
from app.models import Medecin, Patient, Proche, Capteur, TypeCapteur, DonneesMedicale, Alerte, TypeAlerte, UrgenceEnum
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Création des utilisateurs
    '''medecin = Medecin(
        nom="Anzize",
        prenom="Mohamed",
        email="anzize@gmedical.sn",
        phone="770000001",
        mot_de_passe=bcrypt.generate_password_hash("Passer123").decode("utf-8"),
        role="medecin",
        date_naissance="2000-12-28",
        specialite="Cardiologie",
        adresse="Dakar"
    )'''

    medecin = Medecin(
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

    donnees = [
        DonneesMedicale(patient_id=2, capteur_id=1, valeur_mesuree=36.8, date_heure_mesure=datetime.now() - timedelta(hours=5)),
        DonneesMedicale(patient_id=2, capteur_id=1, valeur_mesuree=37.1, date_heure_mesure=datetime.now() - timedelta(hours=3)),
        DonneesMedicale(patient_id=2, capteur_id=1, valeur_mesuree=36.9, date_heure_mesure=datetime.now() - timedelta(hours=1)),
    ]

    alerte = Alerte(
        patient_id=2,
        medecin_id=1,
        niveau_urgence=UrgenceEnum.critique,
        type_alerte=TypeAlerte.urgence,
        description="Température corporelle anormalement détectée par le capteur.",
        etat_traitement=False
    )

    # Insertion dans la base
    db.session.add(medecin)
    db.session.commit()

    print("Utilisateurs insérés avec succès")