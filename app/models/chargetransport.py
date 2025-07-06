from app.database import db

class Chargetransport(db.Model):
    __tablename__ = 'chargetransport'
    chargetransport_id = db.Column(db.Integer, db.ForeignKey('utilisateur.utilisateur_id'), primary_key=True)
    # Relation pour accéder à l'utilisateur (nom, login, etc.)
    utilisateur = db.relationship('Utilisateur', backref='chargetransport', uselist=False)
