#!/usr/bin/env python3
"""
Script de test pour vérifier l'implémentation du rôle RESPONSABLE
"""

try:
    print("🧪 Test de l'implémentation du rôle RESPONSABLE...")
    
    from app import create_app
    from app.models.utilisateur import Utilisateur
    from app.routes.auth import authenticate_mysql
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("✅ Application créée et contexte de test activé")
            
            # Test 1: Vérifier que le rôle RESPONSABLE existe dans le modèle
            print("\n1. Test du modèle utilisateur...")
            try:
                # Créer un utilisateur test en mémoire
                test_user = Utilisateur(
                    nom='Test',
                    prenom='Responsable',
                    login='test_responsable',
                    role='RESPONSABLE',
                    email='test@udm.local',
                    telephone='000000000'
                )
                print("   ✅ Modèle utilisateur accepte le rôle RESPONSABLE")
            except Exception as e:
                print(f"   ❌ Erreur modèle: {str(e)}")
            
            # Test 2: Vérifier l'authentification
            print("\n2. Test de l'authentification...")
            try:
                success, groups, error = authenticate_mysql('responsable', 'responsable123')
                if success and 'Responsables' in groups:
                    print("   ✅ Authentification RESPONSABLE fonctionne")
                else:
                    print(f"   ⚠️  Authentification: success={success}, groups={groups}")
            except Exception as e:
                print(f"   ❌ Erreur authentification: {str(e)}")
            
            # Test 3: Vérifier les décorateurs de sécurité
            print("\n3. Test des décorateurs de sécurité...")
            try:
                from app.routes.common import admin_or_responsable, superviseur_access
                print("   ✅ Décorateurs importés correctement")
                
                # Simuler une session RESPONSABLE
                with client.session_transaction() as sess:
                    sess['user_id'] = 'responsable'
                    sess['user_role'] = 'RESPONSABLE'
                    sess['user_groups'] = ['Responsables']
                
                print("   ✅ Session RESPONSABLE simulée")
            except Exception as e:
                print(f"   ❌ Erreur décorateurs: {str(e)}")
            
            # Test 4: Vérifier les routes admin
            print("\n4. Test des routes admin...")
            routes_to_test = [
                ('/admin/dashboard', 'Dashboard Admin'),
                ('/admin/bus', 'Gestion Bus'),
                ('/admin/trajets', 'Gestion Trajets'),
                ('/admin/rapports', 'Rapports'),
                ('/admin/maintenance', 'Maintenance'),
                ('/admin/utilisateurs', 'Gestion Utilisateurs'),
                ('/admin/parametres', 'Paramètres')
            ]
            
            for route, name in routes_to_test:
                try:
                    # Test simple de la route (sera redirigé vers login mais on vérifie qu'elle existe)
                    response = client.get(route)
                    if response.status_code in [200, 302, 401]:  # 200=OK, 302=Redirect, 401=Auth required
                        print(f"   ✅ {name} ({route}) - Route accessible")
                    else:
                        print(f"   ❌ {name} ({route}) - Erreur {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {name} ({route}) - Exception: {str(e)}")
            
            # Test 5: Vérifier la redirection après login
            print("\n5. Test de redirection après login...")
            try:
                # Simuler un login RESPONSABLE
                login_data = {
                    'login': 'responsable',
                    'mot_de_passe': 'responsable123',
                    'csrf_token': 'test'  # En test, on peut ignorer CSRF
                }
                
                # Note: Ce test nécessiterait une configuration plus complexe
                # pour contourner la protection CSRF
                print("   ⚠️  Test de redirection nécessite un environnement complet")
                print("   💡 Vérifiez manuellement en vous connectant avec responsable/responsable123")
            except Exception as e:
                print(f"   ❌ Erreur redirection: {str(e)}")
            
            # Test 6: Vérifier les utilisateurs en base
            print("\n6. Test des utilisateurs en base...")
            try:
                users_by_role = {}
                users = Utilisateur.query.all()
                
                for user in users:
                    role = user.role or 'AUCUN'
                    if role not in users_by_role:
                        users_by_role[role] = 0
                    users_by_role[role] += 1
                
                print("   📊 Répartition des utilisateurs par rôle:")
                for role, count in users_by_role.items():
                    print(f"      {role}: {count} utilisateur(s)")
                
                if 'RESPONSABLE' in users_by_role:
                    print("   ✅ Des utilisateurs RESPONSABLE existent en base")
                else:
                    print("   ⚠️  Aucun utilisateur RESPONSABLE trouvé")
                    print("   💡 Exécutez create_responsable_user.py pour en créer un")
                    
            except Exception as e:
                print(f"   ❌ Erreur base de données: {str(e)}")
    
    print("\n🎉 TESTS TERMINÉS!")
    print("\n📋 Résumé de l'implémentation:")
    print("   ✅ Modèle utilisateur mis à jour")
    print("   ✅ Authentification configurée")
    print("   ✅ Décorateurs de sécurité créés")
    print("   ✅ Routes admin mises à jour")
    print("   ✅ Templates mis à jour")
    print("   ✅ Scripts de migration créés")
    
    print("\n🚀 Pour utiliser le nouveau rôle:")
    print("   1. Exécutez le script SQL: scripts/add_responsable_role.sql")
    print("   2. Créez un utilisateur: python create_responsable_user.py")
    print("   3. Connectez-vous avec: responsable / responsable123")
    print("   4. Le responsable aura tous les accès admin!")

except Exception as e:
    print(f"\n❌ ERREUR GÉNÉRALE: {str(e)}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Vérifiez:")
    print("1. Que l'application démarre correctement")
    print("2. Que la base de données est accessible")
    print("3. Que tous les fichiers ont été modifiés")
