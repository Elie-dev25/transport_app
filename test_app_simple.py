#!/usr/bin/env python3
"""
Test simple de l'application
"""

try:
    print("🔍 Test de l'application Transport UdM...")
    
    # Test 1: Import de l'application
    print("1. Import de l'application...", end=" ")
    from app import create_app
    print("✅")
    
    # Test 2: Création de l'application
    print("2. Création de l'application...", end=" ")
    app = create_app()
    print("✅")
    
    # Test 3: Test du contexte
    print("3. Test du contexte d'application...", end=" ")
    with app.app_context():
        print("✅")
        
        # Test 4: Import des modèles
        print("4. Import des modèles...", end=" ")
        from app.models.bus_udm import BusUdM
        from app.models.utilisateur import Utilisateur
        from app.models.trajet import Trajet
        print("✅")
        
        # Test 5: Connexion base de données
        print("5. Test connexion base de données...", end=" ")
        from app.database import db
        
        # Compter les enregistrements
        bus_count = BusUdM.query.count()
        user_count = Utilisateur.query.count()
        trajet_count = Trajet.query.count()
        print("✅")
        
        print(f"\n📊 Données en base:")
        print(f"   - Bus UdM: {bus_count}")
        print(f"   - Utilisateurs: {user_count}")
        print(f"   - Trajets: {trajet_count}")
    
    print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    print("✅ L'application est prête à démarrer")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
