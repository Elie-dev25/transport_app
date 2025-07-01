from app.database import db

class Chauffeur(db.Model):
    __tablename__ = 'chauffeur'
    chauffeur_id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    numero_permis = db.Column(db.String(50), nullable=False, unique=True)
    telephone = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Chauffeur {self.nom} {self.prenom}>'
