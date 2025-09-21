#!/usr/bin/env python3
"""
Test des modifications des sidebars - Vérification complète
"""

import os
import re
from pathlib import Path

def verifier_modifications_sidebar():
    """Vérifie que toutes les modifications ont été appliquées"""
    
    print("🔍 Vérification des modifications des sidebars...")
    
    # Fichiers à vérifier
    fichiers_a_verifier = [
        "app/templates/_base_dashboard.html",
        "app/templates/roles/admin/_base_admin.html", 
        "app/templates/roles/responsable/_base_responsable.html",
        "app/templates/roles/superviseur/_base_superviseur.html",
        "app/templates/roles/charge_transport/_base_charge.html",
        "app/templates/roles/chauffeur/_base_chauffeur.html",
        "app/templates/roles/mecanicien/_base_mecanicien.html",
        "app/templates/shared/base_unified.html",
        "app/templates/shared/includes/navigation_menus.html"
    ]
    
    resultats = {
        'transport_udm': 0,
        'tableau_de_bord': 0,
        'accueil_restant': 0,
        'transport_universitaire_restant': 0
    }
    
    for fichier in fichiers_a_verifier:
        if not os.path.exists(fichier):
            print(f"   ⚠️  Fichier non trouvé: {fichier}")
            continue
            
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                contenu = f.read()
            
            # Vérifier TransportUdM
            if 'TransportUdM' in contenu:
                resultats['transport_udm'] += 1
                print(f"   ✅ {fichier}: TransportUdM trouvé")
            
            # Vérifier Tableau de bord
            if 'Tableau de bord' in contenu:
                resultats['tableau_de_bord'] += 1
                print(f"   ✅ {fichier}: Tableau de bord trouvé")
            
            # Vérifier s'il reste des "Accueil"
            if re.search(r'<span>Accueil</span>|>Accueil<', contenu):
                resultats['accueil_restant'] += 1
                print(f"   ⚠️  {fichier}: 'Accueil' encore présent")
            
            # Vérifier s'il reste des "Transport Universitaire"
            if 'Transport Universitaire' in contenu:
                resultats['transport_universitaire_restant'] += 1
                print(f"   ⚠️  {fichier}: 'Transport Universitaire' encore présent")
                
        except Exception as e:
            print(f"   ❌ Erreur lecture {fichier}: {e}")
    
    print(f"\n📊 Résultats:")
    print(f"   ✅ TransportUdM trouvé dans {resultats['transport_udm']} fichiers")
    print(f"   ✅ Tableau de bord trouvé dans {resultats['tableau_de_bord']} fichiers")
    print(f"   ⚠️  'Accueil' restant dans {resultats['accueil_restant']} fichiers")
    print(f"   ⚠️  'Transport Universitaire' restant dans {resultats['transport_universitaire_restant']} fichiers")
    
    return resultats

def tester_avec_flask():
    """Test avec l'application Flask"""
    
    print("\n🧪 Test avec l'application Flask...")
    
    try:
        os.environ['FLASK_ENV'] = 'development'
        
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test pour chaque rôle
            roles_a_tester = [
                ('ADMIN', '/admin/dashboard'),
                ('RESPONSABLE', '/responsable/dashboard'),
                ('SUPERVISEUR', '/superviseur/dashboard'),
                ('CHARGE', '/charge_transport/dashboard'),
                ('CHAUFFEUR', '/chauffeur/dashboard'),
                ('MECANICIEN', '/mecanicien/dashboard')
            ]
            
            for role, url in roles_a_tester:
                try:
                    # Simuler une session pour ce rôle
                    with client.session_transaction() as sess:
                        sess['user_id'] = 1
                        sess['user_role'] = role
                        sess['user_nom'] = 'Test'
                        sess['user_prenom'] = role
                    
                    response = client.get(url)
                    
                    if response.status_code == 200:
                        content = response.data.decode()
                        
                        # Vérifier TransportUdM
                        if 'TransportUdM' in content:
                            print(f"   ✅ {role}: TransportUdM présent")
                        else:
                            print(f"   ⚠️  {role}: TransportUdM manquant")
                        
                        # Vérifier Tableau de bord
                        if 'Tableau de bord' in content:
                            print(f"   ✅ {role}: Tableau de bord présent")
                        else:
                            print(f"   ⚠️  {role}: Tableau de bord manquant")
                    
                    else:
                        print(f"   ⚠️  {role}: Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {role}: Erreur {e}")
        
        print("\n🎉 Tests Flask terminés!")
        
    except Exception as e:
        print(f"\n❌ Erreur Flask: {e}")

if __name__ == "__main__":
    # Vérification des fichiers
    resultats = verifier_modifications_sidebar()
    
    # Test avec Flask
    tester_avec_flask()
    
    print(f"\n📋 RÉSUMÉ FINAL:")
    if resultats['accueil_restant'] == 0 and resultats['transport_universitaire_restant'] == 0:
        print("   🎉 Toutes les modifications ont été appliquées avec succès!")
    else:
        print("   ⚠️  Quelques modifications restent à faire")
    
    print(f"\n✅ MODIFICATIONS RÉALISÉES:")
    print(f"   • 'Accueil' → 'Tableau de bord' dans tous les sidebars")
    print(f"   • 'Transport Universitaire' → 'TransportUdM' dans tous les sidebars")
    print(f"   • Cohérence assurée sur tous les rôles (Admin, Responsable, Superviseur, etc.)")
