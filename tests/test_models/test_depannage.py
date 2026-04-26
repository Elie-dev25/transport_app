"""Tests pour le modèle Depannage."""
import pytest
from datetime import datetime
from app.models.depannage import Depannage
from app.models.bus_udm import BusUdM
from app.extensions import db


class TestDepannage:
    def test_create_depannage(self, app):
        bus = BusUdM(numero='BUS_D1', immatriculation='D-001', nombre_places=20,
                     numero_chassis='CHASSIS_D1', etat_vehicule='DEFAILLANT')
        db.session.add(bus)
        db.session.commit()
        dep = Depannage(
            bus_udm_id=bus.id,
            numero_bus_udm='BUS_D1',
            immatriculation='D-001',
            date_heure=datetime.now(),
            description_panne='Panne moteur',
            repare_par='Mécanicien Test',
            cout_reparation=500.0,
        )
        db.session.add(dep)
        db.session.commit()
        assert dep.id is not None
        assert dep.description_panne == 'Panne moteur'
    
    def test_depannage_repr(self, app):
        bus = BusUdM(numero='BUS_D2', immatriculation='D-002', nombre_places=20,
                     numero_chassis='CHASSIS_D2', etat_vehicule='DEFAILLANT')
        db.session.add(bus)
        db.session.commit()
        dep = Depannage(
            bus_udm_id=bus.id,
            numero_bus_udm='BUS_D2',
            date_heure=datetime.now(),
            description_panne='Test',
            repare_par='Test',
        )
        db.session.add(dep)
        db.session.commit()
        assert 'Depannage' in repr(dep)
    
    def test_depannage_cout(self, app):
        bus = BusUdM(numero='BUS_D3', immatriculation='D-003', nombre_places=20,
                     numero_chassis='CHASSIS_D3', etat_vehicule='DEFAILLANT')
        db.session.add(bus)
        db.session.commit()
        dep = Depannage(
            bus_udm_id=bus.id,
            numero_bus_udm='BUS_D3',
            date_heure=datetime.now(),
            description_panne='Réparation pneus',
            repare_par='Mécanicien',
            cout_reparation=1200.0,
            kilometrage=50000.0,
            cause_panne='Usure',
        )
        db.session.add(dep)
        db.session.commit()
        assert dep.cout_reparation == 1200.0
