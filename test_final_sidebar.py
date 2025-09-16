#!/usr/bin/env python3
"""
Test final de la sidebar superviseur après corrections
"""

try:
    print("🎯 Test final de la sidebar superviseur...")
    
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
            pages = [
                ('/superviseur/carburation', 'Carburation'),
                ('/superviseur/vidanges', 'Vidanges'),
                ('/superviseur/rapports', 'Rapports')
            ]
            
            print("\n📋 Test des pages corrigées:")
            all_good = True
            
            for url, name in pages:
                try:
                    response = client.get(url)
                    content = response.get_data(as_text=True)
                    
                    print(f"\n🔍 {name} ({url}):")
                    print(f"   Status: {response.status_code}")
                    
                    # Vérifications
                    checks = [
                        ('Superviseur Panel', 'Superviseur Panel' in content),
                        ('Interface Superviseur', 'Interface Superviseur' in content),
                        ('Dashboard', '/superviseur/dashboard' in content),
                        ('Carburation', '/superviseur/carburation' in content),
                        ('Bus UdM', '/superviseur/bus-udm' in content),
                        ('Vidanges', '/superviseur/vidanges' in content),
                        ('Chauffeurs', '/superviseur/chauffeurs' in content),
                        ('Utilisateurs', '/superviseur/utilisateurs' in content),
                        ('Rapports', '/superviseur/rapports' in content)
                    ]
                    
                    for check_name, result in checks:
                        if result:
                            print(f"   ✅ {check_name}")
                        else:
                            print(f"   ❌ {check_name}")
                            all_good = False
                            
                except Exception as e:
                    print(f"   ❌ Erreur: {str(e)}")
                    all_good = False
            
            print(f"\n{'='*60}")
            if all_good:
                print("🎉 TOUTES LES PAGES SUPERVISEUR SONT MAINTENANT CORRECTES !")
                print("✅ Sidebar superviseur complète sur toutes les pages")
                print("✅ Navigation fonctionnelle")
                print("✅ Alerte superviseur présente")
            else:
                print("⚠️  Certains éléments manquent encore")
                print("💡 Redémarrez l'application et videz le cache du navigateur")
            
            print("\n🚀 Pour tester manuellement:")
            print("   1. python run.py")
            print("   2. http://localhost:5000")
            print("   3. Login: superviseur / superviseur123")
            print("   4. Testez carburation, vidanges, rapports")
    
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
