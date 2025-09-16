#!/usr/bin/env python3
"""
Test des formulaires du chargé de transport
"""

from app import create_app
from app.models.bus_udm import BusUdM
from app.models.chauffeur import Chauffeur  
from app.models.prestataire import Prestataire
from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
from app.forms.trajet_prestataire_form import TrajetPrestataireForm
from app.services.form_service import FormService

def test_charge_transport_forms():
    """Test des formulaires du chargé de transport"""
    print("🔍 TEST DES FORMULAIRES CHARGÉ DE TRANSPORT")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée avec succès")
        
        # Vérifier les données en base
        print("\n📊 DONNÉES EN BASE:")
        bus_count = BusUdM.query.count()
        bus_bon_count = BusUdM.query.filter_by(etat_vehicule='BON').count()
        chauffeur_count = Chauffeur.query.count()
        prestataire_count = Prestataire.query.count()
        
        print(f"   🚌 Bus total: {bus_count}")
        print(f"   🚌 Bus en bon état: {bus_bon_count}")
        print(f"   👨‍✈️ Chauffeurs: {chauffeur_count}")
        print(f"   🏢 Prestataires: {prestataire_count}")
        
        # Afficher quelques exemples
        if bus_bon_count > 0:
            bus_examples = BusUdM.query.filter_by(etat_vehicule='BON').limit(3).all()
            print(f"   Exemples bus: {[b.numero for b in bus_examples]}")
        
        if chauffeur_count > 0:
            chauffeur_examples = Chauffeur.query.limit(3).all()
            print(f"   Exemples chauffeurs: {[(c.nom, c.prenom) for c in chauffeur_examples]}")
            
        if prestataire_count > 0:
            prestataire_examples = Prestataire.query.limit(3).all()
            print(f"   Exemples prestataires: {[p.nom_prestataire for p in prestataire_examples]}")
        
        # Test du formulaire trajet interne
        print("\n📋 TEST FORMULAIRE TRAJET INTERNE:")
        form_interne = TrajetInterneBusUdMForm()
        
        print(f"   Avant peuplement:")
        print(f"     🚌 Choix bus: {len(form_interne.numero_bus_udm.choices)}")
        print(f"     👨‍✈️ Choix chauffeurs: {len(form_interne.chauffeur_id.choices)}")
        
        FormService.populate_trajet_form_choices(form_interne)
        
        print(f"   Après peuplement:")
        print(f"     🚌 Choix bus: {len(form_interne.numero_bus_udm.choices)}")
        if form_interne.numero_bus_udm.choices:
            print(f"       Premier: {form_interne.numero_bus_udm.choices[0]}")
        
        print(f"     👨‍✈️ Choix chauffeurs: {len(form_interne.chauffeur_id.choices)}")
        if form_interne.chauffeur_id.choices:
            print(f"       Premier: {form_interne.chauffeur_id.choices[0]}")
        
        # Test du formulaire trajet prestataire
        print("\n📋 TEST FORMULAIRE TRAJET PRESTATAIRE:")
        form_prestataire = TrajetPrestataireForm()
        
        print(f"   Avant peuplement:")
        print(f"     🏢 Choix prestataires: {len(form_prestataire.nom_prestataire.choices)}")
        
        FormService.populate_trajet_form_choices(form_prestataire)
        
        print(f"   Après peuplement:")
        print(f"     🏢 Choix prestataires: {len(form_prestataire.nom_prestataire.choices)}")
        if form_prestataire.nom_prestataire.choices:
            print(f"       Premier: {form_prestataire.nom_prestataire.choices[0]}")
        
        # Diagnostic des problèmes potentiels
        print("\n🔍 DIAGNOSTIC:")
        if bus_bon_count == 0:
            print("   ❌ PROBLÈME: Aucun bus en bon état!")
        if chauffeur_count == 0:
            print("   ❌ PROBLÈME: Aucun chauffeur!")
        if prestataire_count == 0:
            print("   ❌ PROBLÈME: Aucun prestataire!")
            
        if (bus_bon_count > 0 and len(form_interne.numero_bus_udm.choices) == 0):
            print("   ❌ PROBLÈME: Bus en base mais pas dans le formulaire!")
            
        if (chauffeur_count > 0 and len(form_interne.chauffeur_id.choices) == 0):
            print("   ❌ PROBLÈME: Chauffeurs en base mais pas dans le formulaire!")
            
        if (prestataire_count > 0 and len(form_prestataire.nom_prestataire.choices) == 0):
            print("   ❌ PROBLÈME: Prestataires en base mais pas dans le formulaire!")
        
        print("\n🎉 TEST TERMINÉ")

if __name__ == "__main__":
    test_charge_transport_forms()
