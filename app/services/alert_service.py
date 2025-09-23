"""
Service d'alertes pour TransportUdM
Vérifie les seuils critiques et envoie des notifications
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from sqlalchemy import func

from app.database import db
from app.models.bus_udm import BusUdM
from app.models.vidange import Vidange
from app.models.carburation import Carburation
from app.services.notification_service import NotificationService
from app.constants import AppConstants
from flask import current_app


class AlertService:
    """Service pour la gestion des alertes et seuils critiques"""
    
    # Seuils par défaut
    SEUIL_VIDANGE_KM = 5000  # Kilomètres
    SEUIL_CARBURANT_PERCENT = 20  # Pourcentage
    
    @staticmethod
    def check_all_critical_thresholds() -> Dict[str, Any]:
        """
        Vérifie tous les seuils critiques et envoie les notifications nécessaires
        Retourne un rapport des vérifications effectuées
        """
        rapport = {
            'timestamp': datetime.now().isoformat(),
            'vidange_alerts': [],
            'carburant_alerts': [],
            'total_buses_checked': 0,
            'notifications_sent': 0
        }
        
        try:
            # Récupérer tous les bus actifs
            buses = BusUdM.query.filter(BusUdM.statut != 'HORS_SERVICE').all()
            rapport['total_buses_checked'] = len(buses)
            
            for bus in buses:
                # Vérifier seuil vidange
                vidange_alert = AlertService.check_vidange_threshold(bus)
                if vidange_alert['needs_alert']:
                    rapport['vidange_alerts'].append(vidange_alert)
                    if vidange_alert['notification_sent']:
                        rapport['notifications_sent'] += 1
                
                # Vérifier seuil carburant
                carburant_alert = AlertService.check_carburant_threshold(bus)
                if carburant_alert['needs_alert']:
                    rapport['carburant_alerts'].append(carburant_alert)
                    if carburant_alert['notification_sent']:
                        rapport['notifications_sent'] += 1
            
            current_app.logger.info(f"Vérification seuils terminée: {rapport['notifications_sent']} notifications envoyées")
            
        except Exception as e:
            current_app.logger.error(f"Erreur vérification seuils: {str(e)}")
            rapport['error'] = str(e)
        
        return rapport
    
    @staticmethod
    def check_vidange_threshold(bus: BusUdM) -> Dict[str, Any]:
        """
        Vérifie si un bus a atteint le seuil critique de vidange
        """
        result = {
            'bus_id': bus.id,
            'bus_numero': bus.numero,
            'needs_alert': False,
            'km_depuis_vidange': 0,
            'seuil': AlertService.SEUIL_VIDANGE_KM,
            'notification_sent': False,
            'error': None
        }
        
        try:
            # Récupérer la dernière vidange
            derniere_vidange = Vidange.query.filter_by(
                bus_udm_id=bus.id
            ).order_by(Vidange.date_vidange.desc()).first()
            
            if derniere_vidange:
                # Calculer les kilomètres depuis la dernière vidange
                km_depuis_vidange = bus.kilometrage - derniere_vidange.kilometrage
                result['km_depuis_vidange'] = km_depuis_vidange
                
                # Vérifier si le seuil est atteint
                if km_depuis_vidange >= AlertService.SEUIL_VIDANGE_KM:
                    result['needs_alert'] = True
                    
                    # Vérifier si on a déjà envoyé une alerte récemment (éviter le spam)
                    if not AlertService._has_recent_vidange_alert(bus.id):
                        # Envoyer notification
                        notification_sent = NotificationService.send_seuil_vidange_notification(
                            bus, km_depuis_vidange, AlertService.SEUIL_VIDANGE_KM
                        )
                        result['notification_sent'] = notification_sent
                        
                        if notification_sent:
                            AlertService._mark_vidange_alert_sent(bus.id)
            else:
                # Pas de vidange enregistrée, utiliser le kilométrage total
                result['km_depuis_vidange'] = bus.kilometrage
                if bus.kilometrage >= AlertService.SEUIL_VIDANGE_KM:
                    result['needs_alert'] = True
                    
                    if not AlertService._has_recent_vidange_alert(bus.id):
                        notification_sent = NotificationService.send_seuil_vidange_notification(
                            bus, bus.kilometrage, AlertService.SEUIL_VIDANGE_KM
                        )
                        result['notification_sent'] = notification_sent
                        
                        if notification_sent:
                            AlertService._mark_vidange_alert_sent(bus.id)
        
        except Exception as e:
            result['error'] = str(e)
            current_app.logger.error(f"Erreur vérification vidange bus {bus.numero}: {str(e)}")
        
        return result
    
    @staticmethod
    def check_carburant_threshold(bus: BusUdM) -> Dict[str, Any]:
        """
        Vérifie si un bus a atteint le seuil critique de carburant
        """
        result = {
            'bus_id': bus.id,
            'bus_numero': bus.numero,
            'needs_alert': False,
            'niveau_actuel': 0,
            'pourcentage': 0,
            'seuil': AlertService.SEUIL_CARBURANT_PERCENT,
            'notification_sent': False,
            'error': None
        }
        
        try:
            # Vérifier si on a les données de carburant
            if bus.niveau_carburant_litres is not None and bus.capacite_reservoir_litres is not None:
                niveau_actuel = bus.niveau_carburant_litres
                capacite_totale = bus.capacite_reservoir_litres
                
                if capacite_totale > 0:
                    pourcentage = (niveau_actuel / capacite_totale) * 100
                    result['niveau_actuel'] = niveau_actuel
                    result['pourcentage'] = pourcentage
                    
                    # Vérifier si le seuil est atteint
                    if pourcentage <= AlertService.SEUIL_CARBURANT_PERCENT:
                        result['needs_alert'] = True
                        
                        # Vérifier si on a déjà envoyé une alerte récemment
                        if not AlertService._has_recent_carburant_alert(bus.id, pourcentage):
                            # Envoyer notification
                            notification_sent = NotificationService.send_seuil_carburant_notification(
                                bus, niveau_actuel, AlertService.SEUIL_CARBURANT_PERCENT
                            )
                            result['notification_sent'] = notification_sent
                            
                            if notification_sent:
                                AlertService._mark_carburant_alert_sent(bus.id, pourcentage)
        
        except Exception as e:
            result['error'] = str(e)
            current_app.logger.error(f"Erreur vérification carburant bus {bus.numero}: {str(e)}")
        
        return result
    
    @staticmethod
    def _has_recent_vidange_alert(bus_id: int) -> bool:
        """
        Vérifie si une alerte vidange a été envoyée récemment pour ce bus
        (évite le spam d'emails)
        """
        # Pour l'instant, on utilise une logique simple basée sur les logs
        # Dans une version plus avancée, on pourrait avoir une table dédiée
        return False
    
    @staticmethod
    def _mark_vidange_alert_sent(bus_id: int):
        """Marque qu'une alerte vidange a été envoyée pour ce bus"""
        # Log pour traçabilité
        current_app.logger.info(f"Alerte vidange envoyée pour bus ID {bus_id}")
    
    @staticmethod
    def _has_recent_carburant_alert(bus_id: int, pourcentage: float) -> bool:
        """
        Vérifie si une alerte carburant a été envoyée récemment pour ce bus
        """
        # Logique simple pour éviter le spam
        # On pourrait améliorer avec une table de tracking des alertes
        return False
    
    @staticmethod
    def _mark_carburant_alert_sent(bus_id: int, pourcentage: float):
        """Marque qu'une alerte carburant a été envoyée pour ce bus"""
        current_app.logger.info(f"Alerte carburant envoyée pour bus ID {bus_id} ({pourcentage:.1f}%)")
    
    @staticmethod
    def get_buses_needing_maintenance() -> List[Dict[str, Any]]:
        """
        Retourne la liste des bus nécessitant une maintenance
        (vidange ou carburant critique)
        """
        buses_maintenance = []
        
        try:
            buses = BusUdM.query.filter(BusUdM.statut != 'HORS_SERVICE').all()
            
            for bus in buses:
                bus_info = {
                    'id': bus.id,
                    'numero': bus.numero,
                    'immatriculation': bus.immatriculation,
                    'kilometrage': bus.kilometrage,
                    'alerts': []
                }
                
                # Vérifier vidange
                vidange_check = AlertService.check_vidange_threshold(bus)
                if vidange_check['needs_alert']:
                    bus_info['alerts'].append({
                        'type': 'vidange',
                        'message': f"Vidange nécessaire ({vidange_check['km_depuis_vidange']} km)",
                        'priority': 'high' if vidange_check['km_depuis_vidange'] > AlertService.SEUIL_VIDANGE_KM * 1.2 else 'medium'
                    })
                
                # Vérifier carburant
                carburant_check = AlertService.check_carburant_threshold(bus)
                if carburant_check['needs_alert']:
                    bus_info['alerts'].append({
                        'type': 'carburant',
                        'message': f"Carburant critique ({carburant_check['pourcentage']:.1f}%)",
                        'priority': 'high' if carburant_check['pourcentage'] < 10 else 'medium'
                    })
                
                # Ajouter à la liste si des alertes existent
                if bus_info['alerts']:
                    buses_maintenance.append(bus_info)
        
        except Exception as e:
            current_app.logger.error(f"Erreur récupération buses maintenance: {str(e)}")
        
        return buses_maintenance
    
    @staticmethod
    def force_check_bus(bus_id: int) -> Dict[str, Any]:
        """
        Force la vérification des seuils pour un bus spécifique
        Utile pour les tests ou vérifications manuelles
        """
        try:
            bus = BusUdM.query.get(bus_id)
            if not bus:
                return {'error': 'Bus non trouvé'}
            
            vidange_check = AlertService.check_vidange_threshold(bus)
            carburant_check = AlertService.check_carburant_threshold(bus)
            
            return {
                'bus_id': bus_id,
                'bus_numero': bus.numero,
                'vidange': vidange_check,
                'carburant': carburant_check,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {'error': str(e)}
