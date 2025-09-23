#!/usr/bin/env python3
"""
Script pour vérifier les adresses email des utilisateurs
"""

import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_user_emails():
    """Vérifier les emails des utilisateurs dans la base"""
    print("📧 VÉRIFICATION DES EMAILS UTILISATEURS")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.database import db
        from app.models.utilisateur import Utilisateur
        
        app = create_app()
        
        with app.app_context():
            print("\n1. 👥 Utilisateurs par rôle avec emails:")
            
            roles = ['MECANICIEN', 'SUPERVISEUR', 'RESPONSABLE', 'CHAUFFEUR', 'ADMIN']
            
            for role in roles:
                users = Utilisateur.query.filter_by(role=role).all()
                print(f"\n   {role}:")
                
                if not users:
                    print(f"      Aucun utilisateur {role}")
                else:
                    for user in users:
                        email = getattr(user, 'email', 'PAS D\'EMAIL')
                        nom_complet = f"{getattr(user, 'nom', '')} {getattr(user, 'prenom', '')}".strip()
                        if not nom_complet:
                            nom_complet = getattr(user, 'login', 'Inconnu')
                        
                        print(f"      - {nom_complet}: {email}")
            
            print("\n2. 🔍 Recherche d'emails contenant 'elienjine':")
            users_elienjine = Utilisateur.query.filter(
                Utilisateur.email.like('%elienjine%')
            ).all()
            
            if users_elienjine:
                for user in users_elienjine:
                    print(f"   - {user.nom} {user.prenom} ({user.role}): {user.email}")
            else:
                print("   Aucun utilisateur avec email contenant 'elienjine'")
            
            print("\n3. ⚙️ Configuration SMTP actuelle:")
            print(f"   SMTP_HOST: {app.config.get('SMTP_HOST', 'Non configuré')}")
            print(f"   SMTP_PORT: {app.config.get('SMTP_PORT', 'Non configuré')}")
            print(f"   SMTP_USERNAME: {app.config.get('SMTP_USERNAME', 'Non configuré')}")
            print(f"   MAIL_FROM: {app.config.get('MAIL_FROM', 'Non configuré')}")
            print(f"   SMTP_USE_TLS: {app.config.get('SMTP_USE_TLS', 'Non configuré')}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_config():
    """Tester la configuration des notifications"""
    print("\n📬 TEST CONFIGURATION NOTIFICATIONS")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.services.notification_service import NotificationService
        
        app = create_app()
        
        with app.app_context():
            # Test de configuration
            result = NotificationService.test_email_configuration()
            
            print(f"Statut: {'✅ Succès' if result['success'] else '❌ Échec'}")
            print(f"Message: {result['message']}")
            if result.get('test_email'):
                print(f"Email de test: {result['test_email']}")
            
            return result['success']
            
    except Exception as e:
        print(f"❌ Erreur test notifications: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSTIC EMAIL ET NOTIFICATIONS")
    print("=" * 60)
    
    emails_ok = check_user_emails()
    config_ok = test_notification_config()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    print(f"Emails utilisateurs: {'✅ OK' if emails_ok else '❌ Problème'}")
    print(f"Configuration SMTP: {'✅ OK' if config_ok else '❌ Problème'}")
    
    if emails_ok and config_ok:
        print("\n✅ Configuration prête pour les notifications")
    else:
        print("\n⚠️ Corrections nécessaires:")
        if not emails_ok:
            print("  - Vérifiez les emails des utilisateurs en base")
        if not config_ok:
            print("  - Configurez les variables SMTP")
            print("  - Utilisez configure_email.ps1 ou configure_email.sh")
