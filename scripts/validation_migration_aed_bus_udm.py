#!/usr/bin/env python3
"""
Script de validation de la migration AED vers Bus UdM
Vérifie que tous les changements ont été correctement effectués

Usage: python scripts/validation_migration_aed_bus_udm.py
"""

import os
import sys
import glob

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} - MANQUANT")
        return False

def check_file_content(filepath, search_terms, description):
    """Vérifie que certains termes sont présents dans un fichier"""
    if not os.path.exists(filepath):
        print(f"✗ {description}: {filepath} - FICHIER MANQUANT")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing_terms = []
        for term in search_terms:
            if term not in content:
                missing_terms.append(term)
        
        if missing_terms:
            print(f"✗ {description}: {filepath} - Termes manquants: {missing_terms}")
            return False
        else:
            print(f"✓ {description}: {filepath}")
            return True
    except Exception as e:
        print(f"✗ {description}: {filepath} - Erreur: {e}")
        return False

def check_old_references(filepath, old_terms, description):
    """Vérifie qu'aucune ancienne référence n'existe dans un fichier"""
    if not os.path.exists(filepath):
        return True  # Fichier n'existe pas, pas de problème
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        found_old_terms = []
        for term in old_terms:
            if term in content:
                found_old_terms.append(term)
        
        if found_old_terms:
            print(f"⚠️  {description}: {filepath} - Anciennes références trouvées: {found_old_terms}")
            return False
        else:
            print(f"✓ {description}: {filepath} - Pas d'anciennes références")
            return True
    except Exception as e:
        print(f"✗ {description}: {filepath} - Erreur: {e}")
        return False

def main():
    """Fonction principale de validation"""
    print("=" * 60)
    print("VALIDATION DE LA MIGRATION AED VERS BUS UDM")
    print("=" * 60)
    
    success_count = 0
    total_checks = 0
    
    # 1. Vérifier les nouveaux modèles
    print("\n1. VÉRIFICATION DES NOUVEAUX MODÈLES")
    print("-" * 40)
    
    models_to_check = [
        ('app/models/bus_udm.py', ['class BusUdM', 'bus_udm', 'numero_chassis', 'modele', 'type_vehicule', 'marque'], 'Modèle BusUdM'),
        ('app/models/document_bus_udm.py', ['class DocumentBusUdM', 'document_bus_udm', 'numero_bus_udm'], 'Modèle DocumentBusUdM'),
        ('app/models/panne_bus_udm.py', ['class PanneBusUdM', 'panne_bus_udm', 'bus_udm_id'], 'Modèle PanneBusUdM')
    ]
    
    for filepath, terms, desc in models_to_check:
        total_checks += 1
        if check_file_content(filepath, terms, desc):
            success_count += 1
    
    # 2. Vérifier les nouveaux formulaires
    print("\n2. VÉRIFICATION DES FORMULAIRES")
    print("-" * 40)
    
    forms_to_check = [
        ('app/forms/bus_udm_form.py', ['class BusUdMForm', 'Bus UdM', 'UDM-001'], 'Formulaire BusUdM'),
        ('app/forms/panne_form.py', ['numero_bus_udm', 'Bus UdM'], 'Formulaire Panne mis à jour')
    ]
    
    for filepath, terms, desc in forms_to_check:
        total_checks += 1
        if check_file_content(filepath, terms, desc):
            success_count += 1
    
    # 3. Vérifier les templates
    print("\n3. VÉRIFICATION DES TEMPLATES")
    print("-" * 40)
    
    templates_to_check = [
        ('app/templates/bus_udm.html', ['Bus UdM', 'bus_udm_list_ajax', 'UDM-'], 'Template Bus UdM'),
        ('app/templates/depart_bus_udm.html', ['Bus UdM', 'numero_bus_udm'], 'Template Départ Bus UdM'),
        ('app/templates/partials/admin/_add_bus_modal.html', ['bus UdM', 'UDM-'], 'Modal Ajout Bus'),
        ('app/templates/partials/admin/_declaration_panne_modal.html', ['Bus UdM', 'numero_bus_udm'], 'Modal Déclaration Panne')
    ]
    
    for filepath, terms, desc in templates_to_check:
        total_checks += 1
        if check_file_content(filepath, terms, desc):
            success_count += 1
    
    # 4. Vérifier les scripts
    print("\n4. VÉRIFICATION DES SCRIPTS")
    print("-" * 40)
    
    scripts_to_check = [
        ('scripts/migration_aed_vers_bus_udm.sql', ['bus_udm', 'document_bus_udm', 'panne_bus_udm'], 'Script de migration SQL'),
        ('scripts/test_bus_udm_nouveaux_champs.py', ['BusUdM', 'UDM-TEST'], 'Script de test Bus UdM'),
        ('scripts/create_panne_bus_udm_table.py', ['PanneBusUdM', 'panne_bus_udm'], 'Script création table panne')
    ]
    
    for filepath, terms, desc in scripts_to_check:
        total_checks += 1
        if check_file_content(filepath, terms, desc):
            success_count += 1
    
    # 5. Vérifier les routes
    print("\n5. VÉRIFICATION DES ROUTES")
    print("-" * 40)
    
    routes_to_check = [
        ('app/routes/admin/gestion_bus.py', ['from app.models.bus_udm import BusUdM', 'bus_udm_list_ajax'], 'Routes Gestion Bus'),
        ('app/routes/admin/dashboard.py', ['from app.models.bus_udm import BusUdM'], 'Routes Dashboard'),
    ]
    
    for filepath, terms, desc in routes_to_check:
        total_checks += 1
        if check_file_content(filepath, terms, desc):
            success_count += 1
    
    # 6. Vérifier l'absence d'anciennes références
    print("\n6. VÉRIFICATION ABSENCE ANCIENNES RÉFÉRENCES")
    print("-" * 40)
    
    files_to_check_old_refs = [
        ('app/models/bus_udm.py', ['class AED', '__tablename__ = \'aed\''], 'Modèle BusUdM - anciennes refs'),
        ('app/forms/bus_udm_form.py', ['class AEDForm', 'AED-001'], 'Formulaire BusUdM - anciennes refs'),
        ('app/templates/bus_udm.html', ['Bus AED', 'aed_list_ajax'], 'Template Bus UdM - anciennes refs')
    ]
    
    for filepath, old_terms, desc in files_to_check_old_refs:
        total_checks += 1
        if check_old_references(filepath, old_terms, desc):
            success_count += 1
    
    # 7. Vérifier la documentation
    print("\n7. VÉRIFICATION DE LA DOCUMENTATION")
    print("-" * 40)
    
    doc_files = [
        ('MIGRATION_AED_VERS_BUS_UDM.md', ['Bus UdM', 'migration', 'bus_udm'], 'Documentation migration')
    ]
    
    for filepath, terms, desc in doc_files:
        total_checks += 1
        if check_file_content(filepath, terms, desc):
            success_count += 1
    
    # Résumé final
    print("\n" + "=" * 60)
    print("RÉSUMÉ DE LA VALIDATION")
    print("=" * 60)
    
    success_rate = (success_count / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"Tests réussis: {success_count}/{total_checks} ({success_rate:.1f}%)")
    
    if success_count == total_checks:
        print("✅ MIGRATION COMPLÈTE ET VALIDÉE!")
        print("\nProchaines étapes:")
        print("1. Exécuter le script de migration SQL")
        print("2. Redémarrer l'application")
        print("3. Tester les fonctionnalités dans l'interface")
        print("4. Exécuter les tests automatisés")
        return True
    else:
        print("❌ MIGRATION INCOMPLÈTE")
        print(f"\n{total_checks - success_count} problème(s) détecté(s)")
        print("Veuillez corriger les problèmes avant de continuer.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
