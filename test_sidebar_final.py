#!/usr/bin/env python3
"""
Test final de la sidebar superviseur
"""

try:
    print("🧪 Test final de la sidebar superviseur...")
    
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
            
            # Tester toutes les pages superviseur
            pages_to_test = [
                ('/superviseur/dashboard', 'Dashboard'),
                ('/superviseur/carburation', 'Carburation'),
                ('/superviseur/bus-udm', 'Bus UdM'),
                ('/superviseur/vidanges', 'Vidanges'),
                ('/superviseur/chauffeurs', 'Chauffeurs'),
                ('/superviseur/utilisateurs', 'Utilisateurs'),
                ('/superviseur/rapports', 'Rapports')
            ]
            
            print("\n📋 Test de toutes les pages superviseur:")
            all_working = True
            
            for url, name in pages_to_test:
                try:
                    response = client.get(url)
                    if response.status_code == 200:
                        print(f"   ✅ {name} - Page accessible")
                        
                        # Vérifier que la sidebar superviseur est présente
                        content = response.get_data(as_text=True)
                        if 'Superviseur Panel' in content:
                            print(f"      ✅ Sidebar superviseur présente")
                        else:
                            print(f"      ❌ Sidebar superviseur MANQUANTE")
                            all_working = False
                            
                        if 'Interface Superviseur' in content:
                            print(f"      ✅ Alerte superviseur présente")
                        else:
                            print(f"      ❌ Alerte superviseur MANQUANTE")
                            all_working = False
                            
                    else:
                        print(f"   ❌ {name} - Erreur {response.status_code}")
                        all_working = False
                        
                except Exception as e:
                    print(f"   ❌ {name} - Exception: {str(e)}")
                    all_working = False
            
            print("\n" + "="*60)
            if all_working:
                print("🎉 TOUTES LES PAGES SUPERVISEUR FONCTIONNENT !")
                print("✅ Sidebar superviseur correcte sur toutes les pages")
                print("✅ Navigation complète disponible")
                print("✅ Alertes superviseur présentes")
            else:
                print("❌ Certaines pages ont encore des problèmes")
                print("💡 Vérifiez les templates et les routes")
            
            print("\n🚀 Pour tester manuellement:")
            print("   1. python start_and_test.py")
            print("   2. Connexion: superviseur / superviseur123")
            print("   3. Testez chaque lien de la sidebar")
    
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
