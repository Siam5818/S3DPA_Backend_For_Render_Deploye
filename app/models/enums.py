import enum

class TypeCapteur(enum.Enum):
    temperature = "Temperature Corporelle"
    pression = "Pression Arterielle"
    rythme = "Rythme Cardiaque"
    
class TypeAlerte(enum.Enum):
    urgence = "Urgence"
    avertissement = "Avertissement"
    information = "Information"
    
class UrgenceEnum(enum.Enum):
    faible = "Faible"
    moyenne = "Moyenne"
    critique = "Critique"
