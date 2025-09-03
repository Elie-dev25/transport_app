from flask_wtf import FlaskForm
from wtforms import DateTimeField, IntegerField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError
from datetime import datetime

class AutresTrajetsForm(FlaskForm):
    """Formulaire pour les autres trajets (remplace sortie hors ville)"""
    
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
    
    chauffeur_id = SelectField(
        'Chauffeur Bus UdM', 
        coerce=int, 
        validators=[DataRequired()]
    )
    
    numero_bus_udm = SelectField(
        'Numéro Bus UdM', 
        validators=[DataRequired()]
    )

    # Champs spécifiques pour autres trajets
    destination = StringField(
        'Destination spécifique', 
        validators=[Length(max=100)],
        render_kw={'placeholder': 'Ex: Hôpital, Aéroport, etc. (optionnel)'}
    )
    
    motif = StringField(
        'Motif du trajet', 
        validators=[DataRequired(), Length(max=255)],
        render_kw={'placeholder': 'Ex: Transport médical, mission officielle, etc.'}
    )
    
    kilometrage_actuel = IntegerField(
        'Kilométrage actuel (km)', 
        validators=[DataRequired(), NumberRange(min=0, max=999999)],
        render_kw={'placeholder': 'Ex: 15200'}
    )

    submit = SubmitField('Enregistrer le trajet')
    
    def validate_lieu_arrivee(self, field):
        """Validation personnalisée : le lieu d'arrivée doit être différent du lieu de départ"""
        if field.data == self.lieu_depart.data:
            raise ValidationError('Le lieu d\'arrivée doit être différent du lieu de départ.')
