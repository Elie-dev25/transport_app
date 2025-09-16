"""
Formulaire de départ (legacy)
Phase 2 - Refactorisé pour utiliser BaseLegacyForm (élimine 20+ lignes dupliquées)
"""

from wtforms import SubmitField
from .base_forms import BaseLegacyForm
from .constants import FormLabels


class TrajetDepartForm(BaseLegacyForm):
    """
    Formulaire de départ (legacy) - maintient la compatibilité
    Hérite de BaseLegacyForm - élimine la duplication de code
    """

    # Bouton de soumission spécifique
    submit = SubmitField(FormLabels.BTN_ENREGISTRER_DEPART)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration legacy si nécessaire
        pass
