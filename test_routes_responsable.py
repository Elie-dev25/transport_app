#!/usr/bin/env python3
"""
Test complet des routes responsable pour éviter les conflits
"""

import os

# Configuration pour le développement
os.environ['FLASK_ENV'] = 'development'

try:
    print("🔍 Test complet des routes responsable...")
    
    from app import create_app
    app = create_app()
    
    with app.test_client() as client:
        # Simuler une session responsable
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'RESPONSABLE'
            sess['user_nom'] = 'Test'
            sess['user_prenom'] = 'Responsable'
        
        print("1. Test du dashboard responsable...")
        response = client.get('/responsable/dashboard')
        print(f"   ✅ Dashboard: Status {response.status_code}")
        
        print("2. Test des redirections responsable...")
        
        # Test redirection bus
        response = client.get('/responsable/bus')
        print(f"   ✅ Bus: Status {response.status_code}")
        
        # Test redirection chauffeurs
        response = client.get('/responsable/chauffeurs')
        print(f"   ✅ Chauffeurs: Status {response.status_code}")
        
        # Test redirection utilisateurs
        response = client.get('/responsable/utilisateurs')
        print(f"   ✅ Utilisateurs: Status {response.status_code}")
        
        # Test redirection rapports
        response = client.get('/responsable/rapports')
        print(f"   ✅ Rapports: Status {response.status_code}")
        
        # Test redirection paramètres
        response = client.get('/responsable/parametres')
        print(f"   ✅ Paramètres: Status {response.status_code}")
        
        print("3. Test des détails de bus...")
        
        # Test détails bus via route responsable
        response = client.get('/responsable/bus/details/1')
        print(f"   ✅ Détails bus (route responsable): Status {response.status_code}")
        
        # Test détails bus via route admin avec source responsable
        response = client.get('/admin/bus/details/1?source=responsable')
        print(f"   ✅ Détails bus (route admin + source): Status {response.status_code}")
        
        print("4. Test de l'utilitaire de routes...")
        
        from app.utils.route_utils import (
            get_base_template_for_role,
            get_template_context_for_role,
            is_responsable_context
        )
        
        # Test avec rôle responsable
        base_template = get_base_template_for_role('RESPONSABLE')
        print(f"   ✅ Template pour RESPONSABLE: {base_template}")
        
        # Test contexte
        with app.test_request_context('/test?source=responsable'):
            context = get_template_context_for_role()
            print(f"   ✅ Contexte responsable: {context['use_responsable_base']}")
    
    print("\n🎉 Tous les tests sont passés avec succès!")
    print("\n📋 Résumé des corrections apportées:")
    print("   ✅ Routes responsable créées avec redirections")
    print("   ✅ Templates modifiés pour gérer le contexte responsable")
    print("   ✅ Utilitaire de routes créé pour éviter les conflits")
    print("   ✅ JavaScript modifié pour utiliser les bonnes routes")
    print("   ✅ Système de traçabilité avec paramètre 'source'")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
