#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 TEST COMPLET DU PIPELINE S3DPA
Valide que les données, analyses et alertes sont correctement créées
"""

import pytest
from app.extension import db
from app.models import DonneesMedicale, Analyseur, Alerte, Patient, Medecin, Capteur, TypeCapteur
from app.services.donnee_medical_service import create_donnee_medicale


def test_pipeline_donnees_normales(app):
    """Test pipeline avec une donnée normale"""
    
    with app.app_context():
        # Setup: Créer données de test
        patient = Patient(
            nom="Test", prenom="Patient",
            email="test@example.com", phone="123456789",
            mot_de_passe="test123", role="patient",
            date_naissance="1990-01-01", adresse="Test"
        )
        medecin = Medecin(
            nom="Test", prenom="Medecin",
            email="medecin@example.com", phone="987654321",
            mot_de_passe="test123", role="medecin",
            date_naissance="1980-01-01", specialite="Cardio",
            adresse="Test"
        )
        capteur = Capteur(type=TypeCapteur.temperature)
        
        db.session.add_all([patient, medecin, capteur])
        db.session.commit()
        
        # Action: Insérer une donnée normale
        donnee = create_donnee_medicale({
            "patient_id": patient.id,
            "capteur_id": capteur.id,
            "valeur_mesuree": 36.8,
            "medecin_id": medecin.id
        })
        
        # Assert: Vérifier que l'analyse a été créée
        assert donnee.id is not None
        assert len(donnee.analyses) == 1
        assert "normal" in donnee.analyses[0].resultat.lower()


def test_pipeline_donnees_anomales_temperature(app):
    """Test pipeline avec une donnée anomale (température basse)"""
    
    with app.app_context():
        # Setup: Créer données de test
        patient = Patient(
            nom="Test2", prenom="Patient",
            email="test2@example.com", phone="123456789",
            mot_de_passe="test123", role="patient",
            date_naissance="1990-01-01", adresse="Test"
        )
        medecin = Medecin(
            nom="Test2", prenom="Medecin",
            email="medecin2@example.com", phone="987654321",
            mot_de_passe="test123", role="medecin",
            date_naissance="1980-01-01", specialite="Cardio",
            adresse="Test"
        )
        capteur = Capteur(type=TypeCapteur.temperature)
        
        db.session.add_all([patient, medecin, capteur])
        db.session.commit()
        
        # Action: Insérer une donnée anomale
        donnee = create_donnee_medicale({
            "patient_id": patient.id,
            "capteur_id": capteur.id,
            "valeur_mesuree": 35.0,
            "medecin_id": medecin.id
        })
        
        # Assert: Vérifier que l'analyse ET l'alerte ont été créées
        assert donnee.id is not None
        assert len(donnee.analyses) == 1
        assert "Anomalie" in donnee.analyses[0].resultat
        
        alerte = Alerte.query.filter_by(patient_id=patient.id).first()
        assert alerte is not None
        assert alerte.niveau_urgence.value == "Critique"


def test_pipeline_donnees_anomales_rythme(app):
    """Test pipeline avec une donnée anomale (rythme cardiaque bas)"""
    
    with app.app_context():
        # Setup: Créer données de test
        patient = Patient(
            nom="Test3", prenom="Patient",
            email="test3@example.com", phone="123456789",
            mot_de_passe="test123", role="patient",
            date_naissance="1990-01-01", adresse="Test"
        )
        medecin = Medecin(
            nom="Test3", prenom="Medecin",
            email="medecin3@example.com", phone="987654321",
            mot_de_passe="test123", role="medecin",
            date_naissance="1980-01-01", specialite="Cardio",
            adresse="Test"
        )
        capteur = Capteur(type=TypeCapteur.rythme)
        
        db.session.add_all([patient, medecin, capteur])
        db.session.commit()
        
        # Action: Insérer une donnée anomale
        donnee = create_donnee_medicale({
            "patient_id": patient.id,
            "capteur_id": capteur.id,
            "valeur_mesuree": 55,
            "medecin_id": medecin.id
        })
        
        # Assert: Vérifier que l'analyse ET l'alerte ont été créées
        assert donnee.id is not None
        assert len(donnee.analyses) == 1
        assert "Anomalie" in donnee.analyses[0].resultat
        
        alerte = Alerte.query.filter_by(patient_id=patient.id).first()
        assert alerte is not None
        assert alerte.niveau_urgence.value == "Moyenne"


def test_pipeline_complete(app):
    """Test complet du pipeline avec plusieurs scénarios"""
    
    with app.app_context():
        initial_donnees = DonneesMedicale.query.count()
        initial_analyses = Analyseur.query.count()
        initial_alertes = Alerte.query.count()
        
        # Setup
        patient = Patient(
            nom="Pipeline", prenom="Test",
            email="pipeline@example.com", phone="123456789",
            mot_de_passe="test123", role="patient",
            date_naissance="1990-01-01", adresse="Test"
        )
        medecin = Medecin(
            nom="Pipeline", prenom="Med",
            email="med@example.com", phone="987654321",
            mot_de_passe="test123", role="medecin",
            date_naissance="1980-01-01", specialite="Cardio",
            adresse="Test"
        )
        capteur_temp = Capteur(type=TypeCapteur.temperature)
        capteur_rythme = Capteur(type=TypeCapteur.rythme)
        
        db.session.add_all([patient, medecin, capteur_temp, capteur_rythme])
        db.session.commit()
        
        # Action: 3 mesures (1 normale, 2 anomales)
        d1 = create_donnee_medicale({
            "patient_id": patient.id, "capteur_id": capteur_temp.id,
            "valeur_mesuree": 36.8, "medecin_id": medecin.id
        })
        d2 = create_donnee_medicale({
            "patient_id": patient.id, "capteur_id": capteur_temp.id,
            "valeur_mesuree": 35.0, "medecin_id": medecin.id
        })
        d3 = create_donnee_medicale({
            "patient_id": patient.id, "capteur_id": capteur_rythme.id,
            "valeur_mesuree": 55, "medecin_id": medecin.id
        })
        
        # Assert
        final_donnees = DonneesMedicale.query.count()
        final_analyses = Analyseur.query.count()
        final_alertes = Alerte.query.count()
        
        assert final_donnees - initial_donnees == 3, "3 données doivent être créées"
        assert final_analyses - initial_analyses == 3, "3 analyses doivent être créées"
        assert final_alertes - initial_alertes == 2, "2 alertes doivent être créées (pour les 2 anomalies)"


