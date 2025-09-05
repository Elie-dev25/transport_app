from app.database import db
from datetime import datetime


class Depannage(db.Model):
    __tablename__ = 'depannage'

    id = db.Column(db.Integer, primary_key=True)
    # Liens
    panne_id = db.Column(db.Integer, db.ForeignKey('panne_bus_udm.id'), nullable=True)
    bus_udm_id = db.Column(db.Integer, db.ForeignKey('bus_udm.id'), nullable=True)

    # Références pratiques
    numero_bus_udm = db.Column(db.String(50), nullable=False)
    immatriculation = db.Column(db.String(50), nullable=True)

    # Données réparation
    date_heure = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    kilometrage = db.Column(db.Float, nullable=True)
    cout_reparation = db.Column(db.Numeric(12, 2), nullable=True)
    description_panne = db.Column(db.Text, nullable=False)
    cause_panne = db.Column(db.Text, nullable=True)

    # Traçabilité
    repare_par = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Depannage {self.numero_bus_udm} {self.date_heure}>'
