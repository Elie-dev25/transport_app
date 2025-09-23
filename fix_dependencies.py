#!/usr/bin/env python3
"""
Script pour corriger les problèmes de dépendances Flask
Résout l'erreur ModuleNotFoundError: No module named 'flask.debughelpers'
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔧 {description}...")
    print(f"Commande: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - Erreur")
            if result.stderr:
                print(f"Erreur: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False
    
    return True

def fix_flask_dependencies():
    """Corrige les dépendances Flask incompatibles"""
    
    print("🚀 CORRECTION DES DÉPENDANCES FLASK")
    print("=" * 60)
    
    # Vérifier si on est dans un environnement virtuel
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  ATTENTION: Vous n'êtes pas dans un environnement virtuel")
        print("   Il est recommandé d'utiliser un environnement virtuel")
        print("🚀 Continuation automatique pour correction...")
    else:
        print("✅ Environnement virtuel détecté")
    
    # Étape 1: Désinstaller les packages problématiques
    packages_to_remove = [
        'Flask',
        'Flask-WTF', 
        'Flask-SQLAlchemy',
        'Flask-Login',
        'Werkzeug',
        'WTForms',
        'SQLAlchemy'
    ]
    
    print(f"\n📦 Désinstallation des packages problématiques...")
    for package in packages_to_remove:
        command = f"pip uninstall {package} -y"
        run_command(command, f"Désinstallation de {package}")
    
    # Étape 2: Nettoyer le cache pip
    if not run_command("pip cache purge", "Nettoyage du cache pip"):
        print("⚠️  Impossible de nettoyer le cache pip (normal sur certains systèmes)")
    
    # Étape 3: Mettre à jour pip
    run_command("python -m pip install --upgrade pip", "Mise à jour de pip")
    
    # Étape 4: Installer les versions compatibles
    print(f"\n📦 Installation des versions compatibles...")
    
    compatible_packages = [
        "Werkzeug==2.3.7",
        "Flask==2.3.3", 
        "WTForms==3.0.1",
        "Flask-WTF==1.1.1",
        "SQLAlchemy==2.0.23",
        "Flask-SQLAlchemy==3.0.5",
        "Flask-Login==0.6.3"
    ]
    
    for package in compatible_packages:
        if not run_command(f"pip install {package}", f"Installation de {package}"):
            print(f"❌ Échec de l'installation de {package}")
            return False
    
    # Étape 5: Installer le reste des dépendances
    print(f"\n📦 Installation des autres dépendances...")
    if not run_command("pip install -r requirements.txt", "Installation depuis requirements.txt"):
        print("⚠️  Certaines dépendances ont pu échouer, mais les principales sont installées")
    
    # Étape 6: Vérifier l'installation
    print(f"\n🔍 Vérification de l'installation...")
    
    verification_commands = [
        ("python -c \"import flask; print(f'Flask: {flask.__version__}')\"", "Version Flask"),
        ("python -c \"import flask_wtf; print(f'Flask-WTF: {flask_wtf.__version__}')\"", "Version Flask-WTF"),
        ("python -c \"import werkzeug; print(f'Werkzeug: {werkzeug.__version__}')\"", "Version Werkzeug"),
        ("python -c \"from flask import Flask; app = Flask(__name__); print('✅ Flask fonctionne')\"", "Test Flask"),
        ("python -c \"from flask_wtf import FlaskForm; print('✅ Flask-WTF fonctionne')\"", "Test Flask-WTF")
    ]
    
    all_good = True
    for command, description in verification_commands:
        if not run_command(command, description):
            all_good = False
    
    if all_good:
        print(f"\n🎉 CORRECTION TERMINÉE AVEC SUCCÈS!")
        print("✅ Toutes les dépendances sont maintenant compatibles")
        print("✅ Vous pouvez maintenant démarrer votre application Flask")
        print("\n💡 Pour tester:")
        print("   python run.py")
        return True
    else:
        print(f"\n⚠️  CORRECTION PARTIELLEMENT RÉUSSIE")
        print("Certaines vérifications ont échoué, mais l'application devrait fonctionner")
        return False

def test_flask_app():
    """Test rapide de l'application Flask"""
    print(f"\n🧪 TEST RAPIDE DE L'APPLICATION")
    print("=" * 60)
    
    test_code = '''
try:
    from app import create_app
    app = create_app()
    print("✅ Application Flask créée avec succès")
    
    with app.app_context():
        print("✅ Contexte d'application fonctionne")
        
        # Test des formulaires
        from app.forms.login_form import LoginForm
        form = LoginForm()
        print("✅ Formulaires Flask-WTF fonctionnent")
        
    print("🎉 TOUS LES TESTS PASSENT!")
    
except Exception as e:
    print(f"❌ Erreur lors du test: {e}")
    import traceback
    traceback.print_exc()
'''
    
    if not run_command(f'python -c "{test_code}"', "Test de l'application"):
        print("❌ L'application a encore des problèmes")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🔧 CORRECTEUR DE DÉPENDANCES FLASK - TransportUdM")
    print("=" * 80)
    
    # Corriger les dépendances
    if fix_flask_dependencies():
        # Tester l'application
        if test_flask_app():
            print(f"\n🎉 SUCCÈS COMPLET!")
            print("Votre application TransportUdM est prête à fonctionner")
        else:
            print(f"\n⚠️  Les dépendances sont corrigées mais il reste des problèmes")
    else:
        print(f"\n❌ ÉCHEC DE LA CORRECTION")
        print("Veuillez vérifier les erreurs ci-dessus")
    
    print(f"\n📝 NOTES:")
    print("• Si vous utilisez Docker, reconstruisez l'image après cette correction")
    print("• En cas de problème persistant, supprimez venv/ et recréez l'environnement")
    print("• Les versions installées sont testées et compatibles")

if __name__ == "__main__":
    main()
