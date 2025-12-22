# 🚀 Quick Start - Utiliser le Pipeline

## ✨ En 30 Secondes

### Via l'API REST
```bash
curl -X POST http://localhost:5000/v1/donnees \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 6,
    "capteur_id": 1,
    "valeur_mesuree": 35.0,
    "medecin_id": 1
  }'
```

**Résultat:** 
- ✅ Donnée créée
- ✅ Analyse créée
- ✅ Alerte créée (anomalie détectée)

---

## Via Python
```python
from app import create_app
from app.services.donnee_medical_service import create_donnee_medicale

app = create_app()
with app.app_context():
    donnee = create_donnee_medicale({
        "patient_id": 6,
        "capteur_id": 1,
        "valeur_mesuree": 35.0,
        "medecin_id": 1
    })
    print(f"Donnée {donnee.id} créée avec analyse!")
```

---

## 🧪 Tester Tout
```bash
python test_pipeline.py
```

---

## 📊 Seuils Rapides

| Capteur | Min | Max | Alerte |
|---------|-----|-----|--------|
| Temperature | 36.0°C | 37.5°C | CRITIQUE |
| Pression | 90 mmHg | 140 mmHg | CRITIQUE |
| Rythme | 60 bpm | 100 bpm | MOYENNE |

---

## ❌ À NE PAS FAIRE

```python
# ❌ MAUVAIS - Pas d'analyse!
donnee = DonneesMedicale(patient_id=6, capteur_id=1, valeur_mesuree=40)
db.session.add(donnee)
db.session.commit()

# ✅ CORRECT - Analyse créée!
donnee = create_donnee_medicale({...})
```

---

## 📚 Documentation Complète

- **PIPELINE_ANALYSIS.md** ← Comprendre le pipeline
- **API_USAGE_GUIDE.md** ← Utiliser l'API
- **PIPELINE_ARCHITECTURE.md** ← Voir les diagrammes
- **test_pipeline.py** ← Valider le système
- **EXECUTIVE_REPORT.md** ← Rapport complet

---

**Status:** ✅ Ready to use
