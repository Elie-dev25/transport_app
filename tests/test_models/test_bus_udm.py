"""
Tests pour le modèle BusUdM.
"""
import pytest
from datetime import date
from app.models.bus_udm import BusUdM
from app.database import db


class TestBusUdM:
    """Tests pour le modèle BusUdM."""
    
    def test_create_bus(self, app):
        """Test de création d'un bus."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS001',
                immatriculation='AB-123-CD',
                marque='Mercedes',
                modele='Sprinter',
                nombre_places=20,
                numero_chassis='WDB1234567890',
                etat_vehicule='BON'
            )
            db.session.add(bus)
            db.session.commit()
            
            assert bus.id is not None
            assert bus.numero == 'BUS001'
            assert bus.immatriculation == 'AB-123-CD'
            assert bus.etat_vehicule == 'BON'
    
    def test_bus_repr(self, app):
        """Test de la représentation string du bus."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS002',
                immatriculation='EF-456-GH',
                marque='Iveco',
                modele='Daily',
                nombre_places=15,
                numero_chassis='ZCFC1234567890',
                etat_vehicule='BON'
            )
            db.session.add(bus)
            db.session.commit()
            
            repr_str = repr(bus)
            assert 'BUS002' in repr_str
            assert 'EF-456-GH' in repr_str
    
    def test_get_info_display(self, app):
        """Test de la méthode get_info_display."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS003',
                immatriculation='IJ-789-KL',
                marque='Renault',
                modele='Master',
                nombre_places=18,
                numero_chassis='VF1234567890',
                etat_vehicule='BON'
            )
            db.session.add(bus)
            db.session.commit()
            
            info = bus.get_info_display()
            assert 'BUS003' in info
            assert 'IJ-789-KL' in info
            assert 'Renault' in info
            assert 'Master' in info
    
    def test_bus_kilometrage(self, app):
        """Test du kilométrage du bus."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS004',
                immatriculation='MN-012-OP',
                marque='Mercedes',
                modele='Vito',
                nombre_places=9,
                numero_chassis='WDB9876543210',
                etat_vehicule='BON',
                kilometrage=75000
            )
            db.session.add(bus)
            db.session.commit()
            
            assert bus.kilometrage == 75000
    
    def test_bus_etat_defaillant(self, app):
        """Test d'un bus en état défaillant."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS005',
                immatriculation='QR-345-ST',
                marque='Iveco',
                modele='Daily',
                nombre_places=12,
                numero_chassis='ZCFC9876543210',
                etat_vehicule='DEFAILLANT'
            )
            db.session.add(bus)
            db.session.commit()
            
            assert bus.etat_vehicule == 'DEFAILLANT'
    
    def test_bus_type_vehicule(self, app):
        """Test des différents types de véhicules."""
        types = ['TOURISME', 'COASTER', 'MINIBUS', 'AUTOCAR', 'AUTRE']
        
        with app.app_context():
            for i, type_v in enumerate(types):
                bus = BusUdM(
                    numero=f'BUS10{i}',
                    immatriculation=f'XX-{i}00-YY',
                    marque='Test',
                    modele='Model',
                    nombre_places=20,
                    numero_chassis=f'CHASSIS{i}',
                    etat_vehicule='BON',
                    type_vehicule=type_v
                )
                db.session.add(bus)
            
            db.session.commit()
            
            # Vérifier que tous les bus ont été créés
            count = BusUdM.query.count()
            assert count == len(types)
    
    def test_bus_gestion_huile(self, app):
        """Test des champs de gestion d'huile."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS006',
                immatriculation='UV-678-WX',
                marque='Mercedes',
                modele='Sprinter',
                nombre_places=20,
                numero_chassis='WDB1111111111',
                etat_vehicule='BON',
                type_huile='5W30',
                km_critique_huile=10000,
                date_derniere_vidange=date(2024, 1, 15)
            )
            db.session.add(bus)
            db.session.commit()
            
            assert bus.type_huile == '5W30'
            assert bus.km_critique_huile == 10000
            assert bus.date_derniere_vidange == date(2024, 1, 15)
    
    def test_bus_gestion_carburant(self, app):
        """Test des champs de gestion de carburant."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS007',
                immatriculation='YZ-901-AB',
                marque='Iveco',
                modele='Daily',
                nombre_places=15,
                numero_chassis='ZCFC2222222222',
                etat_vehicule='BON',
                capacite_reservoir_litres=80.0,
                niveau_carburant_litres=45.5,
                consommation_km_par_litre=8.5
            )
            db.session.add(bus)
            db.session.commit()
            
            assert bus.capacite_reservoir_litres == 80.0
            assert bus.niveau_carburant_litres == 45.5
            assert bus.consommation_km_par_litre == 8.5
    
    def test_bus_maintenance_date(self, app):
        """Test de la date de dernière maintenance."""
        with app.app_context():
            maintenance_date = date(2024, 3, 20)
            bus = BusUdM(
                numero='BUS008',
                immatriculation='CD-234-EF',
                marque='Renault',
                modele='Master',
                nombre_places=18,
                numero_chassis='VF13333333333',
                etat_vehicule='BON',
                derniere_maintenance=maintenance_date
            )
            db.session.add(bus)
            db.session.commit()
            
            assert bus.derniere_maintenance == maintenance_date
    
    def test_bus_nombre_places_required(self, app):
        """Test que nombre_places est obligatoire."""
        with app.app_context():
            bus = BusUdM(
                numero='BUS009',
                immatriculation='GH-567-IJ',
                marque='Test',
                modele='Model',
                numero_chassis='CHASSIS999',
                etat_vehicule='BON'
                # nombre_places manquant
            )
            db.session.add(bus)
            
            with pytest.raises(Exception):
                db.session.commit()
    
    def test_bus_query_by_etat(self, app):
        """Test de requête par état du véhicule."""
        with app.app_context():
            # Créer des bus avec différents états
            bus_bon = BusUdM(
                numero='BUS_BON',
                immatriculation='BON-001',
                nombre_places=20,
                numero_chassis='CHASSIS_BON',
                etat_vehicule='BON'
            )
            bus_def = BusUdM(
                numero='BUS_DEF',
                immatriculation='DEF-001',
                nombre_places=20,
                numero_chassis='CHASSIS_DEF',
                etat_vehicule='DEFAILLANT'
            )
            db.session.add_all([bus_bon, bus_def])
            db.session.commit()
            
            # Requête par état
            bons = BusUdM.query.filter_by(etat_vehicule='BON').all()
            defaillants = BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').all()
            
            assert len(bons) == 1
            assert len(defaillants) == 1
            assert bons[0].numero == 'BUS_BON'
            assert defaillants[0].numero == 'BUS_DEF'
