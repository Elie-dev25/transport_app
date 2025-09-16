#!/usr/bin/env python3
"""
Diagnostic de la liaison entre utilisateur connecté et table chauffeur
"""

try:
    print("🔍 DIAGNOSTIC DE LA LIAISON UTILISATEUR <-> CHAUFFEUR")
    print("=" * 60)
    
    from app import create_app
    from app.models.utilisateur import Utilisateur
    from app.models.chauffeur import Chauffeur
    from app.models.trajet import Trajet
    from app.database import db
    from datetime import date
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée et contexte activé")
        
        # 1. Lister tous les utilisateurs CHAUFFEUR
        print("\n1. 👥 UTILISATEURS AVEC RÔLE CHAUFFEUR:")
        users_chauffeur = Utilisateur.query.filter_by(role='CHAUFFEUR').all()
        
        if users_chauffeur:
            for user in users_chauffeur:
                print(f"   • ID: {user.utilisateur_id} | Login: {user.login} | Nom: '{user.nom}' | Prénom: '{user.prenom}'")
        else:
            print("   ❌ Aucun utilisateur avec le rôle CHAUFFEUR trouvé")
        
        # 2. Lister tous les chauffeurs dans la table chauffeur
        print("\n2. 🚌 CHAUFFEURS DANS LA TABLE CHAUFFEUR:")
        chauffeurs_db = Chauffeur.query.all()
        
        if chauffeurs_db:
            for chauffeur in chauffeurs_db:
                print(f"   • ID: {chauffeur.chauffeur_id} | Nom: '{chauffeur.nom}' | Prénom: '{chauffeur.prenom}' | Permis: {chauffeur.numero_permis}")
        else:
            print("   ❌ Aucun chauffeur trouvé dans la table chauffeur")
        
        # 3. Vérifier les liaisons
        print("\n3. 🔗 VÉRIFICATION DES LIAISONS:")
        liaisons_trouvees = 0
        
        for user in users_chauffeur:
            # Méthode actuelle (par nom/prénom)
            chauffeur_match = Chauffeur.query.filter_by(
                nom=user.nom, 
                prenom=user.prenom
            ).first()
            
            if chauffeur_match:
                print(f"   ✅ LIAISON TROUVÉE: User '{user.login}' -> Chauffeur ID {chauffeur_match.chauffeur_id}")
                liaisons_trouvees += 1
            else:
                print(f"   ❌ LIAISON MANQUANTE: User '{user.login}' ({user.nom} {user.prenom}) -> Aucun chauffeur correspondant")
        
        print(f"\n   📊 Résumé: {liaisons_trouvees}/{len(users_chauffeur)} liaisons trouvées")
        
        # 4. Vérifier les trajets pour chaque chauffeur
        print("\n4. 📋 TRAJETS PAR CHAUFFEUR:")
        today = date.today()
        
        for chauffeur in chauffeurs_db:
            trajets_aujourdhui = Trajet.query.filter(
                db.func.date(Trajet.date_heure_depart) == today,
                Trajet.chauffeur_id == chauffeur.chauffeur_id
            ).all()
            
            print(f"   • Chauffeur ID {chauffeur.chauffeur_id} ({chauffeur.nom} {chauffeur.prenom}): {len(trajets_aujourdhui)} trajets aujourd'hui")
            
            if trajets_aujourdhui:
                for trajet in trajets_aujourdhui:
                    print(f"     - Trajet {trajet.trajet_id}: {trajet.point_depart} → {trajet.point_arriver} ({trajet.nombre_places_occupees or 0} places)")
        
        # 5. Identifier l'utilisateur connecté (simulation)
        print("\n5. 🎯 SIMULATION UTILISATEUR CONNECTÉ:")
        user_connecte = Utilisateur.query.filter_by(login='chauffeur').first()
        
        if user_connecte:
            print(f"   Utilisateur connecté simulé: {user_connecte.login}")
            print(f"   Nom: '{user_connecte.nom}' | Prénom: '{user_connecte.prenom}'")
            
            # Chercher le chauffeur correspondant
            chauffeur_correspondant = Chauffeur.query.filter_by(
                nom=user_connecte.nom,
                prenom=user_connecte.prenom
            ).first()
            
            if chauffeur_correspondant:
                print(f"   ✅ Chauffeur correspondant trouvé: ID {chauffeur_correspondant.chauffeur_id}")
                
                # Calculer ses statistiques
                mes_trajets = Trajet.query.filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == chauffeur_correspondant.chauffeur_id
                ).count()
                
                etudiants_pour_campus = db.session.query(
                    db.func.sum(Trajet.nombre_places_occupees)
                ).filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == chauffeur_correspondant.chauffeur_id,
                    Trajet.point_arriver == 'Banekane'
                ).scalar() or 0
                
                personnes_du_campus = db.session.query(
                    db.func.sum(Trajet.nombre_places_occupees)
                ).filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == chauffeur_correspondant.chauffeur_id,
                    Trajet.point_depart == 'Banekane'
                ).scalar() or 0
                
                print(f"   📊 SES STATISTIQUES RÉELLES:")
                print(f"      - Mes trajets aujourd'hui: {mes_trajets}")
                print(f"      - Étudiants pour campus: {etudiants_pour_campus}")
                print(f"      - Personnes du campus: {personnes_du_campus}")
                
            else:
                print(f"   ❌ Aucun chauffeur correspondant trouvé")
                print(f"   💡 Recherche alternative par login...")
                
                # Recherche alternative
                chauffeur_alt = None
                for chauffeur in chauffeurs_db:
                    if (chauffeur.nom.lower() == user_connecte.login.lower() or 
                        user_connecte.login.lower() in chauffeur.nom.lower()):
                        chauffeur_alt = chauffeur
                        break
                
                if chauffeur_alt:
                    print(f"   ⚠️  Chauffeur trouvé par recherche alternative: ID {chauffeur_alt.chauffeur_id}")
                else:
                    print(f"   ❌ Aucun chauffeur trouvé même avec recherche alternative")
        
        # 6. Recommandations
        print(f"\n6. 💡 RECOMMANDATIONS:")
        
        if liaisons_trouvees == 0:
            print("   🔧 PROBLÈME MAJEUR: Aucune liaison utilisateur <-> chauffeur")
            print("   📋 Solutions possibles:")
            print("      1. Créer une clé étrangère utilisateur_id dans la table chauffeur")
            print("      2. Utiliser le login comme référence")
            print("      3. Créer une table de liaison utilisateur_chauffeur")
            
        elif liaisons_trouvees < len(users_chauffeur):
            print("   ⚠️  LIAISONS PARTIELLES: Certains utilisateurs n'ont pas de chauffeur correspondant")
            print("   📋 Actions recommandées:")
            print("      1. Créer les chauffeurs manquants")
            print("      2. Corriger les noms/prénoms incohérents")
        
        else:
            print("   ✅ LIAISONS CORRECTES: Tous les utilisateurs ont un chauffeur correspondant")
        
        print(f"\n7. 🛠️  SOLUTION TEMPORAIRE:")
        print("   Pour corriger immédiatement le problème:")
        print("   1. Identifier l'utilisateur chauffeur réel")
        print("   2. Créer/modifier le chauffeur correspondant")
        print("   3. Supprimer les trajets de test erronés")
        
        print("\n" + "=" * 60)
        print("🎯 DIAGNOSTIC TERMINÉ")
        print("=" * 60)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
