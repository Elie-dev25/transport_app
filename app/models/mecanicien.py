from app.database import db

class Mecanicien(db.Model):
    __tablename__ = 'mecanicien'
    mecanicien_id = db.Column(db.Integer, primary_key=True)
    numero_permis = db.Column(db.String(50), nullable=False)
    date_delivrance_permis = db.Column(db.Date, nullable=False)
    date_expiration_permis = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Mecanicien {self.mecanicien_id}>'
