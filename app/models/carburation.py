from app.database import db

class Carburation(db.Model):
    __tablename__ = 'carburation'
    id = db.Column(db.Integer, primary_key=True)
    bus_udm_id = db.Column(db.Integer, db.ForeignKey('bus_udm.id'), nullable=False)
    date_carburation = db.Column(db.Date, nullable=False)
    kilometrage = db.Column(db.Integer, nullable=False)
    quantite_litres = db.Column(db.Float, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)
    cout_total = db.Column(db.Float, nullable=False)
    remarque = db.Column(db.String(256), nullable=True)

    bus_udm = db.relationship('BusUdM', backref=db.backref('carburations', lazy=True))
