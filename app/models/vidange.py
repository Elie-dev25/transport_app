from app.extensions import db
from sqlalchemy import Enum

class Vidange(db.Model):
    __tablename__ = 'vidange'
    id = db.Column(db.Integer, primary_key=True)
    bus_udm_id = db.Column(db.Integer, db.ForeignKey('bus_udm.id'), nullable=False)
    date_vidange = db.Column(db.Date, nullable=False)
    kilometrage = db.Column(db.Integer, nullable=False)
    type_huile = db.Column(Enum('QUARTZ', 'RUBIA', name='type_huile_enum'), nullable=False)
    remarque = db.Column(db.String(256), nullable=True)

    bus_udm = db.relationship('BusUdM', backref=db.backref('vidanges', lazy=True))
