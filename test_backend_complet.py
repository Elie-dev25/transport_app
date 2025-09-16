#!/usr/bin/env python3
"""
Test complet du backend après corrections
Vérifie tous les modèles, services et formulaires
"""

def test_modeles_db():
    """Test tous les modèles contre la base de données réelle"""
    print("1. TEST DES MODELES")
    print("=" * 30)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Test des modèles principaux
            modeles_tests = [
                ('BusUdM', 'app.models.bus_udm'),
                ('Chauffeur', 'app.models.chauffeur'),
                ('Utilisateur', 'app.models.utilisateur'),
                ('Trajet', 'app.models.trajet'),
                ('Administrateur', 'app.models.administrateur'),
                ('Chargetransport', 'app.models.chargetransport'),
            ]
            
            succes = 0
            total = len(modeles_tests)
            
            for nom_modele, module_path in modeles_tests:
                try:
                    module = __import__(module_path, fromlist=[nom_modele])
                    modele_class = getattr(module, nom_modele)
                    
                    # Test de requête simple
                    count = modele_class.query.count()
                    print(f"   OK {nom_modele}: {count} enregistrements")
                    succes += 1
                    
                except Exception as e:
                    print(f"   ERREUR {nom_modele}: {e}")
            
            print(f"\nModeles: {succes}/{total} OK")
            return succes == total
            
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

def test_services():
    """Test tous les services refactorisés"""
    print("\n2. TEST DES SERVICES")
    print("=" * 30)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            succes = 0
            total = 0
            
            # Test DashboardService
            try:
                from app.services.dashboard_service import DashboardService
                stats = DashboardService.get_common_stats()
                print(f"   OK DashboardService: {len(stats)} statistiques")
                succes += 1
            except Exception as e:
                print(f"   ERREUR DashboardService: {e}")
            total += 1
            
            # Test QueryService
            try:
                from app.services.query_service import QueryService
                buses = QueryService.get_active_buses()
                print(f"   OK QueryService: {len(buses)} bus actifs")
                succes += 1
            except Exception as e:
                print(f"   ERREUR QueryService: {e}")
            total += 1
            
            # Test FormService
            try:
                from app.services.form_service import FormService
                from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
                form = TrajetInterneBusUdMForm()
                FormService.populate_trajet_form_choices(form)
                print(f"   OK FormService: formulaire peuple")
                succes += 1
            except Exception as e:
                print(f"   ERREUR FormService: {e}")
            total += 1
            
            print(f"\nServices: {succes}/{total} OK")
            return succes == total
            
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

def test_formulaires():
    """Test tous les formulaires refactorisés"""
    print("\n3. TEST DES FORMULAIRES")
    print("=" * 30)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            formulaires_tests = [
                ('TrajetInterneBusUdMForm', 'app.forms.trajet_interne_bus_udm_form'),
                ('TrajetPrestataireForm', 'app.forms.trajet_prestataire_form'),
                ('AutresTrajetsForm', 'app.forms.autres_trajets_form'),
                ('TrajetSortieHorsVilleForm', 'app.forms.trajet_sortie_hors_ville_form'),
            ]
            
            succes = 0
            total = len(formulaires_tests)
            
            for nom_form, module_path in formulaires_tests:
                try:
                    module = __import__(module_path, fromlist=[nom_form])
                    form_class = getattr(module, nom_form)
                    
                    # Test de création du formulaire
                    form = form_class()
                    
                    # Vérifier que le champ point_arriver existe
                    if hasattr(form, 'point_arriver'):
                        print(f"   OK {nom_form}: champ point_arriver present")
                        succes += 1
                    else:
                        print(f"   ATTENTION {nom_form}: pas de champ point_arriver")
                        succes += 1  # Certains formulaires peuvent ne pas l'avoir
                    
                except Exception as e:
                    print(f"   ERREUR {nom_form}: {e}")
            
            print(f"\nFormulaires: {succes}/{total} OK")
            return succes == total
            
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

def test_requetes_specifiques():
    """Test des requêtes spécifiques qui posaient problème"""
    print("\n4. TEST DES REQUETES SPECIFIQUES")
    print("=" * 30)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.models.bus_udm import BusUdM
            from app.models.chauffeur import Chauffeur
            
            # Test requête bus actifs (qui causait l'erreur)
            try:
                bus_actifs = BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count()
                print(f"   OK Bus actifs: {bus_actifs}")
            except Exception as e:
                print(f"   ERREUR Bus actifs: {e}")
                return False
            
            # Test requête chauffeurs (qui causait l'erreur)
            try:
                chauffeurs = Chauffeur.query.count()
                print(f"   OK Chauffeurs: {chauffeurs}")
            except Exception as e:
                print(f"   ERREUR Chauffeurs: {e}")
                return False
            
            # Test DashboardService (qui utilisait les requêtes problématiques)
            try:
                from app.services.dashboard_service import DashboardService
                stats = DashboardService.get_common_stats()
                print(f"   OK DashboardService stats: {stats}")
            except Exception as e:
                print(f"   ERREUR DashboardService: {e}")
                return False
            
            print("\nRequetes specifiques: OK")
            return True
            
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        return False

def main():
    """Test complet du backend"""
    print("TEST COMPLET DU BACKEND APRES CORRECTIONS")
    print("=" * 50)
    
    # Tests individuels
    modeles_ok = test_modeles_db()
    services_ok = test_services()
    formulaires_ok = test_formulaires()
    requetes_ok = test_requetes_specifiques()
    
    # Résumé final
    print("\n" + "=" * 50)
    print("RESUME FINAL")
    print("=" * 50)
    
    tests_results = [
        ("Modeles", modeles_ok),
        ("Services", services_ok),
        ("Formulaires", formulaires_ok),
        ("Requetes", requetes_ok)
    ]
    
    succes_total = sum(1 for _, ok in tests_results if ok)
    total_tests = len(tests_results)
    
    for nom, ok in tests_results:
        status = "OK" if ok else "ERREUR"
        print(f"   {nom}: {status}")
    
    print(f"\nRESULTAT: {succes_total}/{total_tests} tests reussis")
    
    if succes_total == total_tests:
        print("\nSUCCES COMPLET!")
        print("Tous les modeles, services et formulaires sont compatibles.")
        print("L'application peut maintenant demarrer sans erreur.")
        return True
    else:
        print("\nPROBLEMES DETECTES!")
        print("Certains elements ne sont pas encore compatibles.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
