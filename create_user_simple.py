#!/usr/bin/env python3
"""
Script simple pour créer un utilisateur superviseur
"""

from app import create_app
from app.models.utilisateur import Utilisateur
from app.database import db

def main():
    app = create_app()
    
    with app.app_context():
        print("Création utilisateur superviseur...")
        
        # Supprimer l'utilisateur existant s'il existe
        existing = Utilisateur.query.filter_by(login="superviseur").first()
        if existing:
            db.session.delete(existing)
            print("Utilisateur existant supprimé")
        
        # Créer le nouvel utilisateur
        user = Utilisateur(
            nom="Superviseur",
            prenom="Test",
            login="superviseur",
            role="ADMIN",  # Utiliser ADMIN temporairement
            email="superviseur@test.com",
            telephone="123456789"
        )
        user.set_password("superviseur123")
        
        db.session.add(user)
        db.session.commit()
        
        print("Utilisateur créé avec succès!")
        print("Login: superviseur")
        print("Mot de passe: superviseur123")
        print("Rôle: ADMIN (temporaire)")

if __name__ == "__main__":
    main()
