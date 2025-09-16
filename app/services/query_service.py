"""
Service centralisé pour les requêtes communes
Élimine la duplication de requêtes SQL dans les routes et services
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func, and_, or_

from app.database import db
from app.models.bus_udm import BusUdM
from app.models.trajet import Trajet
from app.models.chauffeur import Chauffeur
from app.models.prestataire import Prestataire
from app.models.panne_bus_udm import PanneBusUdM
from app.models.vidange import Vidange
from app.models.carburation import Carburation


class QueryService:
    """Service centralisé pour les requêtes communes réutilisables"""
    
    # ========================================
    # REQUÊTES BUS
    # ========================================
    
    @staticmethod
    def get_active_buses() -> List[BusUdM]:
        """Retourne tous les bus en bon état (inclut NULL/vide comme BON)"""
        from sqlalchemy import or_
        return BusUdM.query.filter(
            or_(
                BusUdM.etat_vehicule == 'BON',
                BusUdM.etat_vehicule.is_(None),
                BusUdM.etat_vehicule == ''
            )
        ).all()
    
    @staticmethod
    def get_all_buses() -> List[BusUdM]:
        """Retourne tous les bus"""
        return BusUdM.query.all()
    
    @staticmethod
    def get_buses_by_status(status: str) -> List[BusUdM]:
        """Retourne les bus par statut"""
        return BusUdM.query.filter_by(etat_vehicule=status).all()
    
    @staticmethod
    def get_bus_stats() -> Dict[str, int]:
        """Statistiques des bus (centralisé)"""
        return {
            'total': BusUdM.query.count(),
            'actifs': BusUdM.query.filter_by(etat_vehicule='BON').count(),
            'defaillants': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count(),
            'maintenance': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count()
        }
    
    # ========================================
    # REQUÊTES TRAJETS
    # ========================================
    
    @staticmethod
    def get_trajets_by_date(target_date: date, filters: Optional[Dict] = None) -> List[Trajet]:
        """Retourne les trajets pour une date donnée avec filtres optionnels"""
        query = Trajet.query.filter(func.date(Trajet.date_heure_depart) == target_date)
        
        if filters:
            if 'type_trajet' in filters:
                query = query.filter(Trajet.type_trajet == filters['type_trajet'])
            if 'type_passagers' in filters:
                query = query.filter(Trajet.type_passagers == filters['type_passagers'])
            if 'chauffeur_id' in filters:
                query = query.filter(Trajet.chauffeur_id == filters['chauffeur_id'])
            if 'bus_udm' in filters and filters['bus_udm']:
                query = query.filter(Trajet.numero_bus_udm != None)
            if 'prestataire' in filters and filters['prestataire']:
                query = query.filter(Trajet.immat_bus != None)
        
        return query.all()
    
    @staticmethod
    def count_trajets_by_date(target_date: date, filters: Optional[Dict] = None) -> int:
        """Compte les trajets pour une date donnée"""
        query = Trajet.query.filter(func.date(Trajet.date_heure_depart) == target_date)
        
        if filters:
            if 'bus_udm' in filters and filters['bus_udm']:
                query = query.filter(Trajet.numero_bus_udm != None)
            if 'prestataire' in filters and filters['prestataire']:
                query = query.filter(Trajet.immat_bus != None)
        
        return query.count()
    
    @staticmethod
    def get_trajet_stats_by_date(target_date: date) -> Dict[str, int]:
        """Statistiques des trajets pour une date (centralisé)"""
        return {
            'total': QueryService.count_trajets_by_date(target_date),
            'bus_udm': QueryService.count_trajets_by_date(target_date, {'bus_udm': True}),
            'prestataire': QueryService.count_trajets_by_date(target_date, {'prestataire': True}),
            'etudiants': QueryService.count_trajets_by_date(target_date, {'type_passagers': 'ETUDIANT'}),
            'personnel': QueryService.count_trajets_by_date(target_date, {'type_passagers': 'PERSONNEL'})
        }
    
    @staticmethod
    def get_student_transport_stats(target_date: date) -> Dict[str, int]:
        """Statistiques transport étudiants (centralisé)"""
        # Arrivées vers le campus
        arrives = db.session.query(func.sum(Trajet.nombre_places_occupees)).filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart.in_(['Mfetum', 'Ancienne Mairie'])
        ).scalar() or 0
        
        # Départs du campus
        partis = db.session.query(func.sum(Trajet.nombre_places_occupees)).filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart == 'Banekane'
        ).scalar() or 0
        
        return {
            'arrives': int(arrives),
            'partis': int(partis),
            'present': int(arrives - partis)
        }
    
    # ========================================
    # REQUÊTES CHAUFFEURS
    # ========================================
    
    @staticmethod
    def get_all_chauffeurs() -> List[Chauffeur]:
        """Retourne tous les chauffeurs"""
        return Chauffeur.query.all()
    
    @staticmethod
    def get_chauffeur_choices() -> List[Tuple[int, str]]:
        """Retourne les choix de chauffeurs pour les formulaires (centralisé)"""
        return [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
    
    @staticmethod
    def get_chauffeur_stats() -> Dict[str, int]:
        """Statistiques des chauffeurs"""
        return {
            'total': Chauffeur.query.count(),
            # TODO: ajouter statuts actif/congé quand disponible
        }
    
    # ========================================
    # REQUÊTES PRESTATAIRES
    # ========================================
    
    @staticmethod
    def get_all_prestataires() -> List[Prestataire]:
        """Retourne tous les prestataires"""
        return Prestataire.query.all()
    
    @staticmethod
    def get_prestataire_choices() -> List[Tuple[int, str]]:
        """Retourne les choix de prestataires pour les formulaires (centralisé)"""
        return [(p.id, p.nom_prestataire) for p in Prestataire.query.all()]
    
    # ========================================
    # REQUÊTES MAINTENANCE
    # ========================================
    
    @staticmethod
    def get_pannes_ouvertes() -> List[PanneBusUdM]:
        """Retourne les pannes non résolues"""
        return PanneBusUdM.query.filter_by(resolue=False).all()
    
    @staticmethod
    def get_pannes_critiques() -> List[PanneBusUdM]:
        """Retourne les pannes critiques non résolues"""
        return PanneBusUdM.query.filter(
            PanneBusUdM.criticite == 'HAUTE',
            PanneBusUdM.resolue == False
        ).all()
    
    @staticmethod
    def get_maintenance_stats(target_date: date) -> Dict[str, int]:
        """Statistiques de maintenance"""
        debut_mois = target_date.replace(day=1)
        
        return {
            'pannes_ouvertes': PanneBusUdM.query.filter_by(resolue=False).count(),
            'pannes_critiques': PanneBusUdM.query.filter(
                PanneBusUdM.criticite == 'HAUTE',
                PanneBusUdM.resolue == False
            ).count(),
            'pannes_mois': PanneBusUdM.query.filter(
                PanneBusUdM.date_heure >= debut_mois
            ).count(),
            'vidanges_mois': Vidange.query.filter(
                Vidange.date_vidange >= debut_mois
            ).count(),
            'carburations_mois': Carburation.query.filter(
                Carburation.date_carburation >= debut_mois
            ).count()
        }
    
    # ========================================
    # REQUÊTES COMPLEXES
    # ========================================
    
    @staticmethod
    def get_monthly_trends(months: int = 6) -> Dict[str, List]:
        """Tendances mensuelles pour les graphiques"""
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
