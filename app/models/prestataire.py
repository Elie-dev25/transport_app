from app.database import db

class Prestataire(db.Model):
    __tablename__ = 'prestataire'
    id = db.Column(db.Integer, primary_key=True)
    nom_prestataire = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    localisation = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
