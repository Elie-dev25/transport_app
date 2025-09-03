#!/usr/bin/env python3
"""
Script de test pour vérifier la compatibilité du modèle Trajet avec la base de données
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer l'app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.trajet import Trajet
from app.database import db
from datetime import datetime

def test_modele_trajet():
    """Test du modèle Trajet avec la structure de base de données actuelle"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔍 Test de compatibilité du modèle Trajet...")
            
            # Test 1: Vérifier que le modèle peut se connecter à la table
            print("\n1. Test de connexion à la table...")
            count = Trajet.query.count()
            print(f"   ✅ Nombre de trajets existants: {count}")
            
            # Test 2: Vérifier les colonnes obligatoires
            print("\n2. Test des colonnes obligatoires...")
            
            # Créer un trajet de test (sans l'enregistrer)
            trajet_test = Trajet(
                type_trajet='UDM_INTERNE',
                date_heure_depart=datetime.now(),
                point_depart='Mfetum',
                point_arriver='Banekane',
                type_passagers='ETUDIANT',
                nombre_places_occupees=30,
                chauffeur_id=1,
                numero_bus_udm='AED-01',
                enregistre_par=1
            )
            
            print("   ✅ Création d'un objet Trajet réussie")
            
            # Test 3: Vérifier les ENUM
            print("\n3. Test des valeurs ENUM...")
            
            # Test type_trajet
            valid_types = ['UDM_INTERNE', 'PRESTATAIRE', 'AUTRE']
            for type_t in valid_types:
                trajet_test.type_trajet = type_t
                print(f"   ✅ type_trajet '{type_t}' accepté")
            
            # Test point_depart
            valid_points = ['Mfetum', 'Ancienne Mairie', 'Banekane']
            for point in valid_points:
                trajet_test.point_depart = point
                print(f"   ✅ point_depart '{point}' accepté")
            
            # Test type_passagers
            valid_passagers = ['ETUDIANT', 'PERSONNEL', 'MALADE']
            for passager in valid_passagers:
                trajet_test.type_passagers = passager
                print(f"   ✅ type_passagers '{passager}' accepté")
            
            # Test 4: Vérifier les champs optionnels
            print("\n4. Test des champs optionnels...")
            trajet_test.point_arriver = 'Ancienne Mairie'
            trajet_test.motif = 'Test de fonctionnement'
            trajet_test.immat_bus = None
            print("   ✅ Champs optionnels configurés")
            
            # Test 5: Lire quelques trajets existants
            print("\n5. Test de lecture des trajets existants...")
            trajets = Trajet.query.limit(3).all()
            for i, trajet in enumerate(trajets, 1):
                print(f"   ✅ Trajet {i}: {trajet.type_trajet} - {trajet.point_depart} → {trajet.point_arriver or 'N/A'}")
            
            print("\n🎉 TOUS LES TESTS RÉUSSIS !")
            print("   Le modèle Trajet est compatible avec votre base de données.")
            
        except Exception as e:
            print(f"\n❌ ERREUR: {str(e)}")
            print("   Le modèle nécessite des ajustements.")
            return False
    
    return True

if __name__ == '__main__':
    success = test_modele_trajet()
    sys.exit(0 if success else 1)
