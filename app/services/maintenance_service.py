"""
Service de maintenance réutilisable
Gestion des pannes, vidanges et carburations pour tous les rôles
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_, or_

from app.database import db
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.vidange import Vidange
from app.models.carburation import Carburation


class MaintenanceService:
    """Service pour la gestion de la maintenance"""
    
    # ==================== PANNES ====================
    
    @staticmethod
    def get_all_pannes(limit: int = None, include_resolved: bool = True) -> List[Dict[str, Any]]:
        """
        Récupère toutes les pannes
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        query = PanneBusUdM.query
        
        if not include_resolved:
            query = query.filter_by(resolue=False)
        
        query = query.order_by(PanneBusUdM.date_heure.desc())
        
        if limit:
            query = query.limit(limit)
        
        pannes = query.all()
        
        result = []
        for panne in pannes:
            bus = BusUdM.query.get(panne.bus_udm_id)
            result.append({
                'id': panne.id,
                'bus_udm_id': panne.bus_udm_id,
                'numero_bus_udm': panne.numero_bus_udm,
                'immatriculation': panne.immatriculation,
                'bus_marque': bus.marque if bus else None,
                'bus_modele': bus.modele if bus else None,
                'kilometrage': panne.kilometrage,
                'date_heure': panne.date_heure,
                'description': panne.description,
                'criticite': panne.criticite,
                'immobilisation': panne.immobilisation,
                'enregistre_par': panne.enregistre_par,
                'resolue': panne.resolue,
                'date_resolution': panne.date_resolution
            })
        
        return result
    
    @staticmethod
    def get_pannes_by_bus(bus_id: int) -> List[Dict[str, Any]]:
        """
        Récupère les pannes d'un bus spécifique
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN, CHAUFFEUR
        """
        pannes = PanneBusUdM.query.filter_by(bus_udm_id=bus_id).order_by(
            PanneBusUdM.date_heure.desc()
        ).all()
        
        return [MaintenanceService._format_panne(panne) for panne in pannes]
    
    @staticmethod
    def get_pannes_critiques() -> List[Dict[str, Any]]:
        """
        Récupère les pannes critiques non résolues
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        pannes = PanneBusUdM.query.filter(
            PanneBusUdM.criticite == 'HAUTE',
            PanneBusUdM.resolue == False
        ).order_by(PanneBusUdM.date_heure.desc()).all()
        
        return [MaintenanceService._format_panne(panne) for panne in pannes]
    
    @staticmethod
    def create_panne(panne_data: Dict[str, Any], user_name: str) -> Tuple[bool, str, Optional[int]]:
        """
        Créer une nouvelle panne
        Utilisable par : ADMIN, CHARGE, CHAUFFEUR, MECANICIEN
        """
        try:
            # Vérifier que le bus existe
            bus = BusUdM.query.get(panne_data['bus_udm_id'])
            if not bus:
                return False, "Bus non trouvé", None
            
            panne = PanneBusUdM(
                bus_udm_id=panne_data['bus_udm_id'],
                numero_bus_udm=bus.numero,
                immatriculation=bus.immatriculation,
                kilometrage=panne_data.get('kilometrage', bus.kilometrage),
                description=panne_data['description'],
                criticite=panne_data['criticite'],
                immobilisation=panne_data.get('immobilisation', False),
                enregistre_par=user_name,
                date_heure=panne_data.get('date_heure', datetime.now())
            )
            
            db.session.add(panne)
            
            # Si immobilisation, mettre le bus en maintenance
            if panne.immobilisation:
                bus.statut = 'MAINTENANCE'
            
            db.session.commit()

            # Envoyer notification email (import local pour éviter les imports circulaires)
            try:
                from app.services.notification_service import NotificationService
                NotificationService.send_panne_notification(panne, user_name)
            except ImportError as e:
                # Import circulaire ou service non disponible
                print(f"Service de notification non disponible: {str(e)}")
            except Exception as e:
                # Ne pas faire échouer la création de panne si l'email échoue
                try:
                    from flask import current_app
                    current_app.logger.warning(f"Échec notification panne: {str(e)}")
                except:
                    print(f"Échec notification panne: {str(e)}")

            return True, "Panne enregistrée avec succès", panne.id
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de l'enregistrement: {str(e)}", None
    
    @staticmethod
    def resolve_panne(panne_id: int, user_name: str) -> Tuple[bool, str]:
        """
        Résoudre une panne
        Utilisable par : ADMIN, CHARGE, MECANICIEN
        """
        try:
            panne = PanneBusUdM.query.get(panne_id)
            if not panne:
                return False, "Panne non trouvée"
            
            if panne.resolue:
                return False, "Panne déjà résolue"
            
            panne.resolue = True
            panne.date_resolution = datetime.now()
            
            # Si c'était une immobilisation, remettre le bus en service
            if panne.immobilisation:
                bus = BusUdM.query.get(panne.bus_udm_id)
                if bus:
                    # Vérifier s'il n'y a pas d'autres pannes immobilisantes
                    autres_pannes = PanneBusUdM.query.filter(
                        PanneBusUdM.bus_udm_id == bus.id,
                        PanneBusUdM.immobilisation == True,
                        PanneBusUdM.resolue == False,
                        PanneBusUdM.id != panne_id
                    ).count()
                    
                    if autres_pannes == 0:
                        bus.statut = 'ACTIF'
            
            db.session.commit()

            # Envoyer notification email de réparation (import local pour éviter les imports circulaires)
            try:
                from app.services.notification_service import NotificationService
                NotificationService.send_vehicule_repare_notification(panne, user_name)
            except ImportError as e:
                # Import circulaire ou service non disponible
                print(f"Service de notification non disponible: {str(e)}")
            except Exception as e:
                # Ne pas faire échouer la résolution si l'email échoue
                try:
                    from flask import current_app
                    current_app.logger.warning(f"Échec notification réparation: {str(e)}")
                except:
                    print(f"Échec notification réparation: {str(e)}")

            return True, "Panne résolue avec succès"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de la résolution: {str(e)}"
    
    # ==================== VIDANGES ====================
    
    @staticmethod
    def get_all_vidanges(limit: int = None) -> List[Dict[str, Any]]:
        """
        Récupère toutes les vidanges
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        query = Vidange.query.order_by(Vidange.date_vidange.desc())
        
        if limit:
            query = query.limit(limit)
        
        vidanges = query.all()
        
        result = []
        for vidange in vidanges:
            bus = BusUdM.query.get(vidange.bus_udm_id)
            result.append({
                'id': vidange.id,
                'bus_udm_id': vidange.bus_udm_id,
                'bus_numero': bus.numero if bus else None,
                'bus_immatriculation': bus.immatriculation if bus else None,
                'date_vidange': vidange.date_vidange,
                'kilometrage': vidange.kilometrage,
                'type_huile': vidange.type_huile,
                'remarque': vidange.remarque
            })
        
        return result
    
    @staticmethod
    def get_vidanges_by_bus(bus_id: int) -> List[Dict[str, Any]]:
        """
        Récupère les vidanges d'un bus spécifique
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        vidanges = Vidange.query.filter_by(bus_udm_id=bus_id).order_by(
            Vidange.date_vidange.desc()
        ).all()
        
        return [MaintenanceService._format_vidange(vidange) for vidange in vidanges]
    
    @staticmethod
    def create_vidange(vidange_data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """
        Créer une nouvelle vidange
        Utilisable par : ADMIN, CHARGE, MECANICIEN
        """
        try:
            # Vérifier que le bus existe
            bus = BusUdM.query.get(vidange_data['bus_udm_id'])
            if not bus:
                return False, "Bus non trouvé", None
            
            vidange = Vidange(
                bus_udm_id=vidange_data['bus_udm_id'],
                date_vidange=vidange_data['date_vidange'],
                kilometrage=vidange_data['kilometrage'],
                type_huile=vidange_data['type_huile'],
                remarque=vidange_data.get('remarque', '')
            )
            
            db.session.add(vidange)
            
            # Mettre à jour la date de dernière révision du bus
            bus.date_derniere_revision = vidange_data['date_vidange']
            
            db.session.commit()
            
            return True, "Vidange enregistrée avec succès", vidange.id
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de l'enregistrement: {str(e)}", None
    
    # ==================== CARBURATIONS ====================
    
    @staticmethod
    def get_all_carburations(limit: int = None) -> List[Dict[str, Any]]:
        """
        Récupère toutes les carburations
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE
        """
        query = Carburation.query.order_by(Carburation.date_carburation.desc())
        
        if limit:
            query = query.limit(limit)
        
        carburations = query.all()
        
        result = []
        for carburation in carburations:
            bus = BusUdM.query.get(carburation.bus_udm_id)
            result.append({
                'id': carburation.id,
                'bus_udm_id': carburation.bus_udm_id,
                'bus_numero': bus.numero if bus else None,
                'bus_immatriculation': bus.immatriculation if bus else None,
                'date_carburation': carburation.date_carburation,
                'kilometrage': carburation.kilometrage,
                'quantite_litres': carburation.quantite_litres,
                'prix_unitaire': carburation.prix_unitaire,
                'cout_total': carburation.cout_total,
                'remarque': carburation.remarque
            })
        
        return result
    
    @staticmethod
    def create_carburation(carburation_data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """
        Créer une nouvelle carburation
        Utilisable par : ADMIN, CHARGE, CHAUFFEUR
        """
        try:
            # Vérifier que le bus existe
            bus = BusUdM.query.get(carburation_data['bus_udm_id'])
            if not bus:
                return False, "Bus non trouvé", None
            
            carburation = Carburation(
                bus_udm_id=carburation_data['bus_udm_id'],
                date_carburation=carburation_data['date_carburation'],
                kilometrage=carburation_data['kilometrage'],
                quantite_litres=carburation_data['quantite_litres'],
                prix_unitaire=carburation_data['prix_unitaire'],
                cout_total=carburation_data['quantite_litres'] * carburation_data['prix_unitaire'],
                remarque=carburation_data.get('remarque', '')
            )
            
            db.session.add(carburation)
            
            # Mettre à jour le niveau de carburant du bus
            nouveau_niveau = min(
                bus.carburant_actuel + carburation_data['quantite_litres'],
                bus.carburant_max
            )
            bus.carburant_actuel = nouveau_niveau
            
            db.session.commit()
            
            return True, "Carburation enregistrée avec succès", carburation.id
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erreur lors de l'enregistrement: {str(e)}", None
    
    # ==================== MÉTHODES UTILITAIRES ====================
    
    @staticmethod
    def _format_panne(panne: PanneBusUdM) -> Dict[str, Any]:
        """Formate une panne pour l'affichage"""
        bus = BusUdM.query.get(panne.bus_udm_id)
        return {
            'id': panne.id,
            'bus_udm_id': panne.bus_udm_id,
            'numero_bus_udm': panne.numero_bus_udm,
            'immatriculation': panne.immatriculation,
            'bus_marque': bus.marque if bus else None,
            'bus_modele': bus.modele if bus else None,
            'kilometrage': panne.kilometrage,
            'date_heure': panne.date_heure,
            'description': panne.description,
            'criticite': panne.criticite,
            'immobilisation': panne.immobilisation,
            'enregistre_par': panne.enregistre_par,
            'resolue': panne.resolue,
            'date_resolution': panne.date_resolution
        }
    
    @staticmethod
    def _format_vidange(vidange: Vidange) -> Dict[str, Any]:
        """Formate une vidange pour l'affichage"""
        bus = BusUdM.query.get(vidange.bus_udm_id)
        return {
            'id': vidange.id,
            'bus_udm_id': vidange.bus_udm_id,
            'bus_numero': bus.numero if bus else None,
            'bus_immatriculation': bus.immatriculation if bus else None,
            'date_vidange': vidange.date_vidange,
            'kilometrage': vidange.kilometrage,
            'type_huile': vidange.type_huile,
            'remarque': vidange.remarque
        }
