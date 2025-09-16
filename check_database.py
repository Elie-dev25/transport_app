#!/usr/bin/env python3
"""
Script pour vérifier l'état de la base de données
"""

import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """Vérifier l'état de la base de données"""
    
    try:
        print("🔍 Vérification de la base de données...")
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.database import db
            
            # Test de connexion
            print("1. Test de connexion à la base de données...")
            try:
                result = db.engine.execute("SELECT 1")
                print("   ✅ Connexion réussie")
            except Exception as e:
                print(f"   ❌ Erreur de connexion: {e}")
                return False
            
            # Vérifier la table utilisateur
            print("2. Vérification de la table utilisateur...")
            try:
                result = db.engine.execute("DESCRIBE utilisateur")
                columns = result.fetchall()
                print("   ✅ Table utilisateur trouvée")
                
                # Vérifier la colonne role
                role_column = None
                for column in columns:
                    if column[0] == 'role':
                        role_column = column
                        break
                
                if role_column:
                    print(f"   📋 Colonne role: {role_column[1]}")
                    
                    # Vérifier si SUPERVISEUR est dans l'ENUM
                    if 'SUPERVISEUR' in role_column[1]:
                        print("   ✅ Rôle SUPERVISEUR disponible")
                    else:
                        print("   ❌ Rôle SUPERVISEUR manquant")
                        print("   💡 Exécutez: mysql -u username -p database < scripts/add_superviseur_role.sql")
                        return False
                else:
                    print("   ❌ Colonne role non trouvée")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Erreur table utilisateur: {e}")
                return False
            
            # Vérifier les utilisateurs existants
            print("3. Vérification des utilisateurs existants...")
            try:
                from app.models.utilisateur import Utilisateur
                users = Utilisateur.query.all()
                print(f"   📊 {len(users)} utilisateur(s) trouvé(s)")
                
                for user in users:
                    print(f"   👤 {user.login} - {user.role}")
                    
            except Exception as e:
                print(f"   ❌ Erreur utilisateurs: {e}")
                return False
            
            print("\n✅ Base de données OK")
            return True
            
    except Exception as e:
        print(f"❌ ERREUR GÉNÉRALE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_database()
    if not success:
        print("\n💡 Actions recommandées:")
        print("1. Vérifiez que MySQL est démarré")
        print("2. Vérifiez la configuration de la base de données dans app/config.py")
        print("3. Exécutez la migration: mysql -u username -p database < scripts/add_superviseur_role.sql")
        sys.exit(1)
    else:
        print("\n🎉 Base de données prête!")
