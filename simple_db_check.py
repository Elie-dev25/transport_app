#!/usr/bin/env python3
"""
Vérification simple de la structure de la base de données
"""

try:
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.database import db
        
        print("STRUCTURE TABLE bus_udm")
        print("=" * 30)
        
        # Requête simple pour voir les colonnes
        result = db.engine.execute("DESCRIBE bus_udm")
        columns = result.fetchall()
        
        print("Colonnes existantes:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
            
except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()
