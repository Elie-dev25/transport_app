#!/usr/bin/env python3
"""
Vérification EXHAUSTIVE ligne par ligne de TOUS les templates dans TOUS les dossiers
"""

import os
import re
from pathlib import Path

def analyser_template_ligne_par_ligne(template_file):
    """Analyse un template ligne par ligne et retourne les problèmes détectés"""
    problemes = []
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('<!--'):
                continue
                
            # Patterns problématiques à détecter
            patterns_problematiques = [
                # Références partials/
                (r"{% include ['\"]partials/([^'\"]*)['\"]", "include partials/"),
                (r"{% from ['\"]partials/([^'\"]*)['\"]", "from partials/"),
                (r"{% extends ['\"]partials/([^'\"]*)['\"]", "extends partials/"),
                
                # Base templates sans roles/
                (r"{% extends ['\"]_base_admin\.html['\"]", "extends _base_admin.html"),
                (r"{% extends ['\"]_base_charge\.html['\"]", "extends _base_charge.html"),
                (r"{% extends ['\"]_base_chauffeur\.html['\"]", "extends _base_chauffeur.html"),
                (r"{% extends ['\"]_base_superviseur\.html['\"]", "extends _base_superviseur.html"),
                (r"{% extends ['\"]_base_mecanicien\.html['\"]", "extends _base_mecanicien.html"),
                
                # Macros sans shared/
                (r"{% from ['\"]macros/([^'\"]*)['\"]", "from macros/"),
                
                # Includes directs de rôles
                (r"{% include ['\"]admin/([^'\"]*\.html)['\"]", "include admin/"),
                (r"{% include ['\"]charge_transport/([^'\"]*\.html)['\"]", "include charge_transport/"),
                (r"{% include ['\"]chauffeur/([^'\"]*\.html)['\"]", "include chauffeur/"),
                (r"{% include ['\"]superviseur/([^'\"]*\.html)['\"]", "include superviseur/"),
                (r"{% include ['\"]mecanicien/([^'\"]*\.html)['\"]", "include mecanicien/"),
            ]
            
            for pattern, description in patterns_problematiques:
                if re.search(pattern, line):
                    problemes.append({
                        'ligne': line_num,
                        'contenu': line_stripped,
                        'probleme': description,
                        'pattern': pattern
                    })
                    
    except Exception as e:
        problemes.append({
            'ligne': 0,
            'contenu': f"Erreur lecture fichier: {e}",
            'probleme': "erreur_lecture",
            'pattern': ""
        })
    
    return problemes

def parcourir_tous_templates():
    """Parcourt TOUS les templates dans TOUS les dossiers"""
    print("🔍 VÉRIFICATION EXHAUSTIVE - TOUS LES TEMPLATES, TOUS LES DOSSIERS")
    print("=" * 100)
    
    templates_dir = Path("app/templates")
    tous_problemes = {}
    total_files = 0
    files_with_problems = 0
    
    # Parcourir récursivement tous les fichiers .html
    for template_file in templates_dir.rglob("*.html"):
        total_files += 1
        print(f"\n📄 Analyse: {template_file.relative_to(templates_dir)}")
        
        problemes = analyser_template_ligne_par_ligne(template_file)
        
        if problemes:
            files_with_problems += 1
            tous_problemes[template_file] = problemes
            
            print(f"❌ {len(problemes)} problème(s) détecté(s):")
            for probleme in problemes:
                print(f"   Ligne {probleme['ligne']}: {probleme['probleme']}")
                print(f"   → {probleme['contenu']}")
        else:
            print("✅ Aucun problème détecté")
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • {total_files} fichiers analysés")
    print(f"   • {files_with_problems} fichiers avec problèmes")
    print(f"   • {sum(len(p) for p in tous_problemes.values())} problèmes au total")
    
    return tous_problemes

def generer_corrections(tous_problemes):
    """Génère les corrections à appliquer"""
    print("\n\n🔧 CORRECTIONS À APPLIQUER")
    print("=" * 100)
    
    corrections_map = {
        # Partials vers shared/modals
        r"{% include ['\"]partials/admin/([^'\"]*)['\"]": r"{% include 'shared/modals/\1' %}",
        r"{% include ['\"]partials/charge_transport/([^'\"]*)['\"]": r"{% include 'shared/modals/\1' %}",
        r"{% include ['\"]partials/shared/([^'\"]*)['\"]": r"{% include 'shared/modals/\1' %}",
        r"{% from ['\"]partials/admin/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        r"{% from ['\"]partials/charge_transport/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        r"{% from ['\"]partials/shared/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        
        # Base templates vers roles/
        r"{% extends ['\"]_base_admin\.html['\"]": r"{% extends 'roles/admin/_base_admin.html' %}",
        r"{% extends ['\"]_base_charge\.html['\"]": r"{% extends 'roles/charge_transport/_base_charge.html' %}",
        r"{% extends ['\"]_base_chauffeur\.html['\"]": r"{% extends 'roles/chauffeur/_base_chauffeur.html' %}",
        r"{% extends ['\"]_base_superviseur\.html['\"]": r"{% extends 'roles/superviseur/_base_superviseur.html' %}",
        r"{% extends ['\"]_base_mecanicien\.html['\"]": r"{% extends 'roles/mecanicien/_base_mecanicien.html' %}",
        
        # Macros vers shared/
        r"{% from ['\"]macros/([^'\"]*)['\"]": r"{% from 'shared/macros/\1'",
        
        # Includes directs vers roles/
        r"{% include ['\"]admin/([^'\"]*\.html)['\"]": r"{% include 'roles/admin/\1' %}",
        r"{% include ['\"]charge_transport/([^'\"]*\.html)['\"]": r"{% include 'roles/charge_transport/\1' %}",
        r"{% include ['\"]chauffeur/([^'\"]*\.html)['\"]": r"{% include 'roles/chauffeur/\1' %}",
        r"{% include ['\"]superviseur/([^'\"]*\.html)['\"]": r"{% include 'roles/superviseur/\1' %}",
        r"{% include ['\"]mecanicien/([^'\"]*\.html)['\"]": r"{% include 'roles/mecanicien/\1' %}",
    }
    
    corrections_appliquees = 0
    
    for template_file, problemes in tous_problemes.items():
        print(f"\n🔧 Correction: {template_file.relative_to(Path('app/templates'))}")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Appliquer toutes les corrections
            for pattern, replacement in corrections_map.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    corrections_appliquees += 1
                    print(f"   ✅ Appliqué: {pattern[:50]}...")
            
            # Sauvegarder si modifié
            if content != original_content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   💾 Fichier sauvegardé")
            
        except Exception as e:
            print(f"   ❌ Erreur correction {template_file}: {e}")
    
    print(f"\n✅ {corrections_appliquees} corrections appliquées")
    return corrections_appliquees

def main():
    """Fonction principale"""
    print("🎯 VÉRIFICATION EXHAUSTIVE DE TOUS LES TEMPLATES")
    print("=" * 120)
    
    # 1. Parcourir tous les templates
    tous_problemes = parcourir_tous_templates()
    
    if not tous_problemes:
        print("\n🎉 PARFAIT ! Aucun problème détecté dans aucun template")
        print("✅ Tous les templates utilisent les chemins corrects")
        return 0
    
    # 2. Générer et appliquer les corrections
    corrections = generer_corrections(tous_problemes)
    
    # 3. Vérification après correction
    print("\n\n🔍 VÉRIFICATION APRÈS CORRECTION")
    print("=" * 100)
    
    nouveaux_problemes = parcourir_tous_templates()
    
    if not nouveaux_problemes:
        print("\n🎉 CORRECTION COMPLÈTE RÉUSSIE !")
        print("✅ Tous les problèmes ont été corrigés")
        print("✅ Tous les templates utilisent maintenant les chemins corrects")
        
        # Test de l'application
        try:
            from app import create_app
            app = create_app()
            print("✅ Application démarre sans erreur")
        except Exception as e:
            print(f"⚠️  Erreur application: {e}")
        
        return 0
    else:
        print(f"\n⚠️  {len(nouveaux_problemes)} fichier(s) ont encore des problèmes")
        return 1

if __name__ == "__main__":
    exit(main())
