from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError
from datetime import datetime

class TrajetPrestataireForm(FlaskForm):
    """Formulaire pour les trajets avec bus prestataire (modernisé)"""

    nom_prestataire = SelectField(
        'Nom Prestataire',
        coerce=int,
        validators=[DataRequired()]
    )
    immat_bus = StringField(
        'Immatriculation Bus',
        validators=[DataRequired(), Length(max=20)]
    )
    nombre_places = IntegerField(
        'Nombre de places bus',
        default=70,
        validators=[DataRequired(), NumberRange(min=10, max=70)]
    )
    nom_chauffeur = StringField(
        'Nom du chauffeur',
        validators=[DataRequired(), Length(max=100)]
    )
    date_heure_depart = DateTimeField(
        'Date et heure de départ',
        format='%Y-%m-%dT%H:%M',
        default=datetime.now,
        validators=[DataRequired()]
    )

    # Nouveaux champs lieu de départ et arrivée
    lieu_depart = SelectField(
        'Lieu de départ',
        choices=[
            ('Mfetum', 'Mfetum'),
            ('Ancienne Mairie', 'Ancienne Mairie'),
            ('Banekane', 'Banekane')
        ],
        validators=[DataRequired()]
    )

    lieu_arrivee = SelectField(
        'Lieu d\'arrivée',
        choices=[
            ('Mfetum', 'Mfetum'),
            ('Ancienne Mairie', 'Ancienne Mairie'),
            ('Banekane', 'Banekane')
        ],
        validators=[DataRequired()]
    )
    type_passagers = SelectField(
        'Type de passagers',
        choices=[('ETUDIANT', 'Étudiant'), ('PERSONNEL', 'Personnel'), ('MALADE', 'Malade'), ('INVITER', 'Invité'), ('MALADE_PERSONNEL', 'Malade Personnel')],
        default='ETUDIANT',
        validators=[DataRequired()]
    )
    nombre_places_occupees = IntegerField(
        'Places occupées',
        validators=[DataRequired(), NumberRange(min=0)]
    )
    submit = SubmitField('Enregistrer le trajet')

    def validate_lieu_arrivee(self, field):
        """Validation personnalisée : le lieu d'arrivée doit être différent du lieu de départ"""
        if field.data == self.lieu_depart.data:
            raise ValidationError('Le lieu d\'arrivée doit être différent du lieu de départ.')
