#!/usr/bin/env python3
"""
Test du refactoring Phase 1 - Services centralisés
"""

print("🔍 TEST PHASE 1 - SERVICES CENTRALISÉS")
print("=" * 50)

try:
    # Test des imports
    print("📦 Test des imports...")
    from app.services.dashboard_service import DashboardService
    from app.services.form_service import FormService
    from app.services.query_service import QueryService
    print("✅ Tous les services importés avec succès")
    
    # Test DashboardService
    print("\n📊 Test DashboardService...")
    try:
        stats = DashboardService.get_common_stats()
        print(f"✅ get_common_stats(): {len(stats)} statistiques récupérées")
        
        # Vérifier les clés importantes
        required_keys = ['bus_actifs', 'trajets_jour_aed', 'etudiants', 'trafic']
        missing_keys = [key for key in required_keys if key not in stats]
        if missing_keys:
            print(f"⚠️  Clés manquantes: {missing_keys}")
        else:
            print("✅ Toutes les clés requises présentes")
            
    except Exception as e:
        print(f"❌ Erreur DashboardService: {e}")
    
    # Test QueryService
    print("\n🔍 Test QueryService...")
    try:
        buses = QueryService.get_active_buses()
        print(f"✅ get_active_buses(): {len(buses)} bus actifs")
        
        bus_stats = QueryService.get_bus_stats()
        print(f"✅ get_bus_stats(): {bus_stats}")
        
    except Exception as e:
        print(f"❌ Erreur QueryService: {e}")
    
    # Test FormService
    print("\n📝 Test FormService...")
    try:
        bus_choices = FormService.get_bus_choices()
        print(f"✅ get_bus_choices(): {len(bus_choices)} choix disponibles")
        
        chauffeur_choices = FormService.get_chauffeur_choices()
        print(f"✅ get_chauffeur_choices(): {len(chauffeur_choices)} chauffeurs")
        
    except Exception as e:
        print(f"❌ Erreur FormService: {e}")
    
    print("\n🎉 PHASE 1 - TESTS TERMINÉS")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ ERREUR CRITIQUE: {e}")
    import traceback
    traceback.print_exc()
