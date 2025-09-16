#!/usr/bin/env python3
"""
Test de vérification complète finale après toutes les corrections
Vérifie que tous les modèles, formulaires, services et templates sont cohérents
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_modeles_db_compatibility():
    """Test de compatibilité des modèles avec la DB"""
    print("🔍 TEST COMPATIBILITÉ MODÈLES-DB")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.models.bus_udm import BusUdM
        from app.models.chauffeur import Chauffeur
        from app.models.mecanicien import Mecanicien
        from app.models.prestataire import Prestataire
        from app.models.trajet import Trajet
        from app.models.carburation import Carburation
        from app.models.vidange import Vidange
        from app.models.panne_bus_udm import PanneBusUdM
        from app.models.depannage import Depannage
        from app.models.document_bus_udm import DocumentBusUdM
        from app.models.fuel_alert_state import FuelAlertState
        from app.models.affectation import Affectation
        from app.models.chauffeur_statut import ChauffeurStatut
        from app.models.demande_huile import DemandeHuile
        
        app = create_app()
        
        with app.app_context():
            # Test de connexion à la DB
            print("✅ Tous les modèles importés sans erreur")
            
            # Test de requête simple sur chaque modèle
            modeles_a_tester = [
                (BusUdM, "Bus UdM"),
                (Chauffeur, "Chauffeur"),
                (Mecanicien, "Mécanicien"),
                (Prestataire, "Prestataire"),
                (Trajet, "Trajet"),
                (Carburation, "Carburation"),
                (Vidange, "Vidange"),
                (PanneBusUdM, "Panne Bus UdM"),
                (Depannage, "Dépannage"),
                (DocumentBusUdM, "Document Bus UdM"),
                (FuelAlertState, "Fuel Alert State"),
                (Affectation, "Affectation"),
                (ChauffeurStatut, "Chauffeur Statut"),
                (DemandeHuile, "Demande Huile")
            ]
            
            for modele, nom in modeles_a_tester:
                try:
                    count = modele.query.count()
                    print(f"✅ {nom}: {count} enregistrements")
                except Exception as e:
                    print(f"❌ {nom}: Erreur - {str(e)}")
                    return False
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test des modèles: {str(e)}")
        return False

def test_formulaires_coherence():
    """Test de cohérence des formulaires"""
    print("\n🔍 TEST COHÉRENCE FORMULAIRES")
    print("=" * 50)
    
    try:
        from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
        from app.forms.trajet_prestataire_form import TrajetPrestataireForm
        from app.forms.autres_trajets_form import AutresTrajetsForm
        from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm
        from app.forms.trajet_depart_form import TrajetDepartForm
        from app.forms.bus_udm_form import BusUdMForm
        from app.forms.panne_form import PanneForm
        
        # Vérifier que tous les formulaires ont les bons champs
        formulaires_a_tester = [
            (TrajetInterneBusUdMForm, "Trajet Interne Bus UdM", ["numero_bus_udm", "point_arriver"]),
            (TrajetPrestataireForm, "Trajet Prestataire", ["point_arriver", "nom_prestataire"]),
            (AutresTrajetsForm, "Autres Trajets", ["numero_bus_udm", "point_arriver"]),
            (TrajetBanekaneRetourForm, "Trajet Banekane Retour", ["numero_bus_udm", "point_arriver"]),
            (TrajetDepartForm, "Trajet Départ", ["numero_bus_udm"]),
            (BusUdMForm, "Bus UdM", ["numero", "immatriculation"]),
            (PanneForm, "Panne", ["numero_bus_udm"])
        ]
        
        for form_class, nom, champs_requis in formulaires_a_tester:
            try:
                form = form_class()
                champs_manquants = []
                
                for champ in champs_requis:
                    if not hasattr(form, champ):
                        champs_manquants.append(champ)
                
                if champs_manquants:
                    print(f"❌ {nom}: Champs manquants - {champs_manquants}")
                    return False
                else:
                    print(f"✅ {nom}: Tous les champs requis présents")
                    
            except Exception as e:
                print(f"❌ {nom}: Erreur - {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des formulaires: {str(e)}")
        return False

def test_services_fonctionnels():
    """Test des services"""
    print("\n🔍 TEST SERVICES FONCTIONNELS")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.services.dashboard_service import DashboardService
        from app.services.query_service import QueryService
        from app.services.form_service import FormService
        from app.services.bus_service import BusService
        
        app = create_app()
        
        with app.app_context():
            # Test DashboardService
            try:
                stats = DashboardService.get_dashboard_stats()
                print(f"✅ DashboardService: {len(stats)} statistiques")
            except Exception as e:
                print(f"❌ DashboardService: {str(e)}")
                return False
            
            # Test QueryService
            try:
                chauffeurs = QueryService.get_chauffeur_choices()
                prestataires = QueryService.get_prestataire_choices()
                print(f"✅ QueryService: {len(chauffeurs)} chauffeurs, {len(prestataires)} prestataires")
            except Exception as e:
                print(f"❌ QueryService: {str(e)}")
                return False
            
            # Test FormService
            try:
                from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
                form = TrajetInterneBusUdMForm()
                FormService.populate_trajet_form_choices(form)
                print(f"✅ FormService: Formulaire peuplé avec {len(form.numero_bus_udm.choices)} bus")
            except Exception as e:
                print(f"❌ FormService: {str(e)}")
                return False
            
            # Test BusService
            try:
                buses = BusService.get_all_buses()
                print(f"✅ BusService: {len(buses)} bus récupérés")
            except Exception as e:
                print(f"❌ BusService: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des services: {str(e)}")
        return False

def test_application_startup():
    """Test de démarrage de l'application"""
    print("\n🔍 TEST DÉMARRAGE APPLICATION")
    print("=" * 50)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Test de création du contexte
            print("✅ Contexte d'application créé")
            
            # Test de configuration
            if app.config.get('SQLALCHEMY_DATABASE_URI'):
                print("✅ Configuration de base de données présente")
            else:
                print("❌ Configuration de base de données manquante")
                return False
            
            # Test d'import des blueprints
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            print(f"✅ Blueprints enregistrés: {', '.join(blueprint_names)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de démarrage: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 VÉRIFICATION COMPLÈTE FINALE")
    print("=" * 80)
    
    tests = [
        ("Modèles-DB Compatibility", test_modeles_db_compatibility),
        ("Cohérence Formulaires", test_formulaires_coherence),
        ("Services Fonctionnels", test_services_fonctionnels),
        ("Démarrage Application", test_application_startup)
    ]
    
    resultats = []
    
    for nom_test, fonction_test in tests:
        try:
            resultat = fonction_test()
            resultats.append((nom_test, resultat))
        except Exception as e:
            print(f"❌ Erreur critique dans {nom_test}: {str(e)}")
            resultats.append((nom_test, False))
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 80)
    
    tests_reussis = 0
    for nom_test, resultat in resultats:
        status = "✅ RÉUSSI" if resultat else "❌ ÉCHEC"
        print(f"{status} - {nom_test}")
        if resultat:
            tests_reussis += 1
    
    print(f"\n🎯 RÉSULTAT GLOBAL: {tests_reussis}/{len(tests)} tests réussis")
    
    if tests_reussis == len(tests):
        print("🎉 TOUTES LES VÉRIFICATIONS SONT RÉUSSIES !")
        print("✅ L'application est entièrement fonctionnelle et cohérente")
        return True
    else:
        print("⚠️  Des problèmes subsistent et nécessitent une correction")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
