from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, IntegerField, StringField, HiddenField, SubmitField, RadioField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import datetime

class TrajetBanekaneRetourForm(FlaskForm):
    # Point de départ fixé à Banekane (hidden pour POST, affiché disabled côté UI)
    point_depart = HiddenField('Point de départ', default='Banekane', validators=[DataRequired()])

    # Sélection du type de bus
    type_bus = RadioField('Type de bus', choices=[('AED', 'Bus AED'), ('AGENCE', 'Bus Agence')], default='AED', validators=[DataRequired()])

    # Champs pour Bus AED
    chauffeur_id = SelectField('Chauffeur AED', coerce=int)
    numero_aed = SelectField('Numéro AED')
    type_passagers = SelectField('Type de passagers', choices=[('ETUDIANT', 'Étudiant'), ('PERSONNEL', 'Personnel'), ('MALADE', 'Malade')])

    # Champs pour Bus Agence
    nom_agence = SelectField('Nom Agence', choices=[('Charter', 'Charter'), ('Noblesse', 'Noblesse')])
    immat_bus = StringField('Immatriculation Bus', [Length(max=20)])
    nom_chauffeur_agence = StringField('Nom du chauffeur (Agence)', [Length(max=100)])

    # Champs communs
    nombre_places_occupees = IntegerField('Nombre de places occupées', validators=[DataRequired(), NumberRange(min=0)])
    date_heure_depart = DateTimeField('Date et heure de départ', format='%Y-%m-%dT%H:%M', default=datetime.now, validators=[DataRequired()])

    submit = SubmitField('Enregistrer le retour')
