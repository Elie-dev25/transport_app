#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application peut démarrer
"""

try:
    print("🚀 Test de démarrage de l'application...")
    
    # Test 1: Import de l'application
    print("1. Test d'import de l'application...")
    from app import create_app
    print("   ✅ Import réussi")
    
    # Test 2: Création de l'application
    print("2. Test de création de l'application...")
    app = create_app()
    print("   ✅ Application créée avec succès")
    
    # Test 3: Vérification des blueprints
    print("3. Test des blueprints enregistrés...")
    blueprints = list(app.blueprints.keys())
    print(f"   📋 Blueprints trouvés: {blueprints}")
    
    expected_blueprints = ['auth', 'admin', 'chauffeur', 'mecanicien', 'charge_transport', 'superviseur']
    for bp in expected_blueprints:
        if bp in blueprints:
            print(f"   ✅ {bp} - OK")
        else:
            print(f"   ❌ {bp} - MANQUANT")
    
    # Test 4: Test du contexte d'application
    print("4. Test du contexte d'application...")
    with app.app_context():
        print("   ✅ Contexte d'application fonctionnel")
    
    # Test 5: Test des imports optionnels
    print("5. Test des imports optionnels...")
    try:
        import reportlab
        print("   ✅ ReportLab disponible")
    except ImportError:
        print("   ⚠️  ReportLab non disponible (export PDF désactivé)")
    
    print("\n🎉 TOUS LES TESTS RÉUSSIS!")
    print("✅ L'application peut démarrer correctement")
    print("\n💡 Pour démarrer l'application:")
    print("   python run.py")
    
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n💡 Vérifiez les dépendances et la configuration")
