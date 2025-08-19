from app import db

class Administrateur(db.Model):
    __tablename__ = 'administrateur'

    administrateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.utilisateur_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)

    def __repr__(self) -> str:
        return f"<Administrateur id={self.administrateur_id}>"
