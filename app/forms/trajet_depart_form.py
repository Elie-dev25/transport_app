from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime

class TrajetDepartForm(FlaskForm):
    date_heure_depart = DateTimeField(
        'Date et heure de départ',
        format='%Y-%m-%dT%H:%M',
        default=datetime.now,
        validators=[DataRequired()]
    )
    point_depart = SelectField('Point de départ', choices=[('Mfetum', 'Mfetum'), ('Ancienne mairie', 'Ancienne mairie')], validators=[DataRequired()])
    type_passagers = SelectField('Type de passagers', choices=[('ETUDIANT', 'Étudiant'), ('PERSONNEL', 'Personnel'), ('MALADE', 'Malade')], validators=[DataRequired()])
    nombre_places_occupees = IntegerField('Nombre de places occupées', validators=[DataRequired(), NumberRange(min=0)])
    chauffeur_id = SelectField('Chauffeur', coerce=int, validators=[DataRequired()])
    numero_aed = SelectField('Numéro AED', validators=[DataRequired()])
    kilometrage_actuel = IntegerField(
        'Kilométrage actuel du véhicule (km)',
        validators=[DataRequired(), NumberRange(min=0, max=999999)],
        render_kw={'placeholder': 'Ex: 15200'}
    )
    submit = SubmitField('Enregistrer le départ')
