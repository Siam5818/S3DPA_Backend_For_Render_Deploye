#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 TEST COMPLET DU PIPELINE S3DPA
Valide que les données, analyses et alertes sont correctement créées
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent pour importer app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.extension import db
from app.models import DonneesMedicale, Analyseur, Alerte, Patient, Medecin, Capteur, TypeCapteur
from app.services.donnee_medical_service import create_donnee_medicale
from datetime import datetime

def test_pipeline():
    """Test complet du pipeline"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("🧪 TEST DU PIPELINE S3DPA")
        print("=" * 80)
        
        # Test 1: Vérifier les données existantes
        print("\n[TEST 1] Vérification de l'état initial")
        print("-" * 80)
        
        donnees_count = DonneesMedicale.query.count()
        analyses_count = Analyseur.query.count()
        alertes_count = Alerte.query.count()
        
        print(f"Données médicales: {donnees_count}")
        print(f"Analyses: {analyses_count}")
        print(f"Alertes: {alertes_count}")
        
        # Test 2: Insérer une donnée NORMALE
        print("\n[TEST 2] Insertion d'une donnée NORMALE (Température 36.8°C)")
        print("-" * 80)
        
        try:
            donnee_normale = create_donnee_medicale({
                "patient_id": 6,
                "capteur_id": 1,  # Temperature
                "valeur_mesuree": 36.8,
                "medecin_id": 1
            })
            print(f"✅ Donnée créée: ID {donnee_normale.id}")
            print(f"   Valeur: {donnee_normale.valeur_mesuree}°C")
            print(f"   Capteur: {donnee_normale.capteur.type.value}")
            
            # Vérifier l'analyse
            if donnee_normale.analyses:
                analyse = donnee_normale.analyses[0]
                print(f"✅ Analyse créée: {analyse.resultat}")
            else:
                print(f"❌ ERREUR: Pas d'analyse créée!")
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
        
        # Test 3: Insérer une donnée ANOMALE (Température trop basse)
        print("\n[TEST 3] Insertion d'une donnée ANOMALE (Température 35.0°C)")
        print("-" * 80)
        
        try:
            donnee_anomale_temp = create_donnee_medicale({
                "patient_id": 6,
                "capteur_id": 1,  # Temperature
                "valeur_mesuree": 35.0,
                "medecin_id": 1
            })
            print(f"✅ Donnée créée: ID {donnee_anomale_temp.id}")
            print(f"   Valeur: {donnee_anomale_temp.valeur_mesuree}°C")
            print(f"   Capteur: {donnee_anomale_temp.capteur.type.value}")
            
            # Vérifier l'analyse
            if donnee_anomale_temp.analyses:
                analyse = donnee_anomale_temp.analyses[0]
                print(f"✅ Analyse créée: {analyse.resultat}")
                
                # Vérifier l'alerte
                alerte = Alerte.query.filter_by(patient_id=6).order_by(Alerte.id.desc()).first()
                if alerte:
                    print(f"⚠️  Alerte créée: {alerte.type_alerte.value} ({alerte.niveau_urgence.value})")
                    print(f"   Description: {alerte.description}")
                else:
                    print(f"❌ ERREUR: Pas d'alerte créée pour l'anomalie!")
            else:
                print(f"❌ ERREUR: Pas d'analyse créée!")
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
        
        # Test 4: Insérer une donnée ANOMALE (Rythme trop bas)
        print("\n[TEST 4] Insertion d'une donnée ANOMALE (Rythme 55 bpm)")
        print("-" * 80)
        
        try:
            donnee_anomale_rhythme = create_donnee_medicale({
                "patient_id": 6,
                "capteur_id": 3,  # Rythme
                "valeur_mesuree": 55,
                "medecin_id": 1
            })
            print(f"✅ Donnée créée: ID {donnee_anomale_rhythme.id}")
            print(f"   Valeur: {donnee_anomale_rhythme.valeur_mesuree} bpm")
            print(f"   Capteur: {donnee_anomale_rhythme.capteur.type.value}")
            
            # Vérifier l'analyse
            if donnee_anomale_rhythme.analyses:
                analyse = donnee_anomale_rhythme.analyses[0]
                print(f"✅ Analyse créée: {analyse.resultat}")
                
                # Vérifier l'alerte
                alertes = Alerte.query.filter_by(patient_id=6).order_by(Alerte.id.desc()).limit(2).all()
                if alertes:
                    alerte = alertes[0]
                    print(f"⚠️  Alerte créée: {alerte.type_alerte.value} ({alerte.niveau_urgence.value})")
                    print(f"   Description: {alerte.description}")
                else:
                    print(f"❌ ERREUR: Pas d'alerte créée pour l'anomalie!")
            else:
                print(f"❌ ERREUR: Pas d'analyse créée!")
                
        except Exception as e:
            print(f"❌ ERREUR: {e}")
        
        # Test 5: Vérification finale
        print("\n[TEST 5] Vérification finale de l'intégrité")
        print("-" * 80)
        
        donnees_count_new = DonneesMedicale.query.count()
        analyses_count_new = Analyseur.query.count()
        alertes_count_new = Alerte.query.count()
        
        print(f"Données médicales: {donnees_count_new} (ajout: {donnees_count_new - donnees_count})")
        print(f"Analyses: {analyses_count_new} (ajout: {analyses_count_new - analyses_count})")
        print(f"Alertes: {alertes_count_new} (ajout: {alertes_count_new - alertes_count})")
        
        # Vérifier les relations
        print("\n[TEST 6] Vérification des relations")
        print("-" * 80)
        
        derniere_donnee = DonneesMedicale.query.order_by(DonneesMedicale.id.desc()).first()
        if derniere_donnee:
            print(f"Donnée ID {derniere_donnee.id}:")
            print(f"  - Patient: {derniere_donnee.patient.nom} {derniere_donnee.patient.prenom}")
            print(f"  - Capteur: {derniere_donnee.capteur.type.value}")
            print(f"  - Valeur: {derniere_donnee.valeur_mesuree}")
            print(f"  - Analyses liées: {len(derniere_donnee.analyses)}")
            if derniere_donnee.analyses:
                for analyse in derniere_donnee.analyses:
                    print(f"    └─ Analyse ID {analyse.id}: {analyse.resultat[:50]}...")
        
        # Résumé final
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ FINAL")
        print("=" * 80)
        
        if analyses_count_new > analyses_count:
            print("✅ Analyses créées correctement")
        else:
            print("❌ Aucune analyse n'a été créée")
        
        if alertes_count_new > alertes_count:
            print("✅ Alertes créées pour les anomalies")
        else:
            print("⚠️  Aucune alerte n'a été créée (vérifiez les valeurs anomales)")
        
        print("=" * 80)

if __name__ == "__main__":
    test_pipeline()
