#!/usr/bin/env python3
"""
Vérification de la structure de la base de données
Pour adapter les modèles à la structure existante
"""

def check_table_structure():
    """Vérifie la structure des tables principales"""
    print("VERIFICATION STRUCTURE BASE DE DONNEES")
    print("=" * 50)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.database import db
            
            # Tables à vérifier
            tables_to_check = ['bus_udm', 'utilisateur', 'trajet', 'chauffeur']
            
            for table_name in tables_to_check:
                print(f"\nTABLE: {table_name}")
                print("-" * 30)
                
                try:
                    # Requête pour obtenir la structure de la table
                    result = db.engine.execute(f"DESCRIBE {table_name}")
                    columns = result.fetchall()
                    
                    print("Colonnes existantes:")
                    for col in columns:
                        field_name = col[0]
                        field_type = col[1]
                        nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                        key = col[3] if col[3] else ""
                        default = col[4] if col[4] else ""
                        
                        print(f"  - {field_name} ({field_type}) {nullable} {key}")
                        
                except Exception as e:
                    print(f"Erreur pour {table_name}: {e}")
            
            return True
            
    except Exception as e:
        print(f"ERREUR GENERALE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_table_structure()
