from app.database import db
from sqlalchemy import Enum

class BusUdM(db.Model):
    __tablename__ = 'bus_udm'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    immatriculation = db.Column(db.String(20), nullable=False)
    # Nouveaux champs pour les informations détaillées du véhicule
    numero_chassis = db.Column(db.String(100), nullable=True)
    modele = db.Column(db.String(100), nullable=True)
    type_vehicule = db.Column(Enum('TOURISME', 'COASTER', 'MINIBUS', 'AUTOCAR', 'AUTRE', name='typevehiculeenum'), nullable=True)
    marque = db.Column(db.String(50), nullable=True)
    etat_vehicule = db.Column(Enum('BON', 'DEFAILLANT', name='etatvehiculeenum'), nullable=False)
    nombre_places = db.Column(db.Integer, nullable=False)
    derniere_maintenance = db.Column(db.Date, nullable=True)
    kilometrage = db.Column(db.Integer, nullable=True)
    # Type d'huile détaillé (ex: "Quartz 5000 20W-50")
    type_huile = db.Column(db.String(50), nullable=True)
    km_critique_huile = db.Column(db.Integer, nullable=True)
    km_critique_carburant = db.Column(db.Integer, nullable=True)
    capacite_plein_carburant = db.Column(db.Integer, nullable=True)
    # Nouvelle colonne: capacité du réservoir en litres
    capacite_reservoir_litres = db.Column(db.Float, nullable=True)
    # Niveau actuel de carburant en litres (suivi en temps réel, manuel ou capteur)
    niveau_carburant_litres = db.Column(db.Float, nullable=True)
    # Consommation spécifique du bus (km par litre). Si null, on utilisera la valeur globale.
    consommation_km_par_litre = db.Column(db.Float, nullable=True)
    date_derniere_vidange = db.Column(db.Date, nullable=True)
    # Relation ORM: un Bus UdM peut avoir plusieurs pannes
    pannes = db.relationship('PanneBusUdM', backref='bus_udm', lazy=True)
