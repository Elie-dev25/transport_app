#!/usr/bin/env python3
"""
Script pour créer un utilisateur chauffeur de test
"""

try:
    print("🚌 Création d'un utilisateur chauffeur de test...")
    
    from app import create_app
    from app.models.utilisateur import Utilisateur
    from app.database import db
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée et contexte activé")
        
        # Vérifier si l'utilisateur chauffeur existe déjà
        existing_chauffeur = Utilisateur.query.filter_by(login='chauffeur').first()
        
        if existing_chauffeur:
            print("⚠️  L'utilisateur 'chauffeur' existe déjà")
            print(f"   Nom: {existing_chauffeur.nom} {existing_chauffeur.prenom}")
            print(f"   Email: {existing_chauffeur.email}")
            print(f"   Rôle: {existing_chauffeur.role}")
        else:
            # Créer l'utilisateur chauffeur
            chauffeur = Utilisateur(
                nom='Dupont',
                prenom='Jean',
                login='chauffeur',
                role='CHAUFFEUR',
                email='chauffeur@udm.local',
                telephone='123-456-789'
            )
            
            # Définir le mot de passe
            chauffeur.set_password('chauffeur123')
            
            # Ajouter à la base de données
            db.session.add(chauffeur)
            db.session.commit()
            
            print("✅ Utilisateur chauffeur créé avec succès!")
            print(f"   Login: chauffeur")
            print(f"   Mot de passe: chauffeur123")
            print(f"   Nom: {chauffeur.nom} {chauffeur.prenom}")
            print(f"   Email: {chauffeur.email}")
            print(f"   Téléphone: {chauffeur.telephone}")
            print(f"   Rôle: {chauffeur.role}")
        
        # Afficher tous les utilisateurs chauffeur
        print("\n📋 Tous les utilisateurs CHAUFFEUR:")
        chauffeurs = Utilisateur.query.filter_by(role='CHAUFFEUR').all()
        
        if chauffeurs:
            for c in chauffeurs:
                print(f"   • {c.nom} {c.prenom} ({c.login}) - {c.email}")
        else:
            print("   Aucun chauffeur trouvé")
        
        print("\n🎯 INSTRUCTIONS DE CONNEXION:")
        print("1. Démarrez l'application: python start_app.py")
        print("2. Allez sur: http://localhost:5000")
        print("3. Connectez-vous avec:")
        print("   Login: chauffeur")
        print("   Mot de passe: chauffeur123")
        print("4. Vous serez redirigé vers: /chauffeur/dashboard")
        
        print("\n✅ Script terminé avec succès!")

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Vérifiez:")
    print("1. Que la base de données est accessible")
    print("2. Que les modèles sont correctement définis")
    print("3. Que l'application démarre sans erreur")
