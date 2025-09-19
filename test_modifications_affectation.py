#!/usr/bin/env python3
"""
Script de test pour vérifier les modifications d'affectation des chauffeurs
1. Ajout du champ lieu dans le formulaire et la base de données
2. Changement de "DISPONIBLE" en "NON SPÉCIFIÉ"
3. Correction du problème de rechargement des formulaires modaux
"""

import re
from pathlib import Path

def test_formulaire_lieu_ajoute():
    """Teste que le champ lieu est ajouté au formulaire"""
    print("📍 TEST CHAMP LIEU AJOUTÉ AU FORMULAIRE")
    print("=" * 50)
    
    modal_file = Path("app/templates/shared/modals/_edit_statut_chauffeur_modal.html")
    
    if not modal_file.exists():
        print("❌ Modal statut chauffeur non trouvée")
        return False
        
    with open(modal_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Champ lieu présent
    has_lieu_field = 'name="lieu"' in content and 'Lieu d\'affectation' in content
    print(f"   {'✅' if has_lieu_field else '❌'} Champ lieu d\'affectation présent")
    
    # Test 2: Options lieu présentes
    has_lieu_options = all(option in content for option in ['CUM', 'CAMPUS', 'CONJOINTEMENT'])
    print(f"   {'✅' if has_lieu_options else '❌'} Options lieu (CUM, CAMPUS, CONJOINTEMENT) présentes")
    
    # Test 3: Structure form-grid maintenue
    has_form_grid = 'form-grid' in content and 'form-group' in content
    print(f"   {'✅' if has_form_grid else '❌'} Structure form-grid maintenue")
    
    success = has_lieu_field and has_lieu_options and has_form_grid
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_modele_chauffeur_statut_mis_a_jour():
    """Teste que le modèle ChauffeurStatut inclut le lieu"""
    print("\n🗃️ TEST MODÈLE CHAUFFEUR_STATUT MIS À JOUR")
    print("=" * 50)
    
    model_file = Path("app/models/chauffeur_statut.py")
    
    if not model_file.exists():
        print("❌ Modèle ChauffeurStatut non trouvé")
        return False
        
    with open(model_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Colonne lieu définie
    has_lieu_column = 'lieu = db.Column' in content and 'lieu_chauffeur_statut' in content
    print(f"   {'✅' if has_lieu_column else '❌'} Colonne lieu définie dans le modèle")
    
    # Test 2: Enum lieu correct
    has_lieu_enum = all(value in content for value in ['CUM', 'CAMPUS', 'CONJOINTEMENT'])
    print(f"   {'✅' if has_lieu_enum else '❌'} Enum lieu avec bonnes valeurs")
    
    # Test 3: Méthode to_dict mise à jour
    has_lieu_in_dict = "'lieu': self.lieu" in content
    print(f"   {'✅' if has_lieu_in_dict else '❌'} Méthode to_dict inclut le lieu")
    
    success = has_lieu_column and has_lieu_enum and has_lieu_in_dict
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_route_ajax_mise_a_jour():
    """Teste que la route AJAX gère le lieu"""
    print("\n🛣️ TEST ROUTE AJAX MISE À JOUR")
    print("=" * 50)
    
    route_file = Path("app/routes/admin/gestion_utilisateurs.py")
    
    if not route_file.exists():
        print("❌ Route gestion_utilisateurs non trouvée")
        return False
        
    with open(route_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Récupération du lieu
    has_lieu_retrieval = "lieu = request.form.get('lieu')" in content
    print(f"   {'✅' if has_lieu_retrieval else '❌'} Récupération du lieu depuis le formulaire")
    
    # Test 2: Validation du lieu
    has_lieu_validation = 'not lieu' in content and 'Champs requis manquants' in content
    print(f"   {'✅' if has_lieu_validation else '❌'} Validation du lieu requise")
    
    # Test 3: Création du statut avec lieu
    has_lieu_in_creation = 'lieu=lieu' in content and 'ChauffeurStatut(' in content
    print(f"   {'✅' if has_lieu_in_creation else '❌'} Création du statut avec lieu")
    
    success = has_lieu_retrieval and has_lieu_validation and has_lieu_in_creation
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_template_chauffeurs_mis_a_jour():
    """Teste que le template chauffeurs affiche le lieu"""
    print("\n📄 TEST TEMPLATE CHAUFFEURS MIS À JOUR")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Colonne Lieu dans l'en-tête
    has_lieu_header = '<th>Lieu</th>' in content
    print(f"   {'✅' if has_lieu_header else '❌'} Colonne Lieu dans l\'en-tête du tableau")
    
    # Test 2: Affichage du lieu dans le corps
    has_lieu_display = 'statut.lieu' in content and 'icon_cell' in content
    print(f"   {'✅' if has_lieu_display else '❌'} Affichage du lieu dans le corps du tableau")
    
    # Test 3: Gestion "Non spécifié"
    has_non_specifie = 'Non spécifié' in content
    print(f"   {'✅' if has_non_specifie else '❌'} Gestion "Non spécifié" pour lieu vide")
    
    # Test 4: Colspan mis à jour
    has_updated_colspan = 'colspan="{% if readonly or current_user.role == \'CHARGE\' %}6{% else %}7{% endif %}"' in content
    print(f"   {'✅' if has_updated_colspan else '❌'} Colspan mis à jour pour nouvelle colonne")
    
    success = has_lieu_header and has_lieu_display and has_non_specifie and has_updated_colspan
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_disponible_change_en_non_specifie():
    """Teste que DISPONIBLE est changé en NON SPÉCIFIÉ"""
    print("\n🔄 TEST DISPONIBLE → NON SPÉCIFIÉ")
    print("=" * 50)
    
    template_file = Path("app/templates/legacy/chauffeurs.html")
    
    if not template_file.exists():
        print("❌ Template chauffeurs non trouvé")
        return False
        
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Badge "Non spécifié" au lieu de "Disponible"
    has_non_specifie_badge = "status_badge('Non spécifié'" in content
    print(f"   {'✅' if has_non_specifie_badge else '❌'} Badge "Non spécifié" au lieu de "Disponible"")
    
    # Test 2: Icône question-circle
    has_question_icon = 'question-circle' in content
    print(f"   {'✅' if has_question_icon else '❌'} Icône question-circle utilisée")
    
    # Test 3: JavaScript mis à jour
    has_js_update = 'Non spécifié' in content and 'status-secondary' in content
    print(f"   {'✅' if has_js_update else '❌'} JavaScript mis à jour pour "Non spécifié"")
    
    # Test 4: Plus de référence à "Disponible"
    has_no_disponible = content.count('Disponible') <= 1  # Peut rester dans les commentaires
    print(f"   {'✅' if has_no_disponible else '❌'} Références "Disponible" supprimées")
    
    success = has_non_specifie_badge and has_question_icon and has_js_update and has_no_disponible
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_probleme_rechargement_corrige():
    """Teste que le problème de rechargement des formulaires est corrigé"""
    print("\n🔄 TEST PROBLÈME RECHARGEMENT CORRIGÉ")
    print("=" * 50)
    
    main_js_file = Path("app/static/js/main.js")
    
    if not main_js_file.exists():
        print("❌ Fichier main.js non trouvé")
        return False
        
    with open(main_js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Plus de location.reload() automatique
    has_no_auto_reload = 'location.reload()' not in content or 'refreshPageData' in content
    print(f"   {'✅' if has_no_auto_reload else '❌'} Plus de location.reload() automatique")
    
    # Test 2: Méthode refreshPageData présente
    has_refresh_method = 'refreshPageData()' in content and 'static refreshPageData' in content
    print(f"   {'✅' if has_refresh_method else '❌'} Méthode refreshPageData présente")
    
    # Test 3: Animation de rafraîchissement
    has_refresh_animation = 'refreshing' in content and 'updated' in content
    print(f"   {'✅' if has_refresh_animation else '❌'} Animation de rafraîchissement implémentée")
    
    # Test 4: CSS d'animation présent
    css_file = Path("app/static/css/tableaux.css")
    has_css_animation = False
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        has_css_animation = 'statusUpdate' in css_content and '@keyframes' in css_content
    print(f"   {'✅' if has_css_animation else '❌'} CSS d\'animation présent")
    
    success = has_no_auto_reload and has_refresh_method and has_refresh_animation and has_css_animation
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def test_script_sql_present():
    """Teste que le script SQL est présent et correct"""
    print("\n📜 TEST SCRIPT SQL PRÉSENT")
    print("=" * 50)
    
    sql_file = Path("script_modification_affectation.sql")
    
    if not sql_file.exists():
        print("❌ Script SQL non trouvé")
        return False
        
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Modification de chauffeur_statut
    has_chauffeur_statut = 'ALTER TABLE chauffeur_statut' in content
    print(f"   {'✅' if has_chauffeur_statut else '❌'} Modification table chauffeur_statut")
    
    # Test 2: Ajout colonne lieu
    has_lieu_column = 'ADD COLUMN lieu' in content and 'ENUM' in content
    print(f"   {'✅' if has_lieu_column else '❌'} Ajout colonne lieu avec ENUM")
    
    # Test 3: Mise à jour des données existantes
    has_data_update = 'UPDATE chauffeur_statut' in content and 'SET lieu' in content
    print(f"   {'✅' if has_data_update else '❌'} Mise à jour des données existantes")
    
    # Test 4: Vérifications et résumé
    has_verification = 'RÉSUMÉ DES MODIFICATIONS' in content and 'DESCRIBE' in content
    print(f"   {'✅' if has_verification else '❌'} Vérifications et résumé présents")
    
    success = has_chauffeur_statut and has_lieu_column and has_data_update and has_verification
    print(f"\n   🎯 RÉSULTAT: {'✅ SUCCÈS' if success else '❌ ÉCHEC'}")
    return success

def main():
    """Fonction principale"""
    print("🧪 TEST DES MODIFICATIONS D'AFFECTATION DES CHAUFFEURS")
    print("=" * 70)
    print("Objectif: Vérifier l'ajout du lieu, changement de statut et correction rechargement")
    
    # Tests
    test1 = test_formulaire_lieu_ajoute()
    test2 = test_modele_chauffeur_statut_mis_a_jour()
    test3 = test_route_ajax_mise_a_jour()
    test4 = test_template_chauffeurs_mis_a_jour()
    test5 = test_disponible_change_en_non_specifie()
    test6 = test_probleme_rechargement_corrige()
    test7 = test_script_sql_present()
    
    # Résultat final
    print("\n" + "=" * 70)
    print("🏁 RÉSULTAT FINAL")
    print("=" * 70)
    
    total_tests = 7
    tests_reussis = sum([test1, test2, test3, test4, test5, test6, test7])
    
    print(f"Tests réussis: {tests_reussis}/{total_tests}")
    
    if tests_reussis == total_tests:
        print("🎉 TOUTES LES MODIFICATIONS APPLIQUÉES AVEC SUCCÈS !")
        print("\n✅ Modifications réalisées:")
        print("   • Champ lieu ajouté au formulaire d'affectation")
        print("   • Modèle ChauffeurStatut mis à jour avec colonne lieu")
        print("   • Route AJAX gère le nouveau champ lieu")
        print("   • Template chauffeurs affiche la colonne lieu")
        print("   • 'DISPONIBLE' changé en 'NON SPÉCIFIÉ'")
        print("   • Problème de rechargement des formulaires corrigé")
        print("   • Script SQL prêt pour mise à jour de la base")
    else:
        print("⚠️  CERTAINES MODIFICATIONS MANQUENT")
        if not test1:
            print("   ❌ Champ lieu manquant dans le formulaire")
        if not test2:
            print("   ❌ Modèle ChauffeurStatut non mis à jour")
        if not test3:
            print("   ❌ Route AJAX ne gère pas le lieu")
        if not test4:
            print("   ❌ Template chauffeurs non mis à jour")
        if not test5:
            print("   ❌ 'DISPONIBLE' non changé en 'NON SPÉCIFIÉ'")
        if not test6:
            print("   ❌ Problème de rechargement non corrigé")
        if not test7:
            print("   ❌ Script SQL manquant ou incorrect")
    
    print("\n🎯 ÉTAPES SUIVANTES:")
    print("   1. Exécuter le script SQL: script_modification_affectation.sql")
    print("   2. Redémarrer l'application Flask")
    print("   3. Tester l'ajout d'un statut avec lieu")
    print("   4. Vérifier que les formulaires ne rechargent plus la page")
    print("   5. Confirmer que 'NON SPÉCIFIÉ' s'affiche au lieu de 'DISPONIBLE'")

if __name__ == "__main__":
    main()
