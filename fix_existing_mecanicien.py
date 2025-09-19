#!/usr/bin/env python3
"""
Script pour corriger les utilisateurs existants qui n'ont pas d'enregistrement 
dans leur table personnelle (chauffeur, mecanicien, etc.)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models.utilisateur import Utilisateur
from app.models.chauffeur import Chauffeur
from app.models.mecanicien import Mecanicien
from app.models.chargetransport import Chargetransport
from app.models.administrateur import Administrateur

def fix_missing_role_records():
    """Corrige les enregistrements manquants dans les tables de rôles"""
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Vérification des utilisateurs sans enregistrement dans leur table personnelle...")
            
            # Récupérer tous les utilisateurs
            users = Utilisateur.query.all()
            fixed_count = 0
            
            for user in users:
                print(f"\n👤 Utilisateur: {user.nom} {user.prenom} (ID: {user.utilisateur_id}, Rôle: {user.role})")
                
                if user.role == 'CHAUFFEUR':
                    # Vérifier si l'enregistrement chauffeur existe
                    chauffeur = Chauffeur.query.get(user.utilisateur_id)
                    if not chauffeur:
                        print(f"   ❌ Enregistrement chauffeur manquant")
                        print(f"   ⚠️  ATTENTION: Pour créer un chauffeur, il faut les données de permis.")
                        print(f"   💡 Utilisez l'interface web pour recréer cet utilisateur avec les bonnes données.")
                    else:
                        print(f"   ✅ Enregistrement chauffeur OK")
                        
                elif user.role == 'MECANICIEN':
                    # Vérifier si l'enregistrement mécanicien existe
                    mecanicien = Mecanicien.query.get(user.utilisateur_id)
                    if not mecanicien:
                        print(f"   ❌ Enregistrement mécanicien manquant - CRÉATION...")
                        
                        # Créer l'enregistrement mécanicien avec des données par défaut
                        # L'utilisateur devra les mettre à jour via l'interface
                        from datetime import date, timedelta
                        
                        mecanicien = Mecanicien(
                            mecanicien_id=user.utilisateur_id,
                            numero_permis="A_DEFINIR",  # À mettre à jour
                            date_delivrance_permis=date.today() - timedelta(days=365),  # Il y a 1 an
                            date_expiration_permis=date.today() + timedelta(days=365*4)  # Dans 4 ans
                        )
                        db.session.add(mecanicien)
                        db.session.commit()
                        
                        print(f"   ✅ Enregistrement mécanicien créé avec des données par défaut")
                        print(f"   💡 IMPORTANT: Mettez à jour le numéro de permis et les dates via l'interface")
                        fixed_count += 1
                    else:
                        print(f"   ✅ Enregistrement mécanicien OK")
                        
                elif user.role == 'CHARGE':
                    # Vérifier si l'enregistrement charge transport existe
                    charge = Chargetransport.query.get(user.utilisateur_id)
                    if not charge:
                        print(f"   ❌ Enregistrement charge transport manquant - CRÉATION...")
                        charge = Chargetransport(chargetransport_id=user.utilisateur_id)
                        db.session.add(charge)
                        db.session.commit()
                        print(f"   ✅ Enregistrement charge transport créé")
                        fixed_count += 1
                    else:
                        print(f"   ✅ Enregistrement charge transport OK")
                        
                elif user.role == 'ADMIN':
                    # Vérifier si l'enregistrement administrateur existe
                    admin = Administrateur.query.get(user.utilisateur_id)
                    if not admin:
                        print(f"   ❌ Enregistrement administrateur manquant - CRÉATION...")
                        admin = Administrateur(administrateur_id=user.utilisateur_id)
                        db.session.add(admin)
                        db.session.commit()
                        print(f"   ✅ Enregistrement administrateur créé")
                        fixed_count += 1
                    else:
                        print(f"   ✅ Enregistrement administrateur OK")
                        
                elif user.role in ['RESPONSABLE', 'SUPERVISEUR']:
                    print(f"   ℹ️  Rôle {user.role} n'a pas de table personnelle (normal)")
                    
                else:
                    print(f"   ⚠️  Rôle inconnu: {user.role}")
            
            print(f"\n🎉 Correction terminée ! {fixed_count} enregistrement(s) créé(s).")
            
            if fixed_count > 0:
                print("\n💡 NOTES IMPORTANTES:")
                print("   - Les mécaniciens créés ont des données de permis par défaut")
                print("   - Mettez à jour ces informations via l'interface web")
                print("   - Testez la connexion de vos utilisateurs")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_missing_role_records()
