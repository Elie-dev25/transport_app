"""
Validateurs centralisés pour les formulaires
Phase 2 - Élimine la duplication des validations dans 5+ formulaires
"""

from wtforms.validators import ValidationError, DataRequired, NumberRange
from wtforms import Field
from datetime import datetime, date, timedelta
from typing import Optional, Any

from .constants import FormMessages, validate_lieu_choice, validate_type_passagers_choice


class FormValidators:
    """Classe contenant tous les validateurs personnalisés"""
    
    @staticmethod
    def validate_lieu_different(form: Any, field: Field) -> None:
        """
        Valide que le lieu d'arrivée est différent du lieu de départ
        Utilisé dans 4+ formulaires
        """
        if hasattr(form, 'lieu_depart') and form.lieu_depart.data:
            if field.data == form.lieu_depart.data:
                raise ValidationError(FormMessages.LIEU_ARRIVEE_DIFFERENT)
    
    @staticmethod
    def validate_point_different(form: Any, field: Field) -> None:
        """
        Valide que le point d'arrivée est différent du point de départ
        Version alternative pour compatibilité legacy
        """
        if hasattr(form, 'point_depart') and form.point_depart.data:
            if field.data == form.point_depart.data:
                raise ValidationError(FormMessages.LIEU_ARRIVEE_DIFFERENT)
    
    @staticmethod
    def validate_date_future_or_today(form: Any, field: Field) -> None:
        """
        Valide que la date n'est pas dans le passé (sauf aujourd'hui)
        """
        if field.data:
            if isinstance(field.data, datetime):
                field_date = field.data.date()
            elif isinstance(field.data, date):
                field_date = field.data
            else:
                return  # Laisser d'autres validateurs gérer le format

            if field_date < date.today():
                raise ValidationError('La date ne peut pas être dans le passé.')

    @staticmethod
    def validate_date_trajet_effectue(form: Any, field: Field) -> None:
        """
        Valide que la date est dans les 48h passées (trajets déjà effectués)
        Empêche les dates futures et les dates trop anciennes
        """
        if field.data:
            if isinstance(field.data, datetime):
                field_datetime = field.data
            else:
                return  # Laisser d'autres validateurs gérer le format

            now = datetime.now()

            # Empêcher les dates futures
            if field_datetime > now:
                raise ValidationError('Impossible d\'enregistrer un trajet futur. Seuls les trajets effectués peuvent être enregistrés.')

            # Empêcher les dates trop anciennes (plus de 48h)
            limite_48h = now - timedelta(hours=48)
            if field_datetime < limite_48h:
                raise ValidationError('Impossible d\'enregistrer un trajet de plus de 48h. Contactez l\'administrateur pour les trajets plus anciens.')
    
    @staticmethod
    def validate_nombre_places_positif(form: Any, field: Field) -> None:
        """
        Valide que le nombre de places est positif et réaliste
        """
        if field.data is not None:
            if field.data < 0:
                raise ValidationError('Le nombre de places ne peut pas être négatif.')
            if field.data > 70:  # Maximum réaliste pour un bus
                raise ValidationError('Le nombre de places semble trop élevé (max: 70).')
    
    @staticmethod
    def validate_kilometrage_realiste(form: Any, field: Field) -> None:
        """
        Valide que le kilométrage est réaliste
        """
        if field.data is not None:
            if field.data < 0:
                raise ValidationError('Le kilométrage ne peut pas être négatif.')
            if field.data > 999999:
                raise ValidationError('Le kilométrage semble trop élevé.')
    
    @staticmethod
    def validate_lieu_autorise(form: Any, field: Field) -> None:
        """
        Valide que le lieu fait partie des lieux autorisés
        """
        if field.data and not validate_lieu_choice(field.data):
            raise ValidationError('Lieu non autorisé. Veuillez choisir dans la liste.')
    
    @staticmethod
    def validate_type_passagers_autorise(form: Any, field: Field) -> None:
        """
        Valide que le type de passagers est autorisé
        """
        if field.data and not validate_type_passagers_choice(field.data):
            raise ValidationError('Type de passagers non autorisé.')
    
    @staticmethod
    def validate_champ_non_vide(form: Any, field: Field) -> None:
        """
        Valide qu'un champ texte n'est pas vide ou ne contient que des espaces
        """
        if field.data and isinstance(field.data, str):
            if not field.data.strip():
                raise ValidationError('Ce champ ne peut pas être vide.')
    
    @staticmethod
    def validate_immatriculation_format(form: Any, field: Field) -> None:
        """
        Valide le format d'une immatriculation (basique)
        """
        if field.data:
            # Format basique: au moins 4 caractères alphanumériques
            if len(field.data.strip()) < 4:
                raise ValidationError('L\'immatriculation doit contenir au moins 4 caractères.')
    
    @staticmethod
    def validate_nom_chauffeur_format(form: Any, field: Field) -> None:
        """
        Valide le format d'un nom de chauffeur
        """
        if field.data:
            nom = field.data.strip()
            if len(nom) < 2:
                raise ValidationError('Le nom du chauffeur doit contenir au moins 2 caractères.')
            if not nom.replace(' ', '').replace('-', '').isalpha():
                raise ValidationError('Le nom du chauffeur ne doit contenir que des lettres, espaces et tirets.')


# Validateurs prêts à l'emploi (combinaisons courantes)
class CommonValidators:
    """Validateurs combinés couramment utilisés"""
    
    # Champ requis avec message personnalisé
    REQUIRED = DataRequired(message=FormMessages.CHAMP_REQUIS)
    
    # Nombre de places (0-70)
    NOMBRE_PLACES = [
        NumberRange(min=0, max=70, message='Le nombre de places doit être entre 0 et 70.'),
        FormValidators.validate_nombre_places_positif
    ]
    
    # Kilométrage (0-999999)
    KILOMETRAGE = [
        NumberRange(min=0, max=999999, message='Le kilométrage doit être entre 0 et 999999.'),
        FormValidators.validate_kilometrage_realiste
    ]
    
    # Lieu avec validation
    LIEU_VALIDE = [
        REQUIRED,
        FormValidators.validate_lieu_autorise
    ]
    
    # Lieu d'arrivée différent du départ
    LIEU_ARRIVEE = [
        REQUIRED,
        FormValidators.validate_lieu_different
    ]
    
    # Point d'arrivée différent du départ (legacy)
    POINT_ARRIVEE = [
        REQUIRED,
        FormValidators.validate_point_different
    ]
    
    # Type de passagers valide
    TYPE_PASSAGERS_VALIDE = [
        REQUIRED,
        FormValidators.validate_type_passagers_autorise
    ]
    
    # Nom de chauffeur
    NOM_CHAUFFEUR = [
        REQUIRED,
        FormValidators.validate_champ_non_vide,
        FormValidators.validate_nom_chauffeur_format
    ]
    
    # Immatriculation
    IMMATRICULATION = [
        REQUIRED,
        FormValidators.validate_champ_non_vide,
        FormValidators.validate_immatriculation_format
    ]
    
    # Date future ou aujourd'hui
    DATE_FUTURE = [
        REQUIRED,
        FormValidators.validate_date_future_or_today
    ]

    # Date pour trajets effectués (48h max dans le passé)
    DATE_TRAJET_EFFECTUE = [
        REQUIRED,
        FormValidators.validate_date_trajet_effectue
    ]


# Fonctions utilitaires pour créer des validateurs dynamiques
def create_lieu_different_validator(depart_field_name: str = 'lieu_depart'):
    """
    Crée un validateur personnalisé pour vérifier que deux lieux sont différents
    
    Args:
        depart_field_name: Nom du champ de départ à comparer
    """
    def validator(form, field):
        depart_field = getattr(form, depart_field_name, None)
        if depart_field and depart_field.data:
            if field.data == depart_field.data:
                raise ValidationError(FormMessages.LIEU_ARRIVEE_DIFFERENT)
    
    return validator


def create_range_validator(min_val: int, max_val: int, field_name: str = 'valeur'):
    """
    Crée un validateur de plage personnalisé avec message adapté
    
    Args:
        min_val: Valeur minimum
        max_val: Valeur maximum  
        field_name: Nom du champ pour le message d'erreur
    """
    message = f'Le {field_name} doit être entre {min_val} et {max_val}.'
    return NumberRange(min=min_val, max=max_val, message=message)


# Validateurs conditionnels
def validate_if_field_present(field_name: str, validators: list):
    """
    Applique des validateurs seulement si un autre champ est présent
    
    Args:
        field_name: Nom du champ à vérifier
        validators: Liste des validateurs à appliquer
    """
    def conditional_validator(form, field):
        other_field = getattr(form, field_name, None)
        if other_field and other_field.data:
            for validator in validators:
                if callable(validator):
                    validator(form, field)
                else:
                    validator(field)
    
    return conditional_validator
