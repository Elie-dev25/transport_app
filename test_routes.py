#!/usr/bin/env python3
"""Script de test pour vérifier les routes disponibles"""

from app import create_app

def test_routes():
    app = create_app()
    
    print("=== TOUTES LES ROUTES DISPONIBLES ===")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
    
    print("\n=== ROUTES ADMIN ===")
    with app.app_context():
        admin_routes = [rule for rule in app.url_map.iter_rules() if 'admin' in str(rule)]
        for rule in admin_routes:
            print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")
    
    print("\n=== ROUTES RAPPORT ===")
    with app.app_context():
        rapport_routes = [rule for rule in app.url_map.iter_rules() if 'rapport' in str(rule)]
        for rule in rapport_routes:
            print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")

if __name__ == "__main__":
    test_routes()
