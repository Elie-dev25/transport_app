"""
Formulaire pour les trajets avec bus prestataire
Phase 2 - Refactorisé pour utiliser BasePrestataireForm (élimine 60+ lignes dupliquées)
"""

from wtforms import SelectField, SubmitField
from .base_forms import BasePrestataireForm
from .constants import FormChoices, FormLabels
from .validators import CommonValidators


class TrajetPrestataireForm(BasePrestataireForm):
    """
    Formulaire pour les trajets avec bus prestataire (modernisé)
    Hérite de BasePrestataireForm - élimine la duplication de code
    """

    # Champs spécifiques aux trajets prestataires avec lieux
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

    # Bouton de soumission spécifique
    submit = SubmitField(FormLabels.BTN_ENREGISTRER_TRAJET)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration spécifique si nécessaire
        pass

    def validate_point_arriver(self, field):
        """Validation héritée: lieu d'arrivée différent du départ"""
        from .validators import FormValidators
        FormValidators.validate_lieu_different(self, field)
