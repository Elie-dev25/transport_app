#!/usr/bin/env python3
"""
Script pour parcourir TOUS les templates et corriger TOUTES les références aux anciens chemins
"""

import os
import re
from pathlib import Path

def analyser_tous_templates():
    """Analyse tous les templates pour trouver les références aux anciens chemins"""
    print("🔍 ANALYSE COMPLÈTE DE TOUS LES TEMPLATES")
    print("=" * 80)
    
    templates_dir = Path("app/templates")
    problemes = []
    
    # Patterns à détecter et corriger
    patterns_corrections = {
        # Références partials/
        r"{% include ['\"]partials/admin/([^'\"]*)['\"]": r"{% include 'shared/modals/\1'",
        r"{% include ['\"]partials/charge_transport/([^'\"]*)['\"]": r"{% include 'shared/modals/\1'",
        r"{% include ['\"]partials/shared/([^'\"]*)['\"]": r"{% include 'shared/modals/\1'",
        r"{% from ['\"]partials/admin/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        r"{% from ['\"]partials/charge_transport/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        r"{% from ['\"]partials/shared/([^'\"]*)['\"]": r"{% from 'shared/modals/\1'",
        
        # Références extends incorrectes
        r"{% extends ['\"]_base_admin\.html['\"]": r"{% extends 'roles/admin/_base_admin.html'",
        r"{% extends ['\"]_base_charge\.html['\"]": r"{% extends 'roles/charge_transport/_base_charge.html'",
        r"{% extends ['\"]_base_chauffeur\.html['\"]": r"{% extends 'roles/chauffeur/_base_chauffeur.html'",
        r"{% extends ['\"]_base_superviseur\.html['\"]": r"{% extends 'roles/superviseur/_base_superviseur.html'",
        r"{% extends ['\"]_base_mecanicien\.html['\"]": r"{% extends 'roles/mecanicien/_base_mecanicien.html'",
        
        # Références macros incorrectes
        r"{% from ['\"]macros/([^'\"]*)['\"]": r"{% from 'shared/macros/\1'",
    }
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                original_content = content
                
            # Appliquer toutes les corrections
            corrections_appliquees = []
            
            for pattern, replacement in patterns_corrections.items():
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    corrections_appliquees.extend(matches)
            
            # Si des corrections ont été appliquées, sauvegarder
            if corrections_appliquees:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ {template_file.relative_to(templates_dir)}")
                for correction in corrections_appliquees:
                    if isinstance(correction, tuple):
                        print(f"   🔄 {correction[0] if correction else 'pattern'}")
                    else:
                        print(f"   🔄 {correction}")
                        
                problemes.append(f"Corrigé: {template_file.relative_to(templates_dir)}")
            
        except Exception as e:
            print(f"⚠️  Erreur avec {template_file}: {e}")
    
    return problemes

def verifier_references_restantes():
    """Vérifie s'il reste des références aux anciens chemins"""
    print("\n\n🔍 VÉRIFICATION DES RÉFÉRENCES RESTANTES")
    print("=" * 80)
    
    templates_dir = Path("app/templates")
    problemes_restants = []
    
    # Patterns problématiques à détecter
    patterns_problematiques = [
        r"{% include ['\"]partials/",
        r"{% from ['\"]partials/",
        r"{% extends ['\"]partials/",
        r"{% extends ['\"]_base_[^/]*\.html['\"]",  # _base_xxx.html sans roles/
        r"{% from ['\"]macros/[^'\"]*['\"]",  # macros/ sans shared/
    ]
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Chercher les patterns problématiques
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern in patterns_problematiques:
                    if re.search(pattern, line):
                        print(f"❌ {template_file.relative_to(templates_dir)}:{line_num}")
                        print(f"   {line.strip()}")
                        problemes_restants.append(f"{template_file}:{line_num}")
                        
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")
    
    if not problemes_restants:
        print("✅ Aucune référence problématique trouvée")
        print("✅ Tous les templates utilisent les nouveaux chemins")
    
    return problemes_restants

def test_application():
    """Teste que l'application démarre sans erreur"""
    print("\n\n🚀 TEST DE L'APPLICATION")
    print("=" * 80)
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Application créée avec succès")
        
        with app.app_context():
            print("✅ Contexte application fonctionnel")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de l'application: {e}")
        return False

def main():
    """Fonction principale"""
    print("🎯 CORRECTION COMPLÈTE DE TOUS LES TEMPLATES")
    print("=" * 100)
    
    # 1. Analyser et corriger tous les templates
    corrections = analyser_tous_templates()
    
    # 2. Vérifier qu'il ne reste plus de références problématiques
    problemes_restants = verifier_references_restantes()
    
    # 3. Tester l'application
    app_ok = test_application()
    
    # Résumé final
    print("\n\n" + "=" * 100)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 100)
    
    if corrections:
        print(f"✅ {len(corrections)} fichier(s) corrigé(s)")
        
    if problemes_restants:
        print(f"❌ {len(problemes_restants)} problème(s) restant(s)")
        for probleme in problemes_restants[:10]:  # Afficher max 10
            print(f"   • {probleme}")
        if len(problemes_restants) > 10:
            print(f"   • ... et {len(problemes_restants) - 10} autres")
        return 1
    
    if not app_ok:
        print("❌ L'application ne démarre pas correctement")
        return 1
    
    print("🎉 CORRECTION COMPLÈTE RÉUSSIE !")
    print("✅ Tous les templates utilisent les nouveaux chemins")
    print("✅ Aucune référence aux anciens chemins")
    print("✅ L'application démarre sans erreur")
    print("✅ Architecture entièrement cohérente")
    
    return 0

if __name__ == "__main__":
    exit(main())
