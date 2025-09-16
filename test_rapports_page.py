#!/usr/bin/env python3
"""
Test de la page rapports côté superviseur
"""

import requests
import sys

def test_rapports_superviseur():
    """Test d'accès à la page rapports superviseur"""
    
    print("🔍 TEST DE LA PAGE RAPPORTS SUPERVISEUR")
    print("=" * 50)
    
    try:
        # URL de test (supposons que l'app tourne sur localhost:5000)
        url = "http://localhost:5000/superviseur/rapports"
        
        print(f"📡 Test d'accès à : {url}")
        
        # Tentative de connexion (sans authentification pour le test)
        response = requests.get(url, timeout=5)
        
        print(f"📊 Code de réponse : {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page accessible - Contenu reçu")
            
            # Vérifier si le contenu contient les éléments attendus
            content = response.text
            
            checks = [
                ('table_container', 'Macro table_container utilisée'),
                ('Statistiques Rapides', 'Section statistiques présente'),
                ('Rapports Détaillés', 'Section rapports présente'),
                ('info-card', 'Cartes d\'information présentes'),
                ('tableaux.css', 'CSS unifié chargé')
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description}")
                    
        elif response.status_code == 302:
            print("🔄 Redirection (probablement vers login)")
            print(f"   Location: {response.headers.get('Location', 'Non spécifiée')}")
            
        elif response.status_code == 403:
            print("🚫 Accès interdit (permissions insuffisantes)")
            
        elif response.status_code == 500:
            print("💥 Erreur serveur interne")
            print("   Vérifiez les logs de l'application")
            
        else:
            print(f"❓ Code de réponse inattendu : {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Vérifiez que l'application Flask est démarrée")
        
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - Le serveur met trop de temps à répondre")
        
    except Exception as e:
        print(f"💥 Erreur inattendue : {str(e)}")

def test_template_syntax():
    """Test de syntaxe du template rapports.html"""
    
    print("\n🔧 TEST DE SYNTAXE DU TEMPLATE")
    print("-" * 40)
    
    template_path = 'app/templates/rapports.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifications basiques
        checks = [
            ('{% from \'macros/tableaux_components.html\'', 'Import des macros'),
            ('{% call table_container(', 'Utilisation de table_container'),
            ('{% endcall %}', 'Fermeture des macros'),
            ('superviseur_mode', 'Mode superviseur géré'),
            ('stats.today', 'Données statistiques utilisées')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description}")
                
        print(f"\n📊 Taille du template : {len(content)} caractères")
        
    except FileNotFoundError:
        print(f"❌ Template non trouvé : {template_path}")
    except Exception as e:
        print(f"💥 Erreur lors de la lecture : {str(e)}")

if __name__ == "__main__":
    test_template_syntax()
    test_rapports_superviseur()
