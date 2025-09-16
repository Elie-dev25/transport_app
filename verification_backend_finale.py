#!/usr/bin/env python3
"""
Vérification finale que tout le backend utilise les nouveaux chemins de templates
"""

import os
import re
from pathlib import Path

def verifier_routes_templates():
    """Vérifie que toutes les routes utilisent les nouveaux chemins de templates"""
    print("🔍 VÉRIFICATION DES ROUTES - CHEMINS DE TEMPLATES")
    print("=" * 60)
    
    routes_dir = Path("app/routes")
    problemes = []
    
    # Patterns d'anciens chemins à détecter
    anciens_patterns = [
        r"render_template\(['\"]dashboard_admin\.html['\"]",
        r"render_template\(['\"]dashboard_charge\.html['\"]", 
        r"render_template\(['\"]dashboard_chauffeur\.html['\"]",
        r"render_template\(['\"]dashboard_mecanicien\.html['\"]",
        r"render_template\(['\"]carburation\.html['\"]",
        r"render_template\(['\"]vidange\.html['\"]",
        r"render_template\(['\"]parametres\.html['\"]",
        r"render_template\(['\"]rapports\.html['\"]",
        r"render_template\(['\"]bus_udm\.html['\"]",
        r"render_template\(['\"]chauffeurs\.html['\"]",
        r"render_template\(['\"]utilisateurs\.html['\"]",
        r"render_template\(['\"]superviseur/[^'\"]*\.html['\"]",  # superviseur/ sans roles/
    ]
    
    # Nouveaux patterns corrects
    nouveaux_patterns = [
        r"render_template\(['\"]roles/admin/dashboard_admin\.html['\"]",
        r"render_template\(['\"]roles/charge_transport/dashboard_charge\.html['\"]",
        r"render_template\(['\"]roles/chauffeur/dashboard_chauffeur\.html['\"]",
        r"render_template\(['\"]roles/mecanicien/dashboard_mecanicien\.html['\"]",
        r"render_template\(['\"]pages/carburation\.html['\"]",
        r"render_template\(['\"]pages/vidange\.html['\"]",
        r"render_template\(['\"]pages/parametres\.html['\"]",
        r"render_template\(['\"]pages/rapports\.html['\"]",
        r"render_template\(['\"]pages/bus_udm\.html['\"]",
        r"render_template\(['\"]legacy/chauffeurs\.html['\"]",
        r"render_template\(['\"]roles/superviseur/[^'\"]*\.html['\"]",
    ]
    
    for route_file in routes_dir.rglob("*.py"):
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Chercher tous les render_template
            render_templates = re.findall(r"render_template\(['\"][^'\"]*\.html['\"]", content)
            
            if render_templates:
                print(f"\n📁 {route_file.relative_to(routes_dir)}:")
                
                for template_call in render_templates:
                    # Extraire le chemin du template
                    template_path = re.search(r"['\"]([^'\"]*\.html)['\"]", template_call).group(1)
                    
                    # Vérifier si c'est un ancien pattern
                    is_old_pattern = any(re.search(pattern, template_call) for pattern in anciens_patterns)
                    
                    if is_old_pattern:
                        print(f"   ❌ {template_path} - ANCIEN CHEMIN")
                        problemes.append(f"{route_file}: {template_path}")
                    else:
                        print(f"   ✅ {template_path} - OK")
                        
        except Exception as e:
            print(f"⚠️  Erreur lecture {route_file}: {e}")
    
    return problemes

def verifier_templates_extends():
    """Vérifie que tous les templates utilisent les bons extends"""
    print("\n\n🎨 VÉRIFICATION DES TEMPLATES - EXTENDS")
    print("=" * 60)
    
    templates_dir = Path("app/templates")
    problemes = []
    
    # Patterns d'anciens extends
    anciens_extends = [
        r'{% extends "_base_admin\.html" %}',
        r'{% extends "_base_chauffeur\.html" %}',
        r'{% extends "_base_superviseur\.html" %}',
        r'{% extends "_base_mecanicien\.html" %}',
        r'{% extends "_base_charge\.html" %}'
    ]
    
    for template_file in templates_dir.rglob("*.html"):
        if template_file.name.startswith('_base_'):
            continue  # Skip base templates
            
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Chercher les extends
            extends_matches = re.findall(r'{% extends [^%]*%}', content)
            
            if extends_matches:
                for extend in extends_matches:
                    is_old_extend = any(re.search(pattern, extend) for pattern in anciens_extends)
                    
                    if is_old_extend:
                        print(f"❌ {template_file.relative_to(templates_dir)}: {extend}")
                        problemes.append(f"{template_file}: {extend}")
                        
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")
    
    if not problemes:
        print("✅ Tous les templates utilisent les nouveaux extends")
    
    return problemes

def verifier_imports_macros():
    """Vérifie que tous les templates utilisent les bons imports de macros"""
    print("\n\n🔧 VÉRIFICATION DES TEMPLATES - IMPORTS MACROS")
    print("=" * 60)
    
    templates_dir = Path("app/templates")
    problemes = []
    
    # Patterns d'anciens imports
    anciens_imports = [
        r"from 'macros/tableaux_components\.html'",
        r"from 'macros/superviseur_components\.html'",
        r"from 'macros/trajet_modals\.html'"
    ]
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Chercher les imports from
            import_matches = re.findall(r"{% from '[^']*' import [^%]*%}", content)
            
            if import_matches:
                for import_line in import_matches:
                    is_old_import = any(re.search(pattern, import_line) for pattern in anciens_imports)
                    
                    if is_old_import:
                        print(f"❌ {template_file.relative_to(templates_dir)}: {import_line}")
                        problemes.append(f"{template_file}: {import_line}")
                        
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")
    
    if not problemes:
        print("✅ Tous les templates utilisent les nouveaux imports de macros")
    
    return problemes

def verifier_structure_fichiers():
    """Vérifie que la structure de fichiers est correcte"""
    print("\n\n📁 VÉRIFICATION DE LA STRUCTURE DE FICHIERS")
    print("=" * 60)
    
    dossiers_requis = [
        "app/templates/shared/modals",
        "app/templates/shared/macros", 
        "app/templates/pages",
        "app/templates/roles/admin",
        "app/templates/roles/superviseur",
        "app/templates/roles/charge_transport",
        "app/templates/roles/chauffeur",
        "app/templates/roles/mecanicien",
        "app/templates/auth",
        "app/templates/legacy"
    ]
    
    fichiers_requis = [
        "app/templates/shared/modals/trajet_interne_modal.html",
        "app/templates/shared/modals/trajet_prestataire_modal.html",
        "app/templates/shared/modals/autres_trajets_modal.html",
        "app/templates/shared/macros/trajet_modals.html",
        "app/templates/shared/macros/tableaux_components.html",
        "app/templates/roles/admin/_base_admin.html",
        "app/templates/roles/admin/dashboard_admin.html",
        "app/templates/roles/charge_transport/_base_charge.html",
        "app/templates/roles/charge_transport/dashboard_charge.html",
        "app/templates/roles/chauffeur/_base_chauffeur.html",
        "app/templates/roles/chauffeur/dashboard_chauffeur.html",
        "app/templates/roles/superviseur/_base_superviseur.html",
        "app/templates/roles/superviseur/dashboard.html",
        "app/templates/roles/mecanicien/_base_mecanicien.html",
        "app/templates/pages/carburation.html",
        "app/templates/pages/vidange.html",
        "app/templates/pages/parametres.html",
        "app/templates/pages/rapports.html"
    ]
    
    problemes = []
    
    # Vérifier les dossiers
    for dossier in dossiers_requis:
        if os.path.exists(dossier):
            print(f"✅ {dossier}")
        else:
            print(f"❌ {dossier} - MANQUANT")
            problemes.append(f"Dossier manquant: {dossier}")
    
    # Vérifier les fichiers
    for fichier in fichiers_requis:
        if os.path.exists(fichier):
            print(f"✅ {fichier}")
        else:
            print(f"❌ {fichier} - MANQUANT")
            problemes.append(f"Fichier manquant: {fichier}")
    
    return problemes

def main():
    """Fonction principale de vérification"""
    print("🚀 VÉRIFICATION FINALE DU BACKEND")
    print("=" * 60)
    
    tous_problemes = []
    
    # 1. Vérifier les routes
    problemes_routes = verifier_routes_templates()
    tous_problemes.extend(problemes_routes)
    
    # 2. Vérifier les extends des templates
    problemes_extends = verifier_templates_extends()
    tous_problemes.extend(problemes_extends)
    
    # 3. Vérifier les imports de macros
    problemes_imports = verifier_imports_macros()
    tous_problemes.extend(problemes_imports)
    
    # 4. Vérifier la structure de fichiers
    problemes_structure = verifier_structure_fichiers()
    tous_problemes.extend(problemes_structure)
    
    # Résumé final
    print("\n\n" + "=" * 60)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if tous_problemes:
        print(f"❌ {len(tous_problemes)} problème(s) détecté(s):")
        for probleme in tous_problemes:
            print(f"   • {probleme}")
        print("\n⚠️  Le backend n'est PAS entièrement à jour")
        return 1
    else:
        print("🎉 AUCUN PROBLÈME DÉTECTÉ !")
        print("✅ Le backend est entièrement à jour avec la nouvelle architecture")
        print("✅ Tous les chemins de templates sont corrects")
        print("✅ Tous les extends utilisent les nouveaux chemins")
        print("✅ Tous les imports de macros sont corrects")
        print("✅ La structure de fichiers est complète")
        return 0

if __name__ == "__main__":
    exit(main())
