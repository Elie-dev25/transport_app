#!/usr/bin/env python3
"""
Script de test pour le rôle SUPERVISEUR
Vérifie que le nouveau rôle fonctionne correctement
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.utilisateur import Utilisateur
from app.database import db
from werkzeug.security import generate_password_hash

def test_superviseur_role():
    """Test complet du rôle SUPERVISEUR"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Test du rôle SUPERVISEUR")
        print("=" * 50)
        
        try:
            # Test 1: Vérifier que l'énumération accepte SUPERVISEUR
            print("\n1. Test de l'énumération des rôles...")
            
            # Créer un utilisateur superviseur de test
            test_user = Utilisateur(
                nom="Test",
                prenom="Superviseur",
                login="test.superviseur",
                role="SUPERVISEUR",
                email="test.superviseur@udm.local",
                telephone="123456789"
            )
            test_user.set_password("password123")
            
            # Tenter d'ajouter à la base
            db.session.add(test_user)
            db.session.commit()
            print("   ✅ Utilisateur SUPERVISEUR créé avec succès")
            
            # Test 2: Vérifier la récupération
            print("\n2. Test de récupération de l'utilisateur...")
            retrieved_user = Utilisateur.query.filter_by(login="test.superviseur").first()
            
            if retrieved_user and retrieved_user.role == "SUPERVISEUR":
                print("   ✅ Utilisateur SUPERVISEUR récupéré correctement")
                print(f"   📋 Détails: {retrieved_user.nom} {retrieved_user.prenom} - {retrieved_user.role}")
            else:
                print("   ❌ Erreur lors de la récupération")
                return False
            
            # Test 3: Vérifier l'authentification
            print("\n3. Test d'authentification...")
            if retrieved_user.check_password("password123"):
                print("   ✅ Authentification réussie")
            else:
                print("   ❌ Échec de l'authentification")
                return False
            
            # Test 4: Compter les utilisateurs par rôle
            print("\n4. Statistiques des rôles...")
            roles_stats = db.session.query(
                Utilisateur.role, 
                db.func.count(Utilisateur.utilisateur_id)
            ).group_by(Utilisateur.role).all()
            
            for role, count in roles_stats:
                print(f"   📊 {role}: {count} utilisateur(s)")
            
            # Test 5: Nettoyer (supprimer l'utilisateur de test)
            print("\n5. Nettoyage...")
            db.session.delete(retrieved_user)
            db.session.commit()
            print("   ✅ Utilisateur de test supprimé")
            
            print("\n" + "=" * 50)
            print("🎉 TOUS LES TESTS RÉUSSIS!")
            print("✅ Le rôle SUPERVISEUR est correctement configuré")
            return True
            
        except Exception as e:
            print(f"\n❌ ERREUR: {str(e)}")
            print("💡 Vérifiez que le script SQL a été exécuté correctement")
            db.session.rollback()
            return False

def create_superviseur_user():
    """Créer un utilisateur superviseur permanent"""
    
    app = create_app()
    
    with app.app_context():
        print("👤 Création d'un utilisateur SUPERVISEUR permanent")
        print("=" * 50)
        
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = Utilisateur.query.filter_by(login="superviseur").first()
            if existing_user:
                print("⚠️  Un utilisateur 'superviseur' existe déjà")
                print(f"   Rôle actuel: {existing_user.role}")
                
                # Mettre à jour le rôle si nécessaire
                if existing_user.role != "SUPERVISEUR":
                    existing_user.role = "SUPERVISEUR"
                    db.session.commit()
                    print("   ✅ Rôle mis à jour vers SUPERVISEUR")
                return True
            
            # Créer un nouvel utilisateur superviseur
            superviseur = Utilisateur(
                nom="Superviseur",
                prenom="Principal",
                login="superviseur",
                role="SUPERVISEUR",
                email="superviseur@udm.local",
                telephone="000000000"
            )
            superviseur.set_password("superviseur123")
            
            db.session.add(superviseur)
            db.session.commit()
            
            print("✅ Utilisateur SUPERVISEUR créé avec succès!")
            print("📋 Détails de connexion:")
            print(f"   Login: superviseur")
            print(f"   Mot de passe: superviseur123")
            print(f"   Rôle: SUPERVISEUR")
            print(f"   Email: superviseur@udm.local")
            
            return True
            
        except Exception as e:
            print(f"❌ ERREUR lors de la création: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Script de test du rôle SUPERVISEUR")
    print("Choisissez une option:")
    print("1. Tester le rôle SUPERVISEUR")
    print("2. Créer un utilisateur SUPERVISEUR permanent")
    print("3. Les deux")
    
    choice = input("\nVotre choix (1/2/3): ").strip()
    
    if choice in ["1", "3"]:
        print("\n" + "🔍" * 20)
        success = test_superviseur_role()
        if not success:
            sys.exit(1)
    
    if choice in ["2", "3"]:
        print("\n" + "👤" * 20)
        success = create_superviseur_user()
        if not success:
            sys.exit(1)
    
    if choice not in ["1", "2", "3"]:
        print("❌ Choix invalide")
        sys.exit(1)
    
    print("\n🎉 Script terminé avec succès!")
