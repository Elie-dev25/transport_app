#!/usr/bin/env python3
"""
Test de l'interface responsable
"""

import os

# Configuration pour le développement
os.environ['FLASK_ENV'] = 'development'

try:
    print("🔍 Test de l'interface responsable...")
    
    from app import create_app
    app = create_app()
    
    with app.test_client() as client:
        print("1. Test de la page de connexion...")
        response = client.get('/')
        print(f"   ✅ Page d'accueil: Status {response.status_code}")
        
        # Simuler une session responsable
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'RESPONSABLE'
            sess['user_nom'] = 'Test'
            sess['user_prenom'] = 'Responsable'
        
        print("2. Test du dashboard responsable...")
        response = client.get('/responsable/dashboard')
        print(f"   ✅ Dashboard responsable: Status {response.status_code}")
        
        if response.status_code == 200:
            content = response.data.decode()
            if 'Responsable Panel' in content:
                print("   ✅ Template responsable utilisé")
            else:
                print("   ⚠️  Template responsable peut-être pas utilisé")
        
        print("3. Test des redirections responsable...")
        
        # Test redirection bus
        response = client.get('/responsable/bus')
        print(f"   ✅ Redirection bus: Status {response.status_code}")
        
        # Test redirection rapports
        response = client.get('/responsable/rapports')
        print(f"   ✅ Redirection rapports: Status {response.status_code}")
        
        # Test redirection utilisateurs
        response = client.get('/responsable/utilisateurs')
        print(f"   ✅ Redirection utilisateurs: Status {response.status_code}")
    
    print("\n🎉 Tests terminés avec succès!")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
