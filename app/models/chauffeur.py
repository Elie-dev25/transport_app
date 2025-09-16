"""
Modèle Chauffeur adapté à la structure DB existante
Compatible avec la table chauffeur réelle (sans mixins pour éviter les conflits)
"""

from app.database import db


class Chauffeur(db.Model):
    """
    Modèle Chauffeur adapté à la structure de base de données existante
    Définit explicitement tous les champs pour correspondre à la table réelle
    """
    __tablename__ = 'chauffeur'

    chauffeur_id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, comment='Nom du chauffeur')
    prenom = db.Column(db.String(100), nullable=False, comment='Prénom du chauffeur')
    numero_permis = db.Column(db.String(50), nullable=False, comment='Numéro du permis de conduire')
    telephone = db.Column(db.String(20), nullable=False, comment='Numéro de téléphone')
    date_delivrance_permis = db.Column(db.Date, nullable=False, comment='Date de délivrance du permis')
    date_expiration_permis = db.Column(db.Date, nullable=False, comment='Date d\'expiration du permis')

    def __repr__(self):
        return f'<Chauffeur {self.nom} {self.prenom}>'

    def get_full_info(self):
        """Retourne toutes les informations du chauffeur"""
        return {
            'id': self.chauffeur_id,
            'nom': self.nom,
            'prenom': self.prenom,
            'nom_complet': f"{self.prenom} {self.nom}",
            'numero_permis': self.numero_permis,
            'date_delivrance_permis': self.date_delivrance_permis,
            'date_expiration_permis': self.date_expiration_permis,
            'telephone': self.telephone
        }

    @property
    def nom_complet(self):
        """Propriété pour obtenir le nom complet"""
        return f"{self.prenom} {self.nom}"

    def is_permis_expire(self):
        """Vérifie si le permis est expiré"""
        from datetime import date
        return self.date_expiration_permis < date.today() if self.date_expiration_permis else True
