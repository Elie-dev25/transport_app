#!/usr/bin/env python3
"""
Test des routes superviseur pour identifier les problèmes
"""

try:
    print("🧪 Test des routes superviseur...")
    
    from app import create_app
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("✅ Application créée")
            
            # Routes à tester
            routes_to_test = [
                ('/superviseur/dashboard', 'Dashboard'),
                ('/superviseur/carburation', 'Carburation'),
                ('/superviseur/bus-udm', 'Bus UdM'),
                ('/superviseur/vidanges', 'Vidanges'),
                ('/superviseur/chauffeurs', 'Chauffeurs'),
                ('/superviseur/utilisateurs', 'Utilisateurs'),
                ('/superviseur/rapports', 'Rapports')
            ]
            
            print("\n📋 Test des routes (sans authentification):")
            for route, name in routes_to_test:
                try:
                    # Test simple de la route (sera redirigé vers login mais on vérifie qu'elle existe)
                    response = client.get(route)
                    if response.status_code in [200, 302]:  # 200 = OK, 302 = Redirect vers login
                        print(f"   ✅ {name} ({route}) - Route accessible")
                    else:
                        print(f"   ❌ {name} ({route}) - Erreur {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {name} ({route}) - Exception: {str(e)}")
            
            # Test des modèles
            print("\n📦 Test des imports de modèles:")
            models_to_test = [
                ('app.models.carburation', 'Carburation'),
                ('app.models.bus_udm', 'BusUdM'),
                ('app.models.vidange', 'Vidange'),
                ('app.models.chauffeur', 'Chauffeur'),
                ('app.models.utilisateur', 'Utilisateur')
            ]
            
            for module_name, class_name in models_to_test:
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    model_class = getattr(module, class_name)
                    print(f"   ✅ {class_name} - Import réussi")
                    
                    # Test de requête simple
                    count = model_class.query.count()
                    print(f"      📊 {count} enregistrements trouvés")
                    
                except Exception as e:
                    print(f"   ❌ {class_name} - Erreur: {str(e)}")
            
            # Test des templates
            print("\n📄 Test des templates:")
            templates_to_test = [
                'superviseur/dashboard.html',
                'superviseur/carburation.html',
                'superviseur/bus_udm.html',
                'superviseur/vidanges.html',
                'superviseur/chauffeurs.html',
                'superviseur/utilisateurs.html',
                'superviseur/rapports.html'
            ]
            
            import os
            for template in templates_to_test:
                template_path = f"app/templates/{template}"
                if os.path.exists(template_path):
                    print(f"   ✅ {template}")
                else:
                    print(f"   ❌ {template} - MANQUANT")
    
    print("\n💡 Si certaines routes ne fonctionnent pas:")
    print("   1. Vérifiez les erreurs dans les logs Flask")
    print("   2. Assurez-vous que la base de données est accessible")
    print("   3. Vérifiez que tous les modèles sont correctement définis")
    
except Exception as e:
    print(f"\n❌ ERREUR GÉNÉRALE: {str(e)}")
    import traceback
    traceback.print_exc()
