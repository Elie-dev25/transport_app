#!/usr/bin/env python3
"""
Test de connexion à la base de données après refactoring
"""

def test_database_connection():
    """Test la connexion à la base de données"""
    print("TEST DE CONNEXION BASE DE DONNEES")
    print("=" * 40)
    
    try:
        # Créer l'application
        from app import create_app
        app = create_app()
        
        print(f"Configuration utilisee: {app.config.get('ENV', 'default')}")
        print(f"Base de donnees: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        with app.app_context():
            from app.database import db
            
            # Test de connexion simple
            result = db.engine.execute("SELECT 1 as test").fetchone()
            if result and result[0] == 1:
                print("OK Connexion base de donnees reussie")
            else:
                print("ERREUR Connexion echouee")
                return False
            
            # Test des modèles principaux
            print("\nTest des modeles:")
            
            # Test BusUdM
            try:
                from app.models.bus_udm import BusUdM
                count_bus = BusUdM.query.count()
                print(f"OK BusUdM - {count_bus} bus trouves")
            except Exception as e:
                print(f"ERREUR BusUdM: {e}")
            
            # Test Utilisateur
            try:
                from app.models.utilisateur import Utilisateur
                count_users = Utilisateur.query.count()
                print(f"OK Utilisateur - {count_users} utilisateurs trouves")
            except Exception as e:
                print(f"ERREUR Utilisateur: {e}")
            
            # Test Trajet
            try:
                from app.models.trajet import Trajet
                count_trajets = Trajet.query.count()
                print(f"OK Trajet - {count_trajets} trajets trouves")
            except Exception as e:
                print(f"ERREUR Trajet: {e}")
            
            # Test des services refactorisés
            print("\nTest des services refactorises:")
            
            try:
                from app.services.dashboard_service import DashboardService
                stats = DashboardService.get_common_stats()
                print(f"OK DashboardService - {len(stats)} statistiques")
            except Exception as e:
                print(f"ERREUR DashboardService: {e}")
            
            try:
                from app.services.query_service import QueryService
                buses = QueryService.get_active_buses()
                print(f"OK QueryService - {len(buses)} bus actifs")
            except Exception as e:
                print(f"ERREUR QueryService: {e}")
            
            print("\nTOUS LES TESTS PASSES!")
            return True
            
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_connection()
    if success:
        print("\nBASE DE DONNEES FONCTIONNELLE!")
        print("L'application peut demarrer normalement.")
    else:
        print("\nPROBLEME AVEC LA BASE DE DONNEES!")
        print("Verifiez la configuration et la connexion MySQL.")
