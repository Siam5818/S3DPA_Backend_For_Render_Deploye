# 🚀 Guide d'Utilisation - Insérer des Données Médicales

## Méthode 1: Via l'API REST (Recommandée)

### Endpoint
```
POST /v1/donnees
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}
```

### Payload
```json
{
  "patient_id": 6,
  "capteur_id": 1,
  "valeur_mesuree": 35.0,
  "medecin_id": 1
}
```

### Exemple cURL
```bash
curl -X POST http://localhost:5000/v1/donnees \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "patient_id": 6,
    "capteur_id": 1,
    "valeur_mesuree": 35.0,
    "medecin_id": 1
  }'
```

### Réponse (201 Created)
```json
{
  "message": "Donnée médicale enregistrée avec succès",
  "donnee": {
    "id": 17,
    "patient_id": 6,
    "capteur_id": 1,
    "valeur_mesuree": 35.0,
    "date_heure_mesure": "2025-12-22T12:00:00Z"
  }
}
```

### Ce qui se passe automatiquement:
1. ✅ DonneesMedicale créée
2. ✅ Analyseur créé 
3. ✅ Alerte créée (si anomalie)

---

## Méthode 2: Insertion par Lot (Multiple)

### Payload - Array de données
```json
[
  {
    "patient_id": 6,
    "capteur_id": 1,
    "valeur_mesuree": 37.0,
    "medecin_id": 1
  },
  {
    "patient_id": 6,
    "capteur_id": 3,
    "valeur_mesuree": 120,
    "medecin_id": 1
  }
]
```

### Chaque donnée déclenche son analyse indépendamment

---

## Méthode 3: Via le Script Python (Développement)

```python
from app import create_app
from app.services.donnee_medical_service import create_donnee_medicale

app = create_app()

with app.app_context():
    # Insérer une donnée
    donnee = create_donnee_medicale({
        "patient_id": 6,
        "capteur_id": 1,
        "valeur_mesuree": 35.5,
        "medecin_id": 1
    })
    
    print(f"Donnée créée: ID {donnee.id}")
    print(f"Analyses: {donnee.analyses}")
```

---

## ⚠️ Erreurs Courantes

### 1. Données insérées directement ❌
```python
# MAUVAIS - Aucune analyse ne sera créée!
donnee = DonneesMedicale(
    patient_id=6,
    capteur_id=1,
    valeur_mesuree=35.0
)
db.session.add(donnee)
db.session.commit()
```

**Résultat:** données en BD, mais pas d'Analyseur, pas d'Alerte

### 2. Champ medecin_id manquant ❌
```python
# MAUVAIS - L'analyse a besoin du medecin_id pour créer l'alerte
create_donnee_medicale({
    "patient_id": 6,
    "capteur_id": 1,
    "valeur_mesuree": 35.0
    # medecin_id manquant!
})
```

**Erreur:** `ValueError: Champs obligatoires manquants`

---

## 📊 Seuils Médicaux - Quand les Alertes se Déclenchent

### Température Corporelle
```
Seuil: 36.0°C - 37.5°C
Anomalie: < 36.0 ou > 37.5
Niveau: CRITIQUE
Exemple:
  ✅ 36.8°C → Pas d'alerte
  ⚠️  35.0°C → Alerte CRITIQUE
```

### Pression Artérielle  
```
Seuil: 90 - 140 mmHg
Anomalie: < 90 ou > 140
Niveau: CRITIQUE
Exemple:
  ✅ 120 mmHg → Pas d'alerte
  ⚠️  150 mmHg → Alerte CRITIQUE
```

### Rythme Cardiaque
```
Seuil: 60 - 100 bpm
Anomalie: < 60 ou > 100
Niveau: MOYEN
Exemple:
  ✅ 75 bpm → Pas d'alerte
  ⚠️  55 bpm → Alerte MOYENNE
```

---

## 🔍 Vérifier ce Qui a Été Créé

### Via Python
```python
from app import create_app
from app.models import DonneesMedicale, Analyseur, Alerte

app = create_app()
with app.app_context():
    donnee = DonneesMedicale.query.get(17)
    
    # Voir les analyses de cette donnée
    print(donnee.analyses)  # [<Analyseur>]
    
    # Voir les alertes du patient
    alertes = Alerte.query.filter_by(patient_id=donnee.patient_id).all()
    print(alertes)  # [<Alerte>, ...]
```

### Via SQL (PostgreSQL)
```sql
-- Voir les 10 dernières données
SELECT id, patient_id, capteur_id, valeur_mesuree, date_heure_mesure
FROM donnees_medicales
ORDER BY date_heure_mesure DESC
LIMIT 10;

-- Voir les analyses associées
SELECT * FROM analyseur WHERE donnee_medicale_id = 17;

-- Voir les alertes
SELECT * FROM alerte WHERE patient_id = 6 ORDER BY date_heure_alerte DESC;
```

---

## 🎯 Flux Complet - Étape par Étape

```
1. Client POST /v1/donnees
   ↓
2. Route: donnees_medicales_route.py
   ↓
3. Service: create_donnee_medicale()
   ├─ Valide les champs
   ├─ Crée DonneesMedicale
   ├─ db.session.flush()  ← Génère l'ID
   ├─ Appelle create_analyse()
   │  ├─ Récupère capteur & seuils
   │  ├─ Compare valeur vs seuils
   │  ├─ Crée Analyseur (toujours)
   │  ├─ Crée Alerte (si anomalie)
   │  └─ db.session.add()
   └─ db.session.commit()  ← Tout est sauvegardé
   ↓
4. Réponse: 201 Created avec la donnée créée
   ↓
5. En base de données:
   ✅ DonneesMedicale inséré
   ✅ Analyseur inséré
   ✅ Alerte inséré (si anomalie)
```

---

## 💾 Backup - Code pour Insérer en Bulk

```python
from app import create_app
from app.services.donnee_medical_service import create_donnee_medicale
import json

app = create_app()

donnees_a_inserer = [
    {"patient_id": 6, "capteur_id": 1, "valeur_mesuree": 35.0, "medecin_id": 1},
    {"patient_id": 6, "capteur_id": 3, "valeur_mesuree": 75.0, "medecin_id": 1},
    {"patient_id": 6, "capteur_id": 2, "valeur_mesuree": 145.0, "medecin_id": 1},
]

with app.app_context():
    for data in donnees_a_inserer:
        try:
            donnee = create_donnee_medicale(data)
            print(f"✓ Donnée {donnee.id} créée")
        except Exception as e:
            print(f"✗ Erreur: {e}")
```

---

**Version:** 1.0  
**Date:** 22 Décembre 2025  
**Status:** ✅ Prêt à utiliser
