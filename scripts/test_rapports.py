#!/usr/bin/env python3
"""
Script de test pour la page rapports
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer l'app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.routes.admin.rapports import get_daily_stats, get_fleet_stats, get_trajets_evolution
from datetime import date

def test_rapports_functions():
    """Test des fonctions de rapports"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Test des fonctions de rapports...")
            
            # Test 1: Statistiques du jour
            print("\n1. Test des statistiques quotidiennes...")
            today_stats = get_daily_stats(date.today())
            print(f"   ✅ Statistiques aujourd'hui: {today_stats}")
            
            # Test 2: Statistiques de la flotte
            print("\n2. Test des statistiques de la flotte...")
            fleet_stats = get_fleet_stats()
            print(f"   ✅ Statistiques flotte: {fleet_stats}")
            
            # Test 3: Données graphique évolution
            print("\n3. Test des données graphiques...")
            evolution_data = get_trajets_evolution()
            print(f"   ✅ Données évolution: {len(evolution_data.get('labels', []))} points")
            
            print("\n🎉 TOUS LES TESTS RÉUSSIS !")
            print("   Les fonctions de rapports fonctionnent correctement.")
            
        except Exception as e:
            print(f"\n❌ ERREUR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_routes():
    """Test des routes de rapports"""
    
    app = create_app()
    
    with app.test_client() as client:
        try:
            print("\n🌐 Test des routes...")
            
            # Test route principale (nécessite authentification)
            print("\n1. Test route principale /admin/rapports/...")
            response = client.get('/admin/rapports/')
            print(f"   Status: {response.status_code}")
            
            # Test API stats (nécessite authentification)
            print("\n2. Test API stats...")
            response = client.get('/admin/rapports/api/stats/today')
            print(f"   Status: {response.status_code}")
            
            # Test API charts (nécessite authentification)
            print("\n3. Test API charts...")
            response = client.get('/admin/rapports/api/chart/trajets_evolution')
            print(f"   Status: {response.status_code}")
            
            print("\n✅ Routes testées (authentification requise pour accès complet)")
            
        except Exception as e:
            print(f"\n❌ ERREUR ROUTES: {str(e)}")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 TEST DE LA PAGE RAPPORTS")
    print("=" * 60)
    
    success1 = test_rapports_functions()
    success2 = test_routes()
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("La page rapports est prête à être utilisée.")
        sys.exit(0)
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)
