#!/usr/bin/env python3
"""
Test final de la nouvelle architecture de templates
Vérifie que tous les templates utilisent les bons chemins
"""

import os
import sys
import re
from pathlib import Path

def test_template_extends():
    """Teste que tous les templates utilisent les bons chemins extends"""
    print("🔍 Test des extends dans les templates...")
    
    # Patterns à vérifier
    old_patterns = [
        r'{% extends "_base_admin\.html" %}',
        r'{% extends "_base_chauffeur\.html" %}',
        r'{% extends "_base_superviseur\.html" %}',
        r'{% extends "_base_mecanicien\.html" %}',
        r'{% extends "_base_charge\.html" %}'
    ]
    
    new_patterns = [
        r'{% extends "roles/admin/_base_admin\.html" %}',
        r'{% extends "roles/chauffeur/_base_chauffeur\.html" %}',
        r'{% extends "roles/superviseur/_base_superviseur\.html" %}',
        r'{% extends "roles/mecanicien/_base_mecanicien\.html" %}',
        r'{% extends "roles/charge_transport/_base_charge\.html" %}'
    ]
    
    templates_dir = Path("app/templates")
    issues = []
    
    for template_file in templates_dir.rglob("*.html"):
        if template_file.name.startswith('_base_'):
            continue  # Skip base templates
            
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérifier les anciens patterns
            for pattern in old_patterns:
                if re.search(pattern, content):
                    issues.append(f"❌ {template_file.relative_to(templates_dir)} utilise encore un ancien extend")
                    
        except Exception as e:
            issues.append(f"⚠️  Erreur lecture {template_file}: {e}")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("✅ Tous les templates utilisent les nouveaux chemins extends")
        return True

def test_macro_imports():
    """Teste que tous les templates utilisent les bons imports de macros"""
    print("\n🔍 Test des imports de macros...")
    
    old_macro_patterns = [
        r"from 'macros/tableaux_components\.html'",
        r"from 'macros/superviseur_components\.html'"
    ]
    
    templates_dir = Path("app/templates")
    issues = []
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérifier les anciens patterns de macros
            for pattern in old_macro_patterns:
                if re.search(pattern, content):
                    issues.append(f"❌ {template_file.relative_to(templates_dir)} utilise encore un ancien import de macro")
                    
        except Exception as e:
            issues.append(f"⚠️  Erreur lecture {template_file}: {e}")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("✅ Tous les templates utilisent les nouveaux imports de macros")
        return True

def test_routes_templates():
    """Teste que les routes utilisent les bons chemins de templates"""
    print("\n🔍 Test des routes...")
    
    routes_dir = Path("app/routes")
    issues = []
    
    # Patterns de templates à vérifier dans les routes
    old_template_patterns = [
        r"render_template\(['\"]dashboard_admin\.html['\"]",
        r"render_template\(['\"]dashboard_charge\.html['\"]",
        r"render_template\(['\"]dashboard_chauffeur\.html['\"]",
        r"render_template\(['\"]dashboard_mecanicien\.html['\"]",
        r"render_template\(['\"]carburation\.html['\"]",
        r"render_template\(['\"]vidange\.html['\"]",
        r"render_template\(['\"]parametres\.html['\"]",
        r"render_template\(['\"]rapports\.html['\"]"
    ]
    
    for route_file in routes_dir.rglob("*.py"):
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérifier les anciens patterns
            for pattern in old_template_patterns:
                if re.search(pattern, content):
                    issues.append(f"❌ {route_file.relative_to(routes_dir)} utilise encore un ancien chemin de template")
                    
        except Exception as e:
            issues.append(f"⚠️  Erreur lecture {route_file}: {e}")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("✅ Toutes les routes utilisent les nouveaux chemins de templates")
        return True

def test_file_structure():
    """Teste que la structure de fichiers est correcte"""
    print("\n🔍 Test de la structure de fichiers...")
    
    required_dirs = [
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
    
    required_files = [
        "app/templates/shared/modals/trajet_interne_modal.html",
        "app/templates/shared/modals/trajet_prestataire_modal.html",
        "app/templates/shared/modals/autres_trajets_modal.html",
        "app/templates/shared/macros/trajet_modals.html",
        "app/templates/shared/macros/tableaux_components.html",
        "app/templates/roles/admin/_base_admin.html",
        "app/templates/roles/admin/dashboard_admin.html",
        "app/templates/roles/charge_transport/_base_charge.html",
        "app/templates/roles/charge_transport/dashboard_charge.html"
    ]
    
    issues = []
    
    # Vérifier les dossiers
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            issues.append(f"❌ Dossier manquant: {dir_path}")
    
    # Vérifier les fichiers
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"❌ Fichier manquant: {file_path}")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("✅ Structure de fichiers correcte")
        return True

def main():
    """Fonction principale de test"""
    print("🚀 Test de la nouvelle architecture de templates")
    print("=" * 60)
    
    tests = [
        ("Structure de fichiers", test_file_structure),
        ("Extends des templates", test_template_extends),
        ("Imports de macros", test_macro_imports),
        ("Routes et templates", test_routes_templates)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'architecture est correctement configurée.")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
