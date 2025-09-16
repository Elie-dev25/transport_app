"""
Formulaire de retour Banekane (legacy)
Phase 2 - Refactorisé pour utiliser les classes de base (élimine 25+ lignes dupliquées)
"""

from wtforms import HiddenField, RadioField, SelectField, StringField, SubmitField
from wtforms.validators import Length
from .base_forms import BaseTrajetForm
from .constants import FormChoices, FormLabels
from .validators import CommonValidators


class TrajetBanekaneRetourForm(BaseTrajetForm):
    """
    Formulaire de retour Banekane (legacy) - maintient la compatibilité
    Hérite de BaseTrajetForm avec champs spécifiques
    """

    # Point de départ fixé à Banekane
    point_depart = HiddenField(
        'Point de départ',
        default='Banekane',
        validators=[CommonValidators.REQUIRED]
    )

    # Sélection du type de bus
    type_bus = RadioField(
        'Type de bus',
        choices=FormChoices.TYPE_BUS,
        default='AED',
        validators=[CommonValidators.REQUIRED]
    )

    # Champs pour Bus UdM
    numero_bus_udm = SelectField('Numéro Bus UdM', choices=[])

    # Point d'arrivée (destination du retour)
    point_arriver = SelectField(
        'Point d\'arrivée',
        choices=FormChoices.LIEUX,
        validators=CommonValidators.LIEU_ARRIVEE
    )

    # Champs pour Prestataire (legacy)
    nom_agence = SelectField(
        'Nom Prestataire',
        choices=FormChoices.PRESTATAIRES_LEGACY
    )
    immat_bus = StringField('Immatriculation Bus', [Length(max=20)])
    nom_chauffeur_agence = StringField('Nom du chauffeur (Prestataire)', [Length(max=100)])

    # Bouton de soumission spécifique
    submit = SubmitField(FormLabels.BTN_ENREGISTRER_RETOUR)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration legacy si nécessaire
        pass
