#!/usr/bin/env python3
"""
Debug détaillé de la sidebar superviseur
"""

try:
    print("🔍 Debug détaillé de la sidebar superviseur...")
    
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
            
            # Pages à tester
            pages_problematiques = [
                ('/superviseur/carburation', 'Carburation'),
                ('/superviseur/vidanges', 'Vidanges'),
                ('/superviseur/rapports', 'Rapports')
            ]
            
            print("\n🔍 Analyse détaillée des pages problématiques:")
            
            for url, name in pages_problematiques:
                print(f"\n{'='*50}")
                print(f"📄 ANALYSE DE {name.upper()} ({url})")
                print('='*50)
                
                try:
                    response = client.get(url)
                    content = response.get_data(as_text=True)
                    
                    print(f"Status: {response.status_code}")
                    
                    # Vérifier le titre de la sidebar
                    if 'Superviseur Panel' in content:
                        print("✅ Titre 'Superviseur Panel' trouvé")
                    elif 'Admin Panel' in content:
                        print("❌ PROBLÈME: Titre 'Admin Panel' trouvé (sidebar admin)")
                    else:
                        print("❓ Aucun titre de panel trouvé")
                    
                    # Vérifier les liens de navigation
                    nav_links = [
                        ('superviseur.dashboard', 'Dashboard'),
                        ('superviseur.carburation', 'Carburation'),
                        ('superviseur.bus_udm', 'Bus UdM'),
                        ('superviseur.vidanges', 'Vidanges'),
                        ('superviseur.chauffeurs', 'Chauffeurs'),
                        ('superviseur.utilisateurs', 'Utilisateurs'),
                        ('superviseur.rapports', 'Rapports')
                    ]
                    
                    print("\n📋 Liens de navigation trouvés:")
                    for route, link_name in nav_links:
                        if route in content:
                            print(f"   ✅ {link_name}")
                        else:
                            print(f"   ❌ {link_name} MANQUANT")
                    
                    # Vérifier l'alerte superviseur
                    if 'Interface Superviseur' in content:
                        print("\n✅ Alerte 'Interface Superviseur' présente")
                    else:
                        print("\n❌ Alerte 'Interface Superviseur' MANQUANTE")
                    
                    # Vérifier si c'est une redirection vers admin
                    if '/admin/' in content:
                        print("\n⚠️  ATTENTION: Contenu admin détecté dans la page")
                    
                    # Extraire un échantillon du contenu pour debug
                    lines = content.split('\n')
                    sidebar_section = []
                    in_sidebar = False
                    
                    for line in lines:
                        if 'nav-menu' in line or 'sidebar' in line.lower():
                            in_sidebar = True
                        if in_sidebar and ('nav-item' in line or 'nav-link' in line):
                            sidebar_section.append(line.strip())
                        if in_sidebar and len(sidebar_section) > 10:
                            break
                    
                    if sidebar_section:
                        print(f"\n📝 Échantillon de la sidebar:")
                        for line in sidebar_section[:5]:
                            print(f"   {line}")
                    
                except Exception as e:
                    print(f"❌ Erreur lors du test de {name}: {str(e)}")
            
            print(f"\n{'='*60}")
            print("💡 SOLUTIONS POSSIBLES:")
            print("1. Vider le cache du navigateur (Ctrl+F5)")
            print("2. Vérifier que vous accédez aux bonnes URLs:")
            print("   - http://localhost:5000/superviseur/carburation")
            print("   - http://localhost:5000/superviseur/vidanges")
            print("   - http://localhost:5000/superviseur/rapports")
            print("3. Redémarrer l'application complètement")
            print("4. Vérifier qu'il n'y a pas de redirections cachées")
    
except Exception as e:
    print(f"\n❌ ERREUR GÉNÉRALE: {str(e)}")
    import traceback
    traceback.print_exc()
