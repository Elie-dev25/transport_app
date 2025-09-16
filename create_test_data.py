#!/usr/bin/env python3
"""
Créer des données de test pour les formulaires
"""

from app import create_app
from app.models.bus_udm import BusUdM
from app.models.chauffeur import Chauffeur  
from app.models.prestataire import Prestataire
from app.database import db

def create_test_data():
    """Créer des données de test"""
    app = create_app()
    
    with app.app_context():
        print("Création des données de test...")
        
        # Créer des bus de test s'ils n'existent pas
        if BusUdM.query.count() == 0:
            print("Création de bus de test...")
            bus1 = BusUdM(numero="001", etat_vehicule="BON", kilometrage=15000)
            bus2 = BusUdM(numero="002", etat_vehicule="BON", kilometrage=22000)
            bus3 = BusUdM(numero="003", etat_vehicule="DEFAILLANT", kilometrage=35000)
            
            db.session.add_all([bus1, bus2, bus3])
        
        # Créer des chauffeurs de test s'ils n'existent pas
        if Chauffeur.query.count() == 0:
            print("Création de chauffeurs de test...")
            chauffeur1 = Chauffeur(nom="Dupont", prenom="Jean", telephone="123456789")
            chauffeur2 = Chauffeur(nom="Martin", prenom="Pierre", telephone="987654321")
            chauffeur3 = Chauffeur(nom="Durand", prenom="Marie", telephone="555666777")
            
            db.session.add_all([chauffeur1, chauffeur2, chauffeur3])
        
        # Créer des prestataires de test s'ils n'existent pas
        if Prestataire.query.count() == 0:
            print("Création de prestataires de test...")
            prest1 = Prestataire(nom_prestataire="Transport Express", contact="contact@express.com")
            prest2 = Prestataire(nom_prestataire="Voyages Rapides", contact="info@rapides.com")
            prest3 = Prestataire(nom_prestataire="Bus Services", contact="service@bus.com")
            
            db.session.add_all([prest1, prest2, prest3])
        
        try:
            db.session.commit()
            print("✅ Données de test créées avec succès!")
            
            # Vérifier les données créées
            print(f"Bus: {BusUdM.query.count()}")
            print(f"Bus en bon état: {BusUdM.query.filter_by(etat_vehicule='BON').count()}")
            print(f"Chauffeurs: {Chauffeur.query.count()}")
            print(f"Prestataires: {Prestataire.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la création: {e}")

if __name__ == "__main__":
    create_test_data()
