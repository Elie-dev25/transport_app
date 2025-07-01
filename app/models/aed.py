from app.database import db
from sqlalchemy import Enum

class AED(db.Model):
    __tablename__ = 'aed'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    niveau_carburant = db.Column(db.Float, nullable=False)
    niveau_huile = db.Column(db.Float, nullable=False)
    seuil_critique_huile = db.Column(db.Float, nullable=False)
    etat_vehicule = db.Column(Enum('BON', 'DEFAILLANT', name='etatvehiculeenum'), nullable=False)
    nombre_places = db.Column(db.Integer, nullable=False, default=30)
    derniere_maintenance = db.Column(db.Date, nullable=True)