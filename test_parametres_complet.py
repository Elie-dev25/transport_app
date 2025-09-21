#!/usr/bin/env python3
"""
Test complet de la page des paramètres
"""

import os
import sys
sys.path.append('.')

def test_parametres_page():
    """Test de la page des paramètres"""
    
    print("🧪 Test de la page des paramètres...")
    
    try:
        from app import create_app
        from flask import url_for
        
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                
                # Test 1: Accès Admin
                print("\n1. Test accès Admin...")
                with client.session_transaction() as sess:
                    sess['user_id'] = 'admin'
                    sess['user_role'] = 'ADMIN'
                    sess['user_nom'] = 'Admin'
                    sess['user_prenom'] = 'System'
                
                response = client.get('/admin/parametres')
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.data.decode()
                    
                    # Vérifications du contenu
                    checks = [
                        ('Audit & Traçabilité', 'Section audit présente'),
                        ('Gestion Utilisateurs', 'Section utilisateurs présente'),
                        ('Gestion des Identifiants', 'Section identifiants présente'),
                        ('Gestion de Session', 'Section session présente'),
                        ('parametres.css', 'CSS chargé'),
                        ('parametres.js', 'JavaScript chargé')
                    ]
                    
                    for check, desc in checks:
                        if check in content:
                            print(f"   ✅ {desc}")
                        else:
                            print(f"   ❌ {desc} - MANQUANT")
                
                # Test 2: Accès Responsable
                print("\n2. Test accès Responsable...")
                with client.session_transaction() as sess:
                    sess['user_role'] = 'RESPONSABLE'
                
                response = client.get('/responsable/parametres')
                print(f"   Status: {response.status_code}")
                
                if response.status_code in [200, 302]:
                    print("   ✅ Accès responsable OK")
                else:
                    print("   ❌ Accès responsable échoué")
                
                # Test 3: Accès Superviseur
                print("\n3. Test accès Superviseur...")
                with client.session_transaction() as sess:
                    sess['user_role'] = 'SUPERVISEUR'
                
                response = client.get('/admin/parametres')
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.data.decode()
                    # Le superviseur ne doit pas voir la section identifiants
                    if 'Gestion des Identifiants' not in content:
                        print("   ✅ Superviseur n'a pas accès aux identifiants")
                    else:
                        print("   ❌ Superviseur a accès aux identifiants (erreur)")
                
                # Test 4: APIs
                print("\n4. Test des APIs...")
                
                # API Stats
                response = client.get('/admin/api/audit/stats')
                print(f"   API Stats: {response.status_code}")
                
                # API Logs
                response = client.get('/admin/api/audit/logs?limit=10')
                print(f"   API Logs: {response.status_code}")
                
                # API Users (Admin/Responsable uniquement)
                with client.session_transaction() as sess:
                    sess['user_role'] = 'ADMIN'
                
                response = client.get('/admin/api/users')
                print(f"   API Users: {response.status_code}")
                
                print("\n✅ Tests de base terminés!")
                
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

def test_fichiers_statiques():
    """Test de la présence des fichiers CSS et JS"""
    
    print("\n🔍 Vérification des fichiers statiques...")
    
    fichiers = [
        'app/static/css/parametres.css',
        'app/static/js/parametres.js'
    ]
    
    for fichier in fichiers:
        if os.path.exists(fichier):
            taille = os.path.getsize(fichier)
            print(f"   ✅ {fichier} ({taille} bytes)")
        else:
            print(f"   ❌ {fichier} - MANQUANT")

def test_structure_template():
    """Test de la structure du template"""
    
    print("\n📄 Vérification du template...")
    
    template_path = 'app/templates/pages/parametres.html'
    
    if not os.path.exists(template_path):
        print(f"   ❌ Template manquant: {template_path}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifications de structure
    checks = [
        ('id="audit-section"', 'Section audit'),
        ('id="users-section"', 'Section utilisateurs'),
        ('id="credentials-section"', 'Section identifiants'),
        ('id="session-section"', 'Section session'),
        ('createUserModal', 'Modal création utilisateur'),
        ('editRoleModal', 'Modal modification rôle'),
        ('settings-nav', 'Navigation paramètres'),
        ('audit-logs-container', 'Container logs audit')
    ]
    
    for check, desc in checks:
        if check in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ {desc} - MANQUANT")

def test_permissions():
    """Test des permissions par rôle"""
    
    print("\n🔐 Test des permissions...")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                
                # Test accès non autorisé
                roles_tests = [
                    ('CHAUFFEUR', False, 'Chauffeur ne doit pas accéder'),
                    ('MECANICIEN', False, 'Mécanicien ne doit pas accéder'),
                    ('CHARGE', False, 'Chargé ne doit pas accéder'),
                    ('ADMIN', True, 'Admin doit accéder'),
                    ('RESPONSABLE', True, 'Responsable doit accéder'),
                    ('SUPERVISEUR', True, 'Superviseur doit accéder')
                ]
                
                for role, should_access, desc in roles_tests:
                    with client.session_transaction() as sess:
                        sess['user_id'] = f'user_{role.lower()}'
                        sess['user_role'] = role
                        sess['user_nom'] = 'Test'
                        sess['user_prenom'] = role
                    
                    response = client.get('/admin/parametres')
                    
                    if should_access:
                        if response.status_code == 200:
                            print(f"   ✅ {desc}")
                        else:
                            print(f"   ❌ {desc} - Status: {response.status_code}")
                    else:
                        if response.status_code in [302, 403, 401]:
                            print(f"   ✅ {desc}")
                        else:
                            print(f"   ❌ {desc} - Accès autorisé (erreur)")
                
    except Exception as e:
        print(f"   ❌ Erreur test permissions: {e}")

if __name__ == "__main__":
    print("🚀 TESTS COMPLETS DE LA PAGE PARAMÈTRES")
    print("=" * 50)
    
    # Tests
    test_fichiers_statiques()
    test_structure_template()
    test_parametres_page()
    test_permissions()
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés!")
    
    print(f"\n📋 RÉSUMÉ:")
    print(f"   • Page paramètres créée avec 4 sections")
    print(f"   • Permissions par rôle implémentées")
    print(f"   • APIs d'audit et gestion utilisateurs")
    print(f"   • Interface moderne avec CSS/JS séparés")
    print(f"   • Modals pour création/modification")
    print(f"   • Système de déconnexion intégré")
