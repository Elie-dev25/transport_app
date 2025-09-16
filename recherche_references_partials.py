#!/usr/bin/env python3
"""
Recherche TOUTES les références aux fichiers partials/ dans TOUS les templates
"""

import os
import re
from pathlib import Path

def rechercher_references_partials():
    """Recherche toutes les références aux fichiers partials/"""
    print("🔍 RECHERCHE DE TOUTES LES RÉFÉRENCES PARTIALS/")
    print("=" * 80)
    
    templates_dir = Path("app/templates")
    references_trouvees = []
    
    # Lister tous les fichiers dans partials/
    partials_dir = templates_dir / "partials"
    if partials_dir.exists():
        print("📁 Fichiers encore présents dans partials/:")
        for fichier in partials_dir.rglob("*.html"):
            print(f"   • {fichier.relative_to(partials_dir)}")
    
    print("\n🔍 Recherche des références dans tous les templates...")
    
    # Parcourir tous les templates
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                # Chercher toutes les références partials/
                if 'partials/' in line:
                    references_trouvees.append({
                        'fichier': template_file.relative_to(templates_dir),
                        'ligne': line_num,
                        'contenu': line.strip()
                    })
                    
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")
    
    # Afficher les résultats
    if references_trouvees:
        print(f"\n❌ {len(references_trouvees)} référence(s) partials/ trouvée(s):")
        for ref in references_trouvees:
            print(f"\n📄 {ref['fichier']}:{ref['ligne']}")
            print(f"   → {ref['contenu']}")
    else:
        print("\n✅ Aucune référence partials/ trouvée")
    
    return references_trouvees

def rechercher_autres_problemes():
    """Recherche d'autres types de problèmes"""
    print("\n\n🔍 RECHERCHE D'AUTRES PROBLÈMES POTENTIELS")
    print("=" * 80)
    
    templates_dir = Path("app/templates")
    autres_problemes = []
    
    patterns_a_verifier = [
        (r"{% extends ['\"]_base_[^/]*\.html['\"]", "Base template sans roles/"),
        (r"{% from ['\"]macros/[^'\"]*['\"]", "Macro sans shared/"),
        (r"{% include ['\"]admin/[^'\"]*\.html['\"]", "Include admin/ direct"),
        (r"{% include ['\"]charge_transport/[^'\"]*\.html['\"]", "Include charge_transport/ direct"),
        (r"{% include ['\"]chauffeur/[^'\"]*\.html['\"]", "Include chauffeur/ direct"),
        (r"{% include ['\"]superviseur/[^'\"]*\.html['\"]", "Include superviseur/ direct"),
        (r"{% include ['\"]mecanicien/[^'\"]*\.html['\"]", "Include mecanicien/ direct"),
    ]
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern, description in patterns_a_verifier:
                matches = re.finditer(pattern, content)
                for match in matches:
                    # Trouver le numéro de ligne
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()
                    
                    autres_problemes.append({
                        'fichier': template_file.relative_to(templates_dir),
                        'ligne': line_num,
                        'contenu': line_content,
                        'probleme': description
                    })
                    
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")
    
    if autres_problemes:
        print(f"\n❌ {len(autres_problemes)} autre(s) problème(s) trouvé(s):")
        for prob in autres_problemes:
            print(f"\n📄 {prob['fichier']}:{prob['ligne']} - {prob['probleme']}")
            print(f"   → {prob['contenu']}")
    else:
        print("\n✅ Aucun autre problème trouvé")
    
    return autres_problemes

def corriger_problemes_trouves(references_partials, autres_problemes):
    """Corrige automatiquement les problèmes trouvés"""
    if not references_partials and not autres_problemes:
        print("\n✅ Aucun problème à corriger")
        return 0
    
    print("\n\n🔧 CORRECTION AUTOMATIQUE DES PROBLÈMES")
    print("=" * 80)
    
    corrections_appliquees = 0
    
    # Corrections pour les références partials/
    corrections_partials = {
        r"{% include ['\"]partials/admin/([^'\"]*)['\"]": r"{% include 'shared/modals/\1' %}",
        r"{% include ['\"]partials/charge_transport/([^'\"]*)['\"]": r"{% include 'shared/modals/\1' %}",
        r"{% include ['\"]partials/shared/([^'\"]*)['\"]": r"{% include 'shared/modals/\1' %}",
        r"{% from ['\"]partials/admin/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        r"{% from ['\"]partials/charge_transport/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        r"{% from ['\"]partials/shared/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
    }
    
    # Corrections pour les autres problèmes
    corrections_autres = {
        r"{% extends ['\"]_base_admin\.html['\"]": r"{% extends 'roles/admin/_base_admin.html' %}",
        r"{% extends ['\"]_base_charge\.html['\"]": r"{% extends 'roles/charge_transport/_base_charge.html' %}",
        r"{% extends ['\"]_base_chauffeur\.html['\"]": r"{% extends 'roles/chauffeur/_base_chauffeur.html' %}",
        r"{% extends ['\"]_base_superviseur\.html['\"]": r"{% extends 'roles/superviseur/_base_superviseur.html' %}",
        r"{% extends ['\"]_base_mecanicien\.html['\"]": r"{% extends 'roles/mecanicien/_base_mecanicien.html' %}",
        r"{% from ['\"]macros/([^'\"]*)['\"]": r"{% from 'shared/macros/\1'",
        r"{% include ['\"]admin/([^'\"]*\.html)['\"]": r"{% include 'roles/admin/\1' %}",
        r"{% include ['\"]charge_transport/([^'\"]*\.html)['\"]": r"{% include 'roles/charge_transport/\1' %}",
        r"{% include ['\"]chauffeur/([^'\"]*\.html)['\"]": r"{% include 'roles/chauffeur/\1' %}",
        r"{% include ['\"]superviseur/([^'\"]*\.html)['\"]": r"{% include 'roles/superviseur/\1' %}",
        r"{% include ['\"]mecanicien/([^'\"]*\.html)['\"]": r"{% include 'roles/mecanicien/\1' %}",
    }
    
    # Combiner toutes les corrections
    toutes_corrections = {**corrections_partials, **corrections_autres}
    
    # Appliquer les corrections
    templates_dir = Path("app/templates")
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            for pattern, replacement in toutes_corrections.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    corrections_appliquees += 1
                    print(f"✅ Corrigé dans {template_file.relative_to(templates_dir)}")
            
            # Sauvegarder si modifié
            if content != original_content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            print(f"❌ Erreur correction {template_file}: {e}")
    
    print(f"\n✅ {corrections_appliquees} correction(s) appliquée(s)")
    return corrections_appliquees

def main():
    """Fonction principale"""
    print("🎯 RECHERCHE EXHAUSTIVE DE TOUS LES PROBLÈMES DANS LES TEMPLATES")
    print("=" * 100)
    
    # 1. Rechercher les références partials/
    references_partials = rechercher_references_partials()
    
    # 2. Rechercher d'autres problèmes
    autres_problemes = rechercher_autres_problemes()
    
    # 3. Corriger automatiquement
    corrections = corriger_problemes_trouves(references_partials, autres_problemes)
    
    # 4. Vérification finale
    if corrections > 0:
        print("\n\n🔍 VÉRIFICATION APRÈS CORRECTION")
        print("=" * 80)
        
        nouvelles_references = rechercher_references_partials()
        nouveaux_problemes = rechercher_autres_problemes()
        
        if not nouvelles_references and not nouveaux_problemes:
            print("\n🎉 CORRECTION COMPLÈTE RÉUSSIE !")
            print("✅ Tous les problèmes ont été corrigés")
        else:
            print(f"\n⚠️  Il reste encore des problèmes à corriger")
            return 1
    
    # 5. Test de l'application
    try:
        from app import create_app
        app = create_app()
        print("\n✅ Application démarre sans erreur")
        return 0
    except Exception as e:
        print(f"\n❌ Erreur application: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
