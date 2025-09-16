#!/usr/bin/env python3
"""
Test de compatibilité des modèles avec la base de données existante
Vérifie que tous les modèles refactorisés fonctionnent avec la DB
"""

def test_models_compatibility():
    """Test la compatibilité de tous les modèles"""
    print("TEST DE COMPATIBILITE DES MODELES")
    print("=" * 40)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.database import db
            
            # Test des modèles principaux
            models_to_test = [
                ('BusUdM', 'app.models.bus_udm'),
                ('Utilisateur', 'app.models.utilisateur'),
                ('Trajet', 'app.models.trajet'),
                ('Chauffeur', 'app.models.chauffeur'),
                ('Administrateur', 'app.models.administrateur'),
                ('Chargetransport', 'app.models.chargetransport'),
            ]
            
            success_count = 0
            total_count = len(models_to_test)
            
            for model_name, module_path in models_to_test:
                try:
                    # Import du modèle
                    module = __import__(module_path, fromlist=[model_name])
                    model_class = getattr(module, model_name)
                    
                    # Test de requête simple
                    count = model_class.query.count()
                    print(f"OK {model_name} - {count} enregistrements")
                    success_count += 1
                    
                except Exception as e:
                    print(f"ERREUR {model_name}: {e}")
            
            # Test des services refactorisés
            print("\nTest des services:")
            
            try:
                from app.services.dashboard_service import DashboardService
                stats = DashboardService.get_common_stats()
                print(f"OK DashboardService - {len(stats)} statistiques")
                success_count += 1
                total_count += 1
            except Exception as e:
                print(f"ERREUR DashboardService: {e}")
                total_count += 1
            
            try:
                from app.services.query_service import QueryService
                buses = QueryService.get_active_buses()
                print(f"OK QueryService - {len(buses)} bus actifs")
                success_count += 1
                total_count += 1
            except Exception as e:
                print(f"ERREUR QueryService: {e}")
                total_count += 1
            
            # Résumé
            print("\n" + "=" * 40)
            print("RESUME")
            print("=" * 40)
            print(f"Tests reussis: {success_count}/{total_count}")
            print(f"Taux de reussite: {(success_count/total_count*100):.1f}%")
            
            if success_count == total_count:
                print("\nTOUS LES MODELES SONT COMPATIBLES!")
                print("L'application peut fonctionner normalement.")
                return True
            else:
                print(f"\n{total_count - success_count} modele(s) ont des problemes.")
                print("Verifiez les erreurs ci-dessus.")
                return False
                
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_queries():
    """Test des requêtes spécifiques qui posaient problème"""
    print("\nTEST DES REQUETES SPECIFIQUES")
    print("=" * 40)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.models.bus_udm import BusUdM
            
            # Test de la requête qui causait l'erreur
            try:
                bus_actifs = BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count()
                print(f"OK Requete bus actifs: {bus_actifs} bus")
            except Exception as e:
                print(f"ERREUR Requete bus actifs: {e}")
                return False
            
            # Test d'autres requêtes communes
            try:
                tous_bus = BusUdM.query.count()
                print(f"OK Requete tous bus: {tous_bus} bus")
            except Exception as e:
                print(f"ERREUR Requete tous bus: {e}")
                return False
            
            try:
                bus_defaillants = BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count()
                print(f"OK Requete bus defaillants: {bus_defaillants} bus")
            except Exception as e:
                print(f"ERREUR Requete bus defaillants: {e}")
                return False
            
            print("\nTOUTES LES REQUETES FONCTIONNENT!")
            return True
            
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("VERIFICATION COMPLETE DE LA COMPATIBILITE")
    print("=" * 50)
    
    # Test des modèles
    models_ok = test_models_compatibility()
    
    # Test des requêtes spécifiques
    queries_ok = test_specific_queries()
    
    # Conclusion
    print("\n" + "=" * 50)
    if models_ok and queries_ok:
        print("SUCCES COMPLET!")
        print("Tous les modeles sont compatibles avec la base de donnees.")
        print("L'application refactorisee peut fonctionner normalement.")
    else:
        print("PROBLEMES DETECTES!")
        print("Certains modeles ne sont pas compatibles.")
        print("Verifiez les erreurs ci-dessus.")
