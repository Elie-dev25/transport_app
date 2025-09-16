"""
Service centralisé pour les statistiques de dashboard
Élimine la duplication de code entre admin, charge_transport, chauffeur et superviseur
"""

from datetime import date, datetime
from typing import Dict, Any, Optional
from sqlalchemy import func

from app.database import db
from app.models.bus_udm import BusUdM
from app.models.trajet import Trajet
from app.models.chauffeur import Chauffeur
from app.models.prestataire import Prestataire
from app.utils.trafic import daily_student_trafic


class DashboardService:
    """Service centralisé pour générer les statistiques de dashboard"""
    
    @staticmethod
    def get_common_stats(target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Statistiques communes à tous les dashboards
        Remplace le code dupliqué dans 4+ fichiers
        """
        if target_date is None:
            target_date = date.today()
        
        # Statistiques des trajets (code dupliqué éliminé)
        trajets_jour_aed = Trajet.query.filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.numero_bus_udm != None
        ).count()
        
        trajets_jour_prestataire = Trajet.query.filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.immat_bus != None
        ).count()
        
        # Statistiques des bus (code dupliqué éliminé)
        bus_actifs = BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count()
        bus_maintenance = BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count()
        
        # Calcul des étudiants présents (code dupliqué éliminé)
        etudiants_stats = DashboardService._calculate_student_presence(target_date)
        
        # Trafic temps réel
        trafic = daily_student_trafic(target_date)
        
        return {
            # Statistiques bus
            'bus_actifs': bus_actifs,
            'bus_actifs_change': 0,  # TODO: calculer le changement
            'bus_inactifs': bus_maintenance,
            'bus_maintenance': bus_maintenance,
            
            # Statistiques trajets
            'trajets_jour_aed': trajets_jour_aed,
            'trajets_jour_bus_agence': trajets_jour_prestataire,
            'trajets_jour_prestataire': trajets_jour_prestataire,
            'trajets_jour_change': 0,  # TODO: calculer le changement
            
            # Statistiques chauffeurs
            'chauffeurs': Chauffeur.query.count(),
            'chauffeurs_disponibles': Chauffeur.query.count(),  # TODO: affiner
            
            # Statistiques étudiants
            'etudiants': etudiants_stats['present'],
            'etudiants_arrives': etudiants_stats['arrives'],
            'etudiants_partis': etudiants_stats['partis'],
            
            # Trafic temps réel
            'trafic': trafic,
            
            # Métadonnées
            'date_maj': datetime.now(),
            'target_date': target_date
        }
    
    @staticmethod
    def get_role_specific_stats(role: str, user_id: Optional[int] = None, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Statistiques spécifiques selon le rôle utilisateur
        """
        if target_date is None:
            target_date = date.today()
            
        if role == 'CHAUFFEUR' and user_id:
            return DashboardService._get_chauffeur_personal_stats(user_id, target_date)
        elif role == 'MECANICIEN':
            return DashboardService._get_mecanicien_stats(target_date)
        elif role == 'CHARGE':
            return DashboardService._get_charge_transport_stats(target_date)
        elif role in ['ADMIN', 'SUPERVISEUR', 'RESPONSABLE']:
            return DashboardService._get_admin_stats(target_date)
        else:
            return {}
    
    @staticmethod
    def _calculate_student_presence(target_date: date) -> Dict[str, int]:
        """
        Calcule la présence étudiante (code dupliqué éliminé)
        """
        # Arrivées : départs depuis Mfetum/Ancienne mairie vers le campus
        arrives = db.session.query(func.sum(Trajet.nombre_places_occupees)).filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart.in_(['Mfetum', 'Ancienne Mairie'])
        ).scalar() or 0
        
        # Départs : départs depuis Banekane (campus) vers l'extérieur
        partis = db.session.query(func.sum(Trajet.nombre_places_occupees)).filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart == 'Banekane'
        ).scalar() or 0
        
        present = arrives - partis
        
        return {
            'arrives': int(arrives),
            'partis': int(partis),
            'present': int(present)
        }
    
    @staticmethod
    def _get_chauffeur_personal_stats(chauffeur_user_id: int, target_date: date) -> Dict[str, Any]:
        """Statistiques personnelles du chauffeur connecté"""
        from app.models.chauffeur import Chauffeur
        
        # Trouver le chauffeur correspondant à l'utilisateur
        from app.models.utilisateur import Utilisateur
        user = Utilisateur.query.get(chauffeur_user_id)
        if not user:
            return {}
            
        chauffeur_db = Chauffeur.query.filter_by(nom=user.nom, prenom=user.prenom).first()
        if not chauffeur_db:
            return {
                'mes_trajets_aujourdhui': 0,
                'etudiants_pour_campus': 0,
                'personnes_du_campus': 0
            }
        
        chauffeur_id = chauffeur_db.chauffeur_id
        
        # Mes trajets aujourd'hui
        mes_trajets_aujourdhui = Trajet.query.filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.chauffeur_id == chauffeur_id
        ).count()
        
        # Étudiants transportés POUR le campus
        etudiants_pour_campus = db.session.query(
            func.sum(Trajet.nombre_places_occupees)
        ).filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.chauffeur_id == chauffeur_id,
            Trajet.point_arriver == 'Banekane'  # Arrivée au campus
        ).scalar() or 0
        
        # Personnes transportées DU campus
        personnes_du_campus = db.session.query(
            func.sum(Trajet.nombre_places_occupees)
        ).filter(
            func.date(Trajet.date_heure_depart) == target_date,
            Trajet.chauffeur_id == chauffeur_id,
            Trajet.point_depart == 'Banekane'  # Départ du campus
        ).scalar() or 0
        
        return {
            'mes_trajets_aujourdhui': mes_trajets_aujourdhui,
            'etudiants_pour_campus': int(etudiants_pour_campus),
            'personnes_du_campus': int(personnes_du_campus)
        }
    
    @staticmethod
    def _get_mecanicien_stats(target_date: date) -> Dict[str, Any]:
        """Statistiques pour les mécaniciens"""
        from app.models.panne_bus_udm import PanneBusUdM
        from app.models.vidange import Vidange
        from app.models.carburation import Carburation
        
        debut_mois = target_date.replace(day=1)
        
        return {
            'pannes_a_traiter': PanneBusUdM.query.filter_by(resolue=False).count(),
            'pannes_critiques': PanneBusUdM.query.filter(
                PanneBusUdM.criticite == 'HAUTE',
                PanneBusUdM.resolue == False
            ).count(),
            'vidanges_mois': Vidange.query.filter(
                Vidange.date_vidange >= debut_mois
            ).count(),
            'carburations_mois': Carburation.query.filter(
                Carburation.date_carburation >= debut_mois
            ).count()
        }
    
    @staticmethod
    def _get_charge_transport_stats(target_date: date) -> Dict[str, Any]:
        """Statistiques pour les chargés de transport"""
        # Accès complet comme admin
        return {}
    
    @staticmethod
    def _get_admin_stats(target_date: date) -> Dict[str, Any]:
        """Statistiques pour les administrateurs et superviseurs"""
        return {
            'prestataires_actifs': Prestataire.query.count(),
            # Autres stats spécifiques admin
        }
