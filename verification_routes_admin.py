#!/usr/bin/env python3
"""
Vérification et correction des routes admin qui utilisent encore des anciens chemins
"""

import os
import re
from pathlib import Path

def verifier_routes_admin():
    """Vérifie tous les render_template dans les routes admin"""
    print("🔍 VÉRIFICATION DES ROUTES ADMIN")
    print("=" * 60)
    
    admin_dir = Path("app/routes/admin")
    problemes = []
    
    # Patterns d'anciens chemins à détecter
    anciens_patterns = [
        r"render_template\(['\"]admin/[^'\"]*\.html['\"]",  # admin/...html
        r"render_template\(['\"]dashboard_admin\.html['\"]",
        r"render_template\(['\"]bus_udm\.html['\"]",
        r"render_template\(['\"]carburation\.html['\"]",
        r"render_template\(['\"]vidange\.html['\"]",
        r"render_template\(['\"]parametres\.html['\"]",
        r"render_template\(['\"]rapports\.html['\"]",
        r"render_template\(['\"]chauffeurs\.html['\"]",
        r"render_template\(['\"]utilisateurs\.html['\"]"
    ]
    
    for route_file in admin_dir.rglob("*.py"):
        if route_file.name == "__init__.py":
            continue
            
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Chercher tous les render_template
            render_templates = re.findall(r"render_template\(['\"][^'\"]*\.html['\"][^)]*\)", content)
            
            if render_templates:
                print(f"\n📁 {route_file.name}:")
                
                for template_call in render_templates:
                    # Extraire le chemin du template
                    template_match = re.search(r"['\"]([^'\"]*\.html)['\"]", template_call)
                    if template_match:
                        template_path = template_match.group(1)
                        
                        # Vérifier si c'est un ancien pattern
                        is_old_pattern = any(re.search(pattern, template_call) for pattern in anciens_patterns)
                        
                        if is_old_pattern:
                            print(f"   ❌ {template_path} - ANCIEN CHEMIN")
                            problemes.append(f"{route_file.name}: {template_path}")
                        else:
                            print(f"   ✅ {template_path} - OK")
                        
        except Exception as e:
            print(f"⚠️  Erreur lecture {route_file}: {e}")
    
    return problemes

def suggerer_corrections():
    """Suggère les corrections à appliquer"""
    print("\n\n💡 CORRECTIONS SUGGÉRÉES")
    print("=" * 60)
    
    corrections = {
        "admin/bus_udm.html": "roles/admin/bus_udm.html",
        "admin/dashboard_admin.html": "roles/admin/dashboard_admin.html", 
        "admin/consultation.html": "roles/admin/consultation.html",
        "admin/audit.html": "roles/admin/audit.html",
        "dashboard_admin.html": "roles/admin/dashboard_admin.html",
        "bus_udm.html": "roles/admin/bus_udm.html",
        "carburation.html": "pages/carburation.html",
        "vidange.html": "pages/vidange.html",
        "parametres.html": "pages/parametres.html",
        "rapports.html": "pages/rapports.html",
        "chauffeurs.html": "legacy/chauffeurs.html",
        "utilisateurs.html": "pages/utilisateurs.html"
    }
    
    for ancien, nouveau in corrections.items():
        print(f"'{ancien}' → '{nouveau}'")

def main():
    """Fonction principale"""
    print("🎯 VÉRIFICATION DES ROUTES ADMIN")
    print("=" * 80)
    
    problemes = verifier_routes_admin()
    
    if problemes:
        print(f"\n❌ {len(problemes)} problème(s) détecté(s):")
        for probleme in problemes:
            print(f"   • {probleme}")
        
        suggerer_corrections()
        
        print("\n⚠️  Des routes admin utilisent encore des anciens chemins")
        return 1
    else:
        print("\n✅ Toutes les routes admin utilisent les nouveaux chemins")
        return 0

if __name__ == "__main__":
    exit(main())
