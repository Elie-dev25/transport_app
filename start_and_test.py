#!/usr/bin/env python3
"""
Script pour démarrer l'application et tester les routes superviseur
"""

if __name__ == "__main__":
    try:
        print("🚀 Démarrage de l'application Transport UdM...")
        print("📋 Routes superviseur disponibles:")
        print("   • http://localhost:5000/superviseur/dashboard")
        print("   • http://localhost:5000/superviseur/carburation")
        print("   • http://localhost:5000/superviseur/bus-udm")
        print("   • http://localhost:5000/superviseur/vidanges")
        print("   • http://localhost:5000/superviseur/chauffeurs")
        print("   • http://localhost:5000/superviseur/utilisateurs")
        print("   • http://localhost:5000/superviseur/rapports")
        print()
        print("🔐 Connexion superviseur:")
        print("   Login: superviseur")
        print("   Mot de passe: superviseur123")
        print()
        print("🛑 Appuyez sur Ctrl+C pour arrêter")
        print("=" * 60)
        
        from app import create_app
        app = create_app()
        
        # Test rapide des routes avant démarrage
        with app.app_context():
            print("✅ Application créée avec succès")
            
            # Vérifier que les routes existent
            routes_superviseur = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint.startswith('superviseur.'):
                    routes_superviseur.append(rule.rule)
            
            print(f"✅ {len(routes_superviseur)} routes superviseur enregistrées")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print("\n💡 Solutions possibles:")
        print("1. Vérifiez que MySQL est démarré")
        print("2. Vérifiez la configuration dans app/config.py")
        print("3. Installez les dépendances: pip install -r requirements.txt")
        
        input("\nAppuyez sur Entrée pour quitter...")
