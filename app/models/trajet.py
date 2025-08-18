from app.database import db
from app.models.chargetransport import Chargetransport  # Assure la déclaration de la table pour les FK
from app.models.prestataire import Prestataire
from datetime import datetime

class Trajet(db.Model):
    __tablename__ = 'trajet'
    trajet_id = db.Column(db.Integer, primary_key=True)
    date_heure_depart = db.Column(db.DateTime, nullable=False)
    point_depart = db.Column(db.String(100), nullable=False)  # Modifié pour permettre saisie libre
    type_passagers = db.Column(db.Enum('ETUDIANT', 'PERSONNEL', 'MALADE', name='typepassagersenum'), nullable=True)
    nombre_places_occupees = db.Column(db.Integer, nullable=True)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('chauffeur.chauffeur_id'), nullable=True)
    numero_aed = db.Column(db.String(50), db.ForeignKey('aed.numero'))
    immat_bus = db.Column(db.String(20), db.ForeignKey('prestataire.immatriculation'))
    enregistre_par = db.Column(db.Integer, db.ForeignKey('chargetransport.chargetransport_id'), nullable=False)
    # Nouveaux champs pour sorties hors de la ville (AED uniquement)
    destination = db.Column(db.String(100), nullable=True)
    motif = db.Column(db.String(255), nullable=True)

    # Relation pour accéder au chargé de transport
    chargeur = db.relationship('Chargetransport', backref='trajets')

    def __repr__(self):
        return f'<Trajet {self.trajet_id} {self.date_heure_depart}>'