from app.models.enums import TypeCapteur, TypeAlerte, UrgenceEnum

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
        "type_alerte": TypeAlerte.avertissement    }
}