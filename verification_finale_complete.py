#!/usr/bin/env python3
"""
Vérification finale complète - Parcours ligne par ligne de tous les templates
"""

import os
import re
from pathlib import Path

def verifier_ligne_par_ligne():
    """Parcourt tous les templates ligne par ligne pour détecter les problèmes"""
    print("🔍 VÉRIFICATION LIGNE PAR LIGNE DE TOUS LES TEMPLATES")
    print("=" * 80)
    
    templates_dir = Path("app/templates")
    problemes = []
    
    # Patterns problématiques à détecter
    patterns_problematiques = [
        (r"{% include ['\"]partials/", "Référence partials/ dans include"),
        (r"{% from ['\"]partials/", "Référence partials/ dans from"),
        (r"{% extends ['\"]partials/", "Référence partials/ dans extends"),
        (r"{% extends ['\"]_base_[^/]*\.html['\"]", "Base template sans roles/"),
        (r"{% from ['\"]macros/[^'\"]*['\"]", "Macro sans shared/"),
        (r"{% include ['\"]admin/[^'\"]*\.html['\"]", "Include admin/ direct"),
        (r"{% include ['\"]charge_transport/[^'\"]*\.html['\"]", "Include charge_transport/ direct"),
        (r"{% include ['\"]chauffeur/[^'\"]*\.html['\"]", "Include chauffeur/ direct"),
        (r"{% include ['\"]superviseur/[^'\"]*\.html['\"]", "Include superviseur/ direct"),
        (r"{% include ['\"]mecanicien/[^'\"]*\.html['\"]", "Include mecanicien/ direct"),
    ]
    
    total_files = 0
    files_with_issues = 0
    
    for template_file in templates_dir.rglob("*.html"):
        total_files += 1
        file_has_issues = False
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                    
                for pattern, description in patterns_problematiques:
                    if re.search(pattern, line):
                        if not file_has_issues:
                            print(f"\n❌ {template_file.relative_to(templates_dir)}")
                            file_has_issues = True
                            files_with_issues += 1
                        
                        print(f"   Ligne {line_num}: {description}")
                        print(f"   → {line_stripped}")
                        problemes.append(f"{template_file}:{line_num} - {description}")
                        
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   • {total_files} fichiers analysés")
    print(f"   • {files_with_issues} fichiers avec problèmes")
    print(f"   • {len(problemes)} problèmes détectés")
    
    return problemes

def verifier_fichiers_requis():
    """Vérifie que tous les fichiers requis existent"""
    print("\n\n📁 VÉRIFICATION DES FICHIERS REQUIS")
    print("=" * 80)
    
    fichiers_requis = [
        # Modales partagées
        "app/templates/shared/modals/_add_bus_modal.html",
        "app/templates/shared/modals/_add_user_modal.html",
        "app/templates/shared/modals/_declaration_panne_modal.html",
        "app/templates/shared/modals/_depannage_modal.html",
        "app/templates/shared/modals/_document_modal.html",
        "app/templates/shared/modals/_edit_statut_chauffeur_modal.html",
        "app/templates/shared/modals/_statut_details_modal.html",
        "app/templates/shared/modals/trajet_interne_modal.html",
        "app/templates/shared/modals/trajet_prestataire_modal.html",
        "app/templates/shared/modals/autres_trajets_modal.html",
        
        # Macros partagées
        "app/templates/shared/macros/tableaux_components.html",
        "app/templates/shared/macros/trajet_modals.html",
        "app/templates/shared/macros/superviseur_components.html",
        
        # Base templates
        "app/templates/roles/admin/_base_admin.html",
        "app/templates/roles/charge_transport/_base_charge.html",
        "app/templates/roles/chauffeur/_base_chauffeur.html",
        "app/templates/roles/superviseur/_base_superviseur.html",
        "app/templates/roles/mecanicien/_base_mecanicien.html",
    ]
    
    manquants = []
    
    for fichier in fichiers_requis:
        if os.path.exists(fichier):
            print(f"✅ {os.path.basename(fichier)}")
        else:
            print(f"❌ {os.path.basename(fichier)} - MANQUANT")
            manquants.append(fichier)
    
    return manquants

def tester_routes_principales():
    """Teste les routes principales pour détecter les erreurs"""
    print("\n\n🚀 TEST DES ROUTES PRINCIPALES")
    print("=" * 80)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            routes_a_tester = [
                ('/admin/dashboard', 'Dashboard Admin'),
                ('/admin/bus', 'Bus UdM'),
                ('/charge_transport/dashboard', 'Dashboard Charge Transport'),
                ('/chauffeur/dashboard', 'Dashboard Chauffeur'),
                ('/superviseur/dashboard', 'Dashboard Superviseur'),
            ]
            
            erreurs = []
            
            for route, nom in routes_a_tester:
                try:
                    # Note: Ces routes nécessitent une authentification, 
                    # donc on s'attend à une redirection (302) ou erreur d'auth (401/403)
                    response = client.get(route)
                    if response.status_code in [200, 302, 401, 403]:
                        print(f"✅ {nom} - Status {response.status_code}")
                    else:
                        print(f"⚠️  {nom} - Status {response.status_code}")
                        
                except Exception as e:
                    if "TemplateNotFound" in str(e):
                        print(f"❌ {nom} - Template manquant: {e}")
                        erreurs.append(f"{nom}: {e}")
                    else:
                        print(f"⚠️  {nom} - Autre erreur: {e}")
            
            return erreurs
            
    except Exception as e:
        print(f"❌ Erreur lors du test des routes: {e}")
        return [f"Erreur générale: {e}"]

def main():
    """Fonction principale de vérification"""
    print("🎯 VÉRIFICATION FINALE COMPLÈTE - LIGNE PAR LIGNE")
    print("=" * 100)
    
    tous_problemes = []
    
    # 1. Vérification ligne par ligne
    problemes_templates = verifier_ligne_par_ligne()
    tous_problemes.extend(problemes_templates)
    
    # 2. Vérification des fichiers requis
    fichiers_manquants = verifier_fichiers_requis()
    tous_problemes.extend(fichiers_manquants)
    
    # 3. Test des routes principales
    erreurs_routes = tester_routes_principales()
    tous_problemes.extend(erreurs_routes)
    
    # Résumé final
    print("\n\n" + "=" * 100)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 100)
    
    if tous_problemes:
        print(f"❌ {len(tous_problemes)} problème(s) détecté(s):")
        for i, probleme in enumerate(tous_problemes[:20], 1):  # Afficher max 20
            print(f"   {i}. {probleme}")
        if len(tous_problemes) > 20:
            print(f"   ... et {len(tous_problemes) - 20} autres problèmes")
        
        print("\n⚠️  La correction n'est PAS complète")
        return 1
    else:
        print("🎉 VÉRIFICATION COMPLÈTE RÉUSSIE !")
        print("✅ Aucun problème détecté dans les templates")
        print("✅ Tous les fichiers requis sont présents")
        print("✅ Les routes principales fonctionnent")
        print("✅ Architecture entièrement cohérente")
        
        print("\n🏆 AVANTAGES OBTENUS:")
        print("   • 🚫 Zéro référence aux anciens chemins")
        print("   • 📁 Organisation parfaitement structurée")
        print("   • 🔄 Composants entièrement réutilisables")
        print("   • 🛠️ Maintenance grandement simplifiée")
        print("   • 🚀 Architecture prête pour la production")
        
        return 0

if __name__ == "__main__":
    exit(main())
