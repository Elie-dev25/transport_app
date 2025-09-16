#!/usr/bin/env python3
"""
Script pour créer un utilisateur SUPERVISEUR
Résout le problème de hash de mot de passe
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.utilisateur import Utilisateur
from app.database import db
from werkzeug.security import generate_password_hash

def create_superviseur():
    """Créer un utilisateur superviseur avec mot de passe correctement hashé"""
    
    app = create_app()
    
    with app.app_context():
        print("👤 Création d'un utilisateur SUPERVISEUR")
        print("=" * 50)
        
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = Utilisateur.query.filter_by(login="superviseur").first()
            if existing_user:
                print("⚠️  Un utilisateur 'superviseur' existe déjà")
                print(f"   Rôle actuel: {existing_user.role}")
                print(f"   Hash actuel: {existing_user.mot_de_passe[:20]}...")
                
                # Mettre à jour le mot de passe et le rôle
                existing_user.role = "SUPERVISEUR"
                existing_user.set_password("superviseur123")
                db.session.commit()
                print("   ✅ Utilisateur mis à jour avec nouveau mot de passe")
                
                # Test du mot de passe
                if existing_user.check_password("superviseur123"):
                    print("   ✅ Test du mot de passe réussi")
                else:
                    print("   ❌ Test du mot de passe échoué")
                
                return True
            
            # Créer un nouvel utilisateur superviseur
            print("🆕 Création d'un nouvel utilisateur superviseur...")
            
            superviseur = Utilisateur(
                nom="Superviseur",
                prenom="Principal",
                login="superviseur",
                role="SUPERVISEUR",
                email="superviseur@udm.local",
                telephone="000000000"
            )
            
            # Utiliser la méthode set_password pour hasher correctement
            superviseur.set_password("superviseur123")
            
            print(f"   Hash généré: {superviseur.mot_de_passe[:20]}...")
            
            db.session.add(superviseur)
            db.session.commit()
            
            print("✅ Utilisateur SUPERVISEUR créé avec succès!")
            
            # Test immédiat du mot de passe
            test_user = Utilisateur.query.filter_by(login="superviseur").first()
            if test_user and test_user.check_password("superviseur123"):
                print("✅ Test du mot de passe réussi")
            else:
                print("❌ Test du mot de passe échoué")
                return False
            
            print("\n📋 Détails de connexion:")
            print(f"   Login: superviseur")
            print(f"   Mot de passe: superviseur123")
            print(f"   Rôle: SUPERVISEUR")
            print(f"   Email: superviseur@udm.local")
            
            return True
            
        except Exception as e:
            print(f"❌ ERREUR lors de la création: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def create_admin_user():
    """Créer aussi un utilisateur admin pour les tests"""
    
    app = create_app()
    
    with app.app_context():
        print("\n👑 Création d'un utilisateur ADMIN")
        print("=" * 50)
        
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = Utilisateur.query.filter_by(login="admin").first()
            if existing_user:
                print("⚠️  Un utilisateur 'admin' existe déjà")
                existing_user.role = "ADMIN"
                existing_user.set_password("admin123")
                db.session.commit()
                print("   ✅ Utilisateur admin mis à jour")
                return True
            
            # Créer un nouvel utilisateur admin
            admin = Utilisateur(
                nom="Administrateur",
                prenom="Principal",
                login="admin",
                role="ADMIN",
                email="admin@udm.local",
                telephone="111111111"
            )
            
            admin.set_password("admin123")
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Utilisateur ADMIN créé avec succès!")
            print("📋 Login: admin | Mot de passe: admin123")
            
            return True
            
        except Exception as e:
            print(f"❌ ERREUR lors de la création admin: {str(e)}")
            db.session.rollback()
            return False

def list_users():
    """Lister tous les utilisateurs"""
    
    app = create_app()
    
    with app.app_context():
        print("\n📋 Liste des utilisateurs")
        print("=" * 50)
        
        try:
            users = Utilisateur.query.all()
            
            if not users:
                print("Aucun utilisateur trouvé")
                return
            
            for user in users:
                print(f"👤 {user.login} ({user.nom} {user.prenom})")
                print(f"   Rôle: {user.role}")
                print(f"   Email: {user.email}")
                print(f"   Hash: {user.mot_de_passe[:20]}...")
                print()
                
        except Exception as e:
            print(f"❌ ERREUR: {str(e)}")

if __name__ == "__main__":
    print("🚀 Script de création d'utilisateurs")
    print("Choisissez une option:")
    print("1. Créer utilisateur SUPERVISEUR")
    print("2. Créer utilisateur ADMIN") 
    print("3. Créer les deux")
    print("4. Lister les utilisateurs existants")
    
    choice = input("\nVotre choix (1/2/3/4): ").strip()
    
    if choice in ["1", "3"]:
        success = create_superviseur()
        if not success:
            sys.exit(1)
    
    if choice in ["2", "3"]:
        success = create_admin_user()
        if not success:
            sys.exit(1)
    
    if choice == "4":
        list_users()
    
    if choice not in ["1", "2", "3", "4"]:
        print("❌ Choix invalide")
        sys.exit(1)
    
    print("\n🎉 Script terminé avec succès!")
    print("💡 Vous pouvez maintenant vous connecter à l'application")
