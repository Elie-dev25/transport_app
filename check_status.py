#!/usr/bin/env python3
"""Vérification du statut de l'application - écrit dans un fichier"""

import sys
import traceback

def check_status():
    results = []
    
    # Test Flask
    try:
        import flask
        results.append(f"✅ Flask {flask.__version__}")
    except Exception as e:
        results.append(f"❌ Flask: {e}")
    
    # Test Flask-WTF
    try:
        import flask_wtf
        results.append(f"✅ Flask-WTF {flask_wtf.__version__}")
    except Exception as e:
        results.append(f"❌ Flask-WTF: {e}")
    
    # Test Werkzeug
    try:
        import werkzeug
        results.append(f"✅ Werkzeug {werkzeug.__version__}")
    except Exception as e:
        results.append(f"❌ Werkzeug: {e}")
    
    # Test Application
    try:
        from app import create_app
        app = create_app()
        results.append("✅ Application créée avec succès")
    except Exception as e:
        results.append(f"❌ Application: {e}")
        results.append(f"Traceback: {traceback.format_exc()}")
    
    # Test Formulaires
    try:
        from app.forms.login_form import LoginForm
        form = LoginForm()
        results.append("✅ Formulaires fonctionnent")
    except Exception as e:
        results.append(f"❌ Formulaires: {e}")
        results.append(f"Traceback: {traceback.format_exc()}")
    
    # Écrire les résultats
    with open('status_check.txt', 'w', encoding='utf-8') as f:
        f.write("=== VÉRIFICATION DU STATUT DE L'APPLICATION ===\n\n")
        for result in results:
            f.write(result + "\n")
        f.write("\n=== FIN DE LA VÉRIFICATION ===\n")
    
    # Aussi afficher sur stdout
    for result in results:
        print(result)

if __name__ == "__main__":
    check_status()
