#!/usr/bin/env python3
"""
Test du nouveau système d'audit intelligent
Démontre les fonctionnalités avancées du système d'audit
"""

import os
import sys
import time
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_smart_audit():
    """Test complet du système d'audit intelligent"""
    
    print("🔍 TEST DU SYSTÈME D'AUDIT INTELLIGENT")
    print("=" * 60)
    
    try:
        # Import des modules d'audit
        from app.utils.audit_logger import (
            # Actions critiques
            log_login_success, log_login_failed, log_logout,
            log_creation, log_modification, log_suppression,
            log_user_created, log_user_role_changed,
            log_sensitive_access, log_unauthorized_access,
            log_system_error, log_security_violation,
            log_config_changed, log_system_maintenance,
            
            # Fonctions de lecture
            get_audit_logs, get_role_audit_logs, get_role_statistics,
            get_critical_alerts,
            
            # Décorateurs
            audit_action, smart_audit,
            
            # Enums
            AuditActionType, AuditLevel
        )
        
        print("✅ Modules d'audit importés avec succès")
        
        # Créer un contexte Flask minimal pour les tests
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                print("✅ Contexte Flask créé")
                
                # Simuler différentes sessions utilisateur
                test_sessions = [
                    {'user_id': '1', 'user_role': 'ADMIN', 'user_login': 'admin'},
                    {'user_id': '2', 'user_role': 'RESPONSABLE', 'user_login': 'responsable'},
                    {'user_id': '3', 'user_role': 'SUPERVISEUR', 'user_login': 'superviseur'},
                    {'user_id': '4', 'user_role': 'CHARGE', 'user_login': 'charge'},
                    {'user_id': '5', 'user_role': 'CHAUFFEUR', 'user_login': 'chauffeur'},
                    {'user_id': '6', 'user_role': 'MECANICIEN', 'user_login': 'mecanicien'}
                ]
                
                print("\n📝 GÉNÉRATION D'ACTIONS D'AUDIT PAR RÔLE")
                print("-" * 50)
                
                for session_data in test_sessions:
                    with client.session_transaction() as sess:
                        sess.update(session_data)
                    
                    role = session_data['user_role']
                    user_id = session_data['user_id']
                    login = session_data['user_login']
                    
                    print(f"\n🔸 Test pour {role} (ID: {user_id})")
                    
                    # 1. Authentification
                    log_login_success(user_id, role, f"Test login for {login}")
                    
                    # 2. Actions CRUD selon le rôle
                    if role in ['ADMIN', 'RESPONSABLE']:
                        log_creation('bus', 'BUS-001', f'Nouveau bus créé par {role}')
                        log_user_created('new_user_123', 'CHAUFFEUR', role)
                        log_config_changed('system_timeout', '300', '600')
                        
                    elif role == 'SUPERVISEUR':
                        log_sensitive_access('reports', 'monthly_report', 'Consultation rapport mensuel')
                        
                    elif role == 'CHARGE':
                        log_creation('trajet', 'TRJ-456', f'Nouveau trajet créé par {role}')
                        log_modification('trajet', 'TRJ-123', {'status': 'planned'}, {'status': 'active'})
                        
                    elif role == 'CHAUFFEUR':
                        log_modification('fuel_record', 'FUEL-789', {'liters': '45'}, {'liters': '50'})
                        
                    elif role == 'MECANICIEN':
                        log_creation('maintenance', 'MAINT-999', 'Nouvelle intervention maintenance')
                        log_modification('bus', 'BUS-002', {'status': 'operational'}, {'status': 'maintenance'})
                    
                    # 3. Tentative d'accès non autorisé (pour certains rôles)
                    if role in ['CHAUFFEUR', 'MECANICIEN']:
                        log_unauthorized_access('admin_panel', f'{role} tried to access admin functions')
                    
                    # 4. Déconnexion
                    log_logout(user_id, role)
                    
                    print(f"   ✅ Actions générées pour {role}")
                
                # Générer quelques erreurs système
                print(f"\n⚠️  GÉNÉRATION D'ERREURS SYSTÈME")
                print("-" * 30)
                
                with client.session_transaction() as sess:
                    sess.update({'user_id': '1', 'user_role': 'ADMIN', 'user_login': 'admin'})
                
                log_system_error('Database Connection', 'Connection timeout after 30s', 'User registration')
                log_security_violation('Brute Force', 'Multiple failed login attempts from IP 192.168.1.100')
                log_login_failed('hacker123', 'Invalid credentials - potential attack')
                
                print("   ✅ Erreurs système générées")
                
                # Attendre un peu pour que les logs soient écrits
                time.sleep(1)
                
                print(f"\n📊 ANALYSE DES LOGS GÉNÉRÉS")
                print("-" * 40)
                
                # Statistiques par rôle
                stats = get_role_statistics()
                for role, role_stats in stats.items():
                    if role_stats['total'] > 0:
                        print(f"\n🔸 {role}:")
                        print(f"   Total actions: {role_stats['total']}")
                        print(f"   Taux de succès: {role_stats['success_rate']}%")
                        print(f"   Niveaux: {role_stats['levels']}")
                        print(f"   Actions principales: {list(role_stats['actions'].keys())[:3]}")
                
                # Alertes critiques
                alerts = get_critical_alerts(hours=1)
                if alerts:
                    print(f"\n🚨 ALERTES CRITIQUES ({len(alerts)}):")
                    for alert in alerts[:3]:  # Afficher les 3 premières
                        print(f"   {alert['timestamp']} | {alert['role']} | {alert['log'][:80]}...")
                
                # Logs par rôle
                print(f"\n📋 EXEMPLES DE LOGS PAR RÔLE:")
                for role in ['ADMIN', 'CHAUFFEUR', 'SUPERVISEUR']:
                    logs = get_role_audit_logs(role, limit=2)
                    if logs:
                        print(f"\n🔸 {role} (2 derniers logs):")
                        for log in logs:
                            print(f"   {log[:100]}...")
                
                print(f"\n✅ SYSTÈME D'AUDIT INTELLIGENT TESTÉ AVEC SUCCÈS!")
                print(f"📁 Logs sauvegardés dans: logs/audit/")
                print(f"   - audit_admin.log")
                print(f"   - audit_responsable.log") 
                print(f"   - audit_superviseur.log")
                print(f"   - audit_charge.log")
                print(f"   - audit_chauffeur.log")
                print(f"   - audit_mecanicien.log")
                
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Assurez-vous que l'application Flask est correctement configurée")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_audit()
