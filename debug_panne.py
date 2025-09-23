#!/usr/bin/env python3
"""
Script de debug pour tester la route de déclaration de panne
"""

import requests
import json

def test_declaration_panne():
    """Test de la route de déclaration avec différents jeux de données"""
    
    url = "http://127.0.0.1:5000/admin/declarer_panne"
    
    # Test cases
    test_cases = [
        {
            "name": "Données complètes",
            "data": {
                "numero_bus_udm": "TEST-001",
                "numero_aed": "TEST-001",
                "immatriculation": "AB-123-CD",
                "kilometrage": 15000,
                "description": "Test de déclaration de panne",
                "criticite": "FAIBLE",
                "immobilisation": False
            }
        },
        {
            "name": "Numéro manquant",
            "data": {
                "numero_bus_udm": "",
                "description": "Test de déclaration de panne",
                "criticite": "FAIBLE",
                "immobilisation": False
            }
        },
        {
            "name": "Description manquante",
            "data": {
                "numero_bus_udm": "TEST-001",
                "description": "",
                "criticite": "FAIBLE",
                "immobilisation": False
            }
        },
        {
            "name": "Criticité manquante",
            "data": {
                "numero_bus_udm": "TEST-001",
                "description": "Test de déclaration de panne",
                "criticite": "",
                "immobilisation": False
            }
        },
        {
            "name": "Données comme envoyées par le JavaScript",
            "data": {
                "numero_bus_udm": "UDM-001",
                "numero_aed": "UDM-001",
                "immatriculation": "AB-123-CD",
                "kilometrage": "15000",  # String comme envoyé par le formulaire
                "description": "Problème moteur",
                "criticite": "MOYENNE",
                "immobilisation": True
            }
        }
    ]
    
    print("🧪 TEST DE LA ROUTE DE DÉCLARATION DE PANNE")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Test: {test_case['name']}")
        print(f"   Données: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(
                url,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"   Status: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"   Réponse: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Réponse (texte): {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Erreur: Impossible de se connecter au serveur")
            print("   Vérifiez que l'application Flask est démarrée sur http://127.0.0.1:5000")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
    
    print("\n" + "=" * 60)
    print("💡 CONSEILS:")
    print("1. Vérifiez que l'application Flask est démarrée")
    print("2. Regardez les logs de l'application pour voir les données reçues")
    print("3. Les messages d'erreur vous indiqueront quel champ pose problème")

if __name__ == "__main__":
    test_declaration_panne()
