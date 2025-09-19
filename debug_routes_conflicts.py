#!/usr/bin/env python3
"""
Script pour déboguer les conflits de routes entre admin et mécanicien
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_routes():
    """Debug des routes pour identifier les conflits"""
    app = create_app()
    
    print("🔍 ANALYSE DES ROUTES - CONFLITS ADMIN/MÉCANICIEN")
    print("=" * 60)
    
    # Récupérer toutes les routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'rule': rule.rule,
            'methods': list(rule.methods)
        })
    
    # Filtrer les routes qui nous intéressent
    admin_routes = [r for r in routes if r['endpoint'].startswith('admin.')]
    mecanicien_routes = [r for r in routes if r['endpoint'].startswith('mecanicien.')]
    
    print("\n📋 ROUTES ADMIN CONCERNÉES:")
    for route in admin_routes:
        if any(keyword in route['rule'] for keyword in ['carburation', 'vidange', 'depanage']):
            print(f"   {route['endpoint']} → {route['rule']} {route['methods']}")
    
    print("\n🔧 ROUTES MÉCANICIEN:")
    for route in mecanicien_routes:
        print(f"   {route['endpoint']} → {route['rule']} {route['methods']}")
    
    print("\n⚠️  CONFLITS POTENTIELS:")
    
    # Vérifier les conflits spécifiques
    conflicts = [
        ('carburation', '/admin/carburation', '/mecanicien/carburation'),
        ('vidange', '/admin/vidange', '/mecanicien/vidange'),
        ('depannage', '/admin/depanage', '/mecanicien/depannage'),
        ('declaration_panne', '/admin/depanage', '/mecanicien/declaration_panne')
    ]
    
    for name, admin_url, mecanicien_url in conflicts:
        admin_exists = any(r['rule'] == admin_url for r in admin_routes)
        mecanicien_exists = any(r['rule'] == mecanicien_url for r in mecanicien_routes)
        
        print(f"\n   📄 {name.upper()}:")
        print(f"      Admin: {admin_url} {'✅' if admin_exists else '❌'}")
        print(f"      Mécanicien: {mecanicien_url} {'✅' if mecanicien_exists else '❌'}")
        
        if admin_exists and mecanicien_exists:
            print(f"      🔥 CONFLIT DÉTECTÉ!")
    
    print("\n🧪 TEST DES REDIRECTIONS:")
    
    # Test avec un client de test
    with app.test_client() as client:
        test_urls = [
            '/mecanicien/dashboard',
            '/mecanicien/carburation', 
            '/mecanicien/vidange',
            '/mecanicien/depannage',
            '/mecanicien/declaration_panne'
        ]
        
        for url in test_urls:
            try:
                response = client.get(url)
                if response.status_code == 302:
                    location = response.headers.get('Location', 'Unknown')
                    print(f"   {url} → {response.status_code} (Redirect to: {location})")
                else:
                    print(f"   {url} → {response.status_code}")
            except Exception as e:
                print(f"   {url} → ERROR: {e}")

if __name__ == '__main__':
    debug_routes()
