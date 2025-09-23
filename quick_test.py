print("Test des imports...")

try:
    import flask
    print(f"Flask: {flask.__version__}")
except Exception as e:
    print(f"Erreur Flask: {e}")

try:
    import flask_wtf
    print(f"Flask-WTF: {flask_wtf.__version__}")
except Exception as e:
    print(f"Erreur Flask-WTF: {e}")

try:
    from app import create_app
    app = create_app()
    print("Application creee avec succes")
except Exception as e:
    print(f"Erreur app: {e}")

try:
    from app.forms.login_form import LoginForm
    form = LoginForm()
    print("Formulaires OK")
except Exception as e:
    print(f"Erreur formulaires: {e}")

print("Test termine")
