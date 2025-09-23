#!/usr/bin/env python3
"""
Script de nettoyage des fichiers inutiles dans l'application TransportUdM
Supprime tous les fichiers temporaires, de test, de debug et de documentation obsolète
"""

import os
import shutil
from pathlib import Path

def supprimer_fichiers_inutiles():
    """Supprime tous les fichiers inutiles identifiés"""
    
    print("🧹 NETTOYAGE DES FICHIERS INUTILES")
    print("=" * 60)
    
    # 1. FICHIERS MARKDOWN DE DOCUMENTATION OBSOLÈTE
    fichiers_md_obsoletes = [
        "ADAPTATION_NOUVELLE_ARCHITECTURE_COMPLETE.md",
        "AMELIORATIONS_DESIGN_RAPPORT_ENTITY.md",
        "AMELIORATIONS_FICHE_BUS_COMPLETE.md",
        "AMELIORATIONS_FINALES.md",
        "AMELIORATIONS_FINALES_FICHE_BUS.md",
        "AMELIORATIONS_PAGE_CHAUFFEURS.md",
        "AMELIORATIONS_PAGE_RAPPORTS_COMPLETE.md",
        "AMELIORATIONS_RAPPORT_ENTITY.md",
        "AMELIORATION_DESIGN_DEPANNAGE.md",
        "AUDIT_RESPONSIVITE_COMPLET.md",
        "BACKEND_MISE_A_JOUR_FINALE.md",
        "CORRECTIONS_BUS_DETAILS_ET_ICONES.md",
        "CORRECTIONS_FINALES.md",
        "CORRECTIONS_FINALES_CHAUFFEUR.md",
        "CORRECTIONS_FINALES_FICHE_BUS.md",
        "CORRECTIONS_POSITIONNEMENT_FINAL.md",
        "CORRECTIONS_ROUTES_RESPONSABLE.md",
        "CORRECTIONS_STATUT_STATIQUE.md",
        "CORRECTIONS_TITRES_ET_MENTIONS.md",
        "CORRECTIONS_TITRES_ET_TRAJETS.md",
        "CORRECTION_AFFICHAGE_HTML_MACROS.md",
        "CORRECTION_ARCHITECTURE_FINALE.md",
        "CORRECTION_DASHBOARD_CHAUFFEUR.md",
        "CORRECTION_ENTITY_NAME_ERROR.md",
        "CORRECTION_ERREUR_JINJA.md",
        "CORRECTION_ERREUR_PANNES_BUS.md",
        "CORRECTION_ESPACEMENT_SIDEBAR.md",
        "CORRECTION_FILTRES_ACTIFS_RAPPORTS.md",
        "CORRECTION_FINALE_COMPLETE.md",
        "CORRECTION_FOND_SECTIONS.md",
        "CORRECTION_LISTE_BUS.md",
        "CORRECTION_PAGE_CHAUFFEURS.md",
        "CORRECTION_PARTIALS_FINALE.md",
        "CORRECTION_PROFIL_SIDEBAR_RAPPORT_ENTITY.md",
        "CORRECTION_RAPPORTS_SUPERVISEUR.md",
        "CORRECTION_ROUTE_ADMIN_FINALE.md",
        "CORRECTION_SIDEBAR_CHAUFFEURS.md",
        "CORRECTION_TEMPLATES_BASE.md",
        "CORRECTION_TEMPLATE_DEPANNAGE.md",
        "CORRECTION_TYPE_VEHICULE_ERROR.md",
        "CORRECTION_UNDEFINED_FORMAT_ERROR.md",
        "CORRECTION_UTILISATEURS_FINALE.md",
        "CREATION_RAPPORT_ENTITY_CSS.md",
        "DASHBOARD_CHAUFFEUR_FINAL.md",
        "DASHBOARD_CHAUFFEUR_SIMPLIFIE.md",
        "DASHBOARD_RESPONSABLE_FINAL.md",
        "DASHBOARD_RESPONSABLE_IDENTIQUE.md",
        "DESIGN_FINAL_SIMPLIFIE.md",
        "DESIGN_RAPPORT_ENTITY_AMELIORE.md",
        "DIAGNOSTIC_LOGIN_CSS.md",
        "FONCTIONNALITES_IMPRESSION_CHAUFFEURS.md",
        "GUIDE_CONFIGURATION_DB.md",
        "GUIDE_DEPANNAGE_BOUTON.md",
        "IMPLEMENTATION_NOTIFICATIONS_RESUME.md",
        "IMPLEMENTATION_ROLE_RESPONSABLE.md",
        "IMPLEMENTATION_ROLE_SUPERVISEUR.md",
        "MIGRATION_AED_VERS_BUS_UDM.md",
        "MIGRATION_COMPLETE_RAPPORT.md",
        "MODIFICATIONS_AED_NOUVEAUX_CHAMPS.md",
        "MODIFICATIONS_TOP_BAR.md",
        "MODIFICATION_TRAFIC_ETUDIANT_SUPERVISEUR.md",
        "NOTIFICATIONS_EMAIL_GUIDE.md",
        "NOUVEAU_STYLE_STATUT_CHAUFFEUR.md",
        "OPTIMISATION_FILTRES_RAPPORTS.md",
        "OPTIMISATION_GRANDS_ECRANS.md",
        "PLAN_REFACTORISATION_TEMPLATES_SUPERVISEUR.md",
        "POSITIONNEMENT_FINAL_CORRECT.md",
        "RAPPORT_CORRECTIONS_BACKEND.md",
        "RAPPORT_IMPLEMENTATION.md",
        "REFACTORISATION_TEMPLATES_COMPLETE.md",
        "REPOSITIONNEMENT_BOUTON_CHAUFFEURS.md",
        "RESOLUTION_COMPLETE_BUS_ETAT.md",
        "RESTRUCTURATION_ARCHITECTURE_COMPLETE.md",
        "RESUME_MIGRATION_COMPLETE.md",
        "SEPARATION_SECTIONS_DASHBOARD.md",
        "SEPARATION_TRAJETS_DASHBOARD_SUPERVISEUR.md",
        "SOLUTION_RESPONSABLE_OPTIMALE.md",
        "STATS_CHAUFFEUR_REELLES.md",
        "SUPPRESSION_SECTIONS_MODE_CONSULTATION.md",
        "TABLEAUX_UNIFIES_RESUME.md",
        "VERIFICATION_EXHAUSTIVE_FINALE.md",
        "resume_final_6_roles.md"
    ]
    
    # 2. FICHIERS PYTHON DE TEST ET DEBUG
    fichiers_python_test = [
        "analyse_complete_6_roles.py",
        "check_database.py",
        "check_db_structure.py",
        "check_emails.py",
        "correction_complete_templates.py",
        "create_charge_user.py",
        "create_chauffeur_test.py",
        "create_responsable_user.py",
        "create_superviseur_user.py",
        "create_test_data.py",
        "create_test_user.py",
        "create_user_simple.py",
        "debug_app.py",
        "debug_dashboard_chauffeur.py",
        "debug_panne.py",
        "debug_routes_conflicts.py",
        "debug_sidebar.py",
        "diagnostic_complet.py",
        "diagnostic_dashboard_chauffeur.py",
        "diagnostic_declaration.py",
        "diagnostic_liaison_chauffeur.py",
        "fix_bus_etat_vehicule.py",
        "fix_existing_mecanicien.py",
        "fix_user_emails.py",
        "generer_hash_mot_de_passe.py",
        "nettoyer_trajets_test.py",
        "optimisations_performance.py",
        "quick_test.py",
        "recherche_references_partials.py",
        "set_env.py",
        "simple_db_check.py",
        "start_and_test.py",
        "start_app.py",
        "start_debug.py",
        "start_server.py"
    ]
    
    # 3. FICHIERS DE TEST SPÉCIFIQUES
    fichiers_test_specifiques = [
        f for f in os.listdir('.') 
        if f.startswith('test_') and f.endswith('.py')
    ]
    
    # 4. FICHIERS DIVERS
    fichiers_divers = [
        "routes_check.txt",
        "test_curl.txt",
        "test_output.txt",
        "test_results.txt",
        "backup_avant_migration.sql",
        "backup_before_superviseur.sql",
        "script_modification_affectation.sql",
        "script_xampp_responsable.sql",
        "script_xampp_responsable_final.sql",
        "configure_email.ps1",
        "configure_email.sh",
        "test_bouton_declaration.html",
        "verification_backend_finale.py",
        "verification_exhaustive_templates.py",
        "verification_finale_complete.py",
        "verification_finale_responsable.py",
        "verification_partials_finale.py",
        "verification_routes_admin.py",
        "verification_routes_complete.py",
        "verification_routes_templates.py",
        "verify_templates.py"
    ]
    
    # Combiner tous les fichiers à supprimer
    tous_fichiers_a_supprimer = (
        fichiers_md_obsoletes + 
        fichiers_python_test + 
        fichiers_test_specifiques + 
        fichiers_divers
    )
    
    print(f"📋 {len(tous_fichiers_a_supprimer)} fichiers identifiés pour suppression")
    
    # Supprimer les fichiers
    fichiers_supprimes = 0
    fichiers_non_trouves = 0
    
    for fichier in tous_fichiers_a_supprimer:
        if os.path.exists(fichier):
            try:
                os.remove(fichier)
                print(f"   ✅ {fichier}")
                fichiers_supprimes += 1
            except Exception as e:
                print(f"   ❌ {fichier} - Erreur: {e}")
        else:
            fichiers_non_trouves += 1
    
    print(f"\n📊 RÉSULTATS:")
    print(f"   ✅ {fichiers_supprimes} fichiers supprimés")
    print(f"   ⚠️  {fichiers_non_trouves} fichiers non trouvés")
    
    return fichiers_supprimes

def supprimer_dossiers_inutiles():
    """Supprime les dossiers inutiles"""
    
    print("\n\n📁 SUPPRESSION DES DOSSIERS INUTILES")
    print("=" * 60)
    
    # Dossiers à supprimer
    dossiers_a_supprimer = [
        "venv",  # Environnement virtuel (peut être recréé)
        "instance",  # Base SQLite de test
        "docs",  # Documentation PlantUML obsolète
        "tests",  # Tests obsolètes
        "scripts/__pycache__"  # Cache Python dans scripts
    ]
    
    dossiers_supprimes = 0
    
    for dossier in dossiers_a_supprimer:
        if os.path.exists(dossier):
            try:
                if os.path.isdir(dossier):
                    shutil.rmtree(dossier)
                    print(f"   ✅ {dossier}/ (dossier complet)")
                    dossiers_supprimes += 1
                else:
                    os.remove(dossier)
                    print(f"   ✅ {dossier}")
                    dossiers_supprimes += 1
            except Exception as e:
                print(f"   ❌ {dossier} - Erreur: {e}")
        else:
            print(f"   ⚠️  {dossier} - Non trouvé")
    
    print(f"\n📊 {dossiers_supprimes} dossiers supprimés")
    
    return dossiers_supprimes

def nettoyer_cache_python():
    """Supprime tous les fichiers cache Python"""
    
    print("\n\n🐍 NETTOYAGE DU CACHE PYTHON")
    print("=" * 60)
    
    cache_supprimes = 0
    
    # Supprimer tous les dossiers __pycache__
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"   ✅ {pycache_path}")
                cache_supprimes += 1
            except Exception as e:
                print(f"   ❌ {pycache_path} - Erreur: {e}")
    
    # Supprimer les fichiers .pyc individuels
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"   ✅ {pyc_path}")
                    cache_supprimes += 1
                except Exception as e:
                    print(f"   ❌ {pyc_path} - Erreur: {e}")
    
    print(f"\n📊 {cache_supprimes} éléments de cache supprimés")
    
    return cache_supprimes

def main():
    """Fonction principale de nettoyage"""
    
    print("🚀 NETTOYAGE COMPLET DE L'APPLICATION TRANSPORT UDM")
    print("=" * 80)
    
    # Exécution automatique sans confirmation pour le nettoyage
    print("\n🚀 DÉMARRAGE DU NETTOYAGE AUTOMATIQUE...")
    print("   • Tous les fichiers de documentation obsolète (.md)")
    print("   • Tous les fichiers de test et debug (.py)")
    print("   • Tous les dossiers temporaires (venv, docs, tests, etc.)")
    print("   • Tout le cache Python (__pycache__, .pyc)")
    
    # Effectuer le nettoyage
    fichiers_supprimes = supprimer_fichiers_inutiles()
    dossiers_supprimes = supprimer_dossiers_inutiles()
    cache_supprimes = nettoyer_cache_python()
    
    # Résumé final
    print("\n\n🎉 NETTOYAGE TERMINÉ")
    print("=" * 80)
    print(f"📊 RÉSUMÉ TOTAL:")
    print(f"   • {fichiers_supprimes} fichiers supprimés")
    print(f"   • {dossiers_supprimes} dossiers supprimés")
    print(f"   • {cache_supprimes} éléments de cache supprimés")
    
    total_supprimes = fichiers_supprimes + dossiers_supprimes + cache_supprimes
    print(f"   🗑️  TOTAL: {total_supprimes} éléments supprimés")
    
    print("\n✅ Votre application est maintenant propre et optimisée!")
    print("💡 Vous pouvez recréer l'environnement virtuel avec: python -m venv venv")

if __name__ == "__main__":
    main()
