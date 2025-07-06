from app.database import db

class Busagence(db.Model):
    __tablename__ = 'busagence'
    immatriculation = db.Column(db.String(20), primary_key=True)
    nom_agence = db.Column(db.String(100), nullable=False)
    nombre_places = db.Column(db.Integer, nullable=False)
