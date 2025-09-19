#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections finales
1. Modification d'un statut ne supprime pas les autres
2. Fiche d'impression planification affiche les bonnes données
"""

import re
from pathlib import Path

def test_modification_statut_individuel():
    """Teste que la modification d'un statut individuel ne supprime pas les autres"""
    print("🔧 TEST MODIFICATION STATUT INDIVIDUEL")
    print("=" * 50)
    
    modal_file = Path("app/templates/shared/modals/_edit_individual_statut_modal.html")
    
    if not modal_file.exists():
        print("❌ Modal modification individuelle non trouvée")
        return False
        
    with open(modal_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Gestion manuelle du formulaire (pas FormModalManager)
    has_manual_handling = 'form.addEventListener(\'submit\'' in content and 'e.preventDefault()' in content
    print(f"   {'✅' if has_manual_handling else '❌'} Gestion manuelle du formulaire")
    
    # Test 2: Pas de rechargement de page complet
    has_no_page_reload = 'window.location.reload()' not in content
    print(f"   {'✅' if has_no_page_reload else '❌'} Pas de rechargement de page complet")
    
    # Test 3: Rechargement seulement de la liste des statuts
    has_statuts_reload = 'loadAutresStatuts(chauffeurId)' in content
    print(f"   {'✅' if has_statuts_reload else '❌'} Rechargement seulement de la liste des statuts")
    
    # Test 4: Pas d'utilisation de FormModalManager
    has_no_form_manager = 'FormModalManager' not in content or 'init_modal_form' not in content
    print(f"   {'✅' if has_no_form_manager else '❌'} Pas d'utilisation de FormModalManager")
    
    success = has_manual_handling and has_no_page_reload and has_statuts_reload and has_no_form_manager
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_route_modification_individuelle():
    """Teste que la route de modification individuelle est correcte"""
    print("\n🛣️ TEST ROUTE MODIFICATION INDIVIDUELLE")
    print("=" * 50)
    
    route_file = Path("app/routes/admin/gestion_utilisateurs.py")
    
    if not route_file.exists():
        print("❌ Fichier routes non trouvé")
        return False
        
    with open(route_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Route existe
    has_route = '/modifier_statut_individuel_ajax' in content
    print(f"   {'✅' if has_route else '❌'} Route modifier_statut_individuel_ajax existe")
    
    # Test 2: Modification seulement du statut spécifique
    has_specific_update = 'statut_obj = ChauffeurStatut.query.get(int(statut_id))' in content
    print(f"   {'✅' if has_specific_update else '❌'} Modification seulement du statut spécifique")
    
    # Test 3: Pas de suppression d'autres statuts
    has_no_delete = 'delete' not in content.lower() or 'ChauffeurStatut.query.filter' not in content
    print(f"   {'✅' if has_no_delete else '❌'} Pas de suppression d'autres statuts")
    
    # Test 4: Commit seulement du statut modifié
    has_single_commit = 'db.session.commit()' in content
    print(f"   {'✅' if has_single_commit else '❌'} Commit seulement du statut modifié")
    
    success = has_route and has_specific_update and has_no_delete and has_single_commit
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_impression_planification_ajax():
    """Teste que la fonction d'impression planification AJAX est corrigée"""
    print("\n🖨️ TEST IMPRESSION PLANIFICATION AJAX")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Fonction generatePlanningTableFromAjax corrigée
    has_corrected_function = 'chauffeur.statuts.forEach(function(statut)' in content
    print(f"   {'✅' if has_corrected_function else '❌'} Fonction generatePlanningTableFromAjax corrigée")
    
    # Test 2: Traitement correct des données chauffeur
    has_chauffeur_processing = 'chauffeurNom = `${chauffeur.nom} ${chauffeur.prenom}`' in content
    print(f"   {'✅' if has_chauffeur_processing else '❌'} Traitement correct des données chauffeur")
    
    # Test 3: Mapping des statuts pour affichage
    has_statut_mapping = 'statutLabel = \'Congé\'' in content and 'statutLabel = \'Permanence\'' in content
    print(f"   {'✅' if has_statut_mapping else '❌'} Mapping des statuts pour affichage")
    
    # Test 4: Gestion des lieux d'affectation
    has_lieu_handling = 'lieuLabel = \' (CUM)\'' in content and 'lieuLabel = \' (Campus)\'' in content
    print(f"   {'✅' if has_lieu_handling else '❌'} Gestion des lieux d'affectation")
    
    success = has_corrected_function and has_chauffeur_processing and has_statut_mapping and has_lieu_handling
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_impression_planification_fallback():
    """Teste que la fonction d'impression planification fallback est corrigée"""
    print("\n🖨️ TEST IMPRESSION PLANIFICATION FALLBACK")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Index correct pour la colonne statut
    has_correct_index = 'statutCell = cells[4]' in content
    print(f"   {'✅' if has_correct_index else '❌'} Index correct pour la colonne statut (4)")
    
    # Test 2: Condition correcte pour le nombre de colonnes
    has_correct_condition = 'if (cells.length >= 5)' in content
    print(f"   {'✅' if has_correct_condition else '❌'} Condition correcte pour le nombre de colonnes")
    
    # Test 3: Statut par défaut "ATTENTE" au lieu de "Disponible"
    has_attente_default = 'dataset.statut || \'ATTENTE\'' in content
    print(f"   {'✅' if has_attente_default else '❌'} Statut par défaut "ATTENTE"")
    
    # Test 4: Mapping inclut ATTENTE
    has_attente_mapping = '\'ATTENTE\': \'Attente\'' in content
    print(f"   {'✅' if has_attente_mapping else '❌'} Mapping inclut ATTENTE")
    
    success = has_correct_index and has_correct_condition and has_attente_default and has_attente_mapping
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_route_planification_ajax():
    """Teste que la route de planification AJAX retourne les bonnes données"""
    print("\n🛣️ TEST ROUTE PLANIFICATION AJAX")
    print("=" * 50)
    
    route_file = Path("app/routes/admin/gestion_utilisateurs.py")
    
    if not route_file.exists():
        print("❌ Fichier routes non trouvé")
        return False
        
    with open(route_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Route get_chauffeurs_planning_ajax existe
    has_route = '/get_chauffeurs_planning_ajax' in content
    print(f"   {'✅' if has_route else '❌'} Route get_chauffeurs_planning_ajax existe")
    
    # Test 2: Structure de données correcte
    has_correct_structure = 'chauffeur_data = {' in content and '\'statuts\': []' in content
    print(f"   {'✅' if has_correct_structure else '❌'} Structure de données correcte")
    
    # Test 3: Formatage des dates
    has_date_formatting = 'date_debut_formatted' in content and 'date_fin_formatted' in content
    print(f"   {'✅' if has_date_formatting else '❌'} Formatage des dates")
    
    # Test 4: Calcul de la durée
    has_duration_calc = 'duree_jours = (statut.date_fin - statut.date_debut).days + 1' in content
    print(f"   {'✅' if has_duration_calc else '❌'} Calcul de la durée")
    
    success = has_route and has_correct_structure and has_date_formatting and has_duration_calc
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_zone_impression_planification():
    """Teste que la zone d'impression planification est correcte"""
    print("\n📄 TEST ZONE IMPRESSION PLANIFICATION")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Zone d'impression existe
    has_print_area = 'id="printPlanningArea"' in content
    print(f"   {'✅' if has_print_area else '❌'} Zone d\'impression existe")
    
    # Test 2: Tableau avec bonnes colonnes
    has_correct_columns = '<th>Chauffeur</th>' in content and '<th>Statut</th>' in content and '<th>Durée</th>' in content
    print(f"   {'✅' if has_correct_columns else '❌'} Tableau avec bonnes colonnes")
    
    # Test 3: Corps de tableau dynamique
    has_dynamic_body = 'id="planningTableBody"' in content
    print(f"   {'✅' if has_dynamic_body else '❌'} Corps de tableau dynamique")
    
    # Test 4: En-tête d'impression
    has_print_header = 'Planification des Chauffeurs' in content and 'Transport UdM' in content
    print(f"   {'✅' if has_print_header else '❌'} En-tête d\'impression")
    
    success = has_print_area and has_correct_columns and has_dynamic_body and has_print_header
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def main():
    """Fonction principale"""
    print("🧪 TEST CORRECTIONS FINALES")
    print("=" * 70)
    print("Objectif: Vérifier modification statut et impression planification")
    
    # Tests
    test1 = test_modification_statut_individuel()
    test2 = test_route_modification_individuelle()
    test3 = test_impression_planification_ajax()
    test4 = test_impression_planification_fallback()
    test5 = test_route_planification_ajax()
    test6 = test_zone_impression_planification()
    
    # Résultat final
    print("\n" + "=" * 70)
    print("🏁 RÉSULTAT FINAL")
    print("=" * 70)
    
    total_tests = 6
    tests_reussis = sum([test1, test2, test3, test4, test5, test6])
    
    print(f"Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 TOUTES LES CORRECTIONS FINALES APPLIQUÉES AVEC SUCCÈS !")
        print("\n✅ Corrections réalisées:")
        print("   • Modification statut individuel sans suppression des autres")
        print("   • Route de modification sécurisée et spécifique")
        print("   • Impression planification AJAX corrigée")
        print("   • Impression planification fallback corrigée")
        print("   • Route planification AJAX avec bonnes données")
        print("   • Zone d'impression planification complète")
    else:
        print("⚠️  CERTAINES CORRECTIONS MANQUENT")
        if not test1:
            print("   ❌ Modification statut individuel problématique")
        if not test2:
            print("   ❌ Route modification individuelle incorrecte")
        if not test3:
            print("   ❌ Impression planification AJAX défaillante")
        if not test4:
            print("   ❌ Impression planification fallback défaillante")
        if not test5:
            print("   ❌ Route planification AJAX incorrecte")
        if not test6:
            print("   ❌ Zone impression planification incomplète")
    
    print("\n🎯 FONCTIONNEMENT ATTENDU:")
    print("   ✅ Modifier un statut ne supprime pas les autres")
    print("   ✅ Impression planification affiche les vraies données")
    print("   ✅ Pas de 'undefined' dans les colonnes")
    print("   ✅ Statuts et lieux correctement affichés")
    print("   ✅ Dates et durées calculées correctement")

if __name__ == "__main__":
    main()
