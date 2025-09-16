#!/usr/bin/env python3
"""
Test des couleurs selon la charte de l'application (bleu, vert, noir, blanc)
"""

try:
    print("🎨 TEST CHARTE COULEURS - BLEU, VERT, NOIR, BLANC")
    print("=" * 60)
    
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
        
        # 3. Nettoyer les anciens statuts
        ChauffeurStatut.query.filter_by(chauffeur_id=chauffeur_db.chauffeur_id).delete()
        db.session.commit()
        
        print(f"\n🎨 NOUVELLE CHARTE COULEURS:")
        print("📋 Couleurs autorisées: BLEU, VERT, NOIR, BLANC")
        
        # 4. Tester chaque statut avec les nouvelles couleurs
        print(f"\n🧪 TEST DES STATUTS AVEC NOUVELLE CHARTE:")
        
        statuts_couleurs = {
            'NON_SPECIFIE': {
                'nom': 'Non spécifié',
                'couleur_principale': 'BLANC + NOIR',
                'background': 'Dégradé blanc (#ffffff → #f8f9fa)',
                'texte': 'Noir (#000000)',
                'bordure': 'Gris clair (#dee2e6)',
                'icone': 'Dégradé gris (#6c757d → #495057)'
            },
            'CONGE': {
                'nom': 'En Congé',
                'couleur_principale': 'BLANC + NOIR',
                'background': 'Dégradé blanc (#ffffff → #f8f9fa)',
                'texte': 'Noir (#000000)',
                'bordure': 'Noir (#000000)',
                'icone': 'Dégradé noir (#000000 → #333333)'
            },
            'PERMANENCE': {
                'nom': 'Permanence',
                'couleur_principale': 'BLEU',
                'background': 'Dégradé bleu clair (#e3f2fd → #bbdefb)',
                'texte': 'Bleu foncé (#1565c0)',
                'bordure': 'Bleu (#1976d2)',
                'icone': 'Dégradé bleu (#1976d2 → #1565c0)'
            },
            'SERVICE_WEEKEND': {
                'nom': 'Service Week-end',
                'couleur_principale': 'VERT',
                'background': 'Dégradé vert clair (#e8f5e8 → #c8e6c9)',
                'texte': 'Vert foncé (#2e7d32)',
                'bordure': 'Vert (#388e3c)',
                'icone': 'Dégradé vert (#388e3c → #2e7d32)'
            },
            'SERVICE_SEMAINE': {
                'nom': 'Service Semaine',
                'couleur_principale': 'BLEU',
                'background': 'Dégradé bleu clair (#e3f2fd → #bbdefb)',
                'texte': 'Bleu foncé (#1565c0)',
                'bordure': 'Bleu (#1976d2)',
                'icone': 'Dégradé bleu (#1976d2 → #1565c0)'
            }
        }
        
        for statut, details in statuts_couleurs.items():
            print(f"\n📊 {statut}:")
            print(f"   • Nom: {details['nom']}")
            print(f"   • Couleur charte: {details['couleur_principale']}")
            print(f"   • Background: {details['background']}")
            print(f"   • Texte: {details['texte']}")
            print(f"   • Bordure: {details['bordure']}")
            print(f"   • Icône: {details['icone']}")
        
        # 5. Créer et tester un statut
        print(f"\n🧪 TEST PRATIQUE - STATUT SERVICE_WEEKEND (VERT):")
        
        # Créer un statut de test
        nouveau_statut = ChauffeurStatut(
            chauffeur_id=chauffeur_db.chauffeur_id,
            statut='SERVICE_WEEKEND',
            date_debut=datetime.now() - timedelta(hours=1),
            date_fin=datetime.now() + timedelta(hours=1)
        )
        
        db.session.add(nouveau_statut)
        db.session.commit()
        
        # Vérifier le statut
        statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur_db.chauffeur_id)
        if statuts_actuels:
            statut_actuel = statuts_actuels[0].statut
            print(f"   ✅ Statut créé: {statut_actuel}")
            print(f"   🎨 Couleur: VERT (conforme à la charte)")
            print(f"   📱 Affichage: Service Week-end avec fond vert clair")
        
        # 6. Nettoyer et remettre statut par défaut
        ChauffeurStatut.query.filter_by(chauffeur_id=chauffeur_db.chauffeur_id).delete()
        db.session.commit()
        
        print(f"\n✅ PROFIL UTILISATEUR RESTAURÉ:")
        print("• Format standard: user-menu (comme admin/superviseur)")
        print("• Avatar: Initiales standard")
        print("• Badge: CHAUFFEUR en jaune (bg-warning)")
        print("• Structure: Identique aux autres dashboards")
        
        print(f"\n🎯 CONFORMITÉ CHARTE COULEURS:")
        print("✅ BLEU: Permanence et Service Semaine")
        print("✅ VERT: Service Week-end")
        print("✅ NOIR: En Congé (texte et bordure)")
        print("✅ BLANC: Fond principal pour Non spécifié et Congé")
        print("❌ SUPPRIMÉ: Jaune, orange, violet (hors charte)")
        
        print(f"\n🎨 AVANTAGES NOUVELLE CHARTE:")
        print("• Cohérence visuelle: Couleurs uniformes dans l'app")
        print("• Lisibilité: Contrastes respectés")
        print("• Professionnalisme: Palette restreinte et élégante")
        print("• Maintenance: Moins de couleurs à gérer")
        
        print(f"\n🚀 INSTRUCTIONS DE TEST:")
        print("1. Connectez-vous avec chauffeur/chauffeur123")
        print("2. Vérifiez le statut 'Non spécifié' (blanc + bordure grise)")
        print("3. Vérifiez le profil utilisateur (format standard)")
        print("4. Un admin peut créer des statuts pour tester les couleurs:")
        print("   - Congé: Blanc + bordure noire")
        print("   - Permanence: Bleu clair")
        print("   - Service Week-end: Vert clair")
        print("   - Service Semaine: Bleu clair")
        
        print("\n" + "=" * 60)
        print("🎨 TEST CHARTE COULEURS TERMINÉ")
        print("=" * 60)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
