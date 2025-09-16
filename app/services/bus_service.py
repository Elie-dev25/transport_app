"""
Service de gestion des bus réutilisable
Fournit les opérations CRUD et de consultation pour tous les rôles
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, or_

from app.database import db
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.vidange import Vidange
from app.models.carburation import Carburation
from app.models.trajet import Trajet


class BusService:
    """Service pour la gestion des bus"""
    
    @staticmethod
    def get_all_buses(include_stats: bool = False) -> List[Dict[str, Any]]:
        """
        Récupère tous les bus avec statistiques optionnelles
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE
        """
        buses = BusUdM.query.all()
        result = []
        
        for bus in buses:
            bus_data = {
                'id': bus.id,
                'numero': bus.numero,
                'immatriculation': bus.immatriculation,
                'marque': bus.marque,
                'modele': bus.modele,
                # 'annee': bus.annee,  # Champ non présent dans la DB
                'statut': bus.statut,
                'kilometrage': bus.kilometrage,
                'capacite': bus.capacite,
                'carburant_actuel': bus.carburant_actuel,
                'carburant_max': bus.carburant_max,
                'date_acquisition': bus.date_acquisition,
                'date_derniere_revision': bus.date_derniere_revision
            }
            
            if include_stats:
                bus_data.update(BusService.get_bus_statistics(bus.id))
            
            result.append(bus_data)
        
        return result
    
    @staticmethod
    def get_bus_by_id(bus_id: int, include_stats: bool = False) -> Optional[Dict[str, Any]]:
        """
        Récupère un bus par son ID
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, CHAUFFEUR, MECANICIEN
        """
        bus = BusUdM.query.get(bus_id)
        if not bus:
            return None
        
        bus_data = {
            'id': bus.id,
            'numero': bus.numero,
            'immatriculation': bus.immatriculation,
            'marque': bus.marque,
            'modele': bus.modele,
            # 'annee': bus.annee,  # Champ non présent dans la DB
            'statut': bus.statut,
            'kilometrage': bus.kilometrage,
            'capacite': bus.capacite,
            'carburant_actuel': bus.carburant_actuel,
            'carburant_max': bus.carburant_max,
            'date_acquisition': bus.date_acquisition,
            'date_derniere_revision': bus.date_derniere_revision
        }
        
        if include_stats:
            bus_data.update(BusService.get_bus_statistics(bus_id))
        
        return bus_data
    
    @staticmethod
    def get_bus_statistics(bus_id: int) -> Dict[str, Any]:
        """
        Statistiques détaillées d'un bus
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        today = date.today()
        debut_mois = today.replace(day=1)
        
        # Trajets du mois
        trajets_mois = Trajet.query.filter(
            Trajet.bus_udm_id == bus_id,
            func.date(Trajet.date_heure_depart) >= debut_mois
        ).count()
        
        # Kilomètres parcourus ce mois
        km_mois = db.session.query(
            func.sum(Trajet.distance_km)
        ).filter(
            Trajet.bus_udm_id == bus_id,
            func.date(Trajet.date_heure_depart) >= debut_mois
        ).scalar() or 0
        
        # Pannes
        pannes_total = PanneBusUdM.query.filter_by(bus_udm_id=bus_id).count()
        pannes_ouvertes = PanneBusUdM.query.filter(
            PanneBusUdM.bus_udm_id == bus_id,
            PanneBusUdM.resolue == False
        ).count()
        
        # Dernière panne
        derniere_panne = PanneBusUdM.query.filter_by(
            bus_udm_id=bus_id
        ).order_by(PanneBusUdM.date_heure.desc()).first()
        
        # Dernière vidange
        derniere_vidange = Vidange.query.filter_by(
            bus_udm_id=bus_id
        ).order_by(Vidange.date_vidange.desc()).first()
        
        # Dernière carburation
        derniere_carburation = Carburation.query.filter_by(
            bus_udm_id=bus_id
        ).order_by(Carburation.date_carburation.desc()).first()
        
        # Calcul du niveau de carburant en pourcentage
        niveau_carburant = 0
        bus = BusUdM.query.get(bus_id)
        if bus and bus.carburant_max > 0:
            niveau_carburant = (bus.carburant_actuel / bus.carburant_max) * 100
        
        return {
            'trajets_mois': trajets_mois,
            'km_mois': km_mois,
            'pannes_total': pannes_total,
            'pannes_ouvertes': pannes_ouvertes,
            'niveau_carburant': round(niveau_carburant, 1),
            'derniere_panne': {
                'date': derniere_panne.date_heure if derniere_panne else None,
                'description': derniere_panne.description if derniere_panne else None,
                'criticite': derniere_panne.criticite if derniere_panne else None
            } if derniere_panne else None,
            'derniere_vidange': {
                'date': derniere_vidange.date_vidange if derniere_vidange else None,
                'kilometrage': derniere_vidange.kilometrage if derniere_vidange else None
            } if derniere_vidange else None,
            'derniere_carburation': {
                'date': derniere_carburation.date_carburation if derniere_carburation else None,
                'quantite': derniere_carburation.quantite_litres if derniere_carburation else None
            } if derniere_carburation else None
        }
    
    @staticmethod
    def get_buses_by_status(statut: str) -> List[Dict[str, Any]]:
        """
        Récupère les bus par statut
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        buses = BusUdM.query.filter_by(statut=statut).all()
        return [BusService.get_bus_by_id(bus.id) for bus in buses]
    
    @staticmethod
    def get_buses_needing_maintenance() -> List[Dict[str, Any]]:
        """
        Récupère les bus nécessitant une maintenance
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        buses_maintenance = []
        
        # Bus avec pannes ouvertes
        buses_pannes = db.session.query(BusUdM).join(PanneBusUdM).filter(
            PanneBusUdM.resolue == False
        ).distinct().all()
        
        # Bus avec carburant faible (< 20%)
        buses_carburant = BusUdM.query.filter(
            BusUdM.carburant_actuel < (BusUdM.carburant_max * 0.2)
        ).all()
        
        # Bus nécessitant une vidange (> 10000 km depuis dernière vidange)
        buses_vidange = []
        for bus in BusUdM.query.all():
            derniere_vidange = Vidange.query.filter_by(
                bus_udm_id=bus.id
            ).order_by(Vidange.kilometrage.desc()).first()
            
            if not derniere_vidange or (bus.kilometrage - derniere_vidange.kilometrage) > 10000:
                buses_vidange.append(bus)
        
        # Combiner tous les bus nécessitant une maintenance
        all_buses = set(buses_pannes + buses_carburant + buses_vidange)
        
        for bus in all_buses:
            bus_data = BusService.get_bus_by_id(bus.id, include_stats=True)
            
            # Ajouter les raisons de maintenance
            raisons = []
            if bus in buses_pannes:
                raisons.append('Panne ouverte')
            if bus in buses_carburant:
                raisons.append('Carburant faible')
            if bus in buses_vidange:
                raisons.append('Vidange nécessaire')
            
            bus_data['raisons_maintenance'] = raisons
            buses_maintenance.append(bus_data)
        
        return buses_maintenance
    
    @staticmethod
    def create_bus(bus_data: Dict[str, Any], user_id: int) -> Tuple[bool, str, Optional[int]]:
        """
        Créer un nouveau bus
        Utilisable par : ADMIN, CHARGE
        """
        try:
            bus = BusUdM(
                numero=bus_data['numero'],
                immatriculation=bus_data['immatriculation'],
                marque=bus_data['marque'],
                modele=bus_data['modele'],
                # annee=bus_data['annee'],  # Champ non présent dans la DB
                capacite=bus_data['capacite'],
                carburant_max=bus_data['carburant_max'],
                carburant_actuel=bus_data.get('carburant_actuel', 0),
                kilometrage=bus_data.get('kilometrage', 0),
                statut=bus_data.get('statut', 'ACTIF'),
                date_acquisition=bus_data.get('date_acquisition', date.today())
            )
            
            db.session.add(bus)
            db.session.commit()
            
            return True, "Bus créé avec succès", bus.id
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de la création: {str(e)}", None
    
    @staticmethod
    def update_bus(bus_id: int, bus_data: Dict[str, Any], user_id: int) -> Tuple[bool, str]:
        """
        Mettre à jour un bus
        Utilisable par : ADMIN, CHARGE
        """
        try:
            bus = BusUdM.query.get(bus_id)
            if not bus:
                return False, "Bus non trouvé"
            
            # Mettre à jour les champs modifiables
            for field in ['numero', 'immatriculation', 'marque', 'modele',
                         'capacite', 'carburant_max', 'carburant_actuel', 'kilometrage', 'statut']:
                if field in bus_data:
                    setattr(bus, field, bus_data[field])
            
            db.session.commit()
            return True, "Bus mis à jour avec succès"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    @staticmethod
    def delete_bus(bus_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Supprimer un bus
        Utilisable par : ADMIN uniquement
        """
        try:
            bus = BusUdM.query.get(bus_id)
            if not bus:
                return False, "Bus non trouvé"
            
            # Vérifier s'il y a des trajets associés
            trajets_count = Trajet.query.filter_by(bus_udm_id=bus_id).count()
            if trajets_count > 0:
                return False, f"Impossible de supprimer: {trajets_count} trajet(s) associé(s)"
            
            db.session.delete(bus)
            db.session.commit()
            return True, "Bus supprimé avec succès"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    @staticmethod
    def update_fuel_level(bus_id: int, new_level: float, user_id: int) -> Tuple[bool, str]:
        """
        Mettre à jour le niveau de carburant
        Utilisable par : ADMIN, CHARGE, CHAUFFEUR
        """
        try:
            bus = BusUdM.query.get(bus_id)
            if not bus:
                return False, "Bus non trouvé"
            
            if new_level < 0 or new_level > bus.carburant_max:
                return False, f"Niveau invalide (0-{bus.carburant_max}L)"
            
            bus.carburant_actuel = new_level
            db.session.commit()
            
            return True, "Niveau de carburant mis à jour"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur: {str(e)}"
