#!/usr/bin/env python3
"""
Test de syntaxe des templates Jinja2
"""

import os
import re

def test_template_blocks(template_path):
    """Test la cohérence des blocks dans un template"""
    
    print(f"\n📄 Test de {os.path.basename(template_path)}")
    print("-" * 50)
    
    if not os.path.exists(template_path):
        print(f"❌ Fichier non trouvé: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher tous les blocks
    block_starts = re.findall(r'{%\s*block\s+(\w+)\s*%}', content)
    block_ends = re.findall(r'{%\s*endblock\s*(?:\s+(\w+))?\s*%}', content)
    
    print(f"   Blocks ouverts: {block_starts}")
    print(f"   Blocks fermés: {len(block_ends)} endblock trouvés")
    
    # Vérifier l'équilibre
    if len(block_starts) == len(block_ends):
        print("   ✅ Nombre de blocks équilibré")
        return True
    else:
        print(f"   ❌ Déséquilibre: {len(block_starts)} blocks ouverts, {len(block_ends)} fermés")
        
        # Identifier les blocks manquants
        if len(block_starts) > len(block_ends):
            print(f"   🔍 Il manque {len(block_starts) - len(block_ends)} endblock")
        else:
            print(f"   🔍 Il y a {len(block_ends) - len(block_starts)} endblock en trop")
        
        return False

def test_template_structure():
    """Test la structure des templates modifiés"""
    
    print("🔍 TEST DE STRUCTURE DES TEMPLATES")
    print("=" * 60)
    
    templates_to_test = [
        'app/templates/vidange.html',
        'app/templates/carburation.html'
    ]
    
    all_good = True
    
    for template_path in templates_to_test:
        result = test_template_blocks(template_path)
        if not result:
            all_good = False
    
    print(f"\n{'🎉 TOUS LES TEMPLATES SONT CORRECTS' if all_good else '❌ ERREURS DÉTECTÉES'}")
    print("=" * 60)
    
    return all_good

def test_jinja_syntax():
    """Test basique de syntaxe Jinja2"""
    
    print("\n🔧 TEST DE SYNTAXE JINJA2")
    print("-" * 40)
    
    templates = [
        'app/templates/vidange.html',
        'app/templates/carburation.html'
    ]
    
    for template_path in templates:
        if not os.path.exists(template_path):
            print(f"❌ {os.path.basename(template_path)} - Fichier manquant")
            continue
            
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tests basiques
        unclosed_tags = []
        
        # Vérifier les {% ... %}
        jinja_tags = re.findall(r'{%[^%]*%}', content)
        for tag in jinja_tags:
            if not tag.endswith('%}'):
                unclosed_tags.append(tag)
        
        # Vérifier les {{ ... }}
        jinja_vars = re.findall(r'{{[^}]*}}', content)
        for var in jinja_vars:
            if not var.endswith('}}'):
                unclosed_tags.append(var)
        
        if unclosed_tags:
            print(f"❌ {os.path.basename(template_path)} - Tags mal formés: {unclosed_tags[:3]}")
        else:
            print(f"✅ {os.path.basename(template_path)} - Syntaxe de base correcte")

if __name__ == "__main__":
    test_template_structure()
    test_jinja_syntax()
