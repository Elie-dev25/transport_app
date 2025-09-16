#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test avec le rôle RESPONSABLE
"""

try:
    print("🔧 Création d'un utilisateur RESPONSABLE...")
    
    from app import create_app
    from app.models.utilisateur import Utilisateur
    from app.database import db
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée et contexte activé")
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = Utilisateur.query.filter_by(login='responsable').first()
        if existing_user:
            print("⚠️  L'utilisateur 'responsable' existe déjà")
            print(f"   Rôle actuel: {existing_user.role}")
            
            # Mettre à jour le rôle si nécessaire
            if existing_user.role != 'RESPONSABLE':
                existing_user.role = 'RESPONSABLE'
                db.session.commit()
                print("✅ Rôle mis à jour vers RESPONSABLE")
            else:
                print("✅ L'utilisateur a déjà le bon rôle")
        else:
            # Créer le nouvel utilisateur
            responsable_user = Utilisateur(
                nom='Responsable',
                prenom='Transport',
                login='responsable',
                role='RESPONSABLE',
                email='responsable@udm.local',
                telephone='123456789'
            )
            
            # Définir le mot de passe
            responsable_user.set_password('responsable123')
            
            # Ajouter à la base de données
            db.session.add(responsable_user)
            db.session.commit()
            
            print("✅ Utilisateur RESPONSABLE créé avec succès!")
            print("   Login: responsable")
            print("   Mot de passe: responsable123")
        
        # Vérifier tous les utilisateurs avec leurs rôles
        print("\n📋 Liste des utilisateurs par rôle:")
        users = Utilisateur.query.all()
        roles_count = {}
        
        for user in users:
            role = user.role or 'AUCUN'
            if role not in roles_count:
                roles_count[role] = []
            roles_count[role].append(f"{user.login} ({user.nom} {user.prenom})")
        
        for role, users_list in roles_count.items():
            print(f"   {role}: {len(users_list)} utilisateur(s)")
            for user_info in users_list:
                print(f"     - {user_info}")
        
        print("\n🎉 Configuration terminée!")
        print("\n🔐 Comptes de test disponibles:")
        print("   👑 Admin: admin / admin123")
        print("   🏢 Responsable: responsable / responsable123")
        print("   👁️  Superviseur: superviseur / superviseur123")
        
        print("\n💡 Le responsable a les mêmes permissions que l'administrateur")
        print("   Il peut accéder à toutes les fonctionnalités admin")

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Solutions possibles:")
    print("1. Vérifiez que MySQL est démarré")
    print("2. Vérifiez la configuration dans app/config.py")
    print("3. Exécutez d'abord le script de migration SQL")
    print("4. Installez les dépendances: pip install -r requirements.txt")
    
    input("\nAppuyez sur Entrée pour quitter...")
