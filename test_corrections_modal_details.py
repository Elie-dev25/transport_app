#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections de la modal détails du statut
1. Délégation d'événements pour éviter le rechargement
2. Couleur bleue du titre de la modal
3. Suppression des sections inutiles
4. Fermeture de modal avant confirmation
5. Titre bleu de la confirmation
6. Correction du doublement des statuts
"""

import re
from pathlib import Path

def test_delegation_evenements_modal():
    """Teste que la délégation d'événements est correcte pour la modal"""
    print("🎯 TEST DÉLÉGATION ÉVÉNEMENTS MODAL")
    print("=" * 50)
    
    modal_file = Path("app/templates/shared/modals/_statut_details_modal.html")
    
    if not modal_file.exists():
        print("❌ Modal détails non trouvée")
        return False
        
    with open(modal_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Délégation d'événements au lieu de addEventListener
    has_delegation = 'document.addEventListener(\'click\', function(e)' in content
    print(f"   {'✅' if has_delegation else '❌'} Délégation d'événements implémentée")
    
    # Test 2: Plus de DOMContentLoaded
    has_no_dom_ready = 'DOMContentLoaded' not in content
    print(f"   {'✅' if has_no_dom_ready else '❌'} Plus de DOMContentLoaded")
    
    # Test 3: Gestion des deux types de fermeture
    has_close_handling = 'closeStatutDetailsModal' in content and 'statutDetailsModal' in content
    print(f"   {'✅' if has_close_handling else '❌'} Gestion des deux types de fermeture")
    
    success = has_delegation and has_no_dom_ready and has_close_handling
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_couleur_bleue_titre():
    """Teste que le titre de la modal est bleu"""
    print("\n🔵 TEST COULEUR BLEUE TITRE")
    print("=" * 50)
    
    css_file = Path("app/static/css/tableaux.css")
    
    if not css_file.exists():
        print("❌ Fichier CSS non trouvé")
        return False
        
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Couleur bleue pour modal-details header
    has_blue_header = '.modal-details .modal-header' in content and '#3b82f6' in content
    print(f"   {'✅' if has_blue_header else '❌'} Couleur bleue pour modal-details header")
    
    # Test 2: Plus de couleur verte
    has_no_green = '#10b981' not in content.split('.modal-details .modal-header')[1].split('}')[0] if '.modal-details .modal-header' in content else True
    print(f"   {'✅' if has_no_green else '❌'} Plus de couleur verte dans le header")
    
    success = has_blue_header and has_no_green
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_sections_supprimees():
    """Teste que les sections inutiles sont supprimées"""
    print("\n🗑️ TEST SECTIONS SUPPRIMÉES")
    print("=" * 50)
    
    modal_file = Path("app/templates/shared/modals/_statut_details_modal.html")
    
    if not modal_file.exists():
        print("❌ Modal détails non trouvée")
        return False
        
    with open(modal_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Plus de section chauffeur
    has_no_chauffeur_section = 'detailChauffeurNom' not in content
    print(f"   {'✅' if has_no_chauffeur_section else '❌'} Plus de section chauffeur")
    
    # Test 2: Plus de section statut actuel
    has_no_statut_section = 'detailStatut' not in content
    print(f"   {'✅' if has_no_statut_section else '❌'} Plus de section statut actuel")
    
    # Test 3: Plus de section période
    has_no_period_section = 'period-info' not in content and 'detailDateDebut' not in content
    print(f"   {'✅' if has_no_period_section else '❌'} Plus de section période")
    
    # Test 4: Seule la section statuts reste
    has_only_statuts = 'autresStatutsList' in content and 'Tous les statuts du chauffeur' in content
    print(f"   {'✅' if has_only_statuts else '❌'} Seule la section statuts reste")
    
    success = has_no_chauffeur_section and has_no_statut_section and has_no_period_section and has_only_statuts
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_fermeture_modal_avant_confirmation():
    """Teste que la modal se ferme avant la confirmation"""
    print("\n🚪 TEST FERMETURE MODAL AVANT CONFIRMATION")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Fermeture de modal avant confirmation
    has_modal_close = 'detailsModal.classList.remove(\'show\')' in content and 'detailsModal.style.display = \'none\'' in content
    print(f"   {'✅' if has_modal_close else '❌'} Fermeture de modal avant confirmation")
    
    # Test 2: Délai avec setTimeout
    has_timeout = 'setTimeout(() => {' in content and 'Swal.fire' in content
    print(f"   {'✅' if has_timeout else '❌'} Délai avec setTimeout")
    
    # Test 3: Réouverture si annulé
    has_reopen = 'detailsModal.classList.add(\'show\')' in content and 'detailsModal.style.display = \'flex\'' in content
    print(f"   {'✅' if has_reopen else '❌'} Réouverture si annulé")
    
    success = has_modal_close and has_timeout and has_reopen
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_titre_bleu_confirmation():
    """Teste que le titre de confirmation est bleu"""
    print("\n🔵 TEST TITRE BLEU CONFIRMATION")
    print("=" * 50)
    
    css_file = Path("app/static/css/tableaux.css")
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    success_count = 0
    
    # Test CSS
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        has_swal_styles = '.swal-title-blue' in css_content and '#3b82f6' in css_content
        print(f"   {'✅' if has_swal_styles else '❌'} Styles SweetAlert2 pour titre bleu")
        if has_swal_styles:
            success_count += 1
    
    # Test JavaScript
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        has_custom_class = 'customClass:' in js_content and 'swal-title-blue' in js_content
        print(f"   {'✅' if has_custom_class else '❌'} CustomClass pour titre bleu")
        if has_custom_class:
            success_count += 1
        
        has_blue_confirm = 'confirmButtonColor: \'#3b82f6\'' in js_content
        print(f"   {'✅' if has_blue_confirm else '❌'} Couleur bleue pour bouton confirm")
        if has_blue_confirm:
            success_count += 1
    
    success = success_count >= 2
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_correction_doublement():
    """Teste que le doublement des statuts est corrigé"""
    print("\n🔄 TEST CORRECTION DOUBLEMENT")
    print("=" * 50)
    
    main_js_file = Path("app/static/js/main.js")
    
    if not main_js_file.exists():
        print("❌ Fichier main.js non trouvé")
        return False
        
    with open(main_js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Vidage du contenu avant remplacement
    has_clear_content = 'innerHTML = \'\';' in content
    print(f"   {'✅' if has_clear_content else '❌'} Vidage du contenu avant remplacement")
    
    # Test 2: Rechargement de page après délai
    has_reload = 'window.location.reload()' in content and 'setTimeout' in content
    print(f"   {'✅' if has_reload else '❌'} Rechargement de page après délai")
    
    # Test 3: Délai approprié (1500ms)
    has_appropriate_delay = '1500' in content
    print(f"   {'✅' if has_appropriate_delay else '❌'} Délai approprié (1500ms)")
    
    success = has_clear_content and has_reload and has_appropriate_delay
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_delegation_template_chauffeurs():
    """Teste que la délégation est correcte dans le template chauffeurs"""
    print("\n📄 TEST DÉLÉGATION TEMPLATE CHAUFFEURS")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Délégation pour ouverture modal
    has_open_delegation = '$(document).on(\'click\', \'.statut-clickable\'' in content
    print(f"   {'✅' if has_open_delegation else '❌'} Délégation pour ouverture modal")
    
    # Test 2: Délégation pour fermeture modal
    has_close_delegation = '$(document).on(\'click\', \'#closeStatutDetailsModal\'' in content
    print(f"   {'✅' if has_close_delegation else '❌'} Délégation pour fermeture modal")
    
    # Test 3: Display flex pour ouverture
    has_display_flex = 'modal.css(\'display\', \'flex\')' in content
    print(f"   {'✅' if has_display_flex else '❌'} Display flex pour ouverture")
    
    success = has_open_delegation and has_close_delegation and has_display_flex
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def main():
    """Fonction principale"""
    print("🧪 TEST CORRECTIONS MODAL DÉTAILS DU STATUT")
    print("=" * 70)
    print("Objectif: Vérifier toutes les corrections demandées")
    
    # Tests
    test1 = test_delegation_evenements_modal()
    test2 = test_couleur_bleue_titre()
    test3 = test_sections_supprimees()
    test4 = test_fermeture_modal_avant_confirmation()
    test5 = test_titre_bleu_confirmation()
    test6 = test_correction_doublement()
    test7 = test_delegation_template_chauffeurs()
    
    # Résultat final
    print("\n" + "=" * 70)
    print("🏁 RÉSULTAT FINAL")
    print("=" * 70)
    
    total_tests = 7
    tests_reussis = sum([test1, test2, test3, test4, test5, test6, test7])
    
    print(f"Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 TOUTES LES CORRECTIONS APPLIQUÉES AVEC SUCCÈS !")
        print("\n✅ Corrections réalisées:")
        print("   • Délégation d'événements pour éviter rechargement")
        print("   • Couleur bleue pour le titre de la modal")
        print("   • Suppression des sections inutiles")
        print("   • Fermeture modal avant confirmation")
        print("   • Titre bleu pour la confirmation")
        print("   • Correction du doublement des statuts")
        print("   • Délégation complète dans template chauffeurs")
    else:
        print("⚠️  CERTAINES CORRECTIONS MANQUENT")
        if not test1:
            print("   ❌ Délégation événements modal incomplète")
        if not test2:
            print("   ❌ Couleur bleue titre manquante")
        if not test3:
            print("   ❌ Sections inutiles non supprimées")
        if not test4:
            print("   ❌ Fermeture modal avant confirmation manquante")
        if not test5:
            print("   ❌ Titre bleu confirmation manquant")
        if not test6:
            print("   ❌ Correction doublement incomplète")
        if not test7:
            print("   ❌ Délégation template chauffeurs incomplète")
    
    print("\n🎯 FONCTIONNEMENT ATTENDU:")
    print("   ✅ Modal s'ouvre sans problème à chaque fois")
    print("   ✅ Titre bleu pour modal et confirmation")
    print("   ✅ Seuls les statuts sont affichés")
    print("   ✅ Confirmation apparaît au premier plan")
    print("   ✅ Pas de doublement après enregistrement")

if __name__ == "__main__":
    main()
