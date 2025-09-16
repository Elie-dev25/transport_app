#!/usr/bin/env python3
"""
Script de démarrage de l'application avec gestion d'erreurs
"""

try:
    print("🚀 Démarrage de l'application Transport UdM...")
    
    from app import create_app
    
    app = create_app()
    
    print("✅ Application créée avec succès")
    print("🌐 Démarrage du serveur sur http://localhost:5000")
    print("\n📋 Comptes de test disponibles:")
    print("   👑 Admin: admin / admin123")
    print("   🏢 Responsable: responsable / responsable123")
    print("   👁️  Superviseur: superviseur / superviseur123")
    print("\n⚠️  Remarque: Les utilisateurs seront créés automatiquement à la première connexion")
    print("💡 Le Responsable a les mêmes permissions que l'Administrateur")
    print("\n🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Solutions possibles:")
    print("1. Vérifiez que MySQL est démarré")
    print("2. Vérifiez la configuration dans app/config.py")
    print("3. Installez les dépendances: pip install -r requirements.txt")
    
    input("\nAppuyez sur Entrée pour quitter...")
