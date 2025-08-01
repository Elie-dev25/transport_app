from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class AEDForm(FlaskForm):
    """Formulaire pour l'ajout et la modification d'un bus AED"""

    numero = StringField(
        'Numéro du bus',
        validators=[DataRequired(), Length(min=3, max=50)],
        render_kw={'placeholder': 'Ex: AED-001'}
    )

    kilometrage = IntegerField(
        'Niveau de kilométrage (km)',
        validators=[DataRequired(), NumberRange(min=0, max=999999)],
        render_kw={'placeholder': 'Ex: 15000'}
    )

    type_huile = SelectField(
        'Type d\'huile',
        choices=[('', '-- Choisir --'), ('QUARTZ', 'Quartz'), ('RUBIA', 'Rubia')],
        validators=[DataRequired()]
    )

    km_critique_huile = IntegerField(
        'Kilomètre critique pour l\'huile (km)',
        validators=[DataRequired(), NumberRange(min=0, max=999999)],
        render_kw={'placeholder': 'Ex: 20000'}
    )

    km_critique_carburant = IntegerField(
        'Kilomètre critique pour le carburant (km)',
        validators=[DataRequired(), NumberRange(min=0, max=999999)],
        render_kw={'placeholder': 'Ex: 25000'}
    )

    date_derniere_vidange = DateField(
        'Date de la dernière vidange',
        validators=[DataRequired()]
    )

    etat_vehicule = SelectField(
        'État actuel du véhicule',
        choices=[('BON', 'Bon'), ('DEFAILLANT', 'Défaillant')],
        validators=[DataRequired()]
    )

    nombre_places = IntegerField(
        'Nombre de places',
        validators=[DataRequired(), NumberRange(min=1, max=100)],
        default=30
    )

    derniere_maintenance = DateField(
        'Date de la dernière maintenance',
        validators=[DataRequired()]
    )

    submit = SubmitField('Ajouter le bus')

    def validate(self, extra_validators=None):
        """Validation personnalisée"""
        if not super().validate(extra_validators):
            return False

        # Vérifier que le kilométrage critique huile est inférieur au carburant
        if (self.km_critique_huile.data and self.km_critique_carburant.data and
            self.km_critique_huile.data >= self.km_critique_carburant.data):
            self.km_critique_huile.errors.append(
                'Le kilométrage critique pour l\'huile doit être inférieur à celui du carburant.'
            )
            return False

        return True