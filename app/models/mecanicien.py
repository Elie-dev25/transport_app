from app.database import db

class Mecanicien(db.Model):
    __tablename__ = 'mecanicien'
    mecanicien_id = db.Column(db.Integer, primary_key=True)
    # Ajout d'autres champs si besoin

    def __repr__(self):
        return f'<Mecanicien {self.mecanicien_id}>'
