"""Targeted tests to bring new_coverage above 80% on Sonar.

Covers:
- trajet_service utility helpers (_get_bus_autonomie, _get_reservoir_capacity,
  _clamp_fuel_level, update_autocontrol_after_km_change) and the MSG_KM_INVALIDE
  branches that fire on non-numeric kilometrage_actuel data.
- maintenance_service ERR_BUS_NON_TROUVE branches in create_panne /
  create_vidange / create_carburation when bus_udm_id is unknown.
"""
from datetime import datetime, date
from types import SimpleNamespace

import pytest

from app.services import trajet_service as ts
from app.services.maintenance_service import MaintenanceService, ERR_BUS_NON_TROUVE


# ---------------------- trajet_service helpers ----------------------

class _Bus(SimpleNamespace):
    pass


class TestGetBusAutonomie:
    def test_uses_specific_consumption(self):
        bus = _Bus(consommation_km_par_litre=12.5)
        assert ts._get_bus_autonomie(bus) == 12.5

    def test_invalid_specific_falls_back_to_capacities(self):
        bus = _Bus(
            consommation_km_par_litre='not-a-number',
            capacite_plein_carburant=600,
            capacite_reservoir_litres=60,
        )
        assert ts._get_bus_autonomie(bus) == 10.0

    def test_invalid_capacities_falls_back_to_constant(self):
        bus = _Bus(
            consommation_km_par_litre=None,
            capacite_plein_carburant='oops',
            capacite_reservoir_litres='oops',
        )
        # must return float fallback constant; just check it's positive
        result = ts._get_bus_autonomie(bus)
        assert isinstance(result, float)
        assert result > 0

    def test_zero_capacities_falls_back_to_constant(self):
        bus = _Bus(
            consommation_km_par_litre=None,
            capacite_plein_carburant=0,
            capacite_reservoir_litres=0,
        )
        result = ts._get_bus_autonomie(bus)
        assert isinstance(result, float)


class TestGetReservoirCapacity:
    def test_none_when_attribute_missing(self):
        bus = _Bus(capacite_reservoir_litres=None)
        assert ts._get_reservoir_capacity(bus) is None

    def test_returns_float_when_positive(self):
        bus = _Bus(capacite_reservoir_litres=80)
        assert ts._get_reservoir_capacity(bus) == 80.0

    def test_none_when_zero_or_negative(self):
        bus = _Bus(capacite_reservoir_litres=0)
        assert ts._get_reservoir_capacity(bus) is None

    def test_none_on_invalid_value(self):
        bus = _Bus(capacite_reservoir_litres='nope')
        assert ts._get_reservoir_capacity(bus) is None


class TestClampFuelLevel:
    def test_clamps_negative_to_zero(self):
        assert ts._clamp_fuel_level(-5.0, 50.0) == 0.0

    def test_caps_at_capacity(self):
        assert ts._clamp_fuel_level(60.0, 50.0) == 50.0

    def test_within_range(self):
        assert ts._clamp_fuel_level(20.0, 50.0) == 20.0

    def test_no_capacity_returns_value(self):
        assert ts._clamp_fuel_level(20.0, None) == 20.0


class TestUpdateAutocontrolAfterKmChange:
    def test_no_op_when_km_none(self):
        bus = _Bus(niveau_carburant_litres=10.0)
        # should silently return without raising
        ts.update_autocontrol_after_km_change(bus, None, 100)
        ts.update_autocontrol_after_km_change(bus, 100, None)

    def test_no_op_when_invalid_km(self):
        bus = _Bus(niveau_carburant_litres=10.0)
        ts.update_autocontrol_after_km_change(bus, 'abc', 100)

    def test_no_op_when_delta_negative_or_zero(self):
        bus = _Bus(niveau_carburant_litres=10.0)
        ts.update_autocontrol_after_km_change(bus, 50, 100)  # delta < 0
        ts.update_autocontrol_after_km_change(bus, 100, 100)  # delta == 0

    def test_no_op_when_no_fuel_tracking(self):
        bus = _Bus()  # no niveau_carburant_litres attribute
        ts.update_autocontrol_after_km_change(bus, 200, 100)

    def test_updates_fuel_level_when_tracked(self):
        bus = _Bus(
            consommation_km_par_litre=10.0,
            capacite_reservoir_litres=60.0,
            niveau_carburant_litres=50.0,
            km_critique_carburant=0.0,
        )
        ts.update_autocontrol_after_km_change(bus, 200, 100)
        # delta=100, autonomie=10 => consume 10L => 40L
        assert bus.niveau_carburant_litres == round(40.0, 3)


# ---------------------- maintenance_service ERR_BUS_NON_TROUVE ----------------------

class TestCreatePanneBusNotFound:
    def test_returns_err_when_bus_missing(self, app):
        ok, msg, _id = MaintenanceService.create_panne(
            {
                'bus_udm_id': 999999,
                'description': 'Panne test',
                'criticite': 'HAUTE',
                'immobilisation': False,
            },
            user_name='tester',
        )
        assert ok is False
        assert msg == ERR_BUS_NON_TROUVE


class TestCreateVidangeBusNotFound:
    def test_returns_err_when_bus_missing(self, app):
        ok, msg, _id = MaintenanceService.create_vidange(
            {
                'bus_udm_id': 999999,
                'date_vidange': date.today(),
                'kilometrage': 1000,
                'type_huile': '15W40',
            }
        )
        assert ok is False
        assert msg == ERR_BUS_NON_TROUVE


class TestCreateCarburationBusNotFound:
    def test_returns_err_when_bus_missing(self, app):
        ok, msg, _id = MaintenanceService.create_carburation(
            {
                'bus_udm_id': 999999,
                'date_carburation': date.today(),
                'kilometrage': 1000,
                'quantite_litres': 50,
                'prix_unitaire': 700,
                'cout_total': 35000,
            }
        )
        assert ok is False
        assert msg == ERR_BUS_NON_TROUVE


# ---------------------- trajet_service: MSG_KM_INVALIDE branch ----------------------

class _FieldData:
    def __init__(self, value):
        self.data = value


class _Form:
    """Form stub matching the attributes accessed by trajet_service.* enregistrer_*."""
    def __init__(self, numero_aed, kilometrage, **extras):
        self.numero_aed = _FieldData(numero_aed)
        self.kilometrage_actuel = _FieldData(kilometrage)
        self.point_depart = _FieldData('Campus')
        self.date_heure_depart = _FieldData(datetime.now())
        self.type_passagers = _FieldData('ETUDIANTS')
        self.nombre_places_occupees = _FieldData(10)
        self.chauffeur_id = _FieldData(extras.get('chauffeur_id', 1))
        self.motif_trajet = _FieldData('Test')


class TestEnregistrerDepartAedInvalidKm:
    def test_invalid_km_returns_msg_km_invalide(self, app, sample_chauffeur, sample_bus):
        from app.models.utilisateur import Utilisateur
        from app.extensions import db

        user = Utilisateur(
            nom='T', prenom='U', login='trajet_user',
            email='trajet_user@example.com', telephone='000',
            role='CHARGE',
        )
        user.set_password('Pwd12345!')
        db.session.add(user)
        db.session.commit()

        # Set bus current km to a numeric value, then pass non-numeric in the form
        sample_bus.kilometrage = 1000
        db.session.add(sample_bus)
        db.session.commit()

        form = _Form(numero_aed=sample_bus.numero, kilometrage='not-a-number',
                     chauffeur_id=sample_chauffeur.chauffeur_id)
        ok, msg = ts.enregistrer_depart_aed(form, user)
        assert ok is False
        assert ts.MSG_KM_INVALIDE in msg or 'invalide' in msg.lower()
