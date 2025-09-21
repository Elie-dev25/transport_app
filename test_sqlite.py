#!/usr/bin/env python3
"""
Test avec SQLite en mode développement
"""

import os

# Forcer le mode développement pour utiliser SQLite
os.environ['FLASK_ENV'] = 'development'

try:
    print("🔍 Test avec SQLite (mode développement)...")
    
    # Test 1: Import et création de l'application
    print("1. Création de l'application...", end=" ")
    from app import create_app
    app = create_app()
    print("✅")
    
    # Vérifier la configuration
    print(f"2. Configuration: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Test 3: Test du contexte et base de données
    print("3. Test connexion base de données...", end=" ")
    with app.app_context():
        from app.database import db
        
        # Test des modèles
        from app.models.bus_udm import BusUdM
        from app.models.utilisateur import Utilisateur
        from app.models.trajet import Trajet
        
        # Compter les enregistrements
        bus_count = BusUdM.query.count()
        user_count = Utilisateur.query.count()
        trajet_count = Trajet.query.count()
        print("✅")
        
        print(f"\n📊 Données en base SQLite:")
        print(f"   - Bus UdM: {bus_count}")
        print(f"   - Utilisateurs: {user_count}")
        print(f"   - Trajets: {trajet_count}")
    
    print("\n🎉 SUCCÈS! L'application fonctionne avec SQLite")
    print("✅ Prête pour le démarrage en mode développement")
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
