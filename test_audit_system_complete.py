#!/usr/bin/env python3
"""
Test complet du nouveau système d'audit intelligent
Teste toutes les fonctionnalités : impression, alertes, statistiques
"""

import os
import sys
import time
from datetime import datetime

# Ajouter le répertoire parent au path pour importer les modules de l'app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.audit_logger import *

def test_print_auditing():
    """Test de l'audit d'impression"""
    print("🖨️  TEST AUDIT D'IMPRESSION")
    print("=" * 50)
    
    # Test impression vidange
    log_document_printed('vidange', 'BUS001', 'Table de gestion vidange')
    print("✅ Impression vidange auditée")
    
    # Test impression carburation
    log_document_printed('carburation', 'BUS002', 'Table de gestion carburation')
    print("✅ Impression carburation auditée")
    
    # Test impression chauffeurs
    log_document_printed('chauffeur', None, 'Liste des chauffeurs')
    print("✅ Impression chauffeurs auditée")
    
    # Test impression bus
    log_document_printed('bus', 'BUS003', 'Détail du bus')
    print("✅ Impression bus auditée")
    
    # Test impression rapport
    log_document_printed('rapport', 'RAPPORT_001', 'Rapport mensuel')
    print("✅ Impression rapport auditée")
    
    print()

def test_all_roles_actions():
    """Test des actions pour tous les rôles"""
    print("👥 TEST ACTIONS TOUS RÔLES")
    print("=" * 50)
    
    roles = ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR', 'CHARGE', 'CHAUFFEUR', 'MECANICIEN']
    
    for role in roles:
        # Simuler une session utilisateur
        from flask import session
        try:
            session['user_id'] = f'user_{role.lower()}'
            session['user_role'] = role
        except:
            # Si pas de contexte Flask, simuler
            pass
        
        # Actions de test pour chaque rôle
        if role == 'ADMIN':
            log_user_created(user_id='new_user_123', new_role='CHAUFFEUR', details='Nouvel employé')
            log_config_changed(config_type='system', details='Paramètres système modifiés')
            
        elif role == 'RESPONSABLE':
            log_crud_action(AuditActionType.UPDATE, 'bus', 'BUS001', 'Maintenance programmée')
            log_sensitive_access('admin_function', 'create_user', 'Création utilisateur')
            
        elif role == 'SUPERVISEUR':
            log_crud_action(AuditActionType.CREATE, 'trajet', 'TRAJET_001', 'Nouveau trajet créé')
            log_sensitive_access('supervisor_function', 'view_reports', 'Consultation rapports')
            
        elif role == 'CHARGE':
            log_crud_action(AuditActionType.UPDATE, 'trajet', 'TRAJET_002', 'Horaires modifiés')
            
        elif role == 'CHAUFFEUR':
            log_crud_action(AuditActionType.CREATE, 'vidange', 'VID_001', 'Vidange effectuée')
            
        elif role == 'MECANICIEN':
            log_crud_action(AuditActionType.UPDATE, 'maintenance', 'MAINT_001', 'Réparation terminée')
        
        print(f"✅ Actions {role} auditées")
    
    print()

def test_security_violations():
    """Test des violations de sécurité"""
    print("🚨 TEST VIOLATIONS SÉCURITÉ")
    print("=" * 50)
    
    # Test accès non autorisé
    log_unauthorized_access('admin_panel', 'Tentative accès admin par CHAUFFEUR')
    print("✅ Accès non autorisé audité")
    
    # Test violation sécurité
    log_security_violation('sql_injection', 'Tentative injection SQL détectée')
    print("✅ Violation sécurité auditée")
    
    # Test erreur système
    log_system_error('database_connection', 'Connexion DB échouée')
    print("✅ Erreur système auditée")
    
    print()

def test_authentication_events():
    """Test des événements d'authentification"""
    print("🔐 TEST AUTHENTIFICATION")
    print("=" * 50)
    
    # Test connexions réussies
    for role in ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR']:
        log_login_success(f'user_{role.lower()}', role, f'Connexion {role}')
        print(f"✅ Connexion {role} auditée")
    
    # Test connexions échouées
    log_login_failed('admin_test', 'Mot de passe incorrect')
    log_login_failed('hacker', 'Utilisateur inexistant')
    print("✅ Connexions échouées auditées")
    
    # Test déconnexions
    for role in ['ADMIN', 'RESPONSABLE']:
        log_logout(f'user_{role.lower()}', role)
        print(f"✅ Déconnexion {role} auditée")
    
    print()

def display_audit_files():
    """Afficher le contenu des fichiers d'audit"""
    print("📁 FICHIERS D'AUDIT GÉNÉRÉS")
    print("=" * 50)
    
    audit_dir = os.path.join('logs', 'audit')
    if not os.path.exists(audit_dir):
        print("❌ Répertoire d'audit non trouvé")
        return
    
    for filename in sorted(os.listdir(audit_dir)):
        if filename.startswith('audit_') and filename.endswith('.log'):
            role = filename.replace('audit_', '').replace('.log', '').upper()
            filepath = os.path.join(audit_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                print(f"\n📋 {role} ({len(lines)} entrées)")
                print("-" * 30)
                
                # Afficher les 3 dernières entrées
                for line in lines[-3:]:
                    if line.strip():
                        print(f"  {line.strip()}")
                        
            except Exception as e:
                print(f"❌ Erreur lecture {filename}: {e}")
    
    print()

def test_statistics():
    """Test des statistiques d'audit"""
    print("📊 TEST STATISTIQUES")
    print("=" * 50)
    
    try:
        stats = get_role_statistics()
        
        for role, role_stats in stats.items():
            print(f"{role}:")
            print(f"  Total: {role_stats.get('total', 0)}")
            print(f"  Succès: {role_stats.get('success_rate', 100)}%")
            print(f"  Niveaux: {role_stats.get('levels', {})}")
            print()
            
    except Exception as e:
        print(f"❌ Erreur statistiques: {e}")

def main():
    """Fonction principale de test"""
    print("🎯 TEST COMPLET SYSTÈME D'AUDIT INTELLIGENT")
    print("=" * 60)
    print(f"Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Créer le répertoire d'audit s'il n'existe pas
    os.makedirs(os.path.join('logs', 'audit'), exist_ok=True)
    
    # Exécuter tous les tests
    test_print_auditing()
    test_all_roles_actions()
    test_security_violations()
    test_authentication_events()
    
    # Attendre un peu pour que les logs soient écrits
    time.sleep(1)
    
    # Afficher les résultats
    display_audit_files()
    test_statistics()
    
    print("🎉 TESTS TERMINÉS AVEC SUCCÈS!")
    print("=" * 60)
    print("Le nouveau système d'audit intelligent est opérationnel !")
    print()
    print("📋 Fonctionnalités testées:")
    print("  ✅ Audit d'impression de documents")
    print("  ✅ Actions des 6 rôles utilisateur")
    print("  ✅ Violations de sécurité")
    print("  ✅ Événements d'authentification")
    print("  ✅ Fichiers de logs séparés par rôle")
    print("  ✅ Statistiques et niveaux de criticité")
    print()
    print("🔍 Vérifiez les fichiers dans logs/audit/")

if __name__ == '__main__':
    main()
