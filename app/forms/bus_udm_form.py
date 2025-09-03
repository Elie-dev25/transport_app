from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange, Length

class BusUdMForm(FlaskForm):
    """Formulaire pour l'ajout et la modification d'un bus UdM"""

    numero = StringField(
        'Numéro du bus',
        validators=[DataRequired(), Length(min=3, max=50)],
        render_kw={'placeholder': 'Ex: UDM-001'}
    )

    immatriculation = StringField(
        'Immatriculation',
        validators=[DataRequired(), Length(min=3, max=20)],
        render_kw={'placeholder': 'Ex: 1234-AB-01'}
    )

    # Nouveaux champs obligatoires
    numero_chassis = StringField(
        'Numéro de châssis',
        validators=[DataRequired(), Length(min=5, max=100)],
        render_kw={'placeholder': 'Ex: VF1234567890123456'}
    )

    modele = StringField(
        'Modèle',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Ex: Sprinter 515'}
    )

    type_vehicule = SelectField(
        'Type de véhicule',
        choices=[
            ('', '-- Choisir --'),
            ('TOURISME', 'Tourisme'),
            ('COASTER', 'Coaster'),
            ('MINIBUS', 'Minibus'),
            ('AUTOCAR', 'Autocar'),
            ('AUTRE', 'Autre')
        ],
        validators=[DataRequired()]
    )

    marque = StringField(
        'Marque',
        validators=[DataRequired(), Length(min=2, max=50)],
        render_kw={'placeholder': 'Ex: Mercedes, Toyota, Hyundai'}
    )

    kilometrage = IntegerField(
        'Niveau de kilométrage (km)',
        validators=[DataRequired(), NumberRange(min=0, max=999999)],
        render_kw={'placeholder': 'Ex: 15000'}
    )

    type_huile = SelectField(
        'Type d\'huile',
        choices=[
            ('', '-- Choisir --'),
            ('Quartz 5000 20W-50', 'Quartz 5000 20W-50'),
            ('Quartz 7000 10W-40', 'Quartz 7000 10W-40'),
            ('Quartz 9000 5W-40', 'Quartz 9000 5W-40'),
            ('Rubia TIR 7400 15W-40', 'Rubia TIR 7400 15W-40'),
            ('Rubia TIR 9900 FE 5W-30', 'Rubia TIR 9900 FE 5W-30'),
            ('Rubia Fleet HD 400 15W-40', 'Rubia Fleet HD 400 15W-40'),
        ],
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

    # Capacité du réservoir (L) - optionnelle
    capacite_reservoir_litres = FloatField(
        'Capacité réservoir (L)',
        validators=[NumberRange(min=0)],
        render_kw={'placeholder': 'Ex: 70.0'}
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
