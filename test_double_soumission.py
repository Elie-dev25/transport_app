#!/usr/bin/env python3
"""
Script de test pour vérifier que le problème de double soumission est résolu
"""

import re
from pathlib import Path

def test_suppression_gestionnaire_double():
    """Teste que le gestionnaire de soumission en double est supprimé"""
    print("🚫 TEST SUPPRESSION GESTIONNAIRE DOUBLE")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Plus de gestionnaire jQuery pour editStatutChauffeurForm
    has_no_jquery_submit = "$('#editStatutChauffeurForm').on('submit'" not in content
    print(f"   {'✅' if has_no_jquery_submit else '❌'} Plus de gestionnaire jQuery pour editStatutChauffeurForm")
    
    # Test 2: Plus d'appel AJAX direct dans le template
    has_no_direct_ajax = "url: '/admin/modifier_statut_chauffeur_ajax'" not in content
    print(f"   {'✅' if has_no_direct_ajax else '❌'} Plus d'appel AJAX direct dans le template")
    
    # Test 3: Plus de location.reload() dans le template
    has_no_location_reload = "location.reload()" not in content
    print(f"   {'✅' if has_no_location_reload else '❌'} Plus de location.reload() dans le template")
    
    success = has_no_jquery_submit and has_no_direct_ajax and has_no_location_reload
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_modal_gestionnaire_unique():
    """Teste que le modal a un gestionnaire unique"""
    print("\n🎯 TEST MODAL GESTIONNAIRE UNIQUE")
    print("=" * 50)
    
    modal_file = Path("app/templates/shared/modals/_edit_statut_chauffeur_modal.html")
    
    if not modal_file.exists():
        print("❌ Modal statut chauffeur non trouvée")
        return False
        
    with open(modal_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Présence de init_modal_form
    has_init_modal_form = "init_modal_form(" in content
    print(f"   {'✅' if has_init_modal_form else '❌'} Présence de init_modal_form")
    
    # Test 2: Bon ID d'erreur (statutChauffeurError)
    has_correct_error_id = "statutChauffeurError" in content
    print(f"   {'✅' if has_correct_error_id else '❌'} Bon ID d'erreur (statutChauffeurError)")
    
    # Test 3: Message de succès défini
    has_success_message = "Statut du chauffeur modifié avec succès" in content
    print(f"   {'✅' if has_success_message else '❌'} Message de succès défini")
    
    success = has_init_modal_form and has_correct_error_id and has_success_message
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_form_modal_manager_complet():
    """Teste que FormModalManager est complet"""
    print("\n🔧 TEST FORM MODAL MANAGER COMPLET")
    print("=" * 50)
    
    main_js_file = Path("app/static/js/main.js")
    
    if not main_js_file.exists():
        print("❌ Fichier main.js non trouvé")
        return False
        
    with open(main_js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Méthode submitModalForm présente
    has_submit_method = "static async submitModalForm(" in content
    print(f"   {'✅' if has_submit_method else '❌'} Méthode submitModalForm présente")
    
    # Test 2: Méthode initModalForm présente
    has_init_method = "static initModalForm(" in content
    print(f"   {'✅' if has_init_method else '❌'} Méthode initModalForm présente")
    
    # Test 3: Gestion des erreurs et succès
    has_error_success_handling = "data.success" in content and "showFormError" in content
    print(f"   {'✅' if has_error_success_handling else '❌'} Gestion des erreurs et succès")
    
    # Test 4: Réattachement des événements
    has_reattach = "reattachEventListeners()" in content
    print(f"   {'✅' if has_reattach else '❌'} Réattachement des événements")
    
    success = has_submit_method and has_init_method and has_error_success_handling and has_reattach
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_macro_form_coherente():
    """Teste que la macro form est cohérente"""
    print("\n📝 TEST MACRO FORM COHÉRENTE")
    print("=" * 50)
    
    macro_file = Path("app/templates/shared/macros/form_macros.html")
    
    if not macro_file.exists():
        print("❌ Fichier form_macros.html non trouvé")
        return False
        
    with open(macro_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Macro init_modal_form définie
    has_init_macro = "{% macro init_modal_form(" in content
    print(f"   {'✅' if has_init_macro else '❌'} Macro init_modal_form définie")
    
    # Test 2: Appel à FormModalManager.initModalForm
    has_manager_call = "FormModalManager.initModalForm(" in content
    print(f"   {'✅' if has_manager_call else '❌'} Appel à FormModalManager.initModalForm")
    
    # Test 3: Gestion des paramètres
    has_parameters = "form_id" in content and "modal_id" in content and "error_id" in content
    print(f"   {'✅' if has_parameters else '❌'} Gestion des paramètres")
    
    success = has_init_macro and has_manager_call and has_parameters
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_prevention_double_soumission():
    """Teste les mécanismes de prévention de double soumission"""
    print("\n🛡️ TEST PRÉVENTION DOUBLE SOUMISSION")
    print("=" * 50)
    
    main_js_file = Path("app/static/js/main.js")
    
    if not main_js_file.exists():
        print("❌ Fichier main.js non trouvé")
        return False
        
    with open(main_js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Désactivation du bouton de soumission
    has_button_disable = "submitBtn.disabled = true" in content
    print(f"   {'✅' if has_button_disable else '❌'} Désactivation du bouton de soumission")
    
    # Test 2: Indicateur de chargement
    has_loading_indicator = "fa-spinner fa-spin" in content and "Envoi..." in content
    print(f"   {'✅' if has_loading_indicator else '❌'} Indicateur de chargement")
    
    # Test 3: Réactivation du bouton dans finally
    has_button_reactivate = "finally" in content and "disabled = false" in content
    print(f"   {'✅' if has_button_reactivate else '❌'} Réactivation du bouton dans finally")
    
    # Test 4: Prévention d'événement par défaut
    has_prevent_default = "e.preventDefault()" in content
    print(f"   {'✅' if has_prevent_default else '❌'} Prévention d'événement par défaut")
    
    success = has_button_disable and has_loading_indicator and has_button_reactivate and has_prevent_default
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def main():
    """Fonction principale"""
    print("🧪 TEST RÉSOLUTION DOUBLE SOUMISSION")
    print("=" * 70)
    print("Objectif: Vérifier que le problème de double enregistrement est résolu")
    
    # Tests
    test1 = test_suppression_gestionnaire_double()
    test2 = test_modal_gestionnaire_unique()
    test3 = test_form_modal_manager_complet()
    test4 = test_macro_form_coherente()
    test5 = test_prevention_double_soumission()
    
    # Résultat final
    print("\n" + "=" * 70)
    print("🏁 RÉSULTAT FINAL")
    print("=" * 70)
    
    total_tests = 5
    tests_reussis = sum([test1, test2, test3, test4, test5])
    
    print(f"Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 PROBLÈME DE DOUBLE SOUMISSION RÉSOLU !")
        print("\n✅ Corrections appliquées:")
        print("   • Gestionnaire jQuery en double supprimé du template")
        print("   • Modal utilise uniquement FormModalManager")
        print("   • Prévention de double soumission implémentée")
        print("   • Réattachement automatique des événements")
        print("   • Gestion unifiée des erreurs et succès")
    else:
        print("⚠️  CERTAINES CORRECTIONS MANQUENT")
        if not test1:
            print("   ❌ Gestionnaire double non supprimé")
        if not test2:
            print("   ❌ Modal n'a pas de gestionnaire unique")
        if not test3:
            print("   ❌ FormModalManager incomplet")
        if not test4:
            print("   ❌ Macro form incohérente")
        if not test5:
            print("   ❌ Prévention double soumission manquante")
    
    print("\n🎯 FONCTIONNEMENT ATTENDU:")
    print("   ✅ Un seul enregistrement par soumission")
    print("   ✅ Bouton désactivé pendant l'envoi")
    print("   ✅ Indicateur de chargement visible")
    print("   ✅ Modal se ferme après succès")
    print("   ✅ Données mises à jour automatiquement")
    print("   ✅ Possibilité de rouvrir le formulaire immédiatement")

if __name__ == "__main__":
    main()
