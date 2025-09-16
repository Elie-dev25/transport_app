#!/usr/bin/env python3
"""
Script pour définir l'environnement de l'application
Utilise la nouvelle configuration centralisée
"""

import os
import sys

def set_environment(env_name):
    """Définit l'environnement Flask"""
    valid_envs = ['default', 'development', 'production', 'testing']
    
    if env_name not in valid_envs:
        print(f"Environnement invalide: {env_name}")
        print(f"Environnements valides: {', '.join(valid_envs)}")
        return False
    
    # Définir la variable d'environnement
    os.environ['FLASK_ENV'] = env_name
    
    print(f"Environnement défini: {env_name}")
    
    # Afficher la configuration qui sera utilisée
    if env_name == 'production':
        print("Configuration: ProductionConfig")
        print("  - Base de données: transport_udm (production)")
        print("  - Debug: False")
        print("  - Sécurité: Renforcée")
    elif env_name == 'development':
        print("Configuration: DevelopmentConfig")
        print("  - Base de données: transport_udm (même que production)")
        print("  - Debug: True")
        print("  - CSRF: Désactivé")
    elif env_name == 'testing':
        print("Configuration: TestingConfig")
        print("  - Base de données: SQLite en mémoire")
        print("  - Testing: True")
    else:
        print("Configuration: Config (par défaut)")
        print("  - Base de données: transport_udm")
        print("  - Debug: False")
    
    return True

def show_current_config():
    """Affiche la configuration actuelle"""
    print("CONFIGURATION ACTUELLE")
    print("=" * 40)
    
    # Importer et créer l'app pour voir la config
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'non défini')}")
            print(f"DEBUG: {app.config.get('DEBUG')}")
            print(f"ENV: {app.config.get('ENV')}")
            print(f"DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print(f"SECRET_KEY: {'***' if app.config.get('SECRET_KEY') else 'Non défini'}")
            print(f"WTF_CSRF_ENABLED: {app.config.get('WTF_CSRF_ENABLED')}")
            
    except Exception as e:
        print(f"Erreur lors de la lecture de la configuration: {e}")

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("GESTIONNAIRE D'ENVIRONNEMENT - Transport UdM")
        print("=" * 50)
        print("Usage:")
        print("  python set_env.py <environnement>")
        print("  python set_env.py show")
        print("")
        print("Environnements disponibles:")
        print("  default     - Configuration par défaut (recommandé)")
        print("  development - Configuration de développement")
        print("  production  - Configuration de production")
        print("  testing     - Configuration de test")
        print("")
        print("Exemples:")
        print("  python set_env.py default")
        print("  python set_env.py show")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'show':
        show_current_config()
    elif command in ['default', 'development', 'production', 'testing']:
        if set_environment(command):
            print("\nPour appliquer les changements:")
            print("1. Redémarrez l'application Flask")
            print("2. Ou définissez la variable dans votre terminal:")
            if os.name == 'nt':  # Windows
                print(f"   set FLASK_ENV={command}")
            else:  # Unix/Linux/Mac
                print(f"   export FLASK_ENV={command}")
    else:
        print(f"Commande inconnue: {command}")
        print("Utilisez 'python set_env.py' pour voir l'aide")

if __name__ == "__main__":
    main()
