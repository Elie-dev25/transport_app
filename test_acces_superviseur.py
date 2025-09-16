#!/usr/bin/env python3
"""
Test d'accès aux pages superviseur avec authentification
"""

try:
    print("🧪 Test d'accès superviseur avec authentification...")
    
    from app import create_app
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("✅ Application créée")
            
            # Simuler une connexion superviseur
            with client.session_transaction() as sess:
                sess['user_id'] = 999  # ID fictif
                sess['user_role'] = 'SUPERVISEUR'
                sess['user_login'] = 'superviseur'
            
            print("✅ Session superviseur simulée")
            
            # Tester chaque page
            pages_to_test = [
                ('/superviseur/dashboard', 'Dashboard'),
                ('/superviseur/carburation', 'Carburation'),
                ('/superviseur/bus-udm', 'Bus UdM'),
                ('/superviseur/vidanges', 'Vidanges'),
                ('/superviseur/chauffeurs', 'Chauffeurs'),
                ('/superviseur/utilisateurs', 'Utilisateurs'),
                ('/superviseur/rapports', 'Rapports')
            ]
            
            print("\n📋 Test des pages avec authentification:")
            for url, name in pages_to_test:
                try:
                    response = client.get(url)
                    if response.status_code == 200:
                        print(f"   ✅ {name} - Page accessible (200)")
                        
                        # Vérifier que le contenu contient des éléments attendus
                        content = response.get_data(as_text=True)
                        if 'Interface Superviseur' in content:
                            print(f"      ✅ Alerte superviseur présente")
                        if name.lower() in content.lower():
                            print(f"      ✅ Contenu {name} présent")
                        
                    elif response.status_code == 302:
                        print(f"   ⚠️  {name} - Redirection (302)")
                    elif response.status_code == 500:
                        print(f"   ❌ {name} - Erreur serveur (500)")
                        # Essayer d'obtenir plus d'infos sur l'erreur
                        content = response.get_data(as_text=True)
                        if 'Traceback' in content:
                            lines = content.split('\n')
                            for line in lines:
                                if 'Error:' in line or 'Exception:' in line:
                                    print(f"      🔍 {line.strip()}")
                                    break
                    else:
                        print(f"   ❌ {name} - Code {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {name} - Exception: {str(e)}")
            
            print("\n💡 Instructions pour tester manuellement:")
            print("   1. Démarrez l'application: python run.py")
            print("   2. Allez sur: http://localhost:5000")
            print("   3. Connectez-vous avec: superviseur / superviseur123")
            print("   4. Testez chaque lien de la sidebar")
            
            print("\n🔧 Si des pages ne fonctionnent pas:")
            print("   - Vérifiez les logs Flask pour les erreurs détaillées")
            print("   - Assurez-vous que la base de données est accessible")
            print("   - Vérifiez que tous les templates sont corrects")
    
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
