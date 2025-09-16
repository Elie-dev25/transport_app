"""
Modèle Mecanicien adapté à la structure DB existante
Compatible avec la table mecanicien réelle (sans mixins pour éviter les conflits)
"""

from app.database import db


class Mecanicien(db.Model):
    """
    Modèle Mecanicien adapté à la structure de base de données existante
    Définit explicitement tous les champs pour correspondre à la table réelle
    """
    __tablename__ = 'mecanicien'

    mecanicien_id = db.Column(db.Integer, primary_key=True)
    numero_permis = db.Column(db.String(50), nullable=False, comment='Numéro du permis de conduire')
    date_delivrance_permis = db.Column(db.Date, nullable=False, comment='Date de délivrance du permis')
    date_expiration_permis = db.Column(db.Date, nullable=False, comment='Date d\'expiration du permis')

    def __repr__(self):
        return f'<Mecanicien {self.mecanicien_id}>'

    def get_full_info(self):
        """Retourne toutes les informations du mécanicien"""
        return {
            'id': self.mecanicien_id,
            'numero_permis': self.numero_permis,
            'date_delivrance_permis': self.date_delivrance_permis,
            'date_expiration_permis': self.date_expiration_permis
        }
