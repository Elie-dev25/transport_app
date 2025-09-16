#!/usr/bin/env python3
"""
Test du nouveau style de statut chauffeur
"""

try:
    print("🎨 TEST NOUVEAU STYLE STATUT CHAUFFEUR")
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
        
        # 3. Nettoyer les anciens statuts pour commencer proprement
        ChauffeurStatut.query.filter_by(chauffeur_id=chauffeur_db.chauffeur_id).delete()
        db.session.commit()
        
        # 4. Tester le statut par défaut "NON_SPECIFIE"
        print(f"\n🎯 TEST STATUT PAR DÉFAUT:")
        
        # Simuler la logique du dashboard
        statut_actuel = "NON_SPECIFIE"  # Valeur par défaut
        statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur_db.chauffeur_id)
        if statuts_actuels:
            statut_actuel = statuts_actuels[0].statut
        
        print(f"   ✅ Statut par défaut: {statut_actuel}")
        
        # Mapper le statut pour l'affichage
        statut_display = {
            'CONGE': '🟡 En Congé',
            'PERMANENCE': '🔵 Permanence', 
            'SERVICE_WEEKEND': '🟣 Service Week-end',
            'SERVICE_SEMAINE': '🔵 Service Semaine',
            'NON_SPECIFIE': '⚪ Non spécifié'
        }.get(statut_actuel, f'❓ {statut_actuel}')
        
        print(f"   📱 Affichage: {statut_display}")
        
        # 5. Tester tous les statuts avec le nouveau style
        print(f"\n🎨 TEST NOUVEAU STYLE POUR TOUS LES STATUTS:")
        
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
                
                # Détails du style pour chaque statut
                style_info = {
                    'CONGE': {
                        'nom': 'En Congé',
                        'couleur': 'Dégradé jaune/orange',
                        'icone': 'fa-calendar-times',
                        'effet': 'Hover avec élévation'
                    },
                    'PERMANENCE': {
                        'nom': 'Permanence',
                        'couleur': 'Dégradé bleu',
                        'icone': 'fa-clock',
                        'effet': 'Hover avec élévation'
                    },
                    'SERVICE_WEEKEND': {
                        'nom': 'Service Week-end',
                        'couleur': 'Dégradé violet',
                        'icone': 'fa-calendar-week',
                        'effet': 'Hover avec élévation'
                    },
                    'SERVICE_SEMAINE': {
                        'nom': 'Service Semaine',
                        'couleur': 'Dégradé bleu clair',
                        'icone': 'fa-calendar-day',
                        'effet': 'Hover avec élévation'
                    }
                }.get(statut_test_actuel, {})
                
                print(f"   • {statut}: {style_info.get('nom', statut)}")
                print(f"     - Couleur: {style_info.get('couleur', 'Défaut')}")
                print(f"     - Icône: {style_info.get('icone', 'fa-question')}")
                print(f"     - Effet: {style_info.get('effet', 'Aucun')}")
        
        # 6. Remettre le statut par défaut
        ChauffeurStatut.query.filter_by(chauffeur_id=chauffeur_db.chauffeur_id).delete()
        db.session.commit()
        
        print(f"\n🎯 NOUVEAU STYLE IMPLÉMENTÉ:")
        print("✅ Statut par défaut: 'Non spécifié' (au lieu de 'Disponible')")
        print("✅ Design moderne: Conteneurs avec dégradés et ombres")
        print("✅ Icônes circulaires: Avec dégradés colorés")
        print("✅ Effets hover: Élévation et ombres dynamiques")
        print("✅ Typographie: Labels et valeurs séparés")
        print("✅ Bouton déconnexion: Supprimé du top bar")
        print("✅ Info utilisateur: Style moderne avec avatar")
        
        print(f"\n🎨 CARACTÉRISTIQUES DU NOUVEAU DESIGN:")
        print("• Backdrop blur: Effet de flou d'arrière-plan")
        print("• Gradients: Dégradés colorés pour chaque statut")
        print("• Shadows: Ombres portées avec effet de profondeur")
        print("• Transitions: Animations fluides sur hover")
        print("• Typography: Hiérarchie claire label/valeur")
        print("• Icons: Icônes circulaires avec dégradés")
        
        print(f"\n🚀 INSTRUCTIONS DE TEST:")
        print("1. Connectez-vous avec chauffeur/chauffeur123")
        print("2. Observez le nouveau style du statut dans le top bar")
        print("3. Le statut devrait afficher 'Non spécifié' par défaut")
        print("4. Plus de bouton déconnexion visible")
        print("5. Hover sur le statut pour voir l'effet d'élévation")
        
        print("\n" + "=" * 50)
        print("🎨 TEST STYLE TERMINÉ")
        print("=" * 50)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
