#!/usr/bin/env python3
"""
Test des templates et routes responsable
"""

import os

# Configuration pour le développement
os.environ['FLASK_ENV'] = 'development'

try:
    print("🔍 Test des templates responsable...")
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Test 1: Vérifier que les routes responsable existent
        print("1. Test des routes responsable...")
        
        from app.routes import responsable
        print(f"   ✅ Blueprint responsable: {responsable.bp.name}")
        
        # Test 2: Vérifier les templates
        print("2. Test des templates...")
        
        from flask import render_template_string
        
        # Test du template de base
        try:
            with open('app/templates/roles/responsable/_base_responsable.html', 'r', encoding='utf-8') as f:
                base_content = f.read()
            print("   ✅ Template de base responsable lu")
        except Exception as e:
            print(f"   ❌ Erreur template de base: {e}")
        
        # Test du template dashboard
        try:
            with open('app/templates/roles/responsable/dashboard_responsable.html', 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
            print("   ✅ Template dashboard responsable lu")
        except Exception as e:
            print(f"   ❌ Erreur template dashboard: {e}")
        
        # Test 3: Simuler une requête
        print("3. Test de rendu des templates...")
        
        with app.test_client() as client:
            # Simuler une session responsable
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['user_role'] = 'RESPONSABLE'
                sess['user_nom'] = 'Test'
                sess['user_prenom'] = 'Responsable'
            
            try:
                # Test de la route dashboard responsable
                response = client.get('/responsable/dashboard')
                print(f"   ✅ Route dashboard: Status {response.status_code}")
                
                if response.status_code != 200:
                    print(f"   ⚠️  Contenu de l'erreur: {response.data.decode()[:200]}...")
                
            except Exception as e:
                print(f"   ❌ Erreur route dashboard: {e}")
    
    print("\n🎉 Tests terminés!")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
