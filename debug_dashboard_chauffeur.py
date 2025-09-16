#!/usr/bin/env python3
"""
Debug du dashboard chauffeur pour identifier l'erreur
"""

try:
    print("🔍 DEBUG DASHBOARD CHAUFFEUR")
    print("=" * 50)
    
    from app import create_app
    from app.models.utilisateur import Utilisateur
    from app.models.chauffeur import Chauffeur
    from app.models.trajet import Trajet
    from app.models.bus_udm import BusUdM
    from app.database import db
    from app.utils.trafic import daily_student_trafic
    from datetime import date
    from flask_login import current_user
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée et contexte activé")
        
        # Simuler l'utilisateur connecté
        user_chauffeur = Utilisateur.query.filter_by(login='chauffeur').first()
        if not user_chauffeur:
            print("❌ Utilisateur chauffeur non trouvé")
            exit(1)
        
        print(f"✅ Utilisateur trouvé: {user_chauffeur.login}")
        print(f"   Nom: '{user_chauffeur.nom}' | Prénom: '{user_chauffeur.prenom}'")
        
        # Simuler le code du dashboard
        print("\n🔧 SIMULATION DU CODE DASHBOARD:")
        
        try:
            # Statistiques générales (identiques aux autres dashboards)
            today = date.today()
            print(f"   Date aujourd'hui: {today}")
            
            trajets_jour_aed = Trajet.query.filter(
                db.func.date(Trajet.date_heure_depart) == today, 
                Trajet.numero_bus_udm != None
            ).count()
            print(f"   ✅ Trajets jour AED: {trajets_jour_aed}")
            
            trajets_jour_bus_agence = Trajet.query.filter(
                db.func.date(Trajet.date_heure_depart) == today, 
                Trajet.immat_bus != None
            ).count()
            print(f"   ✅ Trajets jour bus agence: {trajets_jour_bus_agence}")
            
            # Trafic étudiant
            etudiants = daily_student_trafic()
            print(f"   ✅ Étudiants: {etudiants}")
            
            stats_generales = {
                'bus_actifs': BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count(),
                'trajets_jour_aed': trajets_jour_aed,
                'trajets_jour_bus_agence': trajets_jour_bus_agence,
                'etudiants': etudiants,
                'bus_maintenance': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count()
            }
            print(f"   ✅ Stats générales créées: {stats_generales}")
            
        except Exception as e:
            print(f"   ❌ ERREUR dans stats générales: {str(e)}")
            import traceback
            traceback.print_exc()
        
        try:
            # Récupérer le chauffeur correspondant pour les informations détaillées
            chauffeur_db = Chauffeur.query.filter_by(
                nom=user_chauffeur.nom, 
                prenom=user_chauffeur.prenom
            ).first()
            print(f"   ✅ Chauffeur DB trouvé: {chauffeur_db.chauffeur_id if chauffeur_db else 'None'}")
            
            # Informations spécifiques au chauffeur
            chauffeur_info = {
                'nom_complet': f"{user_chauffeur.nom} {user_chauffeur.prenom}".strip() or user_chauffeur.login,
                'numero_permis': chauffeur_db.numero_permis if chauffeur_db else 'Non renseigné',
                'telephone': user_chauffeur.telephone or '000-000-000',
                'affectation': 'Service Transport UdM'
            }
            print(f"   ✅ Chauffeur info créé: {chauffeur_info}")
            
        except Exception as e:
            print(f"   ❌ ERREUR dans chauffeur_info: {str(e)}")
            import traceback
            traceback.print_exc()
        
        try:
            # Statistiques personnelles RÉELLES du chauffeur connecté
            if chauffeur_db:
                chauffeur_id = chauffeur_db.chauffeur_id
                print(f"   Chauffeur ID: {chauffeur_id}")
                
                # 1. Mes trajets aujourd'hui
                mes_trajets_aujourdhui = Trajet.query.filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == chauffeur_id
                ).count()
                print(f"   ✅ Mes trajets: {mes_trajets_aujourdhui}")
                
                # 2. Étudiants transportés POUR le campus
                etudiants_pour_campus = db.session.query(
                    db.func.sum(Trajet.nombre_places_occupees)
                ).filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == chauffeur_id,
                    Trajet.point_arriver == 'Banekane'
                ).scalar() or 0
                print(f"   ✅ Étudiants pour campus: {etudiants_pour_campus}")
                
                # 3. Personnes transportées DU campus
                personnes_du_campus = db.session.query(
                    db.func.sum(Trajet.nombre_places_occupees)
                ).filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == chauffeur_id,
                    Trajet.point_depart == 'Banekane'
                ).scalar() or 0
                print(f"   ✅ Personnes du campus: {personnes_du_campus}")
                
            else:
                mes_trajets_aujourdhui = 0
                etudiants_pour_campus = 0
                personnes_du_campus = 0
                print(f"   ⚠️  Chauffeur non trouvé, stats = 0")
            
            stats_personnelles = {
                'mes_trajets_aujourdhui': mes_trajets_aujourdhui,
                'etudiants_pour_campus': etudiants_pour_campus,
                'personnes_du_campus': personnes_du_campus
            }
            print(f"   ✅ Stats personnelles créées: {stats_personnelles}")
            
        except Exception as e:
            print(f"   ❌ ERREUR dans stats personnelles: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n🎯 RÉSULTAT:")
        print("   ✅ Toutes les étapes ont été testées")
        print("   📊 Le dashboard devrait fonctionner")
        
        print(f"\n💡 VÉRIFICATIONS SUPPLÉMENTAIRES:")
        
        # Vérifier les imports
        try:
            from app.models.chauffeur import Chauffeur
            from app.models.trajet import Trajet
            from app.models.bus_udm import BusUdM
            from app.utils.trafic import daily_student_trafic
            print("   ✅ Tous les imports fonctionnent")
        except Exception as e:
            print(f"   ❌ ERREUR d'import: {str(e)}")
        
        # Vérifier la fonction daily_student_trafic
        try:
            trafic_result = daily_student_trafic()
            print(f"   ✅ daily_student_trafic() = {trafic_result}")
        except Exception as e:
            print(f"   ❌ ERREUR daily_student_trafic: {str(e)}")

except Exception as e:
    print(f"\n❌ ERREUR GLOBALE: {str(e)}")
    import traceback
    traceback.print_exc()
