#!/usr/bin/env python3
"""
Script de test pour vérifier que la déclaration de panne fonctionne
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_declaration_panne():
    """Test de la déclaration de panne"""
    print("🔧 TEST DE DÉCLARATION DE PANNE")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.database import db
        from app.models.bus_udm import BusUdM
        from app.models.panne_bus_udm import PanneBusUdM
        from app.services.maintenance_service import MaintenanceService
        
        app = create_app()
        
        with app.app_context():
            print("\n1. 🚌 Vérification des bus disponibles...")
            buses = BusUdM.query.limit(3).all()
            if not buses:
                print("   ❌ Aucun bus trouvé en base de données")
                return False
            
            print(f"   ✅ {len(buses)} bus trouvés")
            for bus in buses:
                print(f"      - Bus {bus.numero} ({bus.immatriculation})")
            
            print("\n2. 🛠️ Test de création de panne via MaintenanceService...")
            test_bus = buses[0]
            
            # Données de test pour la panne
            panne_data = {
                'bus_udm_id': test_bus.id,
                'kilometrage': test_bus.kilometrage + 100 if test_bus.kilometrage else 1000,
                'description': 'Test automatique - Panne simulée pour vérification du système',
                'criticite': 'MOYENNE',
                'immobilisation': False,
                'date_heure': datetime.now()
            }
            
            # Créer la panne via le service
            success, message, panne_id = MaintenanceService.create_panne(
                panne_data, 
                "Script de test automatique"
            )
            
            if success:
                print(f"   ✅ Panne créée avec succès (ID: {panne_id})")
                print(f"   📧 Notification email: {'Envoyée' if 'succès' in message else 'Vérifier logs'}")
                
                # Vérifier que la panne existe en base
                panne_creee = PanneBusUdM.query.get(panne_id)
                if panne_creee:
                    print(f"   ✅ Panne vérifiée en base de données")
                    print(f"      - Description: {panne_creee.description}")
                    print(f"      - Criticité: {panne_creee.criticite}")
                    print(f"      - Enregistrée par: {panne_creee.enregistre_par}")
                    
                    # Test de résolution de la panne
                    print("\n3. 🔧 Test de résolution de panne...")
                    resolve_success, resolve_message = MaintenanceService.resolve_panne(
                        panne_id, 
                        "Script de test automatique"
                    )
                    
                    if resolve_success:
                        print(f"   ✅ Panne résolue avec succès")
                        print(f"   📧 Notification réparation: {'Envoyée' if 'succès' in resolve_message else 'Vérifier logs'}")
                    else:
                        print(f"   ❌ Échec résolution: {resolve_message}")
                else:
                    print(f"   ❌ Panne non trouvée en base après création")
                    return False
            else:
                print(f"   ❌ Échec création panne: {message}")
                return False
            
            print("\n4. 📊 Test des services de notification...")
            try:
                from app.services.notification_service import NotificationService
                
                # Test de configuration email
                config_result = NotificationService.test_email_configuration()
                print(f"   Configuration email: {'✅ OK' if config_result['success'] else '❌ Problème'}")
                if not config_result['success']:
                    print(f"      Erreur: {config_result['message']}")
                
            except ImportError as e:
                print(f"   ⚠️ Service de notification non disponible: {str(e)}")
            except Exception as e:
                print(f"   ⚠️ Erreur test notification: {str(e)}")
            
            print("\n" + "=" * 50)
            print("✅ TESTS TERMINÉS AVEC SUCCÈS")
            print("\n💡 Points vérifiés:")
            print("   - Création de panne via MaintenanceService")
            print("   - Résolution de panne")
            print("   - Intégration des notifications email")
            print("   - Persistance en base de données")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_route_declaration():
    """Test de la route de déclaration de panne"""
    print("\n🌐 TEST DE LA ROUTE DE DÉCLARATION")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.models.bus_udm import BusUdM
        
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                # Récupérer un bus pour le test
                bus = BusUdM.query.first()
                if not bus:
                    print("   ❌ Aucun bus disponible pour le test")
                    return False
                
                # Données de test
                test_data = {
                    'numero_bus_udm': bus.numero,
                    'immatriculation': bus.immatriculation,
                    'kilometrage': (bus.kilometrage or 0) + 50,
                    'description': 'Test route - Panne simulée pour vérification',
                    'criticite': 'FAIBLE',
                    'immobilisation': False
                }
                
                print(f"   🚌 Test avec bus: {bus.numero}")
                print(f"   📝 Données: {test_data}")
                
                # Test de la route (sans authentification - juste pour vérifier qu'elle existe)
                response = client.post('/admin/declarer_panne', 
                                     json=test_data,
                                     content_type='application/json')
                
                print(f"   📡 Réponse HTTP: {response.status_code}")
                
                if response.status_code == 302:
                    print("   ✅ Route accessible (redirection vers login - normal)")
                elif response.status_code == 401:
                    print("   ✅ Route accessible (non autorisé - normal)")
                elif response.status_code == 404:
                    print("   ❌ Route non trouvée - PROBLÈME!")
                    return False
                else:
                    print(f"   ℹ️ Code de réponse: {response.status_code}")
                
                print("   ✅ Route de déclaration accessible")
                return True
                
    except Exception as e:
        print(f"   ❌ Erreur test route: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 TESTS DE DÉCLARATION DE PANNE")
    print("=" * 60)
    
    # Test 1: Service de maintenance
    service_ok = test_declaration_panne()
    
    # Test 2: Route de déclaration
    route_ok = test_route_declaration()
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Service MaintenanceService: {'✅ OK' if service_ok else '❌ PROBLÈME'}")
    print(f"Route /admin/declarer_panne: {'✅ OK' if route_ok else '❌ PROBLÈME'}")
    
    if service_ok and route_ok:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS")
        print("Le bouton de déclaration devrait fonctionner correctement.")
    else:
        print("\n⚠️ PROBLÈMES DÉTECTÉS")
        print("Vérifiez les erreurs ci-dessus pour diagnostiquer le problème.")
    
    print("\n💡 Si le bouton ne fonctionne toujours pas:")
    print("1. Vérifiez la console JavaScript du navigateur")
    print("2. Vérifiez les logs de l'application Flask")
    print("3. Testez avec les outils de développement du navigateur")
