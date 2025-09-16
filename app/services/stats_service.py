"""
Service de statistiques réutilisable
Fournit des statistiques pour tous les rôles utilisateur
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import func, and_

from app.database import db
from app.models.bus_udm import BusUdM
from app.models.trajet import Trajet
from app.models.chauffeur import Chauffeur
from app.models.panne_bus_udm import PanneBusUdM
from app.models.vidange import Vidange
from app.models.carburation import Carburation


class StatsService:
    """Service pour générer des statistiques réutilisables"""
    
    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """
        Statistiques générales du tableau de bord
        Utilisable par : ADMIN, SUPERVISEUR
        """
        today = date.today()
        
        # Statistiques des bus
        bus_stats = StatsService.get_bus_stats()
        
        # Statistiques des trajets
        trajet_stats = StatsService.get_trajet_stats(today)
        
        # Statistiques de maintenance
        maintenance_stats = StatsService.get_maintenance_stats(today)
        
        # Statistiques des chauffeurs
        chauffeur_stats = StatsService.get_chauffeur_stats()
        
        return {
            **bus_stats,
            **trajet_stats,
            **maintenance_stats,
            **chauffeur_stats,
            'date_maj': datetime.now()
        }
    
    @staticmethod
    def get_bus_stats() -> Dict[str, int]:
        """Statistiques des bus"""
        return {
            'bus_total': BusUdM.query.count(),
            'bus_actifs': BusUdM.query.filter_by(statut='ACTIF').count(),
            'bus_maintenance': BusUdM.query.filter_by(statut='MAINTENANCE').count(),
            'bus_hors_service': BusUdM.query.filter_by(statut='HORS_SERVICE').count()
        }
    
    @staticmethod
    def get_trajet_stats(target_date: date = None) -> Dict[str, int]:
        """Statistiques des trajets pour une date donnée"""
        if target_date is None:
            target_date = date.today()
            
        # Trajets du jour
        trajets_jour = Trajet.query.filter(
            func.date(Trajet.date_heure_depart) == target_date
        ).count()
        
        # Trajets par type
        trajets_udm = Trajet.query.filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.type_trajet == 'UDM_INTERNE'
        ).count()
        
        trajets_prestataire = Trajet.query.filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.type_trajet == 'PRESTATAIRE'
        ).count()
        
        # Étudiants transportés
        etudiants_transportes = db.session.query(
            func.sum(Trajet.nombre_places_occupees)
        ).filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.type_passagers == 'ETUDIANT'
        ).scalar() or 0
        
        return {
            'trajets_jour': trajets_jour,
            'trajets_udm': trajets_udm,
            'trajets_prestataire': trajets_prestataire,
            'etudiants_transportes': etudiants_transportes
        }
    
    @staticmethod
    def get_maintenance_stats(target_date: date = None) -> Dict[str, int]:
        """Statistiques de maintenance"""
        if target_date is None:
            target_date = date.today()
            
        # Pannes du mois
        debut_mois = target_date.replace(day=1)
        pannes_mois = PanneBusUdM.query.filter(
            PanneBusUdM.date_heure >= debut_mois
        ).count()
        
        # Pannes non résolues
        pannes_ouvertes = PanneBusUdM.query.filter_by(resolue=False).count()
        
        # Pannes critiques
        pannes_critiques = PanneBusUdM.query.filter(
            PanneBusUdM.criticite == 'HAUTE',
            PanneBusUdM.resolue == False
        ).count()
        
        # Vidanges du mois
        vidanges_mois = Vidange.query.filter(
            Vidange.date_vidange >= debut_mois
        ).count()
        
        return {
            'pannes_mois': pannes_mois,
            'pannes_ouvertes': pannes_ouvertes,
            'pannes_critiques': pannes_critiques,
            'vidanges_mois': vidanges_mois
        }
    
    @staticmethod
    def get_chauffeur_stats() -> Dict[str, int]:
        """Statistiques des chauffeurs"""
        return {
            'chauffeurs_total': Chauffeur.query.count(),
            'chauffeurs_actifs': Chauffeur.query.filter_by(statut='ACTIF').count(),
            'chauffeurs_conge': Chauffeur.query.filter_by(statut='CONGE').count()
        }
    
    @staticmethod
    def get_monthly_trends(months: int = 6) -> Dict[str, List]:
        """
        Tendances mensuelles pour les graphiques
        Utilisable par : ADMIN, SUPERVISEUR
        """
        today = date.today()
        trends = {
            'mois': [],
            'trajets': [],
            'pannes': [],
            'etudiants': []
        }
        
        for i in range(months):
            # Calculer le mois
            if today.month - i <= 0:
                mois = today.month - i + 12
                annee = today.year - 1
            else:
                mois = today.month - i
                annee = today.year
            
            debut_mois = date(annee, mois, 1)
            if mois == 12:
                fin_mois = date(annee + 1, 1, 1) - timedelta(days=1)
            else:
                fin_mois = date(annee, mois + 1, 1) - timedelta(days=1)
            
            # Statistiques du mois
            trajets = Trajet.query.filter(
                func.date(Trajet.date_heure_depart) >= debut_mois,
                func.date(Trajet.date_heure_depart) <= fin_mois
            ).count()
            
            pannes = PanneBusUdM.query.filter(
                func.date(PanneBusUdM.date_heure) >= debut_mois,
                func.date(PanneBusUdM.date_heure) <= fin_mois
            ).count()
            
            etudiants = db.session.query(
                func.sum(Trajet.nombre_places_occupees)
            ).filter(
                func.date(Trajet.date_heure_depart) >= debut_mois,
                func.date(Trajet.date_heure_depart) <= fin_mois,
                Trajet.type_passagers == 'ETUDIANT'
            ).scalar() or 0
            
            trends['mois'].insert(0, f"{mois:02d}/{annee}")
            trends['trajets'].insert(0, trajets)
            trends['pannes'].insert(0, pannes)
            trends['etudiants'].insert(0, etudiants)
        
        return trends
    
    @staticmethod
    def get_user_specific_stats(user_role: str, user_id: int = None) -> Dict[str, Any]:
        """
        Statistiques spécifiques selon le rôle utilisateur
        """
        if user_role == 'CHAUFFEUR' and user_id:
            return StatsService._get_chauffeur_personal_stats(user_id)
        elif user_role == 'MECANICIEN':
            return StatsService._get_mecanicien_stats()
        elif user_role == 'CHARGE':
            return StatsService._get_charge_stats()
        else:
            return {}
    
    @staticmethod
    def _get_chauffeur_personal_stats(chauffeur_id: int) -> Dict[str, Any]:
        """Statistiques personnelles du chauffeur"""
        today = date.today()
        debut_mois = today.replace(day=1)
        
        # Trajets du chauffeur ce mois
        trajets_mois = Trajet.query.filter(
            Trajet.chauffeur_id == chauffeur_id,
            func.date(Trajet.date_heure_depart) >= debut_mois
        ).count()
        
        # Kilomètres parcourus
        km_mois = db.session.query(
            func.sum(Trajet.distance_km)
        ).filter(
            Trajet.chauffeur_id == chauffeur_id,
            func.date(Trajet.date_heure_depart) >= debut_mois
        ).scalar() or 0
        
        return {
            'trajets_mois': trajets_mois,
            'km_mois': km_mois,
            'trajets_aujourd_hui': Trajet.query.filter(
                Trajet.chauffeur_id == chauffeur_id,
                func.date(Trajet.date_heure_depart) == today
            ).count()
        }
    
    @staticmethod
    def _get_mecanicien_stats() -> Dict[str, Any]:
        """Statistiques pour les mécaniciens"""
        today = date.today()
        debut_mois = today.replace(day=1)
        
        return {
            'pannes_a_traiter': PanneBusUdM.query.filter_by(resolue=False).count(),
            'vidanges_mois': Vidange.query.filter(
                Vidange.date_vidange >= debut_mois
            ).count(),
            'carburations_mois': Carburation.query.filter(
                Carburation.date_carburation >= debut_mois
            ).count()
        }
    
    @staticmethod
    def _get_charge_stats() -> Dict[str, Any]:
        """Statistiques pour les chargés de transport"""
        return StatsService.get_dashboard_stats()  # Accès complet comme admin
