#!/usr/bin/env python3
"""Test simple pour vérifier que l'application fonctionne"""

def test_basic():
    print("=== TEST SIMPLE ===")
    
    # Test 1: Imports
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except Exception as e:
        print(f"❌ Flask: {e}")
        return False
    
    # Test 2: Application
    try:
        from app import create_app
        app = create_app()
        print("✅ Application créée")
    except Exception as e:
        print(f"❌ App: {e}")
        return False
    
    # Test 3: Formulaires
    try:
        from app.forms.login_form import LoginForm
        form = LoginForm()
        print("✅ Formulaires OK")
    except Exception as e:
        print(f"❌ Forms: {e}")
        return False
    
    print("🎉 TOUT FONCTIONNE!")
    return True

if __name__ == "__main__":
    test_basic()
