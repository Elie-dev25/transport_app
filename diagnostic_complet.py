#!/usr/bin/env python3
"""
Script de diagnostic complet pour l'application Transport UdM
Identifie tous les problèmes potentiels
"""

import os
import sys
import subprocess
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_environment():
    """Vérifier l'environnement Python et les dépendances"""
    print_section("ENVIRONNEMENT PYTHON")
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Vérifier l'environnement virtuel
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Environnement virtuel activé")
    else:
        print("⚠️  Environnement virtuel non activé")
        print("💡 Activez avec: venv\\Scripts\\activate (Windows) ou source venv/bin/activate (Linux/Mac)")
    
    # Vérifier les dépendances critiques
    critical_packages = ['flask', 'sqlalchemy', 'pymysql', 'wtforms']
    missing_packages = []
    
    for package in critical_packages:
        try:
            __import__(package)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Installez les dépendances manquantes:")
        print(f"   pip install {' '.join(missing_packages)}")
        print(f"   ou: pip install -r requirements.txt")
    
    return len(missing_packages) == 0

def check_file_structure():
    """Vérifier la structure des fichiers"""
    print_section("STRUCTURE DES FICHIERS")
    
    critical_files = [
        'app/__init__.py',
        'app/config.py',
        'app/models/utilisateur.py',
        'app/routes/auth.py',
        'requirements.txt',
        'run.py'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} manquant")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_database_config():
    """Vérifier la configuration de la base de données"""
    print_section("CONFIGURATION BASE DE DONNÉES")
    
    try:
        # Lire le fichier de config
        with open('app/config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        if 'mysql+pymysql://root:@localhost/transport_udm' in config_content:
            print("✅ Configuration MySQL trouvée")
            print("📋 Base de données: transport_udm")
            print("📋 Serveur: localhost")
            print("📋 Utilisateur: root (sans mot de passe)")
        else:
            print("⚠️  Configuration de base de données non standard")
        
        # Vérifier si la base de données SQLite existe (fallback)
        if os.path.exists('instance/transport_udm.db'):
            print("✅ Base de données SQLite trouvée: instance/transport_udm.db")
        else:
            print("⚠️  Base de données SQLite non trouvée")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la configuration: {e}")
        return False

def check_templates():
    """Vérifier les templates critiques"""
    print_section("TEMPLATES CRITIQUES")
    
    template_dirs = [
        'app/templates/auth',
        'app/templates/roles/admin',
        'app/templates/roles/superviseur',
        'app/templates/shared/macros'
    ]
    
    issues = []
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            files = list(Path(template_dir).glob('*.html'))
            print(f"✅ {template_dir} ({len(files)} fichiers)")
        else:
            print(f"❌ {template_dir} manquant")
            issues.append(template_dir)
    
    return len(issues) == 0

def check_static_files():
    """Vérifier les fichiers statiques"""
    print_section("FICHIERS STATIQUES")
    
    static_dirs = [
        'app/static/css',
        'app/static/js',
        'app/static/img'
    ]
    
    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            files = list(Path(static_dir).rglob('*.*'))
            print(f"✅ {static_dir} ({len(files)} fichiers)")
        else:
            print(f"⚠️  {static_dir} manquant")

def main():
    """Fonction principale de diagnostic"""
    print("🚀 DIAGNOSTIC COMPLET - APPLICATION TRANSPORT UDM")
    print("=" * 60)
    
    # Tests
    env_ok = check_environment()
    files_ok = check_file_structure()
    db_ok = check_database_config()
    templates_ok = check_templates()
    check_static_files()
    
    # Résumé
    print_section("RÉSUMÉ DU DIAGNOSTIC")
    
    if env_ok and files_ok and db_ok and templates_ok:
        print("🎉 DIAGNOSTIC RÉUSSI!")
        print("✅ L'application devrait pouvoir démarrer")
        print("\n💡 Pour démarrer l'application:")
        print("   1. Activez l'environnement virtuel si nécessaire")
        print("   2. python run.py")
    else:
        print("⚠️  PROBLÈMES DÉTECTÉS")
        print("❌ Corrigez les erreurs ci-dessus avant de démarrer l'application")
        
        if not env_ok:
            print("\n🔧 PRIORITÉ 1: Installer les dépendances")
            print("   pip install -r requirements.txt")
        
        if not files_ok:
            print("\n🔧 PRIORITÉ 2: Vérifier les fichiers manquants")
        
        if not db_ok:
            print("\n🔧 PRIORITÉ 3: Configurer la base de données")

if __name__ == "__main__":
    main()
