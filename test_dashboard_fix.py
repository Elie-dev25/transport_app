#!/usr/bin/env python3
"""
Test du DashboardService après correction du modèle BusUdM
"""

def test_dashboard_service():
    """Test le DashboardService avec le modèle BusUdM corrigé"""
    print("TEST DASHBOARD SERVICE APRES CORRECTION")
    print("=" * 40)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Test du modèle BusUdM
            from app.models.bus_udm import BusUdM
            
            print("1. Test modele BusUdM:")
            count_bus = BusUdM.query.count()
            print(f"   - Total bus: {count_bus}")
            
            if count_bus > 0:
                bus = BusUdM.query.first()
                print(f"   - Premier bus: {bus.numero} - {bus.immatriculation}")
                print(f"   - Etat: {bus.etat_vehicule}")
            
            # Test de la requête qui causait l'erreur
            print("\n2. Test requete bus actifs:")
            try:
                bus_actifs = BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count()
                print(f"   - Bus actifs: {bus_actifs}")
            except Exception as e:
                print(f"   - ERREUR: {e}")
                return False
            
            # Test du DashboardService
            print("\n3. Test DashboardService:")
            try:
                from app.services.dashboard_service import DashboardService
                stats = DashboardService.get_common_stats()
                print(f"   - Statistiques generees: {len(stats)}")
                
                for key, value in stats.items():
                    print(f"   - {key}: {value}")
                    
            except Exception as e:
                print(f"   - ERREUR DashboardService: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            print("\nTOUS LES TESTS REUSSIS!")
            return True
            
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dashboard_service()
    
    if success:
        print("\nSUCCES COMPLET!")
        print("Le modele BusUdM est maintenant compatible.")
        print("Le DashboardService fonctionne correctement.")
        print("L'application peut demarrer sans erreur.")
    else:
        print("\nPROBLEMES DETECTES!")
        print("Verifiez les erreurs ci-dessus.")
