#!/usr/bin/env python3
"""
Script de correction pour mettre à jour les états des bus
Corrige les valeurs vides/NULL en 'BON' par défaut
"""

def fix_bus_etat_vehicule():
    print("🔧 CORRECTION DES ÉTATS DES BUS")
    print("=" * 50)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.models.bus_udm import BusUdM
            from app.database import db
            
            # Analyser la situation actuelle
            print("\n1. 📊 ANALYSE ACTUELLE:")
            buses_total = BusUdM.query.all()
            print(f"   Total bus: {len(buses_total)}")
            
            buses_vides = BusUdM.query.filter(
                (BusUdM.etat_vehicule == '') | 
                (BusUdM.etat_vehicule.is_(None))
            ).all()
            print(f"   Bus avec état vide/NULL: {len(buses_vides)}")
            
            buses_bon = BusUdM.query.filter_by(etat_vehicule='BON').all()
            print(f"   Bus avec état 'BON': {len(buses_bon)}")
            
            buses_defaillant = BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').all()
            print(f"   Bus avec état 'DEFAILLANT': {len(buses_defaillant)}")
            
            # Afficher les bus avec état vide
            if buses_vides:
                print("\n   Bus avec état vide:")
                for bus in buses_vides[:10]:  # Limiter l'affichage
                    etat = repr(bus.etat_vehicule)
                    print(f"     - {bus.numero}: {etat}")
                if len(buses_vides) > 10:
                    print(f"     ... et {len(buses_vides) - 10} autres")
            
            # Correction des états vides
            if buses_vides:
                print(f"\n2. 🔧 CORRECTION EN COURS:")
                print(f"   Mise à jour de {len(buses_vides)} bus...")
                
                # Stratégie de correction intelligente
                corriges = 0
                for bus in buses_vides:
                    # Vérifier s'il y a des pannes non résolues
                    try:
                        from app.models.panne_bus_udm import PanneBusUdM
                        pannes_ouvertes = PanneBusUdM.query.filter_by(
                            bus_udm_id=bus.id,
                            resolue=False
                        ).count()
                        
                        if pannes_ouvertes > 0:
                            # Bus avec pannes ouvertes = DEFAILLANT
                            bus.etat_vehicule = 'DEFAILLANT'
                            print(f"     ✅ {bus.numero}: DEFAILLANT (pannes ouvertes: {pannes_ouvertes})")
                        else:
                            # Bus sans panne = BON
                            bus.etat_vehicule = 'BON'
                            print(f"     ✅ {bus.numero}: BON")
                        
                        corriges += 1
                        
                    except ImportError:
                        # Si le modèle PanneBusUdM n'existe pas, mettre BON par défaut
                        bus.etat_vehicule = 'BON'
                        print(f"     ✅ {bus.numero}: BON (défaut)")
                        corriges += 1
                
                # Sauvegarder les modifications
                try:
                    db.session.commit()
                    print(f"\n   💾 {corriges} bus mis à jour avec succès!")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"\n   ❌ Erreur lors de la sauvegarde: {e}")
                    return False
            
            else:
                print("\n2. ✅ AUCUNE CORRECTION NÉCESSAIRE")
                print("   Tous les bus ont déjà un état valide")
            
            # Vérification finale
            print(f"\n3. 📊 VÉRIFICATION FINALE:")
            buses_bon_final = BusUdM.query.filter_by(etat_vehicule='BON').all()
            buses_defaillant_final = BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').all()
            buses_vides_final = BusUdM.query.filter(
                (BusUdM.etat_vehicule == '') | 
                (BusUdM.etat_vehicule.is_(None))
            ).all()
            
            print(f"   Bus 'BON': {len(buses_bon_final)}")
            print(f"   Bus 'DEFAILLANT': {len(buses_defaillant_final)}")
            print(f"   Bus vides/NULL: {len(buses_vides_final)}")
            
            # Test des services
            print(f"\n4. 🧪 TEST DES SERVICES:")
            from app.services.query_service import QueryService
            from app.services.form_service import FormService
            
            active_buses = QueryService.get_active_buses()
            print(f"   QueryService.get_active_buses(): {len(active_buses)}")
            
            bus_choices = FormService._get_bus_choices('BON_ONLY')
            print(f"   FormService._get_bus_choices(): {len(bus_choices)}")
            
            if len(buses_vides_final) == 0 and len(active_buses) > 0:
                print("\n🎉 CORRECTION RÉUSSIE!")
                print("   Les listes déroulantes devraient maintenant fonctionner")
                return True
            else:
                print("\n⚠️  PROBLÈME PERSISTANT")
                return False
                
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_default_value_to_column():
    """Ajouter une valeur par défaut à la colonne etat_vehicule"""
    print("\n🔧 AJOUT VALEUR PAR DÉFAUT")
    print("=" * 30)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.database import db
            from sqlalchemy import text
            
            print("Ajout de la valeur par défaut 'BON' à la colonne etat_vehicule...")
            
            # Modifier la colonne pour ajouter une valeur par défaut
            sql = text("""
                ALTER TABLE bus_udm 
                MODIFY COLUMN etat_vehicule 
                ENUM('BON','DEFAILLANT') 
                NOT NULL 
                DEFAULT 'BON'
                COMMENT 'État du véhicule'
            """)
            
            db.session.execute(sql)
            db.session.commit()
            
            print("✅ Valeur par défaut ajoutée avec succès!")
            print("   Nouveaux bus auront automatiquement l'état 'BON'")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DE LA CORRECTION")
    
    # Étape 1: Corriger les données existantes
    success1 = fix_bus_etat_vehicule()
    
    # Étape 2: Ajouter valeur par défaut pour l'avenir
    success2 = add_default_value_to_column()
    
    if success1 and success2:
        print("\n🎉 CORRECTION COMPLÈTE RÉUSSIE!")
        print("✅ Données existantes corrigées")
        print("✅ Valeur par défaut ajoutée")
        print("✅ Listes déroulantes fonctionnelles")
    else:
        print("\n💥 CORRECTION PARTIELLE")
        print("Vérifiez les erreurs ci-dessus")
