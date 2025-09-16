#!/usr/bin/env python3
"""
Test final des formulaires après corrections
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.models.bus_udm import BusUdM
    from app.models.chauffeur import Chauffeur  
    from app.models.prestataire import Prestataire
    from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
    from app.forms.trajet_prestataire_form import TrajetPrestataireForm
    from app.services.form_service import FormService
    from app.database import db

    def test_forms():
        """Test des formulaires"""
        app = create_app()
        
        with app.app_context():
            # Créer des données de test si nécessaire
            if BusUdM.query.count() == 0:
                bus1 = BusUdM(numero="001", etat_vehicule="BON", kilometrage=15000)
                bus2 = BusUdM(numero="002", etat_vehicule="BON", kilometrage=22000)
                db.session.add_all([bus1, bus2])
            
            if Chauffeur.query.count() == 0:
                chauffeur1 = Chauffeur(nom="Dupont", prenom="Jean", telephone="123456789")
                chauffeur2 = Chauffeur(nom="Martin", prenom="Pierre", telephone="987654321")
                db.session.add_all([chauffeur1, chauffeur2])
            
            if Prestataire.query.count() == 0:
                prest1 = Prestataire(nom_prestataire="Transport Express", contact="contact@express.com")
                prest2 = Prestataire(nom_prestataire="Voyages Rapides", contact="info@rapides.com")
                db.session.add_all([prest1, prest2])
            
            try:
                db.session.commit()
            except:
                db.session.rollback()
            
            # Test des formulaires
            print("=== TEST DES FORMULAIRES ===")
            
            # Formulaire trajet interne
            form_interne = TrajetInterneBusUdMForm()
            print(f"Trajet interne - Bus avant: {len(form_interne.numero_bus_udm.choices)}")
            print(f"Trajet interne - Chauffeurs avant: {len(form_interne.chauffeur_id.choices)}")
            
            FormService.populate_trajet_form_choices(form_interne)
            
            print(f"Trajet interne - Bus après: {len(form_interne.numero_bus_udm.choices)}")
            print(f"Trajet interne - Chauffeurs après: {len(form_interne.chauffeur_id.choices)}")
            
            if form_interne.numero_bus_udm.choices:
                print(f"Premier bus: {form_interne.numero_bus_udm.choices[0]}")
            if form_interne.chauffeur_id.choices:
                print(f"Premier chauffeur: {form_interne.chauffeur_id.choices[0]}")
            
            # Formulaire trajet prestataire
            form_prestataire = TrajetPrestataireForm()
            print(f"Trajet prestataire - Prestataires avant: {len(form_prestataire.nom_prestataire.choices)}")
            
            FormService.populate_trajet_form_choices(form_prestataire)
            
            print(f"Trajet prestataire - Prestataires après: {len(form_prestataire.nom_prestataire.choices)}")
            
            if form_prestataire.nom_prestataire.choices:
                print(f"Premier prestataire: {form_prestataire.nom_prestataire.choices[0]}")
            
            # Vérifications
            bus_count = BusUdM.query.filter_by(etat_vehicule='BON').count()
            chauffeur_count = Chauffeur.query.count()
            prestataire_count = Prestataire.query.count()
            
            print(f"\nDonnées en base:")
            print(f"Bus en bon état: {bus_count}")
            print(f"Chauffeurs: {chauffeur_count}")
            print(f"Prestataires: {prestataire_count}")
            
            # Résultats
            success = True
            if bus_count > 0 and len(form_interne.numero_bus_udm.choices) == 0:
                print("❌ ERREUR: Bus en base mais pas dans le formulaire!")
                success = False
            if chauffeur_count > 0 and len(form_interne.chauffeur_id.choices) == 0:
                print("❌ ERREUR: Chauffeurs en base mais pas dans le formulaire!")
                success = False
            if prestataire_count > 0 and len(form_prestataire.nom_prestataire.choices) == 0:
                print("❌ ERREUR: Prestataires en base mais pas dans le formulaire!")
                success = False
            
            if success:
                print("✅ TOUS LES TESTS PASSENT!")
            else:
                print("❌ CERTAINS TESTS ÉCHOUENT!")
            
            return success

    if __name__ == "__main__":
        test_forms()

except Exception as e:
    print(f"ERREUR: {e}")
    import traceback
    traceback.print_exc()
