from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import datetime

class TrajetPrestataireForm(FlaskForm):
    nom_prestataire = SelectField(
        'Nom Prestataire',
        choices=[('Charter', 'Charter'), ('Noblesse', 'Noblesse')],
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
    point_depart = SelectField(
        'Point de départ',
        choices=[('Mfetum', 'Mfetum'), ('Ancienne mairie', 'Ancienne mairie')],
        validators=[DataRequired()]
    )
    type_passagers = SelectField(
        'Type de passagers',
        choices=[('ETUDIANT', 'Étudiant')],
        default='ETUDIANT',
        validators=[DataRequired()],
        render_kw={'disabled': True}
    )
    nombre_places_occupees = IntegerField(
        'Places occupées',
        validators=[DataRequired(), NumberRange(min=0)]
    )
    submit = SubmitField('Enregistrer le départ')
