#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections des problèmes identifiés
1. Bouton dépannage admin
2. Icône ajouter document plus expressive  
3. Statuts documents mécanicien
"""

import sys
import os
import re
from pathlib import Path

def test_bouton_depannage_admin():
    """Teste que le bouton dépannage admin utilise la modal partagée"""
    print("🔧 TEST BOUTON DÉPANNAGE ADMIN")
    print("=" * 50)
    
    template_file = Path("app/templates/roles/admin/bus_udm.html")
    
    if not template_file.exists():
        print("❌ Template admin bus_udm.html non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier que la modal partagée est incluse
    has_shared_modal = 'shared/modals/_declaration_panne_modal.html' in content
    print(f"   {'✅' if has_shared_modal else '❌'} Modal partagée incluse")
    
    # Vérifier qu'il n'y a plus de modal inline
    has_inline_modal = 'id="panneModal"' in content and '<div id="panneModal"' in content
    print(f"   {'❌' if has_inline_modal else '✅'} Plus de modal inline")
    
    # Vérifier la fonction openPanneModal
    has_open_function = 'window.openPanneModal' in content
    print(f"   {'✅' if has_open_function else '❌'} Fonction openPanneModal présente")
    
    # Vérifier le bouton dans le tableau
    has_button = 'onclick="openPanneModal(' in content
    print(f"   {'✅' if has_button else '❌'} Bouton dans tableau présent")
    
    success = has_shared_modal and not has_inline_modal and has_open_function and has_button
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_icone_document_expressive():
    """Teste que l'icône ajouter document est plus expressive"""
    print("\n🎨 TEST ICÔNE DOCUMENT EXPRESSIVE")
    print("=" * 50)
    
    templates_to_check = [
        "app/templates/roles/admin/bus_udm.html",
        "app/templates/pages/bus_udm.html"
    ]
    
    success = True
    
    for template_path in templates_to_check:
        template_file = Path(template_path)
        print(f"\n📄 {template_file.name}")
        
        if not template_file.exists():
            print("   ❌ Template non trouvé")
            success = False
            continue
            
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier l'icône file-plus
        has_file_plus = 'fa-file-plus' in content
        print(f"   {'✅' if has_file_plus else '❌'} Icône fa-file-plus utilisée")
        
        # Vérifier le titre explicite
        has_explicit_title = 'Ajouter un document administratif' in content
        print(f"   {'✅' if has_explicit_title else '❌'} Titre explicite présent")
        
        # Vérifier qu'il n'y a plus de fa-plus générique pour les documents
        doc_button_pattern = r'onclick="openDocModal\([^)]*\)"[^>]*>\s*<i class="fas fa-plus"'
        has_generic_plus = re.search(doc_button_pattern, content)
        print(f"   {'❌' if has_generic_plus else '✅'} Plus d\'icône + générique")
        
        if not (has_file_plus and has_explicit_title and not has_generic_plus):
            success = False
    
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_statuts_documents_mecanicien():
    """Teste que les statuts documents sont calculés pour mécanicien"""
    print("\n📋 TEST STATUTS DOCUMENTS MÉCANICIEN")
    print("=" * 50)
    
    routes_to_check = [
        ("app/routes/mecanicien.py", "mécanicien"),
        ("app/routes/charge_transport.py", "chargé de transport")
    ]
    
    success = True
    
    for route_path, role_name in routes_to_check:
        route_file = Path(route_path)
        print(f"\n📄 Route {role_name}")
        
        if not route_file.exists():
            print("   ❌ Route non trouvée")
            success = False
            continue
            
        with open(route_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier le calcul des statuts
        has_status_calc = 'status = \'ROUGE\'' in content and 'status = \'ORANGE\'' in content
        print(f"   {'✅' if has_status_calc else '❌'} Calcul des statuts présent")
        
        # Vérifier la logique d'expiration
        has_expiration_logic = 'today > d.date_expiration' in content
        print(f"   {'✅' if has_expiration_logic else '❌'} Logique d\'expiration présente")
        
        # Vérifier la logique de pourcentage
        has_percentage_logic = 'ratio <= 0.10' in content
        print(f"   {'✅' if has_percentage_logic else '❌'} Logique de pourcentage présente")
        
        # Vérifier que documents est une liste avec statuts
        has_documents_list = 'documents.append({' in content and '\'status\': status' in content
        print(f"   {'✅' if has_documents_list else '❌'} Liste documents avec statuts")
        
        if not (has_status_calc and has_expiration_logic and has_percentage_logic and has_documents_list):
            success = False
    
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_template_details_bus():
    """Teste que le template details_bus affiche les statuts"""
    print("\n🎨 TEST TEMPLATE DETAILS BUS")
    print("=" * 50)
    
    template_file = Path("app/templates/pages/details_bus.html")
    
    if not template_file.exists():
        print("❌ Template details_bus.html non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier les conditions de statut
    has_rouge_status = "d.status == 'ROUGE'" in content
    print(f"   {'✅' if has_rouge_status else '❌'} Condition statut ROUGE")
    
    has_orange_status = "d.status == 'ORANGE'" in content
    print(f"   {'✅' if has_orange_status else '❌'} Condition statut ORANGE")
    
    # Vérifier les badges de statut
    has_expire_badge = "status_badge('Expiré', 'danger')" in content
    print(f"   {'✅' if has_expire_badge else '❌'} Badge 'Expiré'")
    
    has_bientot_badge = "status_badge('Bientôt expiré', 'warning')" in content
    print(f"   {'✅' if has_bientot_badge else '❌'} Badge 'Bientôt expiré'")
    
    has_valide_badge = "status_badge('Valide', 'success')" in content
    print(f"   {'✅' if has_valide_badge else '❌'} Badge 'Valide'")
    
    success = has_rouge_status and has_orange_status and has_expire_badge and has_bientot_badge and has_valide_badge
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def main():
    """Fonction principale"""
    print("🧪 TEST DES CORRECTIONS DES PROBLÈMES")
    print("=" * 60)
    print("Objectif: Vérifier que tous les problèmes identifiés sont corrigés")
    
    # Tests
    test1 = test_bouton_depannage_admin()
    test2 = test_icone_document_expressive()
    test3 = test_statuts_documents_mecanicien()
    test4 = test_template_details_bus()
    
    # Résultat final
    print("\n" + "=" * 60)
    print("🏁 RÉSULTAT FINAL")
    print("=" * 60)
    
    total_tests = 4
    tests_reussis = sum([test1, test2, test3, test4])
    
    print(f"Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 TOUS LES PROBLÈMES SONT CORRIGÉS !")
        print("\n✅ Corrections appliquées:")
        print("   • Bouton dépannage admin utilise la modal partagée")
        print("   • Icône document plus expressive (fa-file-plus)")
        print("   • Statuts documents calculés pour mécanicien et chargé")
        print("   • Template affiche correctement les statuts")
    else:
        print("⚠️  CERTAINS PROBLÈMES PERSISTENT")
        if not test1:
            print("   ❌ Bouton dépannage admin")
        if not test2:
            print("   ❌ Icône document expressive")
        if not test3:
            print("   ❌ Statuts documents mécanicien")
        if not test4:
            print("   ❌ Template details bus")
    
    print("\n🎯 TESTS À EFFECTUER MANUELLEMENT:")
    print("   • Cliquer sur l'icône panne dans le tableau admin")
    print("   • Vérifier que l'icône document est bien visible")
    print("   • Accéder aux détails bus en tant que mécanicien")
    print("   • Vérifier les statuts des documents (Expiré/Bientôt expiré/Valide)")

if __name__ == "__main__":
    main()
