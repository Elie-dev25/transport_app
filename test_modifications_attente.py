#!/usr/bin/env python3
"""
Script de test pour vérifier les modifications "NON SPÉCIFIÉ" → "ATTENTE"
et suppression de l'icône pour "Conjointement"
"""

import re
from pathlib import Path

def test_non_specifie_vers_attente():
    """Teste que 'NON SPÉCIFIÉ' est changé en 'ATTENTE'"""
    print("🔄 TEST NON SPÉCIFIÉ → ATTENTE")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Badge "Attente" au lieu de "Non spécifié"
    has_attente_badge = "status_badge('Attente'" in content
    print(f"   {'✅' if has_attente_badge else '❌'} Badge 'Attente' au lieu de 'Non spécifié'")
    
    # Test 2: Texte "Attente" dans les cellules vides
    has_attente_text = 'text-muted">Attente</span>' in content
    print(f"   {'✅' if has_attente_text else '❌'} Texte 'Attente' dans les cellules vides")
    
    # Test 3: JavaScript mis à jour
    has_js_attente = 'question-circle"></i> Attente' in content
    print(f"   {'✅' if has_js_attente else '❌'} JavaScript mis à jour pour 'Attente'")
    
    # Test 4: Plus de référence à "Non spécifié"
    non_specifie_count = content.count('Non spécifié')
    has_no_non_specifie = non_specifie_count == 0
    print(f"   {'✅' if has_no_non_specifie else '❌'} Plus de référence à 'Non spécifié' ({non_specifie_count} trouvées)")
    
    success = has_attente_badge and has_attente_text and has_js_attente and has_no_non_specifie
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_conjointement_sans_icone():
    """Teste que 'Conjointement' n'a plus d'icône"""
    print("\n🚫 TEST CONJOINTEMENT SANS ICÔNE")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Plus d'icon_cell pour Conjointement
    has_no_icon_cell = "icon_cell('arrows-alt-h', 'Conjointement')" not in content
    print(f"   {'✅' if has_no_icon_cell else '❌'} Plus d'icon_cell pour Conjointement")
    
    # Test 2: Texte simple pour Conjointement
    has_simple_text = '<span>Conjointement</span>' in content
    print(f"   {'✅' if has_simple_text else '❌'} Texte simple pour Conjointement")
    
    # Test 3: Plus de référence à arrows-alt-h
    has_no_arrows_icon = 'arrows-alt-h' not in content
    print(f"   {'✅' if has_no_arrows_icon else '❌'} Plus de référence à l'icône arrows-alt-h")
    
    success = has_no_icon_cell and has_simple_text and has_no_arrows_icon
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_javascript_main_js_mis_a_jour():
    """Teste que le JavaScript main.js est mis à jour"""
    print("\n📜 TEST JAVASCRIPT MAIN.JS MIS À JOUR")
    print("=" * 50)
    
    main_js_file = Path("app/static/js/main.js")
    
    if not main_js_file.exists():
        print("❌ Fichier main.js non trouvé")
        return False
        
    with open(main_js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: "Attente" au lieu de "Non spécifié"
    has_attente_js = 'Attente</span>' in content
    print(f"   {'✅' if has_attente_js else '❌'} "Attente" au lieu de "Non spécifié" dans JS")
    
    # Test 2: Conjointement sans icône dans generateLieuHTML
    has_conjointement_no_icon = "return 'Conjointement';" in content
    print(f"   {'✅' if has_conjointement_no_icon else '❌'} Conjointement sans icône dans generateLieuHTML")
    
    # Test 3: Plus de référence à arrows-alt-h
    has_no_arrows_js = 'arrows-alt-h' not in content
    print(f"   {'✅' if has_no_arrows_js else '❌'} Plus de référence à arrows-alt-h dans JS")
    
    # Test 4: Plus de "Non spécifié" dans JS
    non_specifie_js_count = content.count('Non spécifié')
    has_no_non_specifie_js = non_specifie_js_count == 0
    print(f"   {'✅' if has_no_non_specifie_js else '❌'} Plus de "Non spécifié" dans JS ({non_specifie_js_count} trouvées)")
    
    success = has_attente_js and has_conjointement_no_icon and has_no_arrows_js and has_no_non_specifie_js
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_coherence_globale():
    """Teste la cohérence globale des modifications"""
    print("\n🎯 TEST COHÉRENCE GLOBALE")
    print("=" * 50)
    
    files_to_check = [
        ("app/templates/legacy/chauffeurs.html", "Template chauffeurs"),
        ("app/static/js/main.js", "JavaScript main.js")
    ]
    
    success_count = 0
    total_files = len(files_to_check)
    
    for file_path, file_name in files_to_check:
        file_obj = Path(file_path)
        if file_obj.exists():
            with open(file_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier cohérence
            has_attente = 'Attente' in content
            has_no_non_specifie = 'Non spécifié' not in content
            has_conjointement_simple = 'Conjointement' in content and 'arrows-alt-h' not in content
            
            file_coherent = has_attente and has_no_non_specifie and has_conjointement_simple
            print(f"   {'✅' if file_coherent else '❌'} {file_name} cohérent")
            
            if file_coherent:
                success_count += 1
        else:
            print(f"   ❌ {file_name} non trouvé")
    
    success = success_count == total_files
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'} ({success_count}/{total_files} fichiers cohérents)")
    return success

def main():
    """Fonction principale"""
    print("🧪 TEST DES MODIFICATIONS ATTENTE ET CONJOINTEMENT")
    print("=" * 70)
    print("Objectif: Vérifier 'NON SPÉCIFIÉ' → 'ATTENTE' et suppression icône Conjointement")
    
    # Tests
    test1 = test_non_specifie_vers_attente()
    test2 = test_conjointement_sans_icone()
    test3 = test_javascript_main_js_mis_a_jour()
    test4 = test_coherence_globale()
    
    # Résultat final
    print("\n" + "=" * 70)
    print("🏁 RÉSULTAT FINAL")
    print("=" * 70)
    
    total_tests = 4
    tests_reussis = sum([test1, test2, test3, test4])
    
    print(f"Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 TOUTES LES MODIFICATIONS APPLIQUÉES AVEC SUCCÈS !")
        print("\n✅ Modifications réalisées:")
        print("   • 'NON SPÉCIFIÉ' changé en 'ATTENTE' partout")
        print("   • Icône supprimée pour 'Conjointement'")
        print("   • JavaScript main.js mis à jour")
        print("   • Cohérence maintenue dans tous les fichiers")
    else:
        print("⚠️  CERTAINES MODIFICATIONS MANQUENT")
        if not test1:
            print("   ❌ 'NON SPÉCIFIÉ' → 'ATTENTE' non complété")
        if not test2:
            print("   ❌ Icône Conjointement non supprimée")
        if not test3:
            print("   ❌ JavaScript main.js non mis à jour")
        if not test4:
            print("   ❌ Incohérences détectées")
    
    print("\n🎯 RÉSULTAT ATTENDU:")
    print("   ✅ Chauffeurs sans affectation affichent 'ATTENTE'")
    print("   ✅ 'Conjointement' affiché sans icône")
    print("   ✅ Cohérence dans toute l'application")

if __name__ == "__main__":
    main()
