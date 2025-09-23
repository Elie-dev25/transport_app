#!/usr/bin/env python3
"""
Script pour corriger les adresses email des utilisateurs
"""

import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_user_emails():
    """Corriger les emails des utilisateurs"""
    print("📧 CORRECTION DES EMAILS UTILISATEURS")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.database import db
        from app.models.utilisateur import Utilisateur
        
        app = create_app()
        
        with app.app_context():
            print("\n1. 🔍 État actuel des emails:")
            
            # Vérifier tous les utilisateurs
            users = Utilisateur.query.all()
            users_without_email = []
            users_with_wrong_email = []
            
            for user in users:
                email = getattr(user, 'email', None)
                nom_complet = f"{getattr(user, 'nom', '')} {getattr(user, 'prenom', '')}".strip()
                if not nom_complet:
                    nom_complet = getattr(user, 'login', 'Inconnu')
                
                print(f"   - {nom_complet} ({user.role}): {email or 'PAS D\'EMAIL'}")
                
                if not email:
                    users_without_email.append(user)
                elif 'elienjine8@gmail.com' in email:
                    users_with_wrong_email.append(user)
            
            print(f"\n2. 📊 Résumé:")
            print(f"   - Total utilisateurs: {len(users)}")
            print(f"   - Sans email: {len(users_without_email)}")
            print(f"   - Email incorrect (elienjine8): {len(users_with_wrong_email)}")
            
            # Proposer des corrections
            if users_with_wrong_email:
                print(f"\n3. 🔧 Correction des emails incorrects:")
                for user in users_with_wrong_email:
                    old_email = user.email
                    new_email = old_email.replace('elienjine8@gmail.com', 'elienjine15@gmail.com')
                    
                    print(f"   - {user.nom} {user.prenom}: {old_email} → {new_email}")
                    
                    response = input(f"   Corriger cet email ? (o/n): ").lower().strip()
                    if response in ['o', 'oui', 'y', 'yes']:
                        user.email = new_email
                        print(f"     ✅ Email corrigé")
                    else:
                        print(f"     ⏭️ Email non modifié")
            
            # Proposer d'ajouter des emails manquants
            if users_without_email:
                print(f"\n4. ➕ Ajout d'emails manquants:")
                
                # Emails par défaut selon le rôle
                default_emails = {
                    'ADMIN': 'admin@transportudm.com',
                    'RESPONSABLE': 'responsable@transportudm.com',
                    'SUPERVISEUR': 'superviseur@transportudm.com',
                    'MECANICIEN': 'mecanicien@transportudm.com',
                    'CHAUFFEUR': 'chauffeur@transportudm.com',
                    'CHARGE': 'charge@transportudm.com'
                }
                
                for user in users_without_email:
                    nom_complet = f"{user.nom} {user.prenom}".strip()
                    if not nom_complet:
                        nom_complet = user.login
                    
                    suggested_email = default_emails.get(user.role, 'user@transportudm.com')
                    
                    print(f"   - {nom_complet} ({user.role})")
                    email = input(f"     Email (suggéré: {suggested_email}): ").strip()
                    
                    if email:
                        user.email = email
                        print(f"     ✅ Email ajouté: {email}")
                    elif input(f"     Utiliser l'email suggéré ? (o/n): ").lower().strip() in ['o', 'oui', 'y', 'yes']:
                        user.email = suggested_email
                        print(f"     ✅ Email ajouté: {suggested_email}")
                    else:
                        print(f"     ⏭️ Pas d'email ajouté")
            
            # Sauvegarder les changements
            try:
                db.session.commit()
                print(f"\n✅ Changements sauvegardés en base de données")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Erreur lors de la sauvegarde: {str(e)}")
                return False
            
            print(f"\n5. 📋 État final des emails:")
            users = Utilisateur.query.all()
            for user in users:
                email = getattr(user, 'email', None)
                nom_complet = f"{getattr(user, 'nom', '')} {getattr(user, 'prenom', '')}".strip()
                if not nom_complet:
                    nom_complet = getattr(user, 'login', 'Inconnu')
                
                print(f"   - {nom_complet} ({user.role}): {email or 'PAS D\'EMAIL'}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_test_users_if_needed():
    """Créer des utilisateurs de test si nécessaire"""
    print("\n👥 VÉRIFICATION UTILISATEURS DE TEST")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.database import db
        from app.models.utilisateur import Utilisateur
        
        app = create_app()
        
        with app.app_context():
            # Vérifier s'il y a des utilisateurs pour chaque rôle critique
            roles_critiques = ['MECANICIEN', 'SUPERVISEUR', 'RESPONSABLE']
            
            for role in roles_critiques:
                users = Utilisateur.query.filter_by(role=role).all()
                
                if not users:
                    print(f"⚠️ Aucun utilisateur {role} trouvé")
                    
                    if input(f"Créer un utilisateur {role} de test ? (o/n): ").lower().strip() in ['o', 'oui', 'y', 'yes']:
                        # Créer un utilisateur de test
                        test_user = Utilisateur(
                            login=f"test_{role.lower()}",
                            nom=f"Test",
                            prenom=role.title(),
                            role=role,
                            email=f"test_{role.lower()}@transportudm.com"
                        )
                        
                        db.session.add(test_user)
                        print(f"✅ Utilisateur {role} de test créé")
                else:
                    print(f"✅ {len(users)} utilisateur(s) {role} trouvé(s)")
            
            try:
                db.session.commit()
                print(f"\n✅ Utilisateurs de test créés")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Erreur création utilisateurs: {str(e)}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("📧 CONFIGURATION DES EMAILS UTILISATEURS")
    print("=" * 60)
    
    # Étape 1: Vérifier/créer les utilisateurs
    users_ok = create_test_users_if_needed()
    
    # Étape 2: Corriger les emails
    if users_ok:
        emails_ok = fix_user_emails()
    else:
        emails_ok = False
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    if emails_ok:
        print("✅ Configuration des emails terminée")
        print("\nProchaines étapes:")
        print("1. Configurez les variables SMTP avec configure_email.ps1")
        print("2. Testez avec: python test_notifications.py config")
        print("3. Redémarrez l'application Flask")
    else:
        print("❌ Problèmes lors de la configuration")
        print("Corrigez les erreurs et relancez le script")
