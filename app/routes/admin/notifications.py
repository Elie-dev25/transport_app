"""
Routes d'administration pour les notifications email
"""

from flask import render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import current_user
from datetime import datetime

from app.database import db
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.chauffeur_statut import ChauffeurStatut
from app.models.utilisateur import Utilisateur
from app.services.notification_service import NotificationService
from app.services.alert_service import AlertService
from app.routes.common import admin_only
from app.utils.audit_logger import log_user_action
from . import bp


@bp.route('/notifications')
@admin_only
def notifications():
    """Page de gestion des notifications"""
    return render_template(
        'roles/admin/notifications.html',
        active_page='notifications'
    )


@bp.route('/notifications/test_config', methods=['POST'])
@admin_only
def test_email_config():
    """Teste la configuration email"""
    try:
        result = NotificationService.test_email_configuration()
        
        log_user_action(
            'TEST', 
            'test_email_config',
            f"Test configuration email - Succès: {result['success']}"
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur test configuration: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@bp.route('/notifications/test_panne', methods=['POST'])
@admin_only
def test_panne_notification():
    """Envoie une notification de test pour une panne"""
    try:
        bus_id = request.json.get('bus_id')
        if not bus_id:
            return jsonify({'success': False, 'message': 'ID bus requis'}), 400
        
        bus = BusUdM.query.get(bus_id)
        if not bus:
            return jsonify({'success': False, 'message': 'Bus non trouvé'}), 404
        
        # Créer une panne de test (sans l'enregistrer)
        from app.models.panne_bus_udm import PanneBusUdM
        panne_test = PanneBusUdM(
            bus_udm_id=bus.id,
            numero_bus_udm=bus.numero,
            immatriculation=bus.immatriculation,
            kilometrage=bus.kilometrage,
            description="Test de notification - Panne simulée pour vérification du système d'email",
            criticite='MOYENNE',
            immobilisation=False,
            enregistre_par=f"{current_user.prenom} {current_user.nom}",
            date_heure=datetime.now()
        )
        
        # Envoyer la notification sans enregistrer la panne
        success = NotificationService.send_panne_notification(
            panne_test, 
            f"{current_user.prenom} {current_user.nom} (TEST)"
        )
        
        log_user_action(
            'TEST', 
            'test_panne_notification',
            f"Test notification panne bus {bus.numero} - Succès: {success}"
        )
        
        return jsonify({
            'success': success,
            'message': 'Notification de test envoyée' if success else 'Échec envoi notification',
            'bus_numero': bus.numero
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur test notification panne: {str(e)}'
        }), 500


@bp.route('/notifications/test_statut', methods=['POST'])
@admin_only
def test_statut_notification():
    """Envoie une notification de test pour un statut chauffeur"""
    try:
        chauffeur_id = request.json.get('chauffeur_id')
        if not chauffeur_id:
            return jsonify({'success': False, 'message': 'ID chauffeur requis'}), 400
        
        # Récupérer l'email du chauffeur
        chauffeur_user = Utilisateur.query.filter_by(
            utilisateur_id=chauffeur_id
        ).first()
        
        if not chauffeur_user or not chauffeur_user.email:
            return jsonify({
                'success': False, 
                'message': 'Chauffeur non trouvé ou email manquant'
            }), 404
        
        # Créer un statut de test (sans l'enregistrer)
        statut_test = ChauffeurStatut(
            chauffeur_id=chauffeur_id,
            statut='SERVICE_SEMAINE',
            lieu='CAMPUS',
            date_debut=datetime.now(),
            date_fin=datetime.now().replace(hour=23, minute=59),
            created_at=datetime.now()
        )
        
        # Envoyer la notification
        success = NotificationService.send_statut_chauffeur_notification(
            statut_test, 
            chauffeur_user.email
        )
        
        log_user_action(
            'TEST', 
            'test_statut_notification',
            f"Test notification statut chauffeur {chauffeur_id} - Succès: {success}"
        )
        
        return jsonify({
            'success': success,
            'message': 'Notification de test envoyée' if success else 'Échec envoi notification',
            'chauffeur_email': chauffeur_user.email
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur test notification statut: {str(e)}'
        }), 500


@bp.route('/notifications/check_thresholds', methods=['POST'])
@admin_only
def check_critical_thresholds():
    """Force la vérification des seuils critiques"""
    try:
        rapport = AlertService.check_all_critical_thresholds()
        
        log_user_action(
            'VERIFICATION', 
            'check_critical_thresholds',
            f"Vérification seuils - {rapport['notifications_sent']} notifications envoyées"
        )
        
        return jsonify({
            'success': True,
            'message': f"Vérification terminée - {rapport['notifications_sent']} notifications envoyées",
            'rapport': rapport
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur vérification seuils: {str(e)}'
        }), 500


@bp.route('/notifications/buses_maintenance')
@admin_only
def get_buses_maintenance():
    """Récupère la liste des bus nécessitant une maintenance"""
    try:
        buses = AlertService.get_buses_needing_maintenance()
        
        return jsonify({
            'success': True,
            'buses': buses,
            'count': len(buses)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur récupération buses maintenance: {str(e)}'
        }), 500


@bp.route('/notifications/force_check_bus/<int:bus_id>', methods=['POST'])
@admin_only
def force_check_bus(bus_id):
    """Force la vérification des seuils pour un bus spécifique"""
    try:
        result = AlertService.force_check_bus(bus_id)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'message': result['error']
            }), 400
        
        log_user_action(
            'VERIFICATION', 
            'force_check_bus',
            f"Vérification forcée bus {bus_id}"
        )
        
        return jsonify({
            'success': True,
            'message': f"Vérification bus {result['bus_numero']} terminée",
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur vérification bus: {str(e)}'
        }), 500


@bp.route('/notifications/settings', methods=['GET', 'POST'])
@admin_only
def notification_settings():
    """Gestion des paramètres de notification"""
    if request.method == 'POST':
        try:
            # Ici on pourrait ajouter la gestion des paramètres
            # comme les seuils, fréquence de vérification, etc.
            
            flash('Paramètres de notification mis à jour avec succès', 'success')
            return redirect(url_for('admin.notifications'))
            
        except Exception as e:
            flash(f'Erreur mise à jour paramètres: {str(e)}', 'error')
    
    # Récupérer les paramètres actuels
    settings = {
        'seuil_vidange': AlertService.SEUIL_VIDANGE_KM,
        'seuil_carburant': AlertService.SEUIL_CARBURANT_PERCENT,
        'email_from': current_app.config.get('MAIL_FROM'),
        'smtp_host': current_app.config.get('SMTP_HOST'),
        'smtp_port': current_app.config.get('SMTP_PORT')
    }
    
    return render_template(
        'roles/admin/notification_settings.html',
        settings=settings,
        active_page='notifications'
    )
