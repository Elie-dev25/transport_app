from app.database import db
from sqlalchemy import Enum

class DemandeHuile(db.Model):
    __tablename__ = 'demandehuile'

    demande_huile_id = db.Column(db.Integer, primary_key=True)
    date_demande = db.Column(db.Date, nullable=False)
    statut_demande = db.Column(Enum('EN_ATTENTE', 'APPROUVEE', name='statut_demande_enum'), nullable=False)
    numero_aed = db.Column(db.String(50), nullable=False)
    mecanicien_id = db.Column(db.Integer, db.ForeignKey('mecanicien.mecanicien_id'), nullable=False)

    mecanicien = db.relationship('Mecanicien', backref=db.backref('demandes_huile', lazy=True))

    def __repr__(self):
        return f"<DemandeHuile {self.demande_huile_id} {self.statut_demande}>"