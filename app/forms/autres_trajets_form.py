"""
Formulaire pour les autres trajets (remplace sortie hors ville)
Phase 2 - Refactorisé pour utiliser BaseAutreTrajetForm (élimine 50+ lignes dupliquées)
"""

from wtforms import SelectField, SubmitField
from .base_forms import BaseAutreTrajetForm
from .constants import FormChoices, FormLabels
from .validators import CommonValidators


class AutresTrajetsForm(BaseAutreTrajetForm):
    """
    Formulaire pour les autres trajets (remplace sortie hors ville)
    Hérite de BaseAutreTrajetForm - élimine la duplication de code
    """

    # Champ lieu de départ spécifique (destination héritée de BaseAutreTrajetForm)
    lieu_depart = SelectField(
        FormLabels.LIEU_DEPART,
        choices=FormChoices.LIEUX,
        validators=CommonValidators.LIEU_VALIDE
    )

    # Bouton de soumission spécifique
    submit = SubmitField(FormLabels.BTN_ENREGISTRER_TRAJET)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration spécifique si nécessaire
        pass

    def validate_point_arriver(self, field):
        """Validation: destination différente du lieu de départ"""
        if field.data and hasattr(self, 'lieu_depart') and self.lieu_depart.data:
            if field.data.strip().lower() == self.lieu_depart.data.lower():
                from .validators import FormMessages
                from wtforms.validators import ValidationError
                raise ValidationError(FormMessages.LIEU_ARRIVEE_DIFFERENT)
