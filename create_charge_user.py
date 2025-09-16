#!/usr/bin/env python3
"""
Script pour créer un utilisateur CHARGE de test
"""
from app import create_app
from app.models.utilisateur import Utilisateur
from app.models.chargetransport import Chargetransport
from app.database import db
from werkzeug.security import generate_password_hash

def create_charge_user():
    app = create_app()
    with app.app_context():
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = Utilisateur.query.filter_by(login='charge_test').first()
            if existing_user:
                print("✅ Utilisateur charge_test existe déjà")
                print(f"   Login: {existing_user.login}")
                print(f"   Nom: {existing_user.nom} {existing_user.prenom}")
                print(f"   Rôle: {existing_user.role}")
                return
            
            # Créer l'utilisateur CHARGE
            password_hash = generate_password_hash('charge123')
            
            charge_user = Utilisateur(
                nom='Transport',
                prenom='Chargé',
                login='charge_test',
                mot_de_passe=password_hash,
                role='CHARGE',
                email='charge@udm.edu.cm',
                telephone='+237123456789'
            )
            
            db.session.add(charge_user)
            db.session.flush()  # Pour obtenir l'ID
            
            # Créer l'entrée dans chargetransport
            charge_transport = Chargetransport(
                chargetransport_id=charge_user.utilisateur_id
            )
            
            db.session.add(charge_transport)
            db.session.commit()
            
            print("✅ Utilisateur CHARGE créé avec succès!")
            print(f"   Login: charge_test")
            print(f"   Mot de passe: charge123")
            print(f"   Nom: Chargé Transport")
            print(f"   Email: charge@udm.edu.cm")
            print(f"   ID: {charge_user.utilisateur_id}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la création: {str(e)}")

if __name__ == '__main__':
    create_charge_user()
