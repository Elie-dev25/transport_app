#!/usr/bin/env python3

# Test simple des formulaires
import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.getcwd())

print("=== TEST FORMULAIRES CHARGE TRANSPORT ===")

try:
    # Import de l'application
    from app import create_app
    print("✅ Import app réussi")
    
    # Création de l'application
    app = create_app()
    print("✅ App créée")
    
    with app.app_context():
        print("✅ Context créé")
        
        # Import des modèles
        from app.models.bus_udm import BusUdM
        from app.models.chauffeur import Chauffeur
        from app.models.prestataire import Prestataire
        from app.database import db
        print("✅ Models importés")
        
        # Créer des données de test si nécessaire
        if BusUdM.query.count() == 0:
            bus1 = BusUdM(numero="001", etat_vehicule="BON", kilometrage=15000)
            bus2 = BusUdM(numero="002", etat_vehicule="BON", kilometrage=22000)
            db.session.add_all([bus1, bus2])
            print("✅ Bus créés")
        
        if Chauffeur.query.count() == 0:
            chauffeur1 = Chauffeur(nom="Dupont", prenom="Jean", telephone="123456789")
            chauffeur2 = Chauffeur(nom="Martin", prenom="Pierre", telephone="987654321")
            db.session.add_all([chauffeur1, chauffeur2])
            print("✅ Chauffeurs créés")
        
        if Prestataire.query.count() == 0:
            prest1 = Prestataire(nom_prestataire="Transport Express", contact="contact@express.com")
            prest2 = Prestataire(nom_prestataire="Voyages Rapides", contact="info@rapides.com")
            db.session.add_all([prest1, prest2])
            print("✅ Prestataires créés")
        
        try:
            db.session.commit()
            print("✅ Données sauvegardées")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Erreur sauvegarde: {e}")
        
        # Test des formulaires
        from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
        from app.forms.trajet_prestataire_form import TrajetPrestataireForm
        from app.services.form_service import FormService
        
        print("\n=== TEST FORMULAIRE TRAJET INTERNE ===")
        form_interne = TrajetInterneBusUdMForm()
        print(f"Bus avant peuplement: {len(form_interne.numero_bus_udm.choices)}")
        print(f"Chauffeurs avant peuplement: {len(form_interne.chauffeur_id.choices)}")
        
        FormService.populate_trajet_form_choices(form_interne)
        
        print(f"Bus après peuplement: {len(form_interne.numero_bus_udm.choices)}")
        print(f"Chauffeurs après peuplement: {len(form_interne.chauffeur_id.choices)}")
        
        if form_interne.numero_bus_udm.choices:
            print(f"Premier bus: {form_interne.numero_bus_udm.choices[0]}")
        if form_interne.chauffeur_id.choices:
            print(f"Premier chauffeur: {form_interne.chauffeur_id.choices[0]}")
        
        print("\n=== TEST FORMULAIRE TRAJET PRESTATAIRE ===")
        form_prestataire = TrajetPrestataireForm()
        print(f"Prestataires avant peuplement: {len(form_prestataire.nom_prestataire.choices)}")
        
        FormService.populate_trajet_form_choices(form_prestataire)
        
        print(f"Prestataires après peuplement: {len(form_prestataire.nom_prestataire.choices)}")
        
        if form_prestataire.nom_prestataire.choices:
            print(f"Premier prestataire: {form_prestataire.nom_prestataire.choices[0]}")
        
        # Vérifications finales
        bus_count = BusUdM.query.filter_by(etat_vehicule='BON').count()
        chauffeur_count = Chauffeur.query.count()
        prestataire_count = Prestataire.query.count()
        
        print(f"\n=== DONNÉES EN BASE ===")
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
            print("\n🎉 TOUS LES TESTS PASSENT!")
            print("✅ Les formulaires du chargé de transport sont correctement peuplés!")
        else:
            print("\n❌ CERTAINS TESTS ÉCHOUENT!")

except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN DU TEST ===")
