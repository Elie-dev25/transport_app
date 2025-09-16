"""
Constantes globales de l'application
Phase 5 - Centralise toutes les constantes pour éliminer la duplication
"""

from enum import Enum
from typing import Dict, List, Tuple


class UserRoles(Enum):
    """Rôles utilisateur de l'application"""
    ADMIN = "ADMIN"
    RESPONSABLE = "RESPONSABLE"
    SUPERVISEUR = "SUPERVISEUR"
    CHARGE = "CHARGE"
    CHAUFFEUR = "CHAUFFEUR"
    MECANICIEN = "MECANICIEN"


class VehicleStates(Enum):
    """États des véhicules"""
    BON = "BON"
    DEFAILLANT = "DEFAILLANT"
    EN_MAINTENANCE = "EN_MAINTENANCE"
    HORS_SERVICE = "HORS_SERVICE"


class PassengerTypes(Enum):
    """Types de passagers"""
    ETUDIANT = "ETUDIANT"
    PERSONNEL = "PERSONNEL"
    MALADE = "MALADE"
    INVITER = "INVITER"
    MALADE_PERSONNEL = "MALADE_PERSONNEL"


class VehicleTypes(Enum):
    """Types de véhicules"""
    TOURISME = "TOURISME"
    COASTER = "COASTER"
    MINIBUS = "MINIBUS"
    AUTOCAR = "AUTOCAR"
    AUTRE = "AUTRE"


class MaintenanceTypes(Enum):
    """Types de maintenance"""
    PREVENTIVE = "PREVENTIVE"
    CORRECTIVE = "CORRECTIVE"
    URGENTE = "URGENTE"


class TripStatuses(Enum):
    """Statuts des trajets"""
    PLANIFIE = "PLANIFIE"
    EN_COURS = "EN_COURS"
    TERMINE = "TERMINE"
    ANNULE = "ANNULE"


# Constantes de l'application
class AppConstants:
    """Constantes générales de l'application"""
    
    # Informations de l'application
    APP_NAME = "Transport UdM"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Système de gestion des transports - Université des Montagnes"
    
    # Pagination
    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 100
    
    # Limites de données
    MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    MAX_FILENAME_LENGTH = 255
    
    # Formats de date/heure
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    TIME_FORMAT = "%H:%M"
    
    # Délais et timeouts
    SESSION_TIMEOUT = 3600  # 1 heure
    CACHE_TIMEOUT = 300     # 5 minutes
    
    # Seuils d'alerte
    LOW_FUEL_THRESHOLD = 20  # Pourcentage
    MAINTENANCE_KM_THRESHOLD = 5000  # Kilomètres
    PERMIT_EXPIRY_DAYS_WARNING = 30  # Jours


class LocationConstants:
    """Constantes des lieux"""
    
    # Lieux principaux
    CAMPUS_LOCATIONS = [
        ("Banekane", "Banekane (Campus)"),
        ("Mfetum", "Mfetum"),
        ("Ancienne Mairie", "Ancienne Mairie")
    ]
    
    # Points de départ autorisés
    DEPARTURE_POINTS = [
        ("Mfetum", "Mfetum"),
        ("Ancienne mairie", "Ancienne mairie")  # Minuscule pour compatibilité
    ]
    
    # Destinations fréquentes hors campus
    COMMON_DESTINATIONS = [
        "Hôpital Central",
        "Aéroport International",
        "Gare Routière",
        "Centre Ville",
        "Université de Yaoundé I",
        "Ministère de l'Enseignement Supérieur"
    ]


class VehicleConstants:
    """Constantes des véhicules"""
    
    # Capacités par défaut
    DEFAULT_BUS_CAPACITY = 50
    COASTER_CAPACITY = 30
    MINIBUS_CAPACITY = 20
    AUTOCAR_CAPACITY = 70
    
    # Limites kilométrage
    MIN_KILOMETRAGE = 0
    MAX_KILOMETRAGE = 999999
    
    # Consommation moyenne (km/litre)
    AVERAGE_FUEL_CONSUMPTION = 8.5
    
    # Types d'huile
    OIL_TYPES = [
        ("QUARTZ", "Quartz"),
        ("RUBIA", "Rubia"),
        ("MOBIL", "Mobil 1"),
        ("CASTROL", "Castrol GTX")
    ]
    
    # Intervalles de maintenance (km)
    MAINTENANCE_INTERVALS = {
        'VIDANGE': 5000,
        'REVISION': 10000,
        'CONTROLE_TECHNIQUE': 20000
    }


class FormConstants:
    """Constantes des formulaires"""
    
    # Messages de validation
    REQUIRED_FIELD = "Ce champ est requis."
    INVALID_EMAIL = "Adresse email invalide."
    INVALID_PHONE = "Numéro de téléphone invalide."
    PASSWORD_TOO_SHORT = "Le mot de passe doit contenir au moins 8 caractères."
    
    # Placeholders
    PLACEHOLDERS = {
        'kilometrage': 'Ex: 15200',
        'destination': 'Entrez le lieu d\'arrivée (ex: Hôpital Central, Aéroport, etc.)',
        'motif': 'Ex: Transport médical, mission officielle, etc.',
        'telephone': 'Ex: +237 6XX XX XX XX',
        'email': 'exemple@email.com'
    }
    
    # Longueurs maximales
    MAX_LENGTHS = {
        'nom': 100,
        'prenom': 100,
        'login': 50,
        'telephone': 30,
        'email': 120,
        'immatriculation': 20,
        'numero_permis': 50,
        'motif': 255,
        'description': 500
    }


class DatabaseConstants:
    """Constantes de base de données"""
    
    # Noms des tables
    TABLE_NAMES = {
        'users': 'utilisateur',
        'buses': 'bus_udm',
        'trips': 'trajet',
        'drivers': 'chauffeur',
        'maintenance': 'maintenance',
        'fuel': 'carburation'
    }
    
    # Contraintes
    UNIQUE_CONSTRAINTS = [
        'numero_bus',
        'immatriculation',
        'numero_permis',
        'login_utilisateur'
    ]


class SecurityConstants:
    """Constantes de sécurité"""
    
    # Permissions par rôle
    ROLE_PERMISSIONS = {
        UserRoles.ADMIN.value: [
            'create_user', 'edit_user', 'delete_user',
            'create_trip', 'edit_trip', 'delete_trip',
            'view_reports', 'manage_vehicles', 'manage_drivers'
        ],
        UserRoles.CHARGE.value: [
            'create_trip', 'edit_trip', 'view_trips',
            'view_vehicles', 'view_drivers'
        ],
        UserRoles.CHAUFFEUR.value: [
            'view_my_trips', 'update_fuel', 'view_my_schedule'
        ],
        UserRoles.SUPERVISEUR.value: [
            'view_trips', 'view_reports', 'view_vehicles'
        ],
        UserRoles.MECANICIEN.value: [
            'manage_maintenance', 'view_vehicles', 'update_vehicle_status'
        ]
    }
    
    # Mots de passe
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_COMPLEXITY_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$'


class UIConstants:
    """Constantes de l'interface utilisateur"""
    
    # Couleurs par statut
    STATUS_COLORS = {
        'BON': 'success',
        'DEFAILLANT': 'danger',
        'EN_MAINTENANCE': 'warning',
        'ACTIF': 'success',
        'INACTIF': 'secondary',
        'EN_COURS': 'info',
        'TERMINE': 'success',
        'ANNULE': 'danger'
    }
    
    # Icônes par type
    ICONS = {
        'bus': 'fas fa-bus',
        'driver': 'fas fa-user-tie',
        'trip': 'fas fa-route',
        'maintenance': 'fas fa-wrench',
        'fuel': 'fas fa-gas-pump',
        'report': 'fas fa-chart-bar',
        'user': 'fas fa-user',
        'settings': 'fas fa-cog',
        'dashboard': 'fas fa-tachometer-alt'
    }
    
    # Tailles de colonnes Bootstrap
    COLUMN_SIZES = {
        'small': 3,
        'medium': 6,
        'large': 9,
        'full': 12
    }


class NotificationConstants:
    """Constantes des notifications"""
    
    # Types de notifications
    NOTIFICATION_TYPES = {
        'INFO': {'class': 'info', 'icon': 'fas fa-info-circle'},
        'SUCCESS': {'class': 'success', 'icon': 'fas fa-check-circle'},
        'WARNING': {'class': 'warning', 'icon': 'fas fa-exclamation-triangle'},
        'ERROR': {'class': 'danger', 'icon': 'fas fa-times-circle'}
    }
    
    # Messages prédéfinis
    MESSAGES = {
        'TRIP_CREATED': 'Trajet créé avec succès.',
        'TRIP_UPDATED': 'Trajet mis à jour avec succès.',
        'TRIP_DELETED': 'Trajet supprimé avec succès.',
        'VEHICLE_UPDATED': 'Véhicule mis à jour avec succès.',
        'MAINTENANCE_SCHEDULED': 'Maintenance programmée avec succès.',
        'FUEL_UPDATED': 'Niveau de carburant mis à jour.',
        'LOGIN_SUCCESS': 'Connexion réussie.',
        'LOGOUT_SUCCESS': 'Déconnexion réussie.',
        'ACCESS_DENIED': 'Accès refusé. Permissions insuffisantes.',
        'DATA_ERROR': 'Erreur lors du traitement des données.'
    }


# Fonctions utilitaires pour les constantes
def get_choices_from_enum(enum_class) -> List[Tuple[str, str]]:
    """Convertit un Enum en liste de choix pour les formulaires"""
    return [(item.value, item.value.replace('_', ' ').title()) for item in enum_class]


def get_role_display_name(role: str) -> str:
    """Retourne le nom d'affichage d'un rôle"""
    role_names = {
        'ADMIN': 'Administrateur',
        'RESPONSABLE': 'Responsable',
        'SUPERVISEUR': 'Superviseur',
        'CHARGE': 'Chargé de Transport',
        'CHAUFFEUR': 'Chauffeur',
        'MECANICIEN': 'Mécanicien'
    }
    return role_names.get(role, role)


def get_status_config(status: str) -> Dict[str, str]:
    """Retourne la configuration d'affichage d'un statut"""
    return {
        'class': UIConstants.STATUS_COLORS.get(status, 'secondary'),
        'text': status.replace('_', ' ').title()
    }


def has_permission(user_role: str, permission: str) -> bool:
    """Vérifie si un rôle a une permission donnée"""
    role_perms = SecurityConstants.ROLE_PERMISSIONS.get(user_role, [])
    return permission in role_perms
