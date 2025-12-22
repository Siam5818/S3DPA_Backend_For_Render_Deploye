# 📊 Analyse du Pipeline S3DPA - Diagnostic Complet

## 🔍 Problème Identifié

**L'analyse automatique et les alertes ne sont pas déclenchées quand les données sont insérées directement en base de données.**

### Root Cause
Vous aviez deux approches différentes :

#### ❌ **MAUVAISE** : Insertion directe (dans l'ancien seed.py)
```python
# Données insérées SANS analyse
donnees = [
    DonneesMedicale(patient_id=6, capteur_id=1, valeur_mesuree=40, ...),
]
db.session.add_all([*donnees])
db.session.commit()
```
**Résultat:** aucune `Analyseur` créée, aucune `Alerte` déclenchée

#### ✅ **CORRECT** : Via le service (nouvelle approche)
```python
# Données insérées AVEC analyse automatique
donnee = create_donnee_medicale({
    "patient_id": 6,
    "capteur_id": 1,
    "valeur_mesuree": 35.0,
    "medecin_id": 1
})
```
**Résultat:** `Analyseur` ET `Alerte` créées automatiquement

---

## 📈 Pipeline Correct

```
┌─────────────┐
│   Capteur   │ (Hardware/IoT)
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────┐
│  create_donnee_medicale()           │ ← SERVICE
│  (donnee_medical_service.py)        │
├─────────────────────────────────────┤
│ 1. Valide les champs               │
│ 2. Crée DonneesMedicale            │
│ 3. db.session.flush() → génère ID  │
│ 4. Appelle create_analyse()        │
│ 5. db.session.commit()             │
└──────┬──────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│  create_analyse()                   │ ← SERVICE LOGIQUE MÉDICALE
│  (analyse_service.py)              │
├─────────────────────────────────────┤
│ 1. Récupère type_capteur           │
│ 2. Récupère seuils de SEUILS.py    │
│ 3. Vérifie: valeur < min/max?      │
│ 4. Si anomalie: crée Alerte        │
│ 5. Crée Analyseur (toujours)       │
│ 6. db.session.add() (pas commit)   │
└──────┬──────────────────────────────┘
       │
       ↓
┌──────────────────────┐
│ Modèles (Tables BD) │
├──────────────────────┤
│ ✅ DonneesMedicale   │ (1 enregistrement)
│ ✅ Analyseur         │ (1 enregistrement)
│ ✅ Alerte (si anomal)│ (0 ou 1 selon seuil)
└──────────────────────┘
```

---

## 🐛 Bugs Corrigés

### Bug #1: Énums Incorrects dans `seuils.py`
**Avant:**
```python
"niveau_urgence": UrgenceEnum.critique.value,  # ❌ String "Critique"
"type_alerte": TypeAlerte.urgence.value,        # ❌ String "Urgence"
```

**Problème:** PostgreSQL attend l'enum, pas une string → `DataError: invalid input value for enum`

**Après:**
```python
"niveau_urgence": UrgenceEnum.critique,  # ✅ Enum object
"type_alerte": TypeAlerte.urgence,        # ✅ Enum object
```

---

## 📋 Architecture Actuelle

### Modèles (app/models/)
| Modèle | Role | Relations |
|--------|------|-----------|
| `DonneesMedicale` | Mesure captée | Patient, Capteur, Analyseur |
| `Analyseur` | Analyse médicale | Patient, Medecin, DonneesMedicale |
| `Alerte` | Alerte critique | Patient, Medecin |
| `Capteur` | Appareil IoT | TypeCapteur (Temp/Pression/Rythme) |

### Services (app/services/)
| Service | Fonction |
|---------|----------|
| `donnee_medical_service.py` | Gère CRUD + déclenche analyse |
| `analyse_service.py` | Vérifie seuils, crée alertes |

### Routes (app/routes/)
| Route | Endpoint |
|-------|----------|
| `donnees_medicales_route.py` | POST `/donnees` → appelle `create_donnee_medicale()` |

---

## 🔧 Seuils Médicaux Configurés

```python
SEUILS_CAPTEURS = {
    TypeCapteur.temperature: {
        "min": 36.0,
        "max": 37.5,
        "niveau_urgence": UrgenceEnum.critique,
        "type_alerte": TypeAlerte.urgence
    },
    TypeCapteur.pression: {
        "min": 90,
        "max": 140,
        "niveau_urgence": UrgenceEnum.critique,
        "type_alerte": TypeAlerte.urgence
    },
    TypeCapteur.rythme: {
        "min": 60,
        "max": 100,
        "niveau_urgence": UrgenceEnum.moyenne,
        "type_alerte": TypeAlerte.avertissement
    }
}
```

**Exemples de déclenchement:**
- Température 35.0°C → ⚠️ Alerte Critique (< 36.0)
- Rythme 55 bpm → ⚠️ Alerte Moyenne (< 60)
- Rythme 80 bpm → ✅ Pas d'alerte (60-100 = normal)

---

## ✅ Checklist - Comment Ça Marche Maintenant

1. **Route POST `/v1/donnees`** accepte:
   ```json
   {
     "patient_id": 6,
     "capteur_id": 1,
     "valeur_mesuree": 35.0,
     "medecin_id": 1
   }
   ```

2. **Service `create_donnee_medicale()`:**
   - Valide les champs
   - Crée DonneesMedicale
   - Appelle `create_analyse()`

3. **Service `create_analyse()`:**
   - Récupère les seuils
   - Compare valeur vs seuils
   - Crée Analyseur (toujours)
   - Crée Alerte (si anomalie)

4. **Commit global:** une seule transaction SQL avec tous les objets

---

## 🧪 Test - Données Insérées par Seed

```
✓ 16 Données Médicales
  ├─ ID 14: Temperature 35.0°C  → Anomalie
  ├─ ID 15: Rythme 55 bpm       → Anomalie
  └─ ID 16: Rythme 80 bpm       → Normal

✓ 3 Analyses Créées
  ├─ ID 1: "Anomalie détectée : valeur 35.0 hors seuil [36.0 - 37.5]"
  ├─ ID 2: "Anomalie détectée : valeur 55 hors seuil [60 - 100]"
  └─ ID 3: "Résultat normal : valeur dans les seuils"

✓ 3 Alertes Créées
  ├─ ID 3: Urgence (Critique) - Température
  ├─ ID 4: Avertissement (Moyenne) - Rythme
  └─ (Pas d'alerte pour rythme normal)
```

---

## 🎯 Recommandations

1. **TOUJOURS** insérer les données via `create_donnee_medicale()`, jamais directement
2. **Pour les tests:** utiliser le seed.py corrigé ou faire des POST sur `/v1/donnees`
3. **Pour l'API REST:** le client doit POST avec `patient_id`, `capteur_id`, `valeur_mesuree`, `medecin_id`
4. **Monitorer les alertes** via route GET `/v1/alertes` (à implémenter si nécessaire)

---

## 📚 Structure des Fichiers Clés

```
app/
├── services/
│   ├── donnee_medical_service.py  ← create_donnee_medicale()
│   └── analyse_service.py          ← create_analyse()
├── models/
│   ├── donnees_medicales.py
│   ├── analyseur.py
│   ├── alerte.py
│   └── enums.py
├── utils/
│   └── seuils.py                   ← SEUILS_CAPTEURS
└── routes/
    └── donnees_medicales_route.py  ← POST /v1/donnees
```

---

**Status:** ✅ Pipeline corrigé et testé avec succès
**Date:** 22 Décembre 2025
