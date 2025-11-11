# -------------------------------------------------------------
# app/utils/serializers.py
# -------------------------------------------------------------
# Ce module regroupe toutes les fonctions de sérialisation
# des modèles SQLAlchemy vers des objets JSON exploitables.
# Chaque fonction prend un objet de modèle et renvoie un dict.
# -------------------------------------------------------------

# Import optionnel pour typer correctement les modèles si besoin
from datetime import datetime


# -------------------------------------------------------------
# Sérialiseur de la classe de base Personne
# -------------------------------------------------------------
def serialize_personne(p):
    """Sérialise les champs communs du modèle Personne."""
    if not p:
        return None

    return {
        "id": p.id,
        "prenom": p.prenom,
        "nom": p.nom,
        "email": p.email,
        "phone": getattr(p, "phone", None),
        "adresse": getattr(p, "adresse", None),
        "date_naissance": safe_date(getattr(p, "date_naissance", None)),
        "role": getattr(p, "role", None),
    }


# -------------------------------------------------------------
# Sérialiseur du modèle Medecin
# -------------------------------------------------------------
def serialize_medecin(m):
    """Sérialise un médecin avec ses attributs et relations."""
    if not m:
        return None

    return {
        **serialize_personne(m),
        "specialite": getattr(m, "specialite", None),
        "analyses": [serialize_analyse(a) for a in getattr(m, "analyses", [])]
        if hasattr(m, "analyses")
        else [],
        "alertes": [serialize_alerte(a) for a in getattr(m, "alertes", [])]
        if hasattr(m, "alertes")
        else [],
    }


# -------------------------------------------------------------
# Sérialiseur du modèle Patient
# -------------------------------------------------------------
def serialize_patient(p):
    """Sérialise un patient avec ses donnees, proches, alertes et analyses."""
    if not p:
        return None

    return {
        **serialize_personne(p),
        "donnees_phys": [serialize_donnee_medicale(d) for d in getattr(p, "donnees_phys", [])],
        "derniere_mesure": (
        serialize_donnee_medicale(
            sorted(p.donnees_phys, key=lambda d: d.date_heure_mesure, reverse=True)[0]
        )
        if getattr(p, "donnees_phys", [])
            else None
        ),
        "proches": [serialize_proche(pr) for pr in getattr(p, "proches", [])],
        "alertes": [serialize_alerte(a) for a in getattr(p, "alertes", [])],
        "analyses": [serialize_analyse(a) for a in getattr(p, "analyses", [])]
        if hasattr(p, "analyses")
        else [],
    }

# -------------------------------------------------------------
# Sérialiseur du modèle Proche
# -------------------------------------------------------------
def serialize_proche(pr):
    """Sérialise un proche lié à un patient."""
    if not pr:
        return None

    return {
        "id": pr.id,
        "lien_parente": getattr(pr, "lien_parente", None),
        "patient_id": getattr(pr, "patient_id", None),
    }


# -------------------------------------------------------------
# Sérialiseur du modèle Alerte
# -------------------------------------------------------------
def serialize_alerte(a):
    """Sérialise une alerte médicale."""
    if not a:
        return None

    return {
        "id": a.id,
        "niveau_urgence": safe_enum(a.niveau_urgence),
        "type_alerte": safe_enum(a.type_alerte),
        "description": a.description,
        "etat_traitement": a.etat_traitement,
        "date_heure_alerte": safe_date(a.date_heure_alerte),
        "patient_id": a.patient_id,
        "medecin_id": a.medecin_id,
    }


# -------------------------------------------------------------
# Sérialiseur du modèle Capteur
# -------------------------------------------------------------
def serialize_capteur(c):
    """Sérialise un capteur biomédical."""
    if not c:
        return None

    return {
        "id": c.id,
        "type": safe_enum(c.type)
    }

# -------------------------------------------------------------
# Sérialiseur du modèle DonneesMedicale
# -------------------------------------------------------------
def serialize_donnee_medicale(m, with_patient=False):
    """Sérialise une donnée médicale captée par un capteur."""
    if not m:
        return None

    return {
        "id": m.id,
        "patient_id": m.patient_id,
        "capteur_id": m.capteur_id,
        "valeur_mesuree": m.valeur_mesuree,
        "date_heure_mesure": safe_date(m.date_heure_mesure),
        "capteur": serialize_capteur(m.capteur) if getattr(m, "capteur", None) else None,
        # on évite la récursion infinie ici :
        "patient": {
            "id": m.patient.id,
            "nom": m.patient.nom,
            "prenom": m.patient.prenom,
        } if with_patient and getattr(m, "patient", None) else None,
    }


# -------------------------------------------------------------
# Sérialiseur du modèle Analyseur
# -------------------------------------------------------------
def serialize_analyse(a):
    """Sérialise une analyse médicale effectuée par un médecin."""
    if not a:
        return None

    return {
        "id": a.id,
        "resultat": a.resultat,
        "date_analyse": safe_date(a.date_analyse),
        "medecin_id": getattr(a, "medecin_id", None),
        "patient_id": getattr(a, "patient_id", None),
        "donnee_medicale_id": getattr(a, "donnee_medicale_id", None),
        "patient": {
            "id": a.patient.id,
            "nom": a.patient.nom,
            "prenom": a.patient.prenom,
        } if getattr(a, "patient", None) else None,
        "medecin": {
            "id": a.medecin.id,
            "nom": a.medecin.nom,
            "prenom": a.medecin.prenom,
            "specialite": a.medecin.specialite,
        } if getattr(a, "medecin", None) else None,
        "donnee_medicale": {
            "id": getattr(a.donnee_medicale, "id", None),
            "valeur_mesuree": a.donnee_medicale.valeur_mesuree,
            "capteur": {
                "id": a.donnee_medicale.capteur.id,
                "type": safe_enum(a.donnee_medicale.capteur.type)
            }
        } if getattr(a, "donnee_medicale", None) else None,
    }


# -------------------------------------------------------------
# Sérialiseur pour les statistiques médicales
# -------------------------------------------------------------
def serialize_statistique(stat):
    """
    Sérialise un tuple de statistique : (capteur_id, min, max, avg)
    """
    from app.models import Capteur  # import local pour éviter les boucles
    capteur = Capteur.query.get(stat[0]) if stat else None

    return {
        "type": capteur.type.value if capteur else None,
        "min": stat[1],
        "max": stat[2],
        "avg": round(stat[3], 2) if stat[3] is not None else None,
    }

# -------------------------------------------------------------
# Sérialiseur sécurisé pour les énumérations
# -------------------------------------------------------------
def safe_enum(enum_obj):
    return enum_obj.value if enum_obj else None

# -------------------------------------------------------------
# Sérialiseur sécurisé pour les dates
# -------------------------------------------------------------
def safe_date(dt):
    return dt.isoformat() if dt else None
