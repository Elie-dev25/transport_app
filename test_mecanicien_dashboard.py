#!/usr/bin/env python3
"""
Script de test pour vérifier le dashboard mécanicien
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models.bus_udm import BusUdM

def test_mecanicien_dashboard():
    """Test du dashboard mécanicien"""
    app = create_app()
    with app.app_context():
        try:
            print("🔧 Test du dashboard mécanicien...")
            
            # Vérifier les bus existants
            bus_list = BusUdM.query.order_by(BusUdM.numero).all()
            print(f"📊 Nombre de bus trouvés: {len(bus_list)}")
            
            if len(bus_list) == 0:
                print("⚠️  Aucun bus trouvé - créons un bus de test")
                
                # Créer un bus de test
                bus_test = BusUdM(
                    numero="TEST001",
                    immatriculation="TEST-001-CM",
                    etat_vehicule="BON",
                    kilometrage=15000,
                    km_critique_huile=20000,
                    type_huile="15W40"
                )
                db.session.add(bus_test)
                db.session.commit()
                print("✅ Bus de test créé")
                
                bus_list = BusUdM.query.order_by(BusUdM.numero).all()
            
            # Calculer les statistiques comme dans la route
            bus_total = len(bus_list)
            bus_bon_etat = 0
            bus_vidange_urgente = 0
            
            print("\n📋 Analyse des bus:")
            for bus in bus_list:
                print(f"   🚌 {bus.numero} - État: {bus.etat_vehicule} - KM: {bus.kilometrage}")
                
                # Compter les bus en bon état
                etat_normalise = str(bus.etat_vehicule or '').lower()
                if 'defaillant' not in etat_normalise and 'hors' not in etat_normalise:
                    bus_bon_etat += 1
                
                # Compter les vidanges urgentes
                niveau = bus.kilometrage or 0
                seuil = bus.km_critique_huile or 0
                if seuil > 0 and niveau >= seuil:
                    bus_vidange_urgente += 1
                    print(f"      ⚠️  Vidange urgente nécessaire!")
            
            print(f"\n📊 Statistiques calculées:")
            print(f"   🚌 Bus total: {bus_total}")
            print(f"   ✅ Bus en bon état: {bus_bon_etat}")
            print(f"   ⚠️  Vidanges urgentes: {bus_vidange_urgente}")
            
            # Test des routes
            with app.test_client() as client:
                print(f"\n🌐 Test des routes mécanicien:")
                
                routes_to_test = [
                    ('/mecanicien/dashboard', 'Dashboard'),
                    ('/mecanicien/vidange', 'Vidange'),
                    ('/mecanicien/carburation', 'Carburation'),
                    ('/mecanicien/declaration_panne', 'Déclaration Panne'),
                    ('/mecanicien/depannage', 'Dépannage')
                ]
                
                for route, name in routes_to_test:
                    try:
                        response = client.get(route)
                        if response.status_code == 200:
                            print(f"   ✅ {name}: OK")
                        elif response.status_code == 302:
                            print(f"   🔄 {name}: Redirection (normal - pas connecté)")
                        else:
                            print(f"   ❌ {name}: Erreur {response.status_code}")
                    except Exception as e:
                        print(f"   ❌ {name}: Exception - {e}")
            
            print(f"\n🎉 Test terminé avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_mecanicien_dashboard()
