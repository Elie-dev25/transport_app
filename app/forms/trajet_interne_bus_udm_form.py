"""
Formulaire pour les trajets internes avec bus UdM
Phase 2 - Refactorisé pour utiliser BaseTrajetInterneForm (élimine 50+ lignes dupliquées)
"""

from wtforms import SubmitField
from .base_forms import BaseTrajetInterneForm
from .constants import FormLabels


class TrajetInterneBusUdMForm(BaseTrajetInterneForm):
    """
    Formulaire pour les trajets internes avec bus UdM (remplace l'ancien départ AED)
    Hérite de BaseTrajetInterneForm - élimine la duplication de code
    """

    # Bouton de soumission spécifique
    submit = SubmitField(FormLabels.BTN_ENREGISTRER_TRAJET)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration spécifique si nécessaire
        pass

    # La validation lieu_arrivee est héritée de BaseTrajetInterneForm
    # Les champs communs sont hérités de BaseTrajetForm et BaseTrajetInterneForm
