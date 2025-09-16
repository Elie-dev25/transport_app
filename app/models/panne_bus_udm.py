from app.database import db
from datetime import datetime
from sqlalchemy import Enum


class PanneBusUdM(db.Model):
    __tablename__ = 'panne_bus_udm'
    
    id = db.Column(db.Integer, primary_key=True)
    # Association ORM (option 2): référence vers BusUdM.id
    bus_udm_id = db.Column(db.Integer, db.ForeignKey('bus_udm.id'), nullable=True)
    numero_bus_udm = db.Column(db.String(50), nullable=False)
    immatriculation = db.Column(db.String(50), nullable=True)
    kilometrage = db.Column(db.Float, nullable=True)
    date_heure = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    criticite = db.Column(Enum('FAIBLE', 'MOYENNE', 'HAUTE', name='criticite_enum'), nullable=False)
    immobilisation = db.Column(db.Boolean, nullable=False, default=False)
    enregistre_par = db.Column(db.String(100), nullable=False)
    # Suivi de résolution
    resolue = db.Column(db.Boolean, nullable=False, default=False)
    date_resolution = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<PanneBusUdM {self.numero_bus_udm} - {self.criticite}>'
