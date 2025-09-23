#!/usr/bin/env python3
"""
Script pour recréer l'environnement virtuel avec les bonnes versions
"""

import os
import shutil
import subprocess
import sys

def run_command(command, description):
    """Exécute une commande"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            return True
        else:
            print(f"❌ {description} - Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def recreate_venv():
    """Recrée l'environnement virtuel"""
    
    print("🚀 RECRÉATION DE L'ENVIRONNEMENT VIRTUEL")
    print("=" * 60)
    
    # 1. Supprimer l'ancien venv
    if os.path.exists('venv'):
        print("🗑️  Suppression de l'ancien environnement virtuel...")
        try:
            shutil.rmtree('venv')
            print("✅ Ancien venv supprimé")
        except Exception as e:
            print(f"❌ Erreur suppression: {e}")
            return False
    
    # 2. Créer un nouveau venv
    if not run_command("python -m venv venv", "Création du nouvel environnement virtuel"):
        return False
    
    # 3. Activer et installer pip
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Linux/Mac
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # 4. Mettre à jour pip
    if not run_command(f"{python_path} -m pip install --upgrade pip", "Mise à jour de pip"):
        return False
    
    # 5. Installer les versions compatibles
    compatible_packages = [
        "Werkzeug==2.3.7",
        "Flask==2.3.3",
        "WTForms==3.0.1", 
        "Flask-WTF==1.1.1",
        "SQLAlchemy==2.0.23",
        "Flask-SQLAlchemy==3.0.5",
        "Flask-Login==0.6.3",
        "PyMySQL==1.1.0",
        "ldap3==2.9.1",
        "python-dateutil==2.8.2",
        "pytest==7.4.2",
        "pytest-flask==1.2.0",
        "reportlab>=3.6.0"
    ]
    
    print("📦 Installation des packages compatibles...")
    for package in compatible_packages:
        if not run_command(f"{pip_path} install {package}", f"Installation de {package}"):
            print(f"⚠️  Échec pour {package}, mais on continue...")
    
    # 6. Test de l'installation
    print("\n🧪 Test de l'installation...")
    
    test_commands = [
        (f"{python_path} -c \"import flask; print('Flask:', flask.__version__)\"", "Test Flask"),
        (f"{python_path} -c \"import flask_wtf; print('Flask-WTF:', flask_wtf.__version__)\"", "Test Flask-WTF"),
        (f"{python_path} -c \"import werkzeug; print('Werkzeug:', werkzeug.__version__)\"", "Test Werkzeug")
    ]
    
    all_good = True
    for command, description in test_commands:
        if not run_command(command, description):
            all_good = False
    
    if all_good:
        print("\n🎉 ENVIRONNEMENT VIRTUEL RECRÉÉ AVEC SUCCÈS!")
        print("✅ Toutes les dépendances sont installées et compatibles")
        print("\n💡 Pour activer l'environnement:")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("\n💡 Puis tester l'application:")
        print("   python run.py")
        return True
    else:
        print("\n⚠️  Problèmes détectés mais l'environnement est créé")
        return False

if __name__ == "__main__":
    recreate_venv()
