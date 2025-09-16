#!/usr/bin/env python3
"""
Script de démarrage simple pour l'application
"""

if __name__ == "__main__":
    try:
        print("🚀 Démarrage de l'application Transport UdM...")
        
        from app import create_app
        app = create_app()
        
        print("✅ Application créée avec succès")
        print("🌐 Serveur démarré sur http://localhost:5000")
        print("\n📋 Comptes de test disponibles:")
        print("   👑 Admin: admin / admin123")
        print("   👁️  Superviseur: superviseur / superviseur123")
        print("\n🔗 URLs importantes:")
        print("   - Admin: http://localhost:5000/admin/dashboard")
        print("   - Superviseur: http://localhost:5000/superviseur/dashboard")
        print("\n🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
        print("=" * 60)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Solutions possibles:")
        print("1. Vérifiez que MySQL est démarré")
        print("2. Vérifiez la configuration dans app/config.py")
        print("3. Installez les dépendances: pip install -r requirements.txt")
        
        input("\nAppuyez sur Entrée pour quitter...")
