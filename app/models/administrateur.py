"""
Modèle Administrateur refactorisé
Phase 3 - Utilise BaseModel avec FK explicite (correction erreur SQLAlchemy)
"""

from app.database import db


class Administrateur(db.Model):
    """
    Modèle Administrateur refactorisé
    Hérite de BaseModel avec FK explicite vers utilisateur
    """
    __tablename__ = 'administrateur'

    # Clé primaire explicite (FK vers utilisateur)
    administrateur_id = db.Column(
        db.Integer,
        db.ForeignKey('utilisateur.utilisateur_id', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True
    )

    # Relation vers utilisateur
    utilisateur = db.relationship(
        'Utilisateur',
        backref='administrateur',
        uselist=False
    )

    def __repr__(self) -> str:
        return f"<Administrateur id={self.administrateur_id}>"

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
