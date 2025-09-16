"""
Constantes centralisées pour les formulaires
Phase 2 - Élimine la duplication des choix dans 5+ formulaires
"""

from typing import List, Tuple


class FormChoices:
    """Centralise tous les choix constants des formulaires"""
    
    # Types de passagers (dupliqué dans 5+ formulaires)
    TYPE_PASSAGERS: List[Tuple[str, str]] = [
        ('ETUDIANT', 'Étudiant'),
        ('PERSONNEL', 'Personnel'),
        ('MALADE', 'Malade'),
        ('INVITER', 'Invité'),
        ('MALADE_PERSONNEL', 'Malade Personnel')
    ]
    
    # Types de passagers basiques (pour certains formulaires)
    TYPE_PASSAGERS_BASIC: List[Tuple[str, str]] = [
        ('ETUDIANT', 'Étudiant'),
        ('PERSONNEL', 'Personnel'),
        ('MALADE', 'Malade')
    ]
    
    # Lieux de départ/arrivée (dupliqué dans 4+ formulaires)
    LIEUX: List[Tuple[str, str]] = [
        ('Mfetum', 'Mfetum'),
        ('Ancienne Mairie', 'Ancienne Mairie'),
        ('Banekane', 'Banekane')
    ]
    
    # Points de départ spécifiques (pour compatibilité legacy)
    POINTS_DEPART: List[Tuple[str, str]] = [
        ('Mfetum', 'Mfetum'),
        ('Ancienne mairie', 'Ancienne mairie')  # Note: minuscule pour compatibilité
    ]
    
    # Types de bus (pour formulaires avec choix)
    TYPE_BUS: List[Tuple[str, str]] = [
        ('AED', 'Bus AED'),
        ('PRESTATAIRE', 'Prestataire')
    ]
    
    # Types d'huile (pour maintenance)
    TYPE_HUILE: List[Tuple[str, str]] = [
        ('QUARTZ', 'Quartz'),
        ('RUBIA', 'Rubia')
    ]
    
    # Prestataires fixes (pour compatibilité legacy)
    PRESTATAIRES_LEGACY: List[Tuple[str, str]] = [
        ('Charter', 'Charter'),
        ('Noblesse', 'Noblesse')
    ]


class FormDefaults:
    """Valeurs par défaut pour les formulaires"""
    
    # Nombre de places par défaut
    NOMBRE_PLACES_BUS_PRESTATAIRE = 70
    NOMBRE_PLACES_MIN = 0
    NOMBRE_PLACES_MAX = 70
    
    # Kilométrage
    KILOMETRAGE_MIN = 0
    KILOMETRAGE_MAX = 999999
    
    # Format date/heure
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M'
    
    # Placeholders
    PLACEHOLDER_KILOMETRAGE = 'Ex: 15200'
    PLACEHOLDER_LIEU_ARRIVEE = 'Entrez le lieu d\'arrivée (ex: Hôpital Central, Aéroport, etc.)'
    PLACEHOLDER_MOTIF = 'Ex: Transport médical, mission officielle, etc.'


class FormLabels:
    """Labels standardisés pour les formulaires"""
    
    # Labels communs
    DATE_HEURE_DEPART = 'Date et heure de départ'
    LIEU_DEPART = 'Lieu de départ'
    LIEU_ARRIVEE = 'Lieu d\'arrivée'
    TYPE_PASSAGERS = 'Type de passagers'
    NOMBRE_PLACES_OCCUPEES = 'Nombre de places occupées'
    CHAUFFEUR = 'Chauffeur'
    NUMERO_BUS_UDM = 'Numéro Bus UdM'
    KILOMETRAGE_ACTUEL = 'Kilométrage actuel du véhicule (km)'
    
    # Labels spécifiques
    NOM_PRESTATAIRE = 'Nom Prestataire'
    IMMAT_BUS = 'Immatriculation Bus'
    NOMBRE_PLACES_BUS = 'Nombre de places bus'
    NOM_CHAUFFEUR_PRESTATAIRE = 'Nom du chauffeur'
    MOTIF_TRAJET = 'Motif du trajet'
    DESTINATION = 'Destination (hors ville)'
    
    # Boutons
    BTN_ENREGISTRER_TRAJET = 'Enregistrer le trajet'
    BTN_ENREGISTRER_DEPART = 'Enregistrer le départ'
    BTN_ENREGISTRER_RETOUR = 'Enregistrer le retour'
    BTN_ENREGISTRER_SORTIE = 'Enregistrer la sortie'


class FormMessages:
    """Messages d'erreur et de validation standardisés"""
    
    # Messages de validation
    LIEU_ARRIVEE_DIFFERENT = 'Le lieu d\'arrivée doit être différent du lieu de départ.'
    CHAMP_REQUIS = 'Ce champ est requis.'
    NOMBRE_INVALIDE = 'Veuillez entrer un nombre valide.'
    DATE_INVALIDE = 'Veuillez entrer une date valide.'
    
    # Messages d'erreur
    ERREUR_SAUVEGARDE = 'Erreur lors de la sauvegarde du trajet.'
    ERREUR_VALIDATION = 'Veuillez corriger les erreurs dans le formulaire.'
    ERREUR_BDD = 'Erreur de connexion à la base de données.'
    
    # Messages de succès
    TRAJET_ENREGISTRE = 'Trajet enregistré avec succès.'
    DEPART_ENREGISTRE = 'Départ enregistré avec succès.'


# Fonctions utilitaires pour les choix dynamiques
def get_type_passagers_choices(include_all: bool = True) -> List[Tuple[str, str]]:
    """
    Retourne les choix de types de passagers
    
    Args:
        include_all: Si True, inclut tous les types. Si False, seulement les basiques.
    """
    return FormChoices.TYPE_PASSAGERS if include_all else FormChoices.TYPE_PASSAGERS_BASIC


def get_lieux_choices() -> List[Tuple[str, str]]:
    """Retourne les choix de lieux standardisés"""
    return FormChoices.LIEUX.copy()


def get_points_depart_choices() -> List[Tuple[str, str]]:
    """Retourne les points de départ (pour compatibilité legacy)"""
    return FormChoices.POINTS_DEPART.copy()


# Validation des choix
def validate_lieu_choice(lieu: str) -> bool:
    """Valide qu'un lieu fait partie des choix autorisés"""
    valid_lieux = [choice[0] for choice in FormChoices.LIEUX]
    return lieu in valid_lieux


def validate_type_passagers_choice(type_passagers: str) -> bool:
    """Valide qu'un type de passagers fait partie des choix autorisés"""
    valid_types = [choice[0] for choice in FormChoices.TYPE_PASSAGERS]
    return type_passagers in valid_types
