"""
Service de notifications par email pour TransportUdM
Gère l'envoi d'emails pour les événements critiques du système
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from flask import current_app

from app.database import db
from app.models.utilisateur import Utilisateur
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.chauffeur_statut import ChauffeurStatut
from app.utils.emailer import send_email
from app.utils.audit_logger import log_user_action


class NotificationService:
    """Service centralisé pour les notifications par email"""
    
    # Configuration des destinataires par type de notification
    NOTIFICATION_RECIPIENTS = {
        'PANNE_DECLAREE': ['MECANICIEN', 'SUPERVISEUR', 'RESPONSABLE'],
        'VEHICULE_REPARE': ['RESPONSABLE', 'SUPERVISEUR'],
        'SEUIL_VIDANGE': ['RESPONSABLE', 'SUPERVISEUR'],
        'SEUIL_CARBURANT': ['RESPONSABLE', 'CHAUFFEUR', 'SUPERVISEUR'],
        'STATUT_CHAUFFEUR': ['CHAUFFEUR']  # Le chauffeur concerné uniquement
    }
    
    @staticmethod
    def get_users_by_roles(roles: List[str]) -> List[Utilisateur]:
        """Récupère les utilisateurs ayant les rôles spécifiés"""
        return Utilisateur.query.filter(Utilisateur.role.in_(roles)).all()
    
    @staticmethod
    def send_panne_notification(panne: PanneBusUdM, declared_by: str) -> bool:
        """
        Envoie une notification lors de la déclaration d'une panne
        Destinataires: MECANICIEN, SUPERVISEUR, RESPONSABLE
        """
        try:
            # Récupérer les destinataires
            recipients = NotificationService.get_users_by_roles(
                NotificationService.NOTIFICATION_RECIPIENTS['PANNE_DECLAREE']
            )
            
            if not recipients:
                current_app.logger.warning("Aucun destinataire trouvé pour notification panne")
                return False
            
            # Récupérer les informations du bus
            bus = BusUdM.query.get(panne.bus_udm_id)
            bus_info = f"Bus {bus.numero} ({bus.immatriculation})" if bus else f"Bus ID {panne.bus_udm_id}"
            
            # Préparer le contenu de l'email
            subject = f"🚨 Nouvelle panne déclarée - {bus_info}"
            
            body = f"""
Bonjour,

Une nouvelle panne a été déclarée dans le système TransportUdM.

📋 DÉTAILS DE LA PANNE:
• Véhicule: {bus_info}
• Date/Heure: {panne.date_heure.strftime('%d/%m/%Y à %H:%M')}
• Kilométrage: {panne.kilometrage:,} km
• Criticité: {panne.criticite}
• Immobilisation: {'Oui' if panne.immobilisation else 'Non'}
• Déclarée par: {declared_by}

📝 DESCRIPTION:
{panne.description}

{'⚠️ ATTENTION: Ce véhicule est immobilisé et ne peut pas être utilisé.' if panne.immobilisation else ''}

Veuillez prendre les mesures nécessaires pour traiter cette panne.

---
Système TransportUdM - Université des Montagnes
Notification automatique - Ne pas répondre à cet email
            """.strip()
            
            # Envoyer l'email à tous les destinataires
            success_count = 0
            for user in recipients:
                if user.email:
                    if send_email(subject, body, user.email):
                        success_count += 1
                        current_app.logger.info(f"Notification panne envoyée à {user.email}")
                    else:
                        current_app.logger.error(f"Échec envoi notification panne à {user.email}")
            
            # Log de l'action
            log_user_action(
                'NOTIFICATION', 
                'send_panne_notification',
                f"Panne {panne.id} - {success_count}/{len(recipients)} emails envoyés"
            )
            
            return success_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Erreur notification panne: {str(e)}")
            return False
    
    @staticmethod
    def send_vehicule_repare_notification(panne: PanneBusUdM, repaired_by: str) -> bool:
        """
        Envoie une notification lorsqu'un véhicule est réparé
        Destinataires: RESPONSABLE, SUPERVISEUR
        """
        try:
            # Récupérer les destinataires
            recipients = NotificationService.get_users_by_roles(
                NotificationService.NOTIFICATION_RECIPIENTS['VEHICULE_REPARE']
            )
            
            if not recipients:
                current_app.logger.warning("Aucun destinataire trouvé pour notification réparation")
                return False
            
            # Récupérer les informations du bus
            bus = BusUdM.query.get(panne.bus_udm_id)
            bus_info = f"Bus {bus.numero} ({bus.immatriculation})" if bus else f"Bus ID {panne.bus_udm_id}"
            
            # Préparer le contenu de l'email
            subject = f"✅ Véhicule réparé - {bus_info}"
            
            body = f"""
Bonjour,

Un véhicule a été réparé et est de nouveau opérationnel.

📋 DÉTAILS DE LA RÉPARATION:
• Véhicule: {bus_info}
• Panne déclarée le: {panne.date_heure.strftime('%d/%m/%Y à %H:%M')}
• Réparation terminée le: {panne.date_resolution.strftime('%d/%m/%Y à %H:%M')}
• Réparé par: {repaired_by}
• Criticité initiale: {panne.criticite}

📝 DESCRIPTION DE LA PANNE:
{panne.description}

✅ Le véhicule est maintenant disponible pour les trajets.

---
Système TransportUdM - Université des Montagnes
Notification automatique - Ne pas répondre à cet email
            """.strip()
            
            # Envoyer l'email à tous les destinataires
            success_count = 0
            for user in recipients:
                if user.email:
                    if send_email(subject, body, user.email):
                        success_count += 1
                        current_app.logger.info(f"Notification réparation envoyée à {user.email}")
                    else:
                        current_app.logger.error(f"Échec envoi notification réparation à {user.email}")
            
            # Log de l'action
            log_user_action(
                'NOTIFICATION', 
                'send_vehicule_repare_notification',
                f"Réparation panne {panne.id} - {success_count}/{len(recipients)} emails envoyés"
            )
            
            return success_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Erreur notification réparation: {str(e)}")
            return False
    
    @staticmethod
    def send_seuil_vidange_notification(bus: BusUdM, km_depuis_vidange: int, seuil: int) -> bool:
        """
        Envoie une notification lorsqu'un véhicule atteint le seuil critique de vidange
        Destinataires: RESPONSABLE, SUPERVISEUR
        """
        try:
            # Récupérer les destinataires
            recipients = NotificationService.get_users_by_roles(
                NotificationService.NOTIFICATION_RECIPIENTS['SEUIL_VIDANGE']
            )
            
            if not recipients:
                current_app.logger.warning("Aucun destinataire trouvé pour notification vidange")
                return False
            
            # Préparer le contenu de l'email
            subject = f"🔧 Seuil vidange atteint - Bus {bus.numero}"
            
            body = f"""
Bonjour,

Un véhicule a atteint le seuil critique pour la vidange.

📋 DÉTAILS DU VÉHICULE:
• Véhicule: Bus {bus.numero} ({bus.immatriculation})
• Kilométrage actuel: {bus.kilometrage:,} km
• Kilomètres depuis dernière vidange: {km_depuis_vidange:,} km
• Seuil critique: {seuil:,} km
• Dépassement: {km_depuis_vidange - seuil:,} km

⚠️ ATTENTION: Ce véhicule nécessite une vidange urgente.

Veuillez programmer une intervention de maintenance dans les plus brefs délais.

---
Système TransportUdM - Université des Montagnes
Notification automatique - Ne pas répondre à cet email
            """.strip()
            
            # Envoyer l'email à tous les destinataires
            success_count = 0
            for user in recipients:
                if user.email:
                    if send_email(subject, body, user.email):
                        success_count += 1
                        current_app.logger.info(f"Notification vidange envoyée à {user.email}")
                    else:
                        current_app.logger.error(f"Échec envoi notification vidange à {user.email}")
            
            # Log de l'action
            log_user_action(
                'NOTIFICATION', 
                'send_seuil_vidange_notification',
                f"Bus {bus.numero} - {success_count}/{len(recipients)} emails envoyés"
            )
            
            return success_count > 0

        except Exception as e:
            current_app.logger.error(f"Erreur notification vidange: {str(e)}")
            return False

    @staticmethod
    def send_seuil_carburant_notification(bus: BusUdM, niveau_actuel: float, seuil: float) -> bool:
        """
        Envoie une notification lorsqu'un véhicule atteint le seuil critique de carburant
        Destinataires: RESPONSABLE, CHAUFFEUR, SUPERVISEUR
        """
        try:
            # Récupérer les destinataires
            recipients = NotificationService.get_users_by_roles(
                NotificationService.NOTIFICATION_RECIPIENTS['SEUIL_CARBURANT']
            )

            if not recipients:
                current_app.logger.warning("Aucun destinataire trouvé pour notification carburant")
                return False

            # Calculer le pourcentage
            pourcentage = (niveau_actuel / bus.capacite_reservoir_litres * 100) if bus.capacite_reservoir_litres else 0

            # Préparer le contenu de l'email
            subject = f"⛽ Seuil carburant critique - Bus {bus.numero}"

            body = f"""
Bonjour,

Un véhicule a atteint le seuil critique de carburant.

📋 DÉTAILS DU VÉHICULE:
• Véhicule: Bus {bus.numero} ({bus.immatriculation})
• Niveau actuel: {niveau_actuel:.1f} L ({pourcentage:.1f}%)
• Capacité totale: {bus.capacite_reservoir_litres:.1f} L
• Seuil critique: {seuil:.1f}%
• Kilométrage: {bus.kilometrage:,} km

⚠️ ATTENTION: Ce véhicule nécessite un ravitaillement urgent.

Veuillez procéder au ravitaillement avant le prochain trajet.

---
Système TransportUdM - Université des Montagnes
Notification automatique - Ne pas répondre à cet email
            """.strip()

            # Envoyer l'email à tous les destinataires
            success_count = 0
            for user in recipients:
                if user.email:
                    if send_email(subject, body, user.email):
                        success_count += 1
                        current_app.logger.info(f"Notification carburant envoyée à {user.email}")
                    else:
                        current_app.logger.error(f"Échec envoi notification carburant à {user.email}")

            # Log de l'action
            log_user_action(
                'NOTIFICATION',
                'send_seuil_carburant_notification',
                f"Bus {bus.numero} - {success_count}/{len(recipients)} emails envoyés"
            )

            return success_count > 0

        except Exception as e:
            current_app.logger.error(f"Erreur notification carburant: {str(e)}")
            return False

    @staticmethod
    def send_statut_chauffeur_notification(chauffeur_statut: ChauffeurStatut, chauffeur_email: str) -> bool:
        """
        Envoie une notification au chauffeur lors de l'affectation d'un statut
        Destinataire: Le chauffeur concerné uniquement
        """
        try:
            if not chauffeur_email:
                current_app.logger.warning("Email chauffeur manquant pour notification statut")
                return False

            # Récupérer les informations du chauffeur
            from app.models.chauffeur import Chauffeur
            chauffeur = Chauffeur.query.get(chauffeur_statut.chauffeur_id)
            chauffeur_nom = f"{chauffeur.prenom} {chauffeur.nom}" if chauffeur else f"Chauffeur ID {chauffeur_statut.chauffeur_id}"

            # Mapper les statuts en français
            statuts_fr = {
                'CONGE': 'Congé',
                'PERMANENCE': 'Permanence',
                'SERVICE_WEEKEND': 'Service Weekend',
                'SERVICE_SEMAINE': 'Service Semaine'
            }

            lieux_fr = {
                'CUM': 'CUM (Centre Urbain de Mbouda)',
                'CAMPUS': 'Campus Universitaire',
                'CONJOINTEMENT': 'CUM et Campus (Conjointement)'
            }

            statut_fr = statuts_fr.get(chauffeur_statut.statut, chauffeur_statut.statut)
            lieu_fr = lieux_fr.get(chauffeur_statut.lieu, chauffeur_statut.lieu)

            # Préparer le contenu de l'email
            subject = f"📋 Nouveau statut affecté - {statut_fr}"

            body = f"""
Bonjour {chauffeur_nom},

Un nouveau statut vous a été affecté dans le système TransportUdM.

📋 DÉTAILS DE VOTRE AFFECTATION:
• Statut: {statut_fr}
• Lieu d'affectation: {lieu_fr}
• Date de début: {chauffeur_statut.date_debut.strftime('%d/%m/%Y à %H:%M')}
• Date de fin: {chauffeur_statut.date_fin.strftime('%d/%m/%Y à %H:%M')}
• Affecté le: {chauffeur_statut.created_at.strftime('%d/%m/%Y à %H:%M')}

📝 INSTRUCTIONS:
{NotificationService._get_statut_instructions(chauffeur_statut.statut, chauffeur_statut.lieu)}

Pour toute question concernant votre affectation, veuillez contacter votre responsable.

---
Système TransportUdM - Université des Montagnes
Notification automatique - Ne pas répondre à cet email
            """.strip()

            # Envoyer l'email
            if send_email(subject, body, chauffeur_email):
                current_app.logger.info(f"Notification statut envoyée à {chauffeur_email}")

                # Log de l'action
                log_user_action(
                    'NOTIFICATION',
                    'send_statut_chauffeur_notification',
                    f"Statut {chauffeur_statut.statut} chauffeur {chauffeur_statut.chauffeur_id} - Email envoyé"
                )

                return True
            else:
                current_app.logger.error(f"Échec envoi notification statut à {chauffeur_email}")
                return False

        except Exception as e:
            current_app.logger.error(f"Erreur notification statut chauffeur: {str(e)}")
            return False

    @staticmethod
    def _get_statut_instructions(statut: str, lieu: str) -> str:
        """Retourne les instructions spécifiques selon le statut et le lieu"""
        instructions = {
            'CONGE': "Vous êtes en congé. Profitez bien de votre repos !",
            'PERMANENCE': "Vous êtes de permanence. Restez disponible pour les urgences et interventions.",
            'SERVICE_WEEKEND': "Vous êtes affecté au service weekend. Assurez-vous d'être disponible samedi et dimanche.",
            'SERVICE_SEMAINE': "Vous êtes affecté au service semaine. Assurez-vous d'être disponible du lundi au vendredi."
        }

        base_instruction = instructions.get(statut, "Veuillez vous conformer à votre affectation.")

        if lieu == 'CUM':
            lieu_instruction = "Votre lieu d'affectation est le Centre Urbain de Mbouda (CUM)."
        elif lieu == 'CAMPUS':
            lieu_instruction = "Votre lieu d'affectation est le Campus Universitaire."
        elif lieu == 'CONJOINTEMENT':
            lieu_instruction = "Vous devez assurer le service entre le CUM et le Campus selon les besoins."
        else:
            lieu_instruction = ""

        return f"{base_instruction}\n{lieu_instruction}".strip()

    @staticmethod
    def test_email_configuration() -> Dict[str, Any]:
        """
        Teste la configuration email en envoyant un email de test
        Retourne un dictionnaire avec le statut du test
        """
        try:
            test_email = current_app.config.get('MAIL_FROM', 'elienjine15@gmail.com')
            subject = "Test de configuration email - TransportUdM"
            body = f"""
Test de configuration email réussi !

Configuration actuelle:
• SMTP Host: {current_app.config.get('SMTP_HOST')}
• SMTP Port: {current_app.config.get('SMTP_PORT')}
• From: {current_app.config.get('MAIL_FROM')}
• TLS: {current_app.config.get('SMTP_USE_TLS')}

Date du test: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}

---
Système TransportUdM - Test automatique
            """.strip()

            success = send_email(subject, body, test_email)

            return {
                'success': success,
                'message': 'Email de test envoyé avec succès' if success else 'Échec envoi email de test',
                'test_email': test_email,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur test email: {str(e)}',
                'test_email': None,
                'timestamp': datetime.now().isoformat()
            }
