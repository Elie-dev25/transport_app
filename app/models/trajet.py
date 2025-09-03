from app.database import db
from app.models.chargetransport import Chargetransport  # Assure la déclaration de la table pour les FK
from app.models.prestataire import Prestataire
from datetime import datetime

class Trajet(db.Model):
    __tablename__ = 'trajet'
    trajet_id = db.Column(db.Integer, primary_key=True)
    type_trajet = db.Column(db.Enum('UDM_INTERNE', 'PRESTATAIRE', 'AUTRE', name='type_trajet_enum'), nullable=False)
    date_heure_depart = db.Column(db.DateTime, nullable=False)
    point_depart = db.Column(db.Enum('Mfetum', 'Ancienne Mairie', 'Banekane', name='point_depart_enum'), nullable=False)
    type_passagers = db.Column(db.Enum('ETUDIANT', 'PERSONNEL', 'MALADE', name='typepassagersenum'), nullable=True)
    nombre_places_occupees = db.Column(db.Integer, nullable=True)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('chauffeur.chauffeur_id'), nullable=True)
    numero_bus_udm = db.Column(db.String(50), db.ForeignKey('bus_udm.numero'), nullable=True)
    immat_bus = db.Column(db.String(20), nullable=True)  # Pour les bus prestataires
    enregistre_par = db.Column(db.Integer, db.ForeignKey('chargetransport.chargetransport_id'), nullable=True)
    point_arriver = db.Column(db.String(100), nullable=True)  # Nom correct selon votre DB
    motif = db.Column(db.String(255), nullable=True)  # Pour les autres trajets

    # Relation pour accéder au chargé de transport
    chargeur = db.relationship('Chargetransport', backref='trajets')

    def __repr__(self):
        return f'<Trajet {self.trajet_id} {self.date_heure_depart}>'