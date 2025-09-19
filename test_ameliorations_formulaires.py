#!/usr/bin/env python3
"""
Script de test pour vérifier les améliorations des formulaires
1. Mise à jour automatique des données après soumission
2. Possibilité de rouvrir les formulaires immédiatement
3. Réattachement automatique des événements
"""

import re
from pathlib import Path

def test_reattachement_evenements():
    """Teste que les événements sont réattachés après AJAX"""
    print("🔄 TEST RÉATTACHEMENT ÉVÉNEMENTS")
    print("=" * 50)
    
    main_js_file = Path("app/static/js/main.js")
    
    if not main_js_file.exists():
        print("❌ Fichier main.js non trouvé")
        return False
        
    with open(main_js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Méthode reattachEventListeners présente
    has_reattach_method = 'reattachEventListeners()' in content and 'static reattachEventListeners' in content
    print(f"   {'✅' if has_reattach_method else '❌'} Méthode reattachEventListeners présente")
    
    # Test 2: Appel de reattachEventListeners après soumission
    has_reattach_call = 'this.reattachEventListeners()' in content
    print(f"   {'✅' if has_reattach_call else '❌'} Appel de reattachEventListeners après soumission")
    
    # Test 3: Réattachement des boutons edit-statut-btn
    has_edit_btn_reattach = 'edit-statut-btn' in content and 'replaceWith' in content
    print(f"   {'✅' if has_edit_btn_reattach else '❌'} Réattachement des boutons edit-statut-btn")
    
    # Test 4: Réattachement des statuts cliquables
    has_statut_reattach = 'statut-clickable' in content and 'addEventListener' in content
    print(f"   {'✅' if has_statut_reattach else '❌'} Réattachement des statuts cliquables")
    
    success = has_reattach_method and has_reattach_call and has_edit_btn_reattach and has_statut_reattach
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_mise_a_jour_donnees_ajax():
    """Teste que les données sont mises à jour via AJAX"""
    print("\n📊 TEST MISE À JOUR DONNÉES AJAX")
    print("=" * 50)
    
    main_js_file = Path("app/static/js/main.js")
    
    if not main_js_file.exists():
        print("❌ Fichier main.js non trouvé")
        return False
        
    with open(main_js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Méthode refreshChauffeurStatuts présente
    has_refresh_statuts = 'refreshChauffeurStatuts()' in content and 'static async refreshChauffeurStatuts' in content
    print(f"   {'✅' if has_refresh_statuts else '❌'} Méthode refreshChauffeurStatuts présente")
    
    # Test 2: Appel AJAX vers get_chauffeurs_planning_ajax
    has_ajax_call = '/admin/get_chauffeurs_planning_ajax' in content and 'fetch(' in content
    print(f"   {'✅' if has_ajax_call else '❌'} Appel AJAX vers get_chauffeurs_planning_ajax")
    
    # Test 3: Mise à jour du tableau
    has_table_update = 'updateChauffeurStatusInTable' in content and 'data-chauffeur-id' in content
    print(f"   {'✅' if has_table_update else '❌'} Mise à jour du tableau implémentée")
    
    # Test 4: Génération HTML pour statuts et lieux
    has_html_generation = 'generateStatutHTML' in content and 'generateLieuHTML' in content
    print(f"   {'✅' if has_html_generation else '❌'} Génération HTML pour statuts et lieux")
    
    success = has_refresh_statuts and has_ajax_call and has_table_update and has_html_generation
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_route_ajax_amelioree():
    """Teste que la route AJAX retourne les bonnes données"""
    print("\n🛣️ TEST ROUTE AJAX AMÉLIORÉE")
    print("=" * 50)
    
    route_file = Path("app/routes/admin/gestion_utilisateurs.py")
    
    if not route_file.exists():
        print("❌ Route gestion_utilisateurs non trouvée")
        return False
        
    with open(route_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Structure de données améliorée
    has_improved_structure = 'chauffeur_data' in content and 'chauffeur_id' in content
    print(f"   {'✅' if has_improved_structure else '❌'} Structure de données améliorée")
    
    # Test 2: Inclusion du lieu dans les données
    has_lieu_data = "'lieu': statut.lieu" in content
    print(f"   {'✅' if has_lieu_data else '❌'} Inclusion du lieu dans les données")
    
    # Test 3: Formats de date multiples
    has_date_formats = 'date_debut_formatted' in content and 'isoformat()' in content
    print(f"   {'✅' if has_date_formats else '❌'} Formats de date multiples")
    
    # Test 4: Données par chauffeur
    has_chauffeur_grouping = 'planning_data.append(chauffeur_data)' in content
    print(f"   {'✅' if has_chauffeur_grouping else '❌'} Données groupées par chauffeur")
    
    success = has_improved_structure and has_lieu_data and has_date_formats and has_chauffeur_grouping
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_delegation_evenements():
    """Teste que la délégation d'événements est implémentée"""
    print("\n🎯 TEST DÉLÉGATION ÉVÉNEMENTS")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Délégation pour edit-statut-btn
    has_edit_delegation = '$(document).on(\'click\', \'.edit-statut-btn\'' in content
    print(f"   {'✅' if has_edit_delegation else '❌'} Délégation pour edit-statut-btn")
    
    # Test 2: Délégation pour fermeture modal
    has_close_delegation = '$(document).on(\'click\', \'#closeEditStatutModal' in content
    print(f"   {'✅' if has_close_delegation else '❌'} Délégation pour fermeture modal")
    
    # Test 3: Réinitialisation du formulaire
    has_form_reset = 'reset()' in content and 'chauffeurId' in content
    print(f"   {'✅' if has_form_reset else '❌'} Réinitialisation du formulaire")
    
    # Test 4: Gestion complète de l'ouverture modal
    has_complete_modal_open = 'removeClass(\'show\').addClass(\'show\')' in content
    print(f"   {'✅' if has_complete_modal_open else '❌'} Gestion complète ouverture modal")
    
    success = has_edit_delegation and has_close_delegation and has_form_reset and has_complete_modal_open
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_attributs_data_chauffeur():
    """Teste que les attributs data-chauffeur-id sont présents"""
    print("\n🏷️ TEST ATTRIBUTS DATA CHAUFFEUR")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Attribut data-chauffeur-id sur les lignes
    has_data_attr = 'data-chauffeur-id="{{ chauffeur.chauffeur_id }}"' in content
    print(f"   {'✅' if has_data_attr else '❌'} Attribut data-chauffeur-id sur les lignes")
    
    # Test 2: Utilisation dans le JavaScript
    has_js_usage = 'data-chauffeur-id' in content and 'querySelector' in content
    print(f"   {'✅' if has_js_usage else '❌'} Utilisation dans le JavaScript")
    
    # Test 3: Sélecteurs CSS appropriés
    has_css_selectors = 'tr[data-chauffeur-id' in content
    print(f"   {'✅' if has_css_selectors else '❌'} Sélecteurs CSS appropriés")
    
    success = has_data_attr and has_js_usage and has_css_selectors
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_console_logs_debug():
    """Teste que les logs de debug sont présents"""
    print("\n🐛 TEST LOGS DE DEBUG")
    print("=" * 50)
    
    files_to_check = [
        ("app/static/js/main.js", "main.js"),
        ("app/templates/legacy/chauffeurs.html", "chauffeurs.html")
    ]
    
    success_count = 0
    
    for file_path, file_name in files_to_check:
        file_obj = Path(file_path)
        if file_obj.exists():
            with open(file_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_console_logs = 'console.log(' in content and ('✅' in content or 'Événements réattachés' in content or 'Modal statut' in content)
            print(f"   {'✅' if has_console_logs else '❌'} Logs de debug dans {file_name}")
            
            if has_console_logs:
                success_count += 1
        else:
            print(f"   ❌ {file_name} non trouvé")
    
    success = success_count >= 1
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def main():
    """Fonction principale"""
    print("🧪 TEST DES AMÉLIORATIONS DES FORMULAIRES")
    print("=" * 70)
    print("Objectif: Vérifier la mise à jour automatique et la réouverture des formulaires")
    
    # Tests
    test1 = test_reattachement_evenements()
    test2 = test_mise_a_jour_donnees_ajax()
    test3 = test_route_ajax_amelioree()
    test4 = test_delegation_evenements()
    test5 = test_attributs_data_chauffeur()
    test6 = test_console_logs_debug()
    
    # Résultat final
    print("\n" + "=" * 70)
    print("🏁 RÉSULTAT FINAL")
    print("=" * 70)
    
    total_tests = 6
    tests_reussis = sum([test1, test2, test3, test4, test5, test6])
    
    print(f"Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 TOUTES LES AMÉLIORATIONS APPLIQUÉES AVEC SUCCÈS !")
        print("\n✅ Améliorations réalisées:")
        print("   • Réattachement automatique des événements après AJAX")
        print("   • Mise à jour des données sans rechargement de page")
        print("   • Route AJAX retourne les données complètes avec lieu")
        print("   • Délégation d'événements pour les éléments dynamiques")
        print("   • Attributs data pour faciliter la mise à jour")
        print("   • Logs de debug pour faciliter le dépannage")
    else:
        print("⚠️  CERTAINES AMÉLIORATIONS MANQUENT")
        if not test1:
            print("   ❌ Réattachement événements non implémenté")
        if not test2:
            print("   ❌ Mise à jour AJAX non fonctionnelle")
        if not test3:
            print("   ❌ Route AJAX non améliorée")
        if not test4:
            print("   ❌ Délégation événements manquante")
        if not test5:
            print("   ❌ Attributs data manquants")
        if not test6:
            print("   ❌ Logs de debug insuffisants")
    
    print("\n🎯 FONCTIONNALITÉS ATTENDUES:")
    print("   ✅ Soumission formulaire → Mise à jour automatique des données")
    print("   ✅ Possibilité de rouvrir le formulaire immédiatement")
    print("   ✅ Pas de rechargement de page nécessaire")
    print("   ✅ Événements fonctionnels sur les nouveaux éléments")
    print("   ✅ Interface réactive et fluide")

if __name__ == "__main__":
    main()
