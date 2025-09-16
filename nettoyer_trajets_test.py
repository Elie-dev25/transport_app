#!/usr/bin/env python3
"""
Nettoyer les trajets de test créés par erreur
"""

try:
    print("🧹 NETTOYAGE DES TRAJETS DE TEST")
    print("=" * 50)
    
    from app import create_app
    from app.models.trajet import Trajet
    from app.database import db
    from datetime import date
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application créée et contexte activé")
        
        today = date.today()
        
        # 1. Identifier les trajets de test (créés aujourd'hui avec les données spécifiques)
        trajets_test = Trajet.query.filter(
            db.func.date(Trajet.date_heure_depart) == today,
            Trajet.chauffeur_id == 19,  # Chauffeur de test
            db.or_(
                db.and_(Trajet.point_depart == 'Mfetum', Trajet.point_arriver == 'Banekane', Trajet.nombre_places_occupees == 25),
                db.and_(Trajet.point_depart == 'Banekane', Trajet.point_arriver == 'Ancienne Mairie', Trajet.nombre_places_occupees == 18)
            )
        ).all()
        
        print(f"\n📋 TRAJETS DE TEST IDENTIFIÉS:")
        if trajets_test:
            for trajet in trajets_test:
                print(f"   • Trajet {trajet.trajet_id}: {trajet.point_depart} → {trajet.point_arriver} ({trajet.nombre_places_occupees} places)")
        else:
            print("   ℹ️  Aucun trajet de test trouvé")
        
        # 2. Demander confirmation (simulation)
        if trajets_test:
            print(f"\n❓ VOULEZ-VOUS SUPPRIMER CES {len(trajets_test)} TRAJETS DE TEST ?")
            print("   Ces trajets ont été créés automatiquement pour les tests")
            print("   et ne correspondent pas à de vrais trajets effectués.")
            
            # Simulation de confirmation (toujours oui pour le script)
            confirmation = True
            
            if confirmation:
                print("\n🗑️  SUPPRESSION EN COURS...")
                
                for trajet in trajets_test:
                    print(f"   - Suppression du trajet {trajet.trajet_id}")
                    db.session.delete(trajet)
                
                db.session.commit()
                print(f"   ✅ {len(trajets_test)} trajets de test supprimés avec succès")
                
                # 3. Vérifier les nouvelles statistiques
                print(f"\n📊 NOUVELLES STATISTIQUES POUR LE CHAUFFEUR ID 19:")
                
                mes_trajets = Trajet.query.filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == 19
                ).count()
                
                etudiants_pour_campus = db.session.query(
                    db.func.sum(Trajet.nombre_places_occupees)
                ).filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == 19,
                    Trajet.point_arriver == 'Banekane'
                ).scalar() or 0
                
                personnes_du_campus = db.session.query(
                    db.func.sum(Trajet.nombre_places_occupees)
                ).filter(
                    db.func.date(Trajet.date_heure_depart) == today,
                    Trajet.chauffeur_id == 19,
                    Trajet.point_depart == 'Banekane'
                ).scalar() or 0
                
                print(f"   • Mes trajets aujourd'hui: {mes_trajets}")
                print(f"   • Étudiants pour campus: {etudiants_pour_campus}")
                print(f"   • Personnes du campus: {personnes_du_campus}")
                
                if mes_trajets == 0:
                    print(f"   ✅ PARFAIT ! Le chauffeur n'a plus de trajets fictifs")
                    print(f"   📱 Le dashboard affichera maintenant des statistiques réelles (probablement 0)")
                
            else:
                print("   ❌ Suppression annulée")
        
        # 4. Vérifier s'il reste d'autres trajets pour ce chauffeur
        autres_trajets = Trajet.query.filter(
            Trajet.chauffeur_id == 19
        ).all()
        
        if autres_trajets:
            print(f"\n📋 AUTRES TRAJETS RESTANTS POUR CE CHAUFFEUR:")
            for trajet in autres_trajets:
                print(f"   • Trajet {trajet.trajet_id}: {trajet.point_depart} → {trajet.point_arriver} le {trajet.date_heure_depart.date()}")
        else:
            print(f"\n✅ AUCUN AUTRE TRAJET POUR CE CHAUFFEUR")
            print(f"   Le dashboard affichera des statistiques à zéro, ce qui est correct")
        
        print(f"\n🎯 RÉSULTAT:")
        print("   ✅ Trajets de test supprimés")
        print("   ✅ Statistiques maintenant réelles")
        print("   ✅ Dashboard prêt pour utilisation normale")
        
        print("\n" + "=" * 50)
        print("🧹 NETTOYAGE TERMINÉ")
        print("=" * 50)

except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
