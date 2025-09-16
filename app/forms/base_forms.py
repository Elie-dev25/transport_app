"""
Formulaires de base pour éliminer la duplication
Phase 2 - Classe BaseTrajetForm avec champs communs
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, SelectField, DateTimeLocalField,
    TextAreaField, HiddenField, SubmitField
)
from wtforms.validators import DataRequired, NumberRange, Optional

from .constants import FormChoices, FormDefaults, FormLabels
from .validators import CommonValidators, FormValidators


class BaseTrajetForm(FlaskForm):
    """
    Classe de base pour tous les formulaires de trajets
    Contient les champs communs pour éliminer la duplication
    """
    
    # Champs communs à tous les trajets
    date_heure_depart = DateTimeLocalField(
        FormLabels.DATE_HEURE_DEPART,
        validators=CommonValidators.DATE_FUTURE,
        format='%Y-%m-%dT%H:%M'
    )
    
    type_passagers = SelectField(
        FormLabels.TYPE_PASSAGERS,
        choices=FormChoices.TYPE_PASSAGERS,
        validators=CommonValidators.TYPE_PASSAGERS_VALIDE
    )
    
    nombre_places_occupees = IntegerField(
        FormLabels.NOMBRE_PLACES_OCCUPEES,
        validators=CommonValidators.NOMBRE_PLACES,
        default=0
    )
    
    chauffeur_id = SelectField(
        FormLabels.CHAUFFEUR,
        choices=[],  # Sera peuplé dynamiquement par FormService
        validators=[CommonValidators.REQUIRED],
        coerce=int
    )
    
    # Champs optionnels communs
    kilometrage_actuel = IntegerField(
        FormLabels.KILOMETRAGE_ACTUEL,
        validators=CommonValidators.KILOMETRAGE,
        render_kw={'placeholder': FormDefaults.PLACEHOLDER_KILOMETRAGE}
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_common_choices()
    
    def _setup_common_choices(self):
        """Configure les choix communs (peut être surchargé)"""
        # Les choix dynamiques (chauffeurs, bus) seront peuplés par FormService
        pass
    
    def validate_common_fields(self):
        """Validation commune à tous les formulaires de trajets"""
        errors = []
        
        # Validation du nombre de places
        if self.nombre_places_occupees.data and self.nombre_places_occupees.data < 0:
            errors.append('Le nombre de places ne peut pas être négatif.')
        
        return errors


class BaseTrajetInterneForm(BaseTrajetForm):
    """
    Classe de base pour les trajets internes (Bus UdM)
    Hérite de BaseTrajetForm et ajoute les champs spécifiques aux bus UdM
    """
    
    lieu_depart = SelectField(
        FormLabels.LIEU_DEPART,
        choices=FormChoices.LIEUX,
        validators=CommonValidators.LIEU_VALIDE
    )
    
    point_arriver = SelectField(
        FormLabels.LIEU_ARRIVEE,
        choices=FormChoices.LIEUX,
        validators=CommonValidators.LIEU_ARRIVEE
    )

    numero_bus_udm = SelectField(
        FormLabels.NUMERO_BUS_UDM,
        choices=[],  # Sera peuplé par FormService
        validators=[CommonValidators.REQUIRED]
    )

    def validate_point_arriver(self, field):
        """Validation spécifique: lieu d'arrivée différent du départ"""
        FormValidators.validate_lieu_different(self, field)


class BasePrestataireForm(BaseTrajetForm):
    """
    Classe de base pour les trajets prestataires
    Hérite de BaseTrajetForm et ajoute les champs spécifiques aux prestataires
    """
    
    nom_prestataire = SelectField(
        FormLabels.NOM_PRESTATAIRE,
        choices=[],  # Sera peuplé par FormService
        validators=[CommonValidators.REQUIRED]
    )
    
    immat_bus = StringField(
        FormLabels.IMMAT_BUS,
        validators=CommonValidators.IMMATRICULATION
    )
    
    nombre_places_bus = IntegerField(
        FormLabels.NOMBRE_PLACES_BUS,
        validators=CommonValidators.NOMBRE_PLACES,
        default=FormDefaults.NOMBRE_PLACES_BUS_PRESTATAIRE
    )
    
    nom_chauffeur_prestataire = StringField(
        FormLabels.NOM_CHAUFFEUR_PRESTATAIRE,
        validators=CommonValidators.NOM_CHAUFFEUR
    )


class BaseAutreTrajetForm(BaseTrajetForm):
    """
    Classe de base pour les autres trajets (hors ville, spéciaux)
    Hérite de BaseTrajetForm et ajoute les champs pour trajets spéciaux
    """
    
    point_arriver = StringField(
        FormLabels.DESTINATION,
        validators=[
            CommonValidators.REQUIRED,
            FormValidators.validate_champ_non_vide
        ],
        render_kw={'placeholder': FormDefaults.PLACEHOLDER_LIEU_ARRIVEE}
    )
    
    motif_trajet = TextAreaField(
        FormLabels.MOTIF_TRAJET,
        validators=[
            CommonValidators.REQUIRED,
            FormValidators.validate_champ_non_vide
        ],
        render_kw={'placeholder': FormDefaults.PLACEHOLDER_MOTIF, 'rows': 3}
    )
    
    numero_bus_udm = SelectField(
        FormLabels.NUMERO_BUS_UDM,
        choices=[],  # Sera peuplé par FormService
        validators=[CommonValidators.REQUIRED]
    )


# Formulaires spécialisés (legacy compatibility)
class BaseLegacyForm(BaseTrajetForm):
    """
    Classe de base pour les anciens formulaires (compatibilité)
    Hérite de BaseTrajetForm et ajoute les champs legacy
    """

    # Champs legacy avec anciens noms
    point_depart = SelectField(
        'Point de départ',
        choices=FormChoices.POINTS_DEPART,
        validators=[CommonValidators.REQUIRED]
    )

    point_arriver = SelectField(  # Note: "arriver" sans 'e' pour compatibilité
        'Point d\'arrivée',
        choices=FormChoices.LIEUX,
        validators=CommonValidators.POINT_ARRIVEE
    )

    numero_bus_udm = SelectField(  # Corrigé pour correspondre à la DB
        'Numéro Bus UdM',
        choices=[],
        validators=[CommonValidators.REQUIRED]
    )

    def validate_point_arriver(self, field):
        """Validation legacy: point d'arrivée différent du départ"""
        FormValidators.validate_point_different(self, field)


# Mixins pour fonctionnalités spécifiques
class SubmitButtonMixin:
    """Mixin pour ajouter des boutons de soumission standardisés"""
    
    def add_submit_button(self, label: str = FormLabels.BTN_ENREGISTRER_TRAJET):
        """Ajoute un bouton de soumission avec le label spécifié"""
        if not hasattr(self, 'submit'):
            self.submit = SubmitField(label)


class HiddenFieldsMixin:
    """Mixin pour les champs cachés communs"""
    
    # Champs cachés pour CSRF et autres données
    csrf_token = HiddenField()
    
    def add_hidden_field(self, name: str, value: str = ''):
        """Ajoute un champ caché dynamiquement"""
        setattr(self, name, HiddenField(default=value))


# Fonctions utilitaires pour créer des formulaires dynamiques
def create_trajet_form(form_type: str = 'interne', **kwargs):
    """
    Factory pour créer des formulaires de trajets selon le type
    
    Args:
        form_type: 'interne', 'prestataire', 'autre', ou 'legacy'
        **kwargs: Arguments supplémentaires pour le formulaire
    """
    form_classes = {
        'interne': BaseTrajetInterneForm,
        'prestataire': BasePrestataireForm,
        'autre': BaseAutreTrajetForm,
        'legacy': BaseLegacyForm
    }
    
    form_class = form_classes.get(form_type, BaseTrajetForm)
    return form_class(**kwargs)


def extend_form_with_fields(base_form_class, additional_fields: dict):
    """
    Étend une classe de formulaire avec des champs supplémentaires
    
    Args:
        base_form_class: Classe de base à étendre
        additional_fields: Dictionnaire {nom_champ: objet_champ}
    """
    class ExtendedForm(base_form_class):
        pass
    
    for field_name, field_obj in additional_fields.items():
        setattr(ExtendedForm, field_name, field_obj)
    
    return ExtendedForm
