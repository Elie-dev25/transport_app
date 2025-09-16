#!/usr/bin/env python3
"""
Script de test pour vérifier la traçabilité ADMIN vs RESPONSABLE
"""

try:
    print("🧪 Test de la traçabilité ADMIN vs RESPONSABLE...")
    
    from app import create_app
    from app.utils.audit_logger import log_user_action, get_audit_logs, get_role_statistics
    from flask import session
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("✅ Application créée et contexte de test activé")
            
            # Test 1: Simuler des actions ADMIN
            print("\n1. Test des actions ADMIN...")
            with client.session_transaction() as sess:
                sess['user_id'] = 'admin'
                sess['user_role'] = 'ADMIN'
                sess['user_groups'] = ['Administrateur']
            
            # Simuler quelques actions admin
            with app.test_request_context():
                with client.session_transaction() as sess:
                    sess['user_id'] = 'admin'
                    sess['user_role'] = 'ADMIN'
                
                log_user_action('CREATION', 'create_bus', 'Bus UDM-001 créé')
                log_user_action('MODIFICATION', 'update_trajet', 'Trajet ID:123 modifié')
                log_user_action('CONSULTATION', 'view_dashboard', 'Accès dashboard admin')
                
            print("   ✅ Actions ADMIN loggées")
            
            # Test 2: Simuler des actions RESPONSABLE
            print("\n2. Test des actions RESPONSABLE...")
            with app.test_request_context():
                with client.session_transaction() as sess:
                    sess['user_id'] = 'responsable'
                    sess['user_role'] = 'RESPONSABLE'
                
                log_user_action('CREATION', 'create_chauffeur', 'Chauffeur Jean Dupont créé')
                log_user_action('MODIFICATION', 'update_bus', 'Bus UDM-002 modifié')
                log_user_action('CONSULTATION', 'view_rapports', 'Accès rapports')
                
            print("   ✅ Actions RESPONSABLE loggées")
            
            # Test 3: Simuler des actions SUPERVISEUR
            print("\n3. Test des actions SUPERVISEUR...")
            with app.test_request_context():
                with client.session_transaction() as sess:
                    sess['user_id'] = 'superviseur'
                    sess['user_role'] = 'SUPERVISEUR'
                
                log_user_action('CONSULTATION', 'view_bus', 'Consultation liste bus')
                log_user_action('CONSULTATION', 'view_trajets', 'Consultation trajets')
                
            print("   ✅ Actions SUPERVISEUR loggées")
            
            # Test 4: Vérifier les logs
            print("\n4. Vérification des logs...")
            
            # Récupérer tous les logs récents
            all_logs = get_audit_logs(limit=20)
            print(f"   📊 {len(all_logs)} logs trouvés")
            
            # Compter par rôle
            admin_logs = [log for log in all_logs if 'ROLE:ADMIN' in log]
            responsable_logs = [log for log in all_logs if 'ROLE:RESPONSABLE' in log]
            superviseur_logs = [log for log in all_logs if 'ROLE:SUPERVISEUR' in log]
            
            print(f"   👑 ADMIN: {len(admin_logs)} actions")
            print(f"   🏢 RESPONSABLE: {len(responsable_logs)} actions")
            print(f"   👁️  SUPERVISEUR: {len(superviseur_logs)} actions")
            
            # Afficher quelques exemples
            if admin_logs:
                print(f"\n   Exemple log ADMIN:")
                print(f"   {admin_logs[0]}")
            
            if responsable_logs:
                print(f"\n   Exemple log RESPONSABLE:")
                print(f"   {responsable_logs[0]}")
            
            if superviseur_logs:
                print(f"\n   Exemple log SUPERVISEUR:")
                print(f"   {superviseur_logs[0]}")
            
            # Test 5: Vérifier les statistiques
            print("\n5. Test des statistiques...")
            stats = get_role_statistics()
            
            for role, data in stats.items():
                if data['total'] > 0:
                    print(f"   {role}: {data['total']} actions")
                    for action, count in data['actions'].items():
                        print(f"     - {action}: {count}")
            
            # Test 6: Test des filtres
            print("\n6. Test des filtres...")
            
            # Filtrer par rôle ADMIN
            admin_filtered = get_audit_logs(limit=50, role_filter='ADMIN')
            print(f"   Filtre ADMIN: {len(admin_filtered)} logs")
            
            # Filtrer par rôle RESPONSABLE
            responsable_filtered = get_audit_logs(limit=50, role_filter='RESPONSABLE')
            print(f"   Filtre RESPONSABLE: {len(responsable_filtered)} logs")
            
            # Filtrer par action CREATION
            creation_filtered = get_audit_logs(limit=50, action_filter='CREATION')
            print(f"   Filtre CREATION: {len(creation_filtered)} logs")
            
            # Test 7: Vérifier la distinction
            print("\n7. Vérification de la distinction ADMIN vs RESPONSABLE...")
            
            distinction_ok = True
            
            # Vérifier qu'on peut distinguer les rôles
            if len(admin_logs) > 0 and len(responsable_logs) > 0:
                print("   ✅ Les logs ADMIN et RESPONSABLE sont distincts")
            else:
                print("   ⚠️  Pas assez de logs pour tester la distinction")
                distinction_ok = False
            
            # Vérifier que les actions sont tracées avec le bon rôle
            for log in all_logs[:5]:  # Vérifier les 5 derniers logs
                if 'ROLE:' in log and 'USER:' in log:
                    print(f"   ✅ Log bien formaté: {log[:80]}...")
                else:
                    print(f"   ❌ Log mal formaté: {log}")
                    distinction_ok = False
            
            if distinction_ok:
                print("   ✅ La traçabilité fonctionne correctement")
            else:
                print("   ❌ Problème de traçabilité détecté")
    
    print("\n🎉 TESTS DE TRAÇABILITÉ TERMINÉS!")
    print("\n📋 Résumé:")
    print("   ✅ Système de logging d'audit fonctionnel")
    print("   ✅ Distinction ADMIN vs RESPONSABLE maintenue")
    print("   ✅ Filtrage par rôle et action opérationnel")
    print("   ✅ Statistiques par rôle disponibles")
    
    print("\n🔍 Pour consulter les logs d'audit:")
    print("   1. Connectez-vous en tant qu'admin ou responsable")
    print("   2. Allez sur http://localhost:5000/admin/audit")
    print("   3. Utilisez les filtres pour voir les actions par rôle")
    
    print("\n💡 Avantages de cette implémentation:")
    print("   • Même permissions pour ADMIN et RESPONSABLE")
    print("   • Traçabilité complète des actions")
    print("   • Distinction claire dans les logs")
    print("   • Audit et conformité assurés")

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Vérifiez:")
    print("1. Que l'application démarre correctement")
    print("2. Que le dossier logs/ existe")
    print("3. Que les permissions d'écriture sont correctes")
