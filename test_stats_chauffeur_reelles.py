#!/usr/bin/env python3
"""
Script pour tester les statistiques réelles du chauffeur
"""

try:
    print("🧪 Test des statistiques réelles du chauffeur...")
    
    from app import create_app
    from app.models.utilisateur import Utilisateur
    from app.models.chauffeur import Chauffeur
    from app.models.trajet import Trajet
    from app.database import db
    from datetime import date, datetime
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée et contexte activé")
        
        # 1. Vérifier l'utilisateur chauffeur
        user_chauffeur = Utilisateur.query.filter_by(login='chauffeur').first()
        if not user_chauffeur:
            print("❌ Utilisateur 'chauffeur' non trouvé")
            exit(1)
        
        print(f"✅ Utilisateur chauffeur trouvé: {user_chauffeur.nom} {user_chauffeur.prenom}")
        
        # 2. Chercher le chauffeur correspondant dans la table chauffeur
        chauffeur_db = Chauffeur.query.filter_by(
            nom=user_chauffeur.nom, 
            prenom=user_chauffeur.prenom
        ).first()
        
        if chauffeur_db:
            print(f"✅ Chauffeur trouvé dans la table chauffeur: ID {chauffeur_db.chauffeur_id}")
            chauffeur_id = chauffeur_db.chauffeur_id
        else:
            print("⚠️  Chauffeur non trouvé dans la table chauffeur")
            print("   Création d'un chauffeur de test...")
            
            # Créer un chauffeur de test
            nouveau_chauffeur = Chauffeur(
                nom=user_chauffeur.nom,
                prenom=user_chauffeur.prenom,
                numero_permis='PERM-TEST-001',
                telephone=user_chauffeur.telephone,
                date_delivrance_permis=date(2020, 1, 1),
                date_expiration_permis=date(2030, 1, 1)
            )
            
            db.session.add(nouveau_chauffeur)
            db.session.commit()
            
            chauffeur_id = nouveau_chauffeur.chauffeur_id
            print(f"✅ Chauffeur créé avec ID: {chauffeur_id}")
        
        # 3. Vérifier les trajets existants pour ce chauffeur aujourd'hui
        today = date.today()
        trajets_aujourdhui = Trajet.query.filter(
            db.func.date(Trajet.date_heure_depart) == today,
            Trajet.chauffeur_id == chauffeur_id
        ).all()
        
        print(f"\n📊 STATISTIQUES ACTUELLES (Chauffeur ID: {chauffeur_id}):")
        print(f"   Date: {today}")
        print(f"   Trajets aujourd'hui: {len(trajets_aujourdhui)}")
        
        if trajets_aujourdhui:
            for trajet in trajets_aujourdhui:
                print(f"   • Trajet {trajet.trajet_id}: {trajet.point_depart} → {trajet.point_arriver} ({trajet.nombre_places_occupees or 0} places)")
        
        # 4. Calculer les statistiques réelles
        # Mes trajets aujourd'hui
        mes_trajets = len(trajets_aujourdhui)
        
        # Étudiants pour le campus (arrivée = Banekane)
        etudiants_pour_campus = db.session.query(
            db.func.sum(Trajet.nombre_places_occupees)
        ).filter(
            db.func.date(Trajet.date_heure_depart) == today,
            Trajet.chauffeur_id == chauffeur_id,
            Trajet.point_arriver == 'Banekane'
        ).scalar() or 0
        
        # Personnes du campus (départ = Banekane)
        personnes_du_campus = db.session.query(
            db.func.sum(Trajet.nombre_places_occupees)
        ).filter(
            db.func.date(Trajet.date_heure_depart) == today,
            Trajet.chauffeur_id == chauffeur_id,
            Trajet.point_depart == 'Banekane'
        ).scalar() or 0
        
        print(f"\n🎯 STATISTIQUES CALCULÉES:")
        print(f"   ✅ Mes trajets aujourd'hui: {mes_trajets}")
        print(f"   ✅ Étudiants transportés POUR le campus: {etudiants_pour_campus}")
        print(f"   ✅ Personnes transportées DU campus: {personnes_du_campus}")
        
        # 5. Vérifier les bus disponibles
        from app.models.bus_udm import BusUdM
        bus_disponibles = BusUdM.query.limit(3).all()

        if bus_disponibles:
            bus_numero = bus_disponibles[0].numero
            print(f"✅ Bus disponible trouvé: {bus_numero}")
        else:
            print("⚠️  Aucun bus trouvé, utilisation d'un trajet prestataire")
            bus_numero = None

        # 5. Créer des trajets de test si aucun n'existe
        if not trajets_aujourdhui:
            print(f"\n🔧 CRÉATION DE TRAJETS DE TEST:")

            if bus_numero:
                # Trajet 1: Mfetum → Banekane (pour le campus)
                trajet1 = Trajet(
                    type_trajet='UDM_INTERNE',
                    date_heure_depart=datetime.now(),
                    point_depart='Mfetum',
                    point_arriver='Banekane',
                    type_passagers='ETUDIANT',
                    nombre_places_occupees=25,
                    chauffeur_id=chauffeur_id,
                    numero_bus_udm=bus_numero
                )

                # Trajet 2: Banekane → Ancienne Mairie (du campus)
                trajet2 = Trajet(
                    type_trajet='UDM_INTERNE',
                    date_heure_depart=datetime.now(),
                    point_depart='Banekane',
                    point_arriver='Ancienne Mairie',
                    type_passagers='ETUDIANT',
                    nombre_places_occupees=18,
                    chauffeur_id=chauffeur_id,
                    numero_bus_udm=bus_numero
                )
            else:
                # Trajets prestataires si pas de bus UdM
                trajet1 = Trajet(
                    type_trajet='PRESTATAIRE',
                    date_heure_depart=datetime.now(),
                    point_depart='Mfetum',
                    point_arriver='Banekane',
                    type_passagers='ETUDIANT',
                    nombre_places_occupees=25,
                    chauffeur_id=chauffeur_id,
                    immat_bus='TEST-001',
                    nom_chauffeur=f"{user_chauffeur.nom} {user_chauffeur.prenom}"
                )

                trajet2 = Trajet(
                    type_trajet='PRESTATAIRE',
                    date_heure_depart=datetime.now(),
                    point_depart='Banekane',
                    point_arriver='Ancienne Mairie',
                    type_passagers='ETUDIANT',
                    nombre_places_occupees=18,
                    chauffeur_id=chauffeur_id,
                    immat_bus='TEST-001',
                    nom_chauffeur=f"{user_chauffeur.nom} {user_chauffeur.prenom}"
                )
            
            db.session.add(trajet1)
            db.session.add(trajet2)
            db.session.commit()
            
            if bus_numero:
                print(f"   ✅ Trajet 1 créé: Mfetum → Banekane (25 étudiants) - Bus {bus_numero}")
                print(f"   ✅ Trajet 2 créé: Banekane → Ancienne Mairie (18 étudiants) - Bus {bus_numero}")
            else:
                print(f"   ✅ Trajet 1 créé: Mfetum → Banekane (25 étudiants) - Prestataire TEST-001")
                print(f"   ✅ Trajet 2 créé: Banekane → Ancienne Mairie (18 étudiants) - Prestataire TEST-001")
            
            # Recalculer les statistiques
            mes_trajets = 2
            etudiants_pour_campus = 25
            personnes_du_campus = 18
            
            print(f"\n🎯 NOUVELLES STATISTIQUES:")
            print(f"   ✅ Mes trajets aujourd'hui: {mes_trajets}")
            print(f"   ✅ Étudiants transportés POUR le campus: {etudiants_pour_campus}")
            print(f"   ✅ Personnes transportées DU campus: {personnes_du_campus}")
        
        print(f"\n🚀 INSTRUCTIONS DE TEST:")
        print("1. Connectez-vous en tant que chauffeur:")
        print("   Login: chauffeur")
        print("   Mot de passe: chauffeur123")
        print("2. Allez sur le dashboard chauffeur")
        print("3. Vérifiez la section 'Mes Statistiques Personnelles'")
        print("4. Les statistiques doivent correspondre aux valeurs ci-dessus")
        
        print(f"\n💡 NOTES IMPORTANTES:")
        print("• Les statistiques sont calculées en temps réel")
        print("• Elles sont remises à zéro chaque jour à 00h00")
        print("• Seuls les trajets du chauffeur connecté sont comptés")
        print("• Point de départ/arrivée 'Banekane' = Campus UdM")
        
        print("\n✅ Test terminé avec succès!")

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Vérifiez:")
    print("1. Que la base de données est accessible")
    print("2. Que les modèles sont correctement définis")
    print("3. Que l'utilisateur chauffeur existe")
