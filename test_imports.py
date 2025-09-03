#!/usr/bin/env python3
"""
Script simple pour tester les imports des nouveaux modèles
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports des nouveaux modèles"""
    print("Test des imports des modèles Bus UdM...")
    
    try:
        # Test import BusUdM
        print("- Import BusUdM...", end=" ")
        from app.models.bus_udm import BusUdM
        print("✓")
        
        # Test import DocumentBusUdM
        print("- Import DocumentBusUdM...", end=" ")
        from app.models.document_bus_udm import DocumentBusUdM
        print("✓")
        
        # Test import PanneBusUdM
        print("- Import PanneBusUdM...", end=" ")
        from app.models.panne_bus_udm import PanneBusUdM
        print("✓")
        
        # Test import BusUdMForm
        print("- Import BusUdMForm...", end=" ")
        from app.forms.bus_udm_form import BusUdMForm
        print("✓")
        
        print("\n✅ Tous les imports ont réussi!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

def check_class_attributes():
    """Vérifier les attributs des classes"""
    print("\nVérification des attributs des classes...")
    
    try:
        from app.models.bus_udm import BusUdM
        
        # Vérifier les nouveaux attributs
        expected_attrs = ['numero_chassis', 'modele', 'type_vehicule', 'marque']
        
        for attr in expected_attrs:
            if hasattr(BusUdM, attr):
                print(f"- {attr}: ✓")
            else:
                print(f"- {attr}: ❌ MANQUANT")
                return False
        
        print("\n✅ Tous les attributs sont présents!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la vérification: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("TEST DES MODÈLES BUS UDM")
    print("=" * 50)
    
    success = True
    
    # Test 1: Imports
    if not test_imports():
        success = False
    
    # Test 2: Attributs (seulement si les imports ont réussi)
    if success and not check_class_attributes():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TOUS LES TESTS ONT RÉUSSI!")
        print("Les modèles Bus UdM sont correctement configurés.")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les erreurs ci-dessus.")
    
    sys.exit(0 if success else 1)
