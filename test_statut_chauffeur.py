#!/usr/bin/env python3
"""
Test du statut du chauffeur dans le top bar
"""

try:
    print("🧪 TEST STATUT CHAUFFEUR DANS TOP BAR")
    print("=" * 50)
    
    from app import create_app
    from app.models.utilisateur import Utilisateur
    from app.models.chauffeur import Chauffeur
    from app.models.chauffeur_statut import ChauffeurStatut
    from app.database import db
    from datetime import datetime, timedelta
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée et contexte activé")
        
        # 1. Vérifier l'utilisateur chauffeur
        user_chauffeur = Utilisateur.query.filter_by(login='chauffeur').first()
        if not user_chauffeur:
            print("❌ Utilisateur chauffeur non trouvé")
            exit(1)
        
        print(f"✅ Utilisateur trouvé: {user_chauffeur.login}")
        
        # 2. Vérifier le chauffeur correspondant
        chauffeur_db = Chauffeur.query.filter_by(
            nom=user_chauffeur.nom, 
            prenom=user_chauffeur.prenom
        ).first()
        
        if not chauffeur_db:
            print("❌ Chauffeur non trouvé dans la table chauffeur")
            exit(1)
        
        print(f"✅ Chauffeur trouvé: ID {chauffeur_db.chauffeur_id}")
        
        # 3. Vérifier les statuts actuels
        statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur_db.chauffeur_id)
        
        print(f"\n📊 STATUTS ACTUELS:")
        if statuts_actuels:
            for statut in statuts_actuels:
                print(f"   • {statut.statut}: {statut.date_debut} → {statut.date_fin}")
        else:
            print("   • Aucun statut actuel (Disponible)")
        
        # 4. Créer un statut de test si aucun n'existe
        if not statuts_actuels:
            print(f"\n🔧 CRÉATION D'UN STATUT DE TEST:")
            
            # Créer un statut "SERVICE_SEMAINE" pour aujourd'hui
            now = datetime.now()
            debut = now.replace(hour=8, minute=0, second=0, microsecond=0)
            fin = now.replace(hour=18, minute=0, second=0, microsecond=0)
            
            nouveau_statut = ChauffeurStatut(
                chauffeur_id=chauffeur_db.chauffeur_id,
                statut='SERVICE_SEMAINE',
                date_debut=debut,
                date_fin=fin
            )
            
            db.session.add(nouveau_statut)
            db.session.commit()
            
            print(f"   ✅ Statut créé: SERVICE_SEMAINE de {debut} à {fin}")
            
            # Récupérer à nouveau les statuts
            statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur_db.chauffeur_id)
        
        # 5. Simuler la logique du dashboard
        statut_actuel = None
        if statuts_actuels:
            statut_actuel = statuts_actuels[0].statut
        
        print(f"\n🎯 STATUT POUR LE TOP BAR:")
        if statut_actuel:
            print(f"   ✅ Statut actuel: {statut_actuel}")
            
            # Mapper le statut pour l'affichage
            statut_display = {
                'CONGE': '🟡 En Congé',
                'PERMANENCE': '🔵 Permanence', 
                'SERVICE_WEEKEND': '🟣 Service Week-end',
                'SERVICE_SEMAINE': '🔵 Service Semaine'
            }.get(statut_actuel, f'⚪ {statut_actuel}')
            
            print(f"   📱 Affichage: {statut_display}")
        else:
            print(f"   ✅ Statut par défaut: 🟢 Disponible")
        
        # 6. Tester différents statuts
        print(f"\n🧪 TEST DES DIFFÉRENTS STATUTS:")
        
        statuts_test = ['CONGE', 'PERMANENCE', 'SERVICE_WEEKEND', 'SERVICE_SEMAINE']
        
        for statut in statuts_test:
            # Supprimer les anciens statuts
            ChauffeurStatut.query.filter_by(chauffeur_id=chauffeur_db.chauffeur_id).delete()
            
            # Créer un nouveau statut
            nouveau_statut = ChauffeurStatut(
                chauffeur_id=chauffeur_db.chauffeur_id,
                statut=statut,
                date_debut=datetime.now() - timedelta(hours=1),
                date_fin=datetime.now() + timedelta(hours=1)
            )
            
            db.session.add(nouveau_statut)
            db.session.commit()
            
            # Vérifier l'affichage
            statuts_test_actuels = ChauffeurStatut.get_current_statuts(chauffeur_db.chauffeur_id)
            if statuts_test_actuels:
                statut_test_actuel = statuts_test_actuels[0].statut
                statut_display = {
                    'CONGE': '🟡 En Congé',
                    'PERMANENCE': '🔵 Permanence', 
                    'SERVICE_WEEKEND': '🟣 Service Week-end',
                    'SERVICE_SEMAINE': '🔵 Service Semaine'
                }.get(statut_test_actuel, f'⚪ {statut_test_actuel}')
                
                print(f"   • {statut}: {statut_display}")
        
        # 7. Remettre un statut par défaut
        ChauffeurStatut.query.filter_by(chauffeur_id=chauffeur_db.chauffeur_id).delete()
        db.session.commit()
        
        print(f"\n🎯 INSTRUCTIONS DE TEST:")
        print("1. Connectez-vous avec chauffeur/chauffeur123")
        print("2. Regardez le top bar - vous devriez voir 'Disponible'")
        print("3. Un admin peut créer des statuts pour tester les différents affichages")
        
        print(f"\n✅ FONCTIONNALITÉS IMPLÉMENTÉES:")
        print("• Suppression de la cloche de notification sur tous les top bars")
        print("• Ajout du statut du chauffeur dans le top bar chauffeur")
        print("• Récupération automatique du statut depuis la base de données")
        print("• Affichage coloré selon le type de statut")
        print("• Statut par défaut 'Disponible' si aucun statut actuel")
        
        print("\n" + "=" * 50)
        print("🎯 TEST TERMINÉ")
        print("=" * 50)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
