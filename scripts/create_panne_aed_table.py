"""
Script de migration pour créer la table panne_aed
"""
from app import create_app
from app.database import db
from app.models.panne_aed import PanneAED

def create_panne_table():
    app = create_app()
    with app.app_context():
        try:
            # Créer la table panne_aed
            db.create_all()
            print("Table panne_aed créée avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création de la table: {e}")

if __name__ == '__main__':
    create_panne_table()
