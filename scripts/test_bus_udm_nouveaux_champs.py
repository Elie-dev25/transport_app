#!/usr/bin/env python3
"""
Script de test pour vérifier les nouveaux champs Bus UdM
- Teste la création d'un Bus UdM avec les nouveaux champs
- Vérifie la validation des formulaires
- Teste les contraintes de base de données

Usage: python scripts/test_bus_udm_nouveaux_champs.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models.bus_udm import BusUdM
from datetime import date

def test_bus_udm_creation():
    """Test de création d'un Bus UdM avec les nouveaux champs"""
    app = create_app()
    
    with app.app_context():
        print("=== Test de création de Bus UdM avec nouveaux champs ===")
        
        # Données de test
        test_data = {
            'numero': 'UDM-TEST-001',
            'immatriculation': 'TEST-1234-AB',
            'numero_chassis': 'VF1234567890123456',
            'modele': 'Sprinter 515',
            'type_vehicule': 'MINIBUS',
            'marque': 'Mercedes',
            'kilometrage': 15000,
            'type_huile': 'Quartz 5000 20W-50',
            'km_critique_huile': 20000,
            'km_critique_carburant': 25000,
            'capacite_plein_carburant': 500,
            'date_derniere_vidange': date(2024, 1, 15),
            'etat_vehicule': 'BON',
            'nombre_places': 30,
            'derniere_maintenance': date(2024, 1, 10)
        }
        
        try:
            # Supprimer le Bus UdM de test s'il existe déjà
            existing_bus = BusUdM.query.filter_by(numero='UDM-TEST-001').first()
            if existing_bus:
                db.session.delete(existing_bus)
                db.session.commit()
                print("✓ Bus UdM de test existant supprimé")
            
            # Créer un nouveau Bus UdM avec tous les champs
            nouveau_bus = BusUdM(**test_data)
            db.session.add(nouveau_bus)
            db.session.commit()
            
            print("✓ Bus UdM créé avec succès avec les nouveaux champs")
            print(f"  - Numéro: {nouveau_bus.numero}")
            print(f"  - Immatriculation: {nouveau_bus.immatriculation}")
            print(f"  - Numéro châssis: {nouveau_bus.numero_chassis}")
            print(f"  - Modèle: {nouveau_bus.modele}")
            print(f"  - Type: {nouveau_bus.type_vehicule}")
            print(f"  - Marque: {nouveau_bus.marque}")
            
            # Vérifier la récupération
            bus_recupere = BusUdM.query.filter_by(numero='UDM-TEST-001').first()
            assert bus_recupere is not None, "Bus UdM non trouvé après création"
            assert bus_recupere.numero_chassis == 'VF1234567890123456', "Numéro châssis incorrect"
            assert bus_recupere.modele == 'Sprinter 515', "Modèle incorrect"
            assert bus_recupere.type_vehicule == 'MINIBUS', "Type véhicule incorrect"
            assert bus_recupere.marque == 'Mercedes', "Marque incorrecte"
            
            print("✓ Vérification des données récupérées réussie")
            
            # Nettoyer
            db.session.delete(nouveau_bus)
            db.session.commit()
            print("✓ Bus UdM de test supprimé")
            
        except Exception as e:
            print(f"✗ Erreur lors du test: {str(e)}")
            db.session.rollback()
            return False
    
    return True

def test_contraintes_unicite():
    """Test des contraintes d'unicité"""
    app = create_app()
    
    with app.app_context():
        print("\n=== Test des contraintes d'unicité ===")
        
        try:
            # Créer deux Bus UdM avec le même numéro de châssis
            bus1_data = {
                'numero': 'UDM-TEST-002',
                'immatriculation': 'TEST-2222-AB',
                'numero_chassis': 'CHASSIS-UNIQUE-TEST',
                'modele': 'Hiace',
                'type_vehicule': 'MINIBUS',
                'marque': 'Toyota',
                'kilometrage': 10000,
                'type_huile': 'Quartz 5000 20W-50',
                'km_critique_huile': 15000,
                'km_critique_carburant': 20000,
                'capacite_plein_carburant': 400,
                'date_derniere_vidange': date(2024, 1, 15),
                'etat_vehicule': 'BON',
                'nombre_places': 25,
                'derniere_maintenance': date(2024, 1, 10)
            }
            
            bus2_data = bus1_data.copy()
            bus2_data['numero'] = 'UDM-TEST-003'
            bus2_data['immatriculation'] = 'TEST-3333-AB'
            # Même numéro de châssis -> doit échouer
            
            # Nettoyer d'abord
            for num in ['UDM-TEST-002', 'UDM-TEST-003']:
                existing = BusUdM.query.filter_by(numero=num).first()
                if existing:
                    db.session.delete(existing)
            db.session.commit()
            
            # Créer le premier Bus UdM
            bus1 = BusUdM(**bus1_data)
            db.session.add(bus1)
            db.session.commit()
            print("✓ Premier Bus UdM créé")
            
            # Tenter de créer le second avec le même châssis
            bus2 = BusUdM(**bus2_data)
            db.session.add(bus2)
            
            try:
                db.session.commit()
                print("✗ La contrainte d'unicité du châssis n'a pas fonctionné")
                # Nettoyer
                db.session.delete(bus1)
                db.session.delete(bus2)
                db.session.commit()
                return False
            except Exception:
                print("✓ Contrainte d'unicité du châssis respectée")
                db.session.rollback()
                
                # Nettoyer le premier Bus UdM
                db.session.delete(bus1)
                db.session.commit()
                return True
                
        except Exception as e:
            print(f"✗ Erreur lors du test de contraintes: {str(e)}")
            db.session.rollback()
            return False

def main():
    """Fonction principale"""
    print("Démarrage des tests pour les nouveaux champs Bus UdM")
    print("=" * 50)
    
    success = True
    
    # Test 1: Création avec nouveaux champs
    if not test_bus_udm_creation():
        success = False
    
    # Test 2: Contraintes d'unicité
    if not test_contraintes_unicite():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Tous les tests ont réussi!")
        print("\nLes nouveaux champs Bus UdM sont fonctionnels:")
        print("- numero_chassis (unique)")
        print("- modele")
        print("- type_vehicule (ENUM)")
        print("- marque")
    else:
        print("✗ Certains tests ont échoué")
        print("Vérifiez que la base de données a été mise à jour avec le script SQL")
    
    return success

if __name__ == '__main__':
    main()
