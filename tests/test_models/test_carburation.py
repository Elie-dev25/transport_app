"""Tests pour le modèle Carburation."""
import pytest
from datetime import date
from app.models.carburation import Carburation
from app.models.bus_udm import BusUdM
from app.extensions import db


class TestCarburation:
    def test_create_carburation(self, app):
        bus = BusUdM(numero='BUS_C1', immatriculation='C-001', nombre_places=20,
                     numero_chassis='CHASSIS_C1', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        carb = Carburation(
            bus_udm_id=bus.id,
            date_carburation=date.today(),
            kilometrage=50000,
            quantite_litres=50.0,
            prix_unitaire=850.0,
            cout_total=42500.0,
        )
        db.session.add(carb)
        db.session.commit()
        assert carb.id is not None
        assert carb.quantite_litres == 50.0
    
    def test_carburation_cout_total(self, app):
        bus = BusUdM(numero='BUS_C2', immatriculation='C-002', nombre_places=20,
                     numero_chassis='CHASSIS_C2', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        carb = Carburation(
            bus_udm_id=bus.id,
            date_carburation=date.today(),
            kilometrage=60000,
            quantite_litres=60.0,
            prix_unitaire=900.0,
            cout_total=54000.0,
        )
        db.session.add(carb)
        db.session.commit()
        assert carb.cout_total == 54000.0
    
    def test_carburation_with_remarque(self, app):
        bus = BusUdM(numero='BUS_C3', immatriculation='C-003', nombre_places=20,
                     numero_chassis='CHASSIS_C3', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        carb = Carburation(
            bus_udm_id=bus.id,
            date_carburation=date.today(),
            kilometrage=70000,
            quantite_litres=40.0,
            prix_unitaire=850.0,
            cout_total=34000.0,
            remarque='Plein essence'
        )
        db.session.add(carb)
        db.session.commit()
        assert carb.remarque == 'Plein essence'
