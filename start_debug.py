#!/usr/bin/env python3
"""
Script de démarrage avec debug détaillé
"""

import os
import sys

# Configuration pour le développement
os.environ['FLASK_ENV'] = 'development'

print("🚀 DÉMARRAGE DEBUG - Transport UdM")
print("=" * 50)

try:
    print("1. Configuration de l'environnement...")
    print(f"   - FLASK_ENV: {os.environ.get('FLASK_ENV', 'non défini')}")
    print(f"   - Python: {sys.version}")
    print(f"   - Répertoire: {os.getcwd()}")
    
    print("\n2. Import de l'application...")
    from app import create_app
    print("   ✅ Import réussi")
    
    print("\n3. Création de l'application...")
    app = create_app()
    print("   ✅ Application créée")
    print(f"   - Config DB: {app.config.get('SQLALCHEMY_DATABASE_URI', 'non définie')}")
    print(f"   - Debug: {app.config.get('DEBUG', False)}")
    
    print("\n4. Test du contexte d'application...")
    with app.app_context():
        print("   ✅ Contexte OK")
        
        print("\n5. Test de la base de données...")
        from app.database import db
        
        # Test simple de connexion
        try:
            from app.models.utilisateur import Utilisateur
            user_count = Utilisateur.query.count()
            print(f"   ✅ Base de données OK - {user_count} utilisateurs")
        except Exception as db_error:
            print(f"   ⚠️  Erreur DB: {db_error}")
    
    print("\n6. Démarrage du serveur...")
    print("   🌐 Serveur sur http://localhost:5000")
    print("   🛑 Ctrl+C pour arrêter")
    print("=" * 50)
    
    # Démarrer le serveur
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False  # Éviter les problèmes de rechargement
    )
    
except Exception as e:
    print(f"\n❌ ERREUR CRITIQUE: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Solutions possibles:")
    print("1. Vérifiez que l'environnement virtuel est activé")
    print("2. Installez les dépendances: pip install -r requirements.txt")
    print("3. Vérifiez la base de données SQLite")
    
    input("\nAppuyez sur Entrée pour quitter...")
