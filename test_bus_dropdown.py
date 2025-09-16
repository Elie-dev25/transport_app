#!/usr/bin/env python3
"""
Test spécifique pour vérifier le peuplement des listes déroulantes de bus
"""

def test_bus_dropdown():
    print("🔍 TEST LISTE DÉROULANTE BUS")
    print("=" * 50)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Test 1: Vérifier les bus en base
            print("\n1. 📊 VÉRIFICATION BASE DE DONNÉES:")
            from app.models.bus_udm import BusUdM
            
            buses_total = BusUdM.query.all()
            print(f"   Total bus en base: {len(buses_total)}")
            
            buses_bon = BusUdM.query.filter_by(etat_vehicule='BON').all()
            print(f"   Bus en bon état: {len(buses_bon)}")
            
            if buses_bon:
                print("   Premiers bus en bon état:")
                for bus in buses_bon[:3]:
                    print(f"     - Bus {bus.numero}: {bus.etat_vehicule}")
            else:
                print("   ⚠️  Aucun bus en bon état trouvé!")
                
                # Vérifier tous les états
                etats = {}
                for bus in buses_total:
                    etat = bus.etat_vehicule or 'NULL'
                    etats[etat] = etats.get(etat, 0) + 1
                print(f"   États des bus: {etats}")
            
            # Test 2: QueryService
            print("\n2. 🔧 TEST QUERYSERVICE:")
            from app.services.query_service import QueryService
            
            active_buses = QueryService.get_active_buses()
            print(f"   QueryService.get_active_buses(): {len(active_buses)}")
            
            # Test 3: FormService
            print("\n3. 📝 TEST FORMSERVICE:")
            from app.services.form_service import FormService
            
            bus_choices = FormService._get_bus_choices('BON_ONLY')
            print(f"   FormService._get_bus_choices('BON_ONLY'): {len(bus_choices)}")
            
            if bus_choices:
                print("   Premiers choix:")
                for choice in bus_choices[:3]:
                    print(f"     - {choice}")
            
            # Test 4: Formulaire TrajetInterneBusUdMForm
            print("\n4. 📋 TEST FORMULAIRE:")
            from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
            
            form = TrajetInterneBusUdMForm()
            print(f"   Avant peuplement - Bus: {len(form.numero_bus_udm.choices)}")
            print(f"   Avant peuplement - Chauffeurs: {len(form.chauffeur_id.choices)}")
            
            # Peupler avec FormService
            try:
                FormService.populate_multiple_forms(form, bus_filter='BON_ONLY')
                print(f"   Après peuplement - Bus: {len(form.numero_bus_udm.choices)}")
                print(f"   Après peuplement - Chauffeurs: {len(form.chauffeur_id.choices)}")
                
                if form.numero_bus_udm.choices:
                    print("   Premiers choix bus:")
                    for choice in form.numero_bus_udm.choices[:3]:
                        print(f"     - {choice}")
                else:
                    print("   ❌ Aucun choix de bus après peuplement!")
                    
            except Exception as e:
                print(f"   ❌ Erreur lors du peuplement: {e}")
                import traceback
                traceback.print_exc()
            
            # Test 5: Vérifier les chauffeurs aussi
            print("\n5. 👨‍✈️ TEST CHAUFFEURS:")
            from app.models.chauffeur import Chauffeur
            
            chauffeurs = Chauffeur.query.all()
            print(f"   Total chauffeurs: {len(chauffeurs)}")
            
            if chauffeurs:
                print("   Premiers chauffeurs:")
                for chauffeur in chauffeurs[:3]:
                    print(f"     - {chauffeur.nom} {chauffeur.prenom}")
            
            # Test 6: Test complet dashboard responsable
            print("\n6. 🎯 TEST DASHBOARD RESPONSABLE:")
            try:
                from app.routes.responsable import dashboard
                from flask import Flask
                from flask_login import AnonymousUserMixin
                
                # Simuler un contexte de requête
                with app.test_request_context('/responsable/dashboard'):
                    # Simuler un utilisateur responsable
                    class MockUser:
                        role = 'RESPONSABLE'
                        is_authenticated = True
                    
                    # Test de la fonction dashboard
                    print("   Test de la fonction dashboard...")
                    # Note: Ne peut pas tester complètement sans authentification
                    print("   ✅ Fonction dashboard importée avec succès")
                    
            except Exception as e:
                print(f"   ❌ Erreur test dashboard: {e}")
            
            # Résumé
            print("\n" + "=" * 50)
            print("📊 RÉSUMÉ:")
            print(f"✅ Bus total: {len(buses_total)}")
            print(f"✅ Bus en bon état: {len(buses_bon)}")
            print(f"✅ QueryService actif: {len(active_buses)} bus")
            print(f"✅ FormService choix: {len(bus_choices)} options")
            print(f"✅ Chauffeurs: {len(chauffeurs)}")
            
            if len(buses_bon) == 0:
                print("\n⚠️  PROBLÈME DÉTECTÉ:")
                print("   Aucun bus avec etat_vehicule='BON'")
                print("   Vérifiez les données en base ou les valeurs d'état")
                
                # Suggestion de correction
                print("\n💡 SOLUTIONS POSSIBLES:")
                print("   1. Vérifier les valeurs dans la colonne etat_vehicule")
                print("   2. Mettre à jour quelques bus: UPDATE bus_udm SET etat_vehicule='BON' WHERE id IN (1,2,3)")
                print("   3. Vérifier la casse: 'BON' vs 'bon' vs 'Bon'")
            
            return len(buses_bon) > 0
            
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bus_dropdown()
    if success:
        print("\n🎉 TEST RÉUSSI - Les listes déroulantes devraient fonctionner!")
    else:
        print("\n💥 PROBLÈME DÉTECTÉ - Vérifiez les données en base")
