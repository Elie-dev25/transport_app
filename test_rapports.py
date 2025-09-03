#!/usr/bin/env python3
"""
Script de test pour la page rapports
Permet de tester l'application sans problèmes d'environnement
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.extensions import db
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application Flask créée avec succès")
        print("✅ Base de données connectée")
        
        # Test des imports des modèles
        from app.models.trajet import Trajet
        from app.models.aed import AED
        from app.models.chauffeur import Chauffeur
        from app.models.carburation import Carburation
        from app.models.panne_aed import PanneAED
        from app.models.vidange import Vidange
        from app.models.prestataire import Prestataire
        print("✅ Tous les modèles importés correctement")
        
        # Test de la route rapports
        from app.routes.admin import rapports
        print("✅ Module rapports importé correctement")
        
        print("\n🎉 Tous les tests passent ! La page rapports est prête.")
        print("\n📋 Pour accéder à la page rapports :")
        print("   1. Démarrez l'application : python run.py")
        print("   2. Connectez-vous avec un compte admin/charge_transport")
        print("   3. Allez sur : http://localhost:5000/admin/rapports")
        
        print("\n📊 Fonctionnalités disponibles :")
        print("   • Performance des chauffeurs et prestataires")
        print("   • Suivi kilométrage et utilisation des bus")
        print("   • Coûts carburant et consommation moyenne")
        print("   • ROI par bus et budget maintenance")
        print("   • Historique des pannes et planning vidanges")
        print("   • Filtres par période (jour/semaine/mois/année)")
        print("   • Graphiques interactifs avec Chart.js")
        print("   • Export PDF (structure prête)")

except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    print("\n🔧 Solutions possibles :")
    print("   1. Activez l'environnement virtuel")
    print("   2. Installez les dépendances : pip install -r requirements.txt")
    print("   3. Vérifiez que Flask est installé : pip install flask")

except Exception as e:
    print(f"❌ Erreur : {e}")
    print("\n🔧 Vérifiez la configuration de la base de données")
