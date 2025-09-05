#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test dans la base MySQL
Usage: python create_test_user.py
"""

from app import create_app
from app.database import db
from app.models.utilisateur import Utilisateur

def create_test_user():
    app = create_app()
    
    with app.app_context():
        # Vérifier si l'utilisateur existe déjà
        existing_user = Utilisateur.query.filter_by(login='admin').first()
        if existing_user:
            print("L'utilisateur 'admin' existe déjà.")
            print(f"Rôle actuel: {existing_user.role}")
            
            # Mettre à jour le mot de passe
            existing_user.set_password('admin123')
            existing_user.role = 'ADMIN'
            db.session.commit()
            print("Mot de passe mis à jour: admin123")
            return
        
        # Créer un nouvel utilisateur admin
        admin_user = Utilisateur(
            nom='Administrateur',
            prenom='Test',
            login='admin',
            role='ADMIN',
            email='admin@domaine.local',
            telephone='0000000000'
        )
        
        # Définir le mot de passe
        admin_user.set_password('admin123')
        
        # Ajouter à la base
        db.session.add(admin_user)
        db.session.commit()
        
        print("Utilisateur de test créé avec succès:")
        print("Login: admin")
        print("Mot de passe: admin123")
        print("Rôle: ADMIN")

if __name__ == '__main__':
    create_test_user()
