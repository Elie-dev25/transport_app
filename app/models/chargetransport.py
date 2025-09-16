"""
Modèle ChargeTransport refactorisé
Phase 3 - Utilise BaseModel avec FK explicite (correction erreur SQLAlchemy)
"""

from app.database import db


class Chargetransport(db.Model):
    """
    Modèle ChargeTransport refactorisé
    Hérite de BaseModel avec FK explicite vers utilisateur
    """
    __tablename__ = 'chargetransport'

    # Clé primaire explicite (FK vers utilisateur)
    chargetransport_id = db.Column(
        db.Integer,
        db.ForeignKey('utilisateur.utilisateur_id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True
    )

    # Relation vers utilisateur
    utilisateur = db.relationship(
        'Utilisateur',
        backref='chargetransport',
        uselist=False
    )

    def __repr__(self):
        return f"<Chargetransport id={self.chargetransport_id}>"

    def get_user_info(self):
        """Retourne les informations utilisateur associées"""
        if self.utilisateur:
            return {
                'nom': self.utilisateur.nom,
                'prenom': self.utilisateur.prenom,
                'login': self.utilisateur.login,
                'role': self.utilisateur.role
            }
        return None
