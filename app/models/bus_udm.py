"""
Modèle BusUdM adapté à la structure DB existante
Compatible avec la table bus_udm réelle (sans VehicleMixin pour éviter les conflits)
"""

from app.database import db
from sqlalchemy import Enum


class BusUdM(db.Model):
    """
    Modèle BusUdM adapté à la structure de base de données existante
    Définit explicitement tous les champs pour correspondre à la table réelle
    """
    __tablename__ = 'bus_udm'

    id = db.Column(db.Integer, primary_key=True)

    # Champs véhicule de base (correspondant à la structure DB réelle)
    numero = db.Column(db.String(50), nullable=False, comment='Numéro du bus')
    immatriculation = db.Column(db.String(20), nullable=False, comment='Plaque d\'immatriculation')
    marque = db.Column(db.String(50), nullable=True, comment='Marque du véhicule')
    modele = db.Column(db.String(100), nullable=True, comment='Modèle du véhicule')
    # Note: pas de champ 'annee' dans la DB réelle
    nombre_places = db.Column(db.Integer, nullable=False, comment='Nombre de places')
    kilometrage = db.Column(db.Integer, nullable=True, comment='Kilométrage actuel')

    # Champs spécifiques aux bus UdM (correspondant à la structure DB réelle)
    numero_chassis = db.Column(db.String(100), nullable=False, comment='Numéro de châssis')
    type_vehicule = db.Column(
        Enum('TOURISME', 'COASTER', 'MINIBUS', 'AUTOCAR', 'AUTRE', name='typevehiculeenum'),
        nullable=True,
        comment='Type de véhicule'
    )
    etat_vehicule = db.Column(
        Enum('BON', 'DEFAILLANT', name='etatvehiculeenum'),
        nullable=False,
        comment='État du véhicule'
    )
    derniere_maintenance = db.Column(db.Date, nullable=True, comment='Date de dernière maintenance')

    # Gestion de l'huile et maintenance
    type_huile = db.Column(db.String(50), nullable=True, comment='Type d\'huile utilisé')
    km_critique_huile = db.Column(db.Integer, nullable=True, comment='Kilométrage critique pour l\'huile')
    date_derniere_vidange = db.Column(db.Date, nullable=True, comment='Date de la dernière vidange')

    # Gestion du carburant
    km_critique_carburant = db.Column(db.Integer, nullable=True, comment='Kilométrage critique pour le carburant')
    capacite_plein_carburant = db.Column(db.Integer, nullable=True, comment='Capacité du plein de carburant en km')
    capacite_reservoir_litres = db.Column(db.Float, nullable=True, comment='Capacité du réservoir en litres')
    niveau_carburant_litres = db.Column(db.Float, nullable=True, comment='Niveau actuel de carburant en litres')
    consommation_km_par_litre = db.Column(db.Float, nullable=True, comment='Consommation spécifique du bus')

    # Relations ORM
    pannes = db.relationship('PanneBusUdM', backref='bus_udm', lazy=True)

    def __repr__(self):
        return f'<BusUdM {self.numero} - {self.immatriculation}>'

    def get_info_display(self):
        """Retourne les informations d'affichage du bus"""
        return f"Bus {self.numero} ({self.immatriculation}) - {self.marque} {self.modele}"
