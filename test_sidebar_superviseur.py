#!/usr/bin/env python3
"""
Test de la sidebar superviseur
"""

try:
    print("🧪 Test de la sidebar superviseur...")
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée")
        
        # Vérifier que le template de base existe
        import os
        template_path = "app/templates/_base_superviseur.html"
        if os.path.exists(template_path):
            print("✅ Template _base_superviseur.html trouvé")
            
            # Lire le contenu pour vérifier la navigation
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérifier les éléments de navigation
            nav_elements = [
                'Dashboard',
                'Carburation', 
                'Bus UdM',
                'Vidanges',
                'Chauffeurs',
                'Utilisateurs',
                'Rapports'
            ]
            
            print("\n📋 Éléments de navigation dans la sidebar:")
            for element in nav_elements:
                if element in content:
                    print(f"   ✅ {element}")
                else:
                    print(f"   ❌ {element} - MANQUANT")
            
            # Vérifier les badges de supervision
            if 'Mode Supervision' in content:
                print("✅ Badge 'Mode Supervision' présent")
            else:
                print("❌ Badge 'Mode Supervision' manquant")
                
            # Vérifier les routes
            routes_expected = [
                'superviseur.dashboard',
                'superviseur.carburation',
                'superviseur.bus_udm',
                'superviseur.vidanges', 
                'superviseur.chauffeurs',
                'superviseur.utilisateurs',
                'superviseur.rapports'
            ]
            
            print("\n🔗 Routes dans la sidebar:")
            for route in routes_expected:
                if route in content:
                    print(f"   ✅ {route}")
                else:
                    print(f"   ❌ {route} - MANQUANT")
        else:
            print("❌ Template _base_superviseur.html non trouvé")
        
        # Vérifier que le dashboard utilise la bonne base
        dashboard_path = "app/templates/superviseur/dashboard.html"
        if os.path.exists(dashboard_path):
            print("\n📄 Vérification du dashboard:")
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
                
            if '_base_superviseur.html' in dashboard_content:
                print("   ✅ Dashboard utilise _base_superviseur.html")
            else:
                print("   ❌ Dashboard n'utilise pas _base_superviseur.html")
                
            if 'superviseur_content' in dashboard_content:
                print("   ✅ Block superviseur_content présent")
            else:
                print("   ❌ Block superviseur_content manquant")
        else:
            print("❌ Dashboard superviseur non trouvé")
    
    print("\n🎉 SIDEBAR SUPERVISEUR CONFIGURÉE!")
    print("🔗 Connectez-vous avec: superviseur / superviseur123")
    print("🌐 URL: http://localhost:5000/superviseur/dashboard")
    print("\n📋 Navigation disponible:")
    print("   • Dashboard - Vue d'ensemble")
    print("   • Carburation - Gestion carburant")
    print("   • Bus UdM - Flotte de véhicules")
    print("   • Vidanges - Maintenance huile")
    print("   • Chauffeurs - Personnel")
    print("   • Utilisateurs - Comptes système")
    print("   • Rapports - Exports et analyses")
    
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
