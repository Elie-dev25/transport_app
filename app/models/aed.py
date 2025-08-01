from app.database import db
from sqlalchemy import Enum

class AED(db.Model):
    __tablename__ = 'aed'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    etat_vehicule = db.Column(Enum('BON', 'DEFAILLANT', name='etatvehiculeenum'), nullable=False)
    nombre_places = db.Column(db.Integer, nullable=False)
    derniere_maintenance = db.Column(db.Date, nullable=True)
    kilometrage = db.Column(db.Integer, nullable=True)
    type_huile = db.Column(Enum('QUARTZ', 'RUBIA', name='typehuileenum'), nullable=True)
    km_critique_huile = db.Column(db.Integer, nullable=True)
    km_critique_carburant = db.Column(db.Integer, nullable=True)
    date_derniere_vidange = db.Column(db.Date, nullable=True)