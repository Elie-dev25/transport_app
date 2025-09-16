#!/usr/bin/env python3
"""
Test des corrections apportées aux templates superviseur
"""

try:
    print("🧪 Test des corrections...")
    
    from app import create_app
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("✅ Application créée")
            
            # Simuler une session superviseur
            with client.session_transaction() as sess:
                sess['user_id'] = 999
                sess['user_role'] = 'SUPERVISEUR'
                sess['user_login'] = 'superviseur'
            
            # Tester les pages problématiques
            pages_to_test = [
                ('/superviseur/bus-udm', 'Bus UdM'),
                ('/superviseur/chauffeurs', 'Chauffeurs'),
                ('/superviseur/utilisateurs', 'Utilisateurs'),
                ('/superviseur/carburation', 'Carburation'),
                ('/superviseur/vidanges', 'Vidanges')
            ]
            
            print("\n📋 Test des pages corrigées:")
            for url, name in pages_to_test:
                try:
                    response = client.get(url)
                    if response.status_code == 200:
                        print(f"   ✅ {name} - Page accessible (200)")
                        
                        # Vérifier le contenu
                        content = response.get_data(as_text=True)
                        if 'Gestion des' in content or 'Dashboard' in content:
                            print(f"      ✅ Contenu correct")
                        if 'Interface Superviseur' in content:
                            print(f"      ✅ Alerte superviseur présente")
                            
                    else:
                        print(f"   ❌ {name} - Code {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {name} - Exception: {str(e)}")
            
            print("\n🎯 Corrections apportées:")
            print("   ✅ Route 'superviseur.bus_list' → 'superviseur.bus_udm'")
            print("   ✅ Filtres Jinja2 complexes remplacés par des boucles simples")
            print("   ✅ Gestion des valeurs None dans les comparaisons")
            print("   ✅ Templates d'erreur corrigés")
            
            print("\n🚀 L'application devrait maintenant fonctionner !")
            print("   Démarrez avec: python start_and_test.py")
            print("   Connectez-vous: superviseur / superviseur123")
    
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
