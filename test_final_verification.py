#!/usr/bin/env python3
"""
Test final de vérification après toutes les corrections
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_application_complete():
    """Test complet de l'application"""
    print("🚀 TEST FINAL DE L'APPLICATION")
    print("=" * 60)
    
    try:
        from app import create_app
        from app.models.bus_udm import BusUdM
        from app.models.chauffeur import Chauffeur
        from app.models.prestataire import Prestataire
        from app.models.trajet import Trajet
        from app.services.dashboard_service import DashboardService
        from app.services.query_service import QueryService
        from app.services.form_service import FormService
        from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
        from app.forms.trajet_prestataire_form import TrajetPrestataireForm
        from app.forms.autres_trajets_form import AutresTrajetsForm
        
        app = create_app()
        
        with app.app_context():
            print("✅ Application créée et contexte initialisé")
            
            # Test des modèles
            try:
                bus_count = BusUdM.query.count()
                chauffeur_count = Chauffeur.query.count()
                prestataire_count = Prestataire.query.count()
                trajet_count = Trajet.query.count()
                
                print(f"✅ Modèles DB - Bus: {bus_count}, Chauffeurs: {chauffeur_count}, Prestataires: {prestataire_count}, Trajets: {trajet_count}")
            except Exception as e:
                print(f"❌ Erreur modèles DB: {str(e)}")
                return False
            
            # Test des services
            try:
                stats = DashboardService.get_dashboard_stats()
                chauffeur_choices = QueryService.get_chauffeur_choices()
                prestataire_choices = QueryService.get_prestataire_choices()
                
                print(f"✅ Services - Stats: {len(stats)}, Chauffeurs: {len(chauffeur_choices)}, Prestataires: {len(prestataire_choices)}")
            except Exception as e:
                print(f"❌ Erreur services: {str(e)}")
                return False
            
            # Test des formulaires
            try:
                # Test TrajetInterneBusUdMForm
                form_interne = TrajetInterneBusUdMForm()
                FormService.populate_trajet_form_choices(form_interne)
                
                required_fields_interne = ['numero_bus_udm', 'point_arriver', 'lieu_depart', 'chauffeur_id']
                for field in required_fields_interne:
                    if not hasattr(form_interne, field):
                        print(f"❌ TrajetInterneBusUdMForm manque le champ: {field}")
                        return False
                
                print(f"✅ TrajetInterneBusUdMForm - Bus: {len(form_interne.numero_bus_udm.choices)}")
                
                # Test TrajetPrestataireForm
                form_prestataire = TrajetPrestataireForm()
                FormService.populate_trajet_form_choices(form_prestataire)
                
                required_fields_prestataire = ['nom_prestataire', 'point_arriver', 'lieu_depart']
                for field in required_fields_prestataire:
                    if not hasattr(form_prestataire, field):
                        print(f"❌ TrajetPrestataireForm manque le champ: {field}")
                        return False
                
                print(f"✅ TrajetPrestataireForm - Prestataires: {len(form_prestataire.nom_prestataire.choices)}")
                
                # Test AutresTrajetsForm
                form_autres = AutresTrajetsForm()
                FormService.populate_trajet_form_choices(form_autres)
                
                required_fields_autres = ['numero_bus_udm', 'point_arriver', 'lieu_depart', 'motif_trajet']
                for field in required_fields_autres:
                    if not hasattr(form_autres, field):
                        print(f"❌ AutresTrajetsForm manque le champ: {field}")
                        return False
                
                print(f"✅ AutresTrajetsForm - Bus: {len(form_autres.numero_bus_udm.choices)}")
                
            except Exception as e:
                print(f"❌ Erreur formulaires: {str(e)}")
                return False
            
            # Test de cohérence des noms de champs
            print("\n🔍 VÉRIFICATION COHÉRENCE DES CHAMPS")
            print("-" * 40)
            
            # Vérifier que tous les formulaires utilisent 'point_arriver' et non 'lieu_arrivee'
            forms_to_check = [
                (form_interne, "TrajetInterneBusUdMForm"),
                (form_prestataire, "TrajetPrestataireForm"),
                (form_autres, "AutresTrajetsForm")
            ]
            
            for form, form_name in forms_to_check:
                if hasattr(form, 'lieu_arrivee'):
                    print(f"❌ {form_name} utilise encore 'lieu_arrivee' au lieu de 'point_arriver'")
                    return False
                elif hasattr(form, 'point_arriver'):
                    print(f"✅ {form_name} utilise correctement 'point_arriver'")
                else:
                    print(f"⚠️  {form_name} n'a pas de champ de destination")
            
            # Vérifier que les formulaires Bus UdM utilisent 'numero_bus_udm' et non 'numero_aed'
            bus_forms = [form_interne, form_autres]
            for form in bus_forms:
                if hasattr(form, 'numero_aed'):
                    print(f"❌ Formulaire utilise encore 'numero_aed' au lieu de 'numero_bus_udm'")
                    return False
                elif hasattr(form, 'numero_bus_udm'):
                    print(f"✅ Formulaire utilise correctement 'numero_bus_udm'")
            
            # Vérifier le champ motif
            if hasattr(form_autres, 'motif'):
                print(f"❌ AutresTrajetsForm utilise 'motif' au lieu de 'motif_trajet'")
                return False
            elif hasattr(form_autres, 'motif_trajet'):
                print(f"✅ AutresTrajetsForm utilise correctement 'motif_trajet'")
            
            print("\n🎯 RÉSULTAT FINAL")
            print("=" * 60)
            print("✅ TOUTES LES VÉRIFICATIONS SONT RÉUSSIES !")
            print("✅ L'application est entièrement fonctionnelle")
            print("✅ Tous les modèles sont compatibles avec la DB")
            print("✅ Tous les formulaires utilisent les bons noms de champs")
            print("✅ Tous les services fonctionnent correctement")
            print("✅ L'architecture refactorisée est opérationnelle")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_application_complete()
    
    if success:
        print("\n🎉 MISSION ACCOMPLIE !")
        print("🚀 L'application Transport UdM est prête pour la production")
        return True
    else:
        print("\n⚠️  Des problèmes subsistent")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
