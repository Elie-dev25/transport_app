#!/usr/bin/env python3
"""
Script de debug pour identifier le problème
"""

print("🔍 Debug de l'application...")

try:
    print("1. Test d'import de l'application...")
    from app import create_app
    print("   ✅ Import réussi")
    
    print("2. Test de création de l'application...")
    app = create_app()
    print("   ✅ Application créée")
    
    print("3. Test du contexte d'application...")
    with app.app_context():
        print("   ✅ Contexte OK")
        
        print("4. Test de connexion à la base de données...")
        from app.database import db
        
        # Test simple de connexion
        try:
            # Utiliser une requête simple qui fonctionne avec SQLAlchemy 2.x
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
                print("   ✅ Connexion DB réussie")
        except Exception as e:
            print(f"   ❌ Erreur DB: {e}")
            print("   💡 Vérifiez que MySQL est démarré et accessible")
            
        print("5. Test des modèles...")
        try:
            from app.models.utilisateur import Utilisateur
            print("   ✅ Modèles importés")
        except Exception as e:
            print(f"   ❌ Erreur modèles: {e}")
    
    print("\n🎉 Application prête à démarrer!")
    print("💡 Utilisez: python run.py")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
