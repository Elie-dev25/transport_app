from app.database import db

class Prestataire(db.Model):
    __tablename__ = 'prestataire'
    immatriculation = db.Column(db.String(20), primary_key=True)
    nom_prestataire = db.Column(db.String(100), nullable=False)
    nombre_places = db.Column(db.Integer, nullable=False)
    nom_chauffeur = db.Column(db.String(100))
