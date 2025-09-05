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
    
    lieu_arrivee = StringField(
        'Lieu d\'arrivée', 
        validators=[DataRequired(), Length(max=100)],
        render_kw={'placeholder': 'Entrez le lieu d\'arrivée (ex: Hôpital Central, Aéroport, etc.)'}
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

    # Supprimé le champ destination redondant avec lieu_arrivee
    
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
        if field.data and field.data.strip().lower() == self.lieu_depart.data.lower():
            raise ValidationError('Le lieu d\'arrivée doit être différent du lieu de départ.')
