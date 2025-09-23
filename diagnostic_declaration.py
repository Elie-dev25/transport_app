#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes avec la déclaration de panne
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """Vérifier tous les imports nécessaires"""
    print("🔍 VÉRIFICATION DES IMPORTS")
    print("=" * 40)
    
    imports_to_check = [
        ('app', 'Application Flask'),
        ('app.database', 'Base de données'),
        ('app.models.bus_udm', 'Modèle Bus'),
        ('app.models.panne_bus_udm', 'Modèle Panne'),
        ('app.services.maintenance_service', 'Service Maintenance'),
        ('app.services.notification_service', 'Service Notification'),
        ('app.routes.admin.maintenance', 'Routes Maintenance'),
        ('flask', 'Flask Framework'),
        ('flask_login', 'Flask-Login'),
        ('sqlalchemy', 'SQLAlchemy')
    ]
    
    all_ok = True
    
    for module_name, description in imports_to_check:
        try:
            __import__(module_name)
            print(f"   ✅ {description}: OK")
        except ImportError as e:
            print(f"   ❌ {description}: ERREUR - {str(e)}")
            all_ok = False
        except Exception as e:
            print(f"   ⚠️ {description}: PROBLÈME - {str(e)}")
            all_ok = False
    
    return all_ok

def check_database_connection():
    """Vérifier la connexion à la base de données"""
    print("\n🗄️ VÉRIFICATION BASE DE DONNÉES")
    print("=" * 40)
    
    try:
        from app import create_app
        from app.database import db
        from app.models.bus_udm import BusUdM
        from app.models.panne_bus_udm import PanneBusUdM
        
        app = create_app()
        
        with app.app_context():
            # Test de connexion
            try:
                db.engine.execute('SELECT 1')
                print("   ✅ Connexion base de données: OK")
            except Exception as e:
                print(f"   ❌ Connexion base de données: ERREUR - {str(e)}")
                return False
            
            # Test des modèles
            try:
                bus_count = BusUdM.query.count()
                print(f"   ✅ Modèle Bus: OK ({bus_count} bus en base)")
            except Exception as e:
                print(f"   ❌ Modèle Bus: ERREUR - {str(e)}")
                return False
            
            try:
                panne_count = PanneBusUdM.query.count()
                print(f"   ✅ Modèle Panne: OK ({panne_count} pannes en base)")
            except Exception as e:
                print(f"   ❌ Modèle Panne: ERREUR - {str(e)}")
                return False
            
            return True
            
    except Exception as e:
        print(f"   ❌ Erreur générale base de données: {str(e)}")
        return False

def check_routes():
    """Vérifier les routes de maintenance"""
    print("\n🌐 VÉRIFICATION DES ROUTES")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        # Vérifier que les routes existent
        routes_to_check = [
            '/admin/declarer_panne',
            '/admin/enregistrer_depannage',
            '/admin/maintenance',
            '/admin/notifications'
        ]
        
        with app.app_context():
            for route in routes_to_check:
                try:
                    # Vérifier si la route existe dans l'application
                    found = False
                    for rule in app.url_map.iter_rules():
                        if rule.rule == route:
                            found = True
                            print(f"   ✅ Route {route}: OK (méthodes: {', '.join(rule.methods)})")
                            break
                    
                    if not found:
                        print(f"   ❌ Route {route}: NON TROUVÉE")
                        
                except Exception as e:
                    print(f"   ⚠️ Route {route}: ERREUR - {str(e)}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Erreur vérification routes: {str(e)}")
        return False

def check_services():
    """Vérifier les services"""
    print("\n🔧 VÉRIFICATION DES SERVICES")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Test MaintenanceService
            try:
                from app.services.maintenance_service import MaintenanceService
                print("   ✅ MaintenanceService: Import OK")
                
                # Vérifier les méthodes
                if hasattr(MaintenanceService, 'create_panne'):
                    print("   ✅ MaintenanceService.create_panne: OK")
                else:
                    print("   ❌ MaintenanceService.create_panne: MANQUANTE")
                
                if hasattr(MaintenanceService, 'resolve_panne'):
                    print("   ✅ MaintenanceService.resolve_panne: OK")
                else:
                    print("   ❌ MaintenanceService.resolve_panne: MANQUANTE")
                    
            except Exception as e:
                print(f"   ❌ MaintenanceService: ERREUR - {str(e)}")
            
            # Test NotificationService
            try:
                from app.services.notification_service import NotificationService
                print("   ✅ NotificationService: Import OK")
                
                # Test de configuration
                config_result = NotificationService.test_email_configuration()
                if config_result['success']:
                    print("   ✅ Configuration email: OK")
                else:
                    print(f"   ⚠️ Configuration email: {config_result['message']}")
                    
            except Exception as e:
                print(f"   ⚠️ NotificationService: {str(e)}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Erreur vérification services: {str(e)}")
        return False

def check_templates():
    """Vérifier les templates"""
    print("\n📄 VÉRIFICATION DES TEMPLATES")
    print("=" * 40)
    
    templates_to_check = [
        'app/templates/shared/modals/_declaration_panne_modal.html',
        'app/templates/pages/bus_udm.html',
        'app/templates/roles/admin/maintenance.html'
    ]
    
    all_ok = True
    
    for template_path in templates_to_check:
        if os.path.exists(template_path):
            print(f"   ✅ {os.path.basename(template_path)}: OK")
        else:
            print(f"   ❌ {os.path.basename(template_path)}: MANQUANT")
            all_ok = False
    
    return all_ok

def check_javascript():
    """Vérifier les fichiers JavaScript"""
    print("\n📜 VÉRIFICATION JAVASCRIPT")
    print("=" * 40)
    
    js_files_to_check = [
        'app/static/js/main.js',
        'app/static/js/depannage.js',
        'app/static/js/parametres.js'
    ]
    
    all_ok = True
    
    for js_path in js_files_to_check:
        if os.path.exists(js_path):
            print(f"   ✅ {os.path.basename(js_path)}: OK")
            
            # Vérifier le contenu pour des erreurs évidentes
            try:
                with open(js_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Rechercher des patterns problématiques
                if 'FormModalManager' in content:
                    print(f"      ✅ FormModalManager trouvé dans {os.path.basename(js_path)}")
                    
                if 'declarer_panne' in content or 'panneForm' in content:
                    print(f"      ✅ Code de déclaration trouvé dans {os.path.basename(js_path)}")
                    
            except Exception as e:
                print(f"      ⚠️ Erreur lecture {os.path.basename(js_path)}: {str(e)}")
        else:
            print(f"   ❌ {os.path.basename(js_path)}: MANQUANT")
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC COMPLET - DÉCLARATION DE PANNE")
    print("=" * 60)
    
    results = {
        'imports': check_imports(),
        'database': check_database_connection(),
        'routes': check_routes(),
        'services': check_services(),
        'templates': check_templates(),
        'javascript': check_javascript()
    }
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 60)
    
    all_ok = True
    for component, status in results.items():
        status_text = "✅ OK" if status else "❌ PROBLÈME"
        print(f"{component.capitalize():15}: {status_text}")
        if not status:
            all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("🎉 DIAGNOSTIC COMPLET: TOUT SEMBLE OK")
        print("\nSi le bouton ne fonctionne toujours pas:")
        print("1. Vérifiez la console JavaScript du navigateur (F12)")
        print("2. Vérifiez que vous êtes connecté avec les bons droits")
        print("3. Essayez de rafraîchir la page (Ctrl+F5)")
        print("4. Vérifiez les logs de l'application Flask")
    else:
        print("⚠️ PROBLÈMES DÉTECTÉS")
        print("\nCorrigez les erreurs ci-dessus avant de continuer.")
        print("Les composants marqués ❌ nécessitent une attention.")
    
    print(f"\nDiagnostic effectué le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
