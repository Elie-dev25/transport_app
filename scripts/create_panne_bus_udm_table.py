"""
Script de migration pour créer la table panne_bus_udm
"""
from app import create_app
from app.database import db
from app.models.panne_bus_udm import PanneBusUdM

def create_panne_table():
    app = create_app()
    with app.app_context():
        try:
            # Créer la table panne_bus_udm
            db.create_all()
            print("Table panne_bus_udm créée avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création de la table: {e}")

if __name__ == '__main__':
    create_panne_table()
