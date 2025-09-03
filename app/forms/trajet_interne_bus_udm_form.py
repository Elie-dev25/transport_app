from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import datetime

class TrajetInterneBusUdMForm(FlaskForm):
    """Formulaire pour les trajets internes avec bus UdM (remplace l'ancien départ AED)"""
    
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
        choices=[
            ('ETUDIANT', 'Étudiant'), 
            ('PERSONNEL', 'Personnel'), 
            ('MALADE', 'Malade')
        ], 
        validators=[DataRequired()]
    )
    
    nombre_places_occupees = IntegerField(
        'Nombre de places occupées', 
        validators=[DataRequired(), NumberRange(min=0)]
    )
    
    chauffeur_id = SelectField(
        'Chauffeur', 
        coerce=int, 
        validators=[DataRequired()]
    )
    
    numero_bus_udm = SelectField(
        'Numéro Bus UdM', 
        validators=[DataRequired()]
    )
    
    kilometrage_actuel = IntegerField(
        'Kilométrage actuel du véhicule (km)',
        validators=[DataRequired(), NumberRange(min=0, max=999999)],
        render_kw={'placeholder': 'Ex: 15200'}
    )
    
    submit = SubmitField('Enregistrer le trajet')
    
    def validate_lieu_arrivee(self, field):
        """Validation personnalisée : le lieu d'arrivée doit être différent du lieu de départ"""
        if field.data == self.lieu_depart.data:
            raise ValidationError('Le lieu d\'arrivée doit être différent du lieu de départ.')
