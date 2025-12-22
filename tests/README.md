# 🧪 Tests du Pipeline S3DPA

## Vue d'ensemble

Le dossier `tests/` contient tous les tests unitaires et d'intégration du projet S3DPA, y compris les tests du pipeline de données médicales.

## Structure des tests

```
tests/
├── conftest.py                          # Configuration pytest (fixtures)
├── test_app_startup.py                 # Test du démarrage de l'application
├── test_auth_*.py                      # Tests d'authentification
├── test_donnee_medicale_*.py           # Tests CRUD des données médicales
└── test_pipeline.py                    # ⭐ Tests du pipeline complet
```

## Fichier: test_pipeline.py

Ce fichier contient **4 tests indépendants** du pipeline complet :

### 1. `test_pipeline_donnees_normales(app)`
Valide qu'une donnée **normale** crée une **analyse seulement** (pas d'alerte)

```python
Donnée: Température 36.8°C (dans les seuils)
Résultat:
  ✅ DonneesMedicale créée
  ✅ Analyseur créé avec "normal"
  ❌ Pas d'Alerte
```

### 2. `test_pipeline_donnees_anomales_temperature(app)`
Valide qu'une donnée **anomale** (température basse) crée **analyse + alerte CRITIQUE**

```python
Donnée: Température 35.0°C (< 36.0)
Résultat:
  ✅ DonneesMedicale créée
  ✅ Analyseur créé avec "Anomalie"
  ✅ Alerte créée (niveau: CRITIQUE)
```

### 3. `test_pipeline_donnees_anomales_rythme(app)`
Valide qu'une donnée **anomale** (rythme bas) crée **analyse + alerte MOYENNE**

```python
Donnée: Rythme 55 bpm (< 60)
Résultat:
  ✅ DonneesMedicale créée
  ✅ Analyseur créé avec "Anomalie"
  ✅ Alerte créée (niveau: MOYENNE)
```

### 4. `test_pipeline_complete(app)`
Test **complet** : 3 mesures (1 normale + 2 anomalies) = validation des comptages

```python
Données insérées: 3
Analyses créées: 3 (100%)
Alertes créées: 2 (pour les 2 anomalies)
```

---

## Comment Exécuter les Tests

### Via Pytest (Recommended - CI/CD)

```bash
# Tous les tests
pytest tests/

# Test du pipeline seulement
pytest tests/test_pipeline.py -v

# Un test spécifique
pytest tests/test_pipeline.py::test_pipeline_donnees_normales -v

# Avec output détaillé
pytest tests/test_pipeline.py -vv -s
```

### Via Python Direct (Développement Local)

```bash
# Depuis la racine du projet
python seed.py      # Crée les données + analyses + alertes
```

---

## Résultats Attendus

### ✅ SUCCÈS (Tous les tests passent)

```
tests/test_app_startup.py .                           [  9%]
tests/test_auth_login.py .                            [ 18%]
tests/test_auth_login_success.py .                    [ 27%]
tests/test_auth_me_protected.py .                     [ 36%]
tests/test_donnee_medicale_create.py ..               [ 54%]
tests/test_donnee_medicale_get.py ..                  [ 72%]
tests/test_donnee_medicale_patient.py ..              [ 90%]
tests/test_pipeline.py ....                           [100%]

======================== 11 passed in 1.23s ========================
```

### ❌ ÉCHEC (Le pipeline n'a pas créé les données)

```
FAILED tests/test_pipeline.py::test_pipeline_donnees_normales
  AssertionError: 3 données doivent être créées
```

**Solution:** Vérifier que `create_donnee_medicale()` est bien appelé dans le service

---

## Dépendances

Les tests utilisent les fixtures de `conftest.py` :

- **`app` fixture**: Crée une app Flask avec une BD SQLite en mémoire
- **`client` fixture**: Client test pour les requêtes HTTP
- **`runner` fixture**: CLI runner pour les commandes

### Exemple d'utilisation de la fixture:

```python
def test_pipeline_donnees_normales(app):
    with app.app_context():
        # Les tables sont automatiquement créées par la fixture
        donnee = create_donnee_medicale({...})
        assert donnee.id is not None
```

---

## Configuration Pytest

Le fichier `conftest.py` configure :

1. **BD de test**: SQLite en mémoire (rapide, isolé)
2. **Mode TEST**: `app.config['TESTING'] = True`
3. **Cleanup**: Supprime les tables après chaque test

---

## Checklist - Avant de Commiter

- [ ] Tous les tests passent: `pytest tests/`
- [ ] Le seed fonctionne: `python seed.py`
- [ ] Aucune erreur de type d'énumération
- [ ] Les analyses sont créées pour chaque donnée
- [ ] Les alertes sont créées pour les anomalies

---

## Dépannage

### Erreur: "relation donnees_medicales does not exist"
**Cause**: Les fixtures pytest ne crée pas les tables
**Solution**: Vérifier que vous utilisez la fixture `app` en paramètre

### Erreur: "No module named pytest"
**Cause**: pytest n'est pas installé localement
**Solution**: C'est normal pour le développement local. Les tests s'exécutent en CI/CD

### Données de test ne créent pas d'alerte
**Cause**: La valeur mesurée n'est pas hors des seuils
**Solution**: Vérifier les seuils dans `app/utils/seuils.py`

---

## Seuils Médicaux de Référence

| Capteur | Min | Max | Alerte Anomalie |
|---------|-----|-----|-----------------|
| Temperature | 36.0°C | 37.5°C | CRITIQUE |
| Pression | 90 mmHg | 140 mmHg | CRITIQUE |
| Rythme | 60 bpm | 100 bpm | MOYENNE |

---

**Dernière mise à jour**: 22 Décembre 2025  
**Version**: 1.0  
**Status**: ✅ Prêt pour CI/CD
