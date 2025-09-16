from flask_wtf import FlaskForm
from wtforms import DateTimeField, IntegerField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length
from datetime import datetime

class TrajetSortieHorsVilleForm(FlaskForm):
    # Uniquement AED
    point_depart = StringField('Point de départ', validators=[DataRequired(), Length(max=100)])
    chauffeur_id = SelectField('Chauffeur AED', coerce=int, validators=[DataRequired()])
    numero_aed = SelectField('Numéro AED', validators=[DataRequired()])

    # Champs spécifiques sortie
    point_arriver = StringField('Destination (hors ville)', [DataRequired(), Length(max=100)])
    motif = StringField('Motif de la sortie', [DataRequired(), Length(max=255)])
    kilometrage_actuel = IntegerField('Kilométrage actuel (km)', validators=[DataRequired(), NumberRange(min=0, max=999999)])

    # Date et heure
    date_heure_depart = DateTimeField('Date et heure de départ', format='%Y-%m-%dT%H:%M', default=datetime.now, validators=[DataRequired()])

    submit = SubmitField('Enregistrer la sortie')
