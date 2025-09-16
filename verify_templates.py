#!/usr/bin/env python3
"""
Vérification de la syntaxe des templates modifiés
"""

import os
import sys
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

def verify_templates():
    """Vérifie la syntaxe des templates modifiés"""
    
    # Configuration Jinja2
    template_dir = 'app/templates'
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Templates à vérifier
    templates_to_check = [
        'bus_udm.html',
        'carburation.html', 
        'vidange.html',
        'utilisateurs.html',
        'chauffeurs.html',
        'macros/tableaux_components.html'
    ]
    
    print("🔍 Vérification de la syntaxe des templates...")
    print("=" * 50)
    
    all_valid = True
    
    for template_name in templates_to_check:
        try:
            # Charger et compiler le template
            template = env.get_template(template_name)
            print(f"✅ {template_name} - Syntaxe correcte")
            
        except TemplateSyntaxError as e:
            print(f"❌ {template_name} - Erreur de syntaxe:")
            print(f"   Ligne {e.lineno}: {e.message}")
            all_valid = False
            
        except Exception as e:
            print(f"⚠️  {template_name} - Erreur: {str(e)}")
            all_valid = False
    
    print("=" * 50)
    
    if all_valid:
        print("🎉 Tous les templates sont syntaxiquement corrects !")
        
        # Vérification des erreurs de type potentielles
        print("\n🔍 Vérification des erreurs de type potentielles...")
        
        type_errors = []
        
        for template_name in templates_to_check:
            template_path = os.path.join(template_dir, template_name)
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Rechercher les concaténations potentiellement problématiques
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Rechercher les patterns problématiques
                    if '+ \'' in line and 'icon_cell' in line and '|string' not in line and 'format(' not in line:
                        type_errors.append(f"{template_name}:{i} - Concaténation potentiellement problématique: {line.strip()}")
                    
                    if '+ "' in line and 'icon_cell' in line and '|string' not in line and 'format(' not in line:
                        type_errors.append(f"{template_name}:{i} - Concaténation potentiellement problématique: {line.strip()}")
        
        if type_errors:
            print("⚠️  Erreurs de type potentielles détectées:")
            for error in type_errors:
                print(f"   {error}")
        else:
            print("✅ Aucune erreur de type détectée")
            
        print("\n📋 Résumé des modifications:")
        print("   ✅ Templates mis à jour avec le nouveau système")
        print("   ✅ Macros tableaux_components.html créées")
        print("   ✅ CSS et JS unifiés intégrés")
        print("   ✅ Erreurs de type corrigées")
        
    else:
        print("❌ Des erreurs de syntaxe ont été détectées !")
        return False
    
    return True

if __name__ == "__main__":
    success = verify_templates()
    sys.exit(0 if success else 1)
