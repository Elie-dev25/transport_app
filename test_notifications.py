#!/usr/bin/env python3
"""
Script de test pour le système de notifications email
"""

import os
import sys
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_notification_system():
    """Test complet du système de notifications"""
    print("🔔 TEST DU SYSTÈME DE NOTIFICATIONS EMAIL")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.database import db
        from app.models.bus_udm import BusUdM
        from app.models.panne_bus_udm import PanneBusUdM
        from app.models.utilisateur import Utilisateur
        from app.models.chauffeur_statut import ChauffeurStatut
        from app.services.notification_service import NotificationService
        from app.services.alert_service import AlertService
        
        app = create_app()
        
        with app.app_context():
            print("\n1. 📧 Test de configuration email...")
            config_result = NotificationService.test_email_configuration()
            print(f"   Configuration: {'✅ OK' if config_result['success'] else '❌ ERREUR'}")
            if not config_result['success']:
                print(f"   Erreur: {config_result['message']}")
                return False
            
            print("\n2. 🚌 Test notification panne...")
            # Récupérer un bus pour le test
            bus = BusUdM.query.first()
            if bus:
                # Créer une panne de test
                panne_test = PanneBusUdM(
                    bus_udm_id=bus.id,
                    numero_bus_udm=bus.numero,
                    immatriculation=bus.immatriculation,
                    kilometrage=bus.kilometrage,
                    description="Test automatique - Panne simulée pour vérification du système",
                    criticite='HAUTE',
                    immobilisation=True,
                    enregistre_par="Script de test",
                    date_heure=datetime.now()
                )
                
                # Test notification panne
                panne_success = NotificationService.send_panne_notification(
                    panne_test, "Script de test automatique"
                )
                print(f"   Notification panne: {'✅ Envoyée' if panne_success else '❌ Échec'}")
                
                # Test notification réparation
                panne_test.resolue = True
                panne_test.date_resolution = datetime.now()
                repair_success = NotificationService.send_vehicule_repare_notification(
                    panne_test, "Script de test automatique"
                )
                print(f"   Notification réparation: {'✅ Envoyée' if repair_success else '❌ Échec'}")
            else:
                print("   ❌ Aucun bus trouvé pour le test")
            
            print("\n3. 👨‍💼 Test notification statut chauffeur...")
            # Récupérer un utilisateur chauffeur
            chauffeur_user = Utilisateur.query.filter_by(role='CHAUFFEUR').first()
            if chauffeur_user and chauffeur_user.email:
                # Créer un statut de test
                statut_test = ChauffeurStatut(
                    chauffeur_id=chauffeur_user.utilisateur_id,
                    statut='SERVICE_SEMAINE',
                    lieu='CAMPUS',
                    date_debut=datetime.now(),
                    date_fin=datetime.now() + timedelta(days=1),
                    created_at=datetime.now()
                )
                
                statut_success = NotificationService.send_statut_chauffeur_notification(
                    statut_test, chauffeur_user.email
                )
                print(f"   Notification statut: {'✅ Envoyée' if statut_success else '❌ Échec'}")
                print(f"   Email destinataire: {chauffeur_user.email}")
            else:
                print("   ❌ Aucun chauffeur avec email trouvé pour le test")
            
            print("\n4. ⚠️ Test vérification seuils critiques...")
            # Test des seuils
            if bus:
                # Test seuil vidange
                vidange_result = AlertService.check_vidange_threshold(bus)
                print(f"   Vérification vidange: {'✅ OK' if not vidange_result.get('error') else '❌ Erreur'}")
                if vidange_result['needs_alert']:
                    print(f"   ⚠️ Alerte vidange nécessaire: {vidange_result['km_depuis_vidange']} km")
                
                # Test seuil carburant
                carburant_result = AlertService.check_carburant_threshold(bus)
                print(f"   Vérification carburant: {'✅ OK' if not carburant_result.get('error') else '❌ Erreur'}")
                if carburant_result['needs_alert']:
                    print(f"   ⚠️ Alerte carburant nécessaire: {carburant_result['pourcentage']:.1f}%")
            
            print("\n5. 📊 Test vérification globale...")
            rapport = AlertService.check_all_critical_thresholds()
            print(f"   Bus vérifiés: {rapport['total_buses_checked']}")
            print(f"   Alertes vidange: {len(rapport['vidange_alerts'])}")
            print(f"   Alertes carburant: {len(rapport['carburant_alerts'])}")
            print(f"   Notifications envoyées: {rapport['notifications_sent']}")
            
            print("\n6. 🔍 Test buses nécessitant maintenance...")
            buses_maintenance = AlertService.get_buses_needing_maintenance()
            print(f"   Buses nécessitant maintenance: {len(buses_maintenance)}")
            for bus_info in buses_maintenance[:3]:  # Afficher les 3 premiers
                print(f"   - Bus {bus_info['numero']}: {len(bus_info['alerts'])} alerte(s)")
            
            print("\n" + "=" * 60)
            print("✅ TESTS TERMINÉS AVEC SUCCÈS")
            print("\n💡 Points à vérifier:")
            print("   - Vérifiez votre boîte email pour les notifications de test")
            print("   - Configurez les variables d'environnement SMTP si nécessaire")
            print("   - Les notifications sont automatiques lors des événements réels")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_email_configuration_only():
    """Test uniquement la configuration email"""
    print("📧 TEST DE CONFIGURATION EMAIL UNIQUEMENT")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.services.notification_service import NotificationService
        
        app = create_app()
        
        with app.app_context():
            result = NotificationService.test_email_configuration()
            
            print(f"Statut: {'✅ Succès' if result['success'] else '❌ Échec'}")
            print(f"Message: {result['message']}")
            if result.get('test_email'):
                print(f"Email de test envoyé à: {result['test_email']}")
            print(f"Timestamp: {result['timestamp']}")
            
            # Afficher la configuration actuelle
            print("\n📋 Configuration actuelle:")
            print(f"   SMTP_HOST: {app.config.get('SMTP_HOST')}")
            print(f"   SMTP_PORT: {app.config.get('SMTP_PORT')}")
            print(f"   SMTP_USERNAME: {app.config.get('SMTP_USERNAME')}")
            print(f"   SMTP_USE_TLS: {app.config.get('SMTP_USE_TLS')}")
            print(f"   MAIL_FROM: {app.config.get('MAIL_FROM')}")
            
            return result['success']
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def show_configuration_help():
    """Affiche l'aide pour la configuration"""
    print("🔧 AIDE À LA CONFIGURATION EMAIL")
    print("=" * 50)
    print("""
Pour configurer les notifications email, définissez ces variables d'environnement :

Windows (PowerShell):
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="elienjine15@gmail.com"
$env:SMTP_PASSWORD="votre_mot_de_passe_app"
$env:SMTP_USE_TLS="true"
$env:MAIL_FROM="elienjine15@gmail.com"

Linux/Mac (Bash):
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="elienjine15@gmail.com"
export SMTP_PASSWORD="votre_mot_de_passe_app"
export SMTP_USE_TLS="true"
export MAIL_FROM="elienjine15@gmail.com"

⚠️ IMPORTANT pour Gmail:
1. Activez l'authentification à 2 facteurs
2. Générez un "mot de passe d'application" 
3. Utilisez ce mot de passe d'application (pas votre mot de passe Gmail)

📧 Types de notifications automatiques:
• Déclaration de panne → Mécanicien, Superviseur, Responsable
• Véhicule réparé → Responsable, Superviseur  
• Seuil vidange critique → Responsable, Superviseur
• Seuil carburant critique → Responsable, Chauffeur, Superviseur
• Affectation statut chauffeur → Chauffeur concerné
    """)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "config":
            test_email_configuration_only()
        elif sys.argv[1] == "help":
            show_configuration_help()
        else:
            print("Usage: python test_notifications.py [config|help]")
    else:
        test_notification_system()
