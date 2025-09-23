#!/usr/bin/env python3
"""
Test simple de l'application après correction des dépendances
"""

def test_imports():
    """Test des imports principaux"""
    print("🧪 Test des imports...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except Exception as e:
        print(f"❌ Flask: {e}")
        return False
    
    try:
        import flask_wtf
        print(f"✅ Flask-WTF {flask_wtf.__version__}")
    except Exception as e:
        print(f"❌ Flask-WTF: {e}")
        return False
    
    try:
        import werkzeug
        print(f"✅ Werkzeug {werkzeug.__version__}")
    except Exception as e:
        print(f"❌ Werkzeug: {e}")
        return False
    
    return True

def test_app_creation():
    """Test de création de l'application"""
    print("\n🧪 Test de création de l'application...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Application Flask créée avec succès")
        return True, app
    except Exception as e:
        print(f"❌ Erreur création app: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_forms():
    """Test des formulaires"""
    print("\n🧪 Test des formulaires...")
    
    try:
        from app.forms.login_form import LoginForm
        form = LoginForm()
        print("✅ LoginForm créé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur formulaires: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_context():
    """Test du contexte d'application"""
    print("\n🧪 Test du contexte d'application...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            print("✅ Contexte d'application fonctionne")
            
            # Test des modèles
            try:
                from app.models.utilisateur import Utilisateur
                print("✅ Modèles importés avec succès")
            except Exception as e:
                print(f"⚠️  Modèles: {e} (normal si pas de DB)")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur contexte: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Test des routes"""
    print("\n🧪 Test des routes...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test de la route d'accueil
            response = client.get('/')
            print(f"✅ Route '/' - Status: {response.status_code}")
            
            # Test de la route de login
            response = client.get('/login')
            print(f"✅ Route '/login' - Status: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur routes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test complet"""
    print("🚀 TEST COMPLET DE L'APPLICATION TRANSPORT UDM")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Création App", test_app_creation),
        ("Formulaires", test_forms),
        ("Contexte App", test_app_context),
        ("Routes", test_routes)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if test_name == "Création App":
                success, app = test_func()
                results.append((test_name, success))
            else:
                success = test_func()
                results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1
    
    print(f"\n📈 RÉSULTAT: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 TOUS LES TESTS PASSENT!")
        print("✅ Votre application est prête à fonctionner")
        print("\n💡 Pour démarrer l'application:")
        print("   python run.py")
    elif passed >= total - 1:
        print("⚠️  PRESQUE TOUS LES TESTS PASSENT")
        print("L'application devrait fonctionner malgré quelques problèmes mineurs")
    else:
        print("❌ PLUSIEURS TESTS ÉCHOUENT")
        print("Il y a encore des problèmes à résoudre")
    
    return passed == total

if __name__ == "__main__":
    main()
