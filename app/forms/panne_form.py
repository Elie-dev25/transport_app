from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length


class PanneForm(FlaskForm):
    numero_bus_udm = StringField('Numéro Bus UdM', validators=[DataRequired()])
    immatriculation = StringField('Immatriculation')
    kilometrage = FloatField('Kilométrage')
    description = TextAreaField('Description de la panne', validators=[DataRequired(), Length(min=10, max=500)])
    criticite = SelectField('Criticité',
                          choices=[('FAIBLE', 'Faible'), ('MOYENNE', 'Moyenne'), ('HAUTE', 'Haute')],
                          validators=[DataRequired()])
    immobilisation = BooleanField('Bus immobilisé')
