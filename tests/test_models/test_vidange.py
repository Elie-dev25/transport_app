"""Tests pour le modèle Vidange."""
import pytest
from datetime import date
from app.models.vidange import Vidange
from app.models.bus_udm import BusUdM
from app.extensions import db


class TestVidange:
    def test_create_vidange(self, app):
        bus = BusUdM(numero='BUS_V1', immatriculation='V-001', nombre_places=20,
                     numero_chassis='CHASSIS_V1', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        vidange = Vidange(
            bus_udm_id=bus.id,
            date_vidange=date.today(),
            kilometrage=75000,
            type_huile='QUARTZ',
        )
        db.session.add(vidange)
        db.session.commit()
        assert vidange.id is not None
        assert vidange.type_huile == 'QUARTZ'
    
    def test_vidange_with_remarque(self, app):
        bus = BusUdM(numero='BUS_V2', immatriculation='V-002', nombre_places=20,
                     numero_chassis='CHASSIS_V2', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        vidange = Vidange(
            bus_udm_id=bus.id,
            date_vidange=date.today(),
            kilometrage=80000,
            type_huile='RUBIA',
            remarque='Vidange complète'
        )
        db.session.add(vidange)
        db.session.commit()
        assert vidange.remarque == 'Vidange complète'
    
    def test_vidange_relationship(self, app):
        bus = BusUdM(numero='BUS_V3', immatriculation='V-003', nombre_places=20,
                     numero_chassis='CHASSIS_V3', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        vidange = Vidange(
            bus_udm_id=bus.id,
            date_vidange=date.today(),
            kilometrage=90000,
            type_huile='QUARTZ',
        )
        db.session.add(vidange)
        db.session.commit()
        assert vidange.bus_udm.numero == 'BUS_V3'
