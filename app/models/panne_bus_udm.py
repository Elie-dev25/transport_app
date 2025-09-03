from app.database import db
from datetime import datetime


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
    criticite = db.Column(db.String(20), nullable=False)  # FAIBLE, MOYENNE, HAUTE
    immobilisation = db.Column(db.Boolean, nullable=False, default=False)
    enregistre_par = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<PanneBusUdM {self.numero_bus_udm} - {self.criticite}>'
