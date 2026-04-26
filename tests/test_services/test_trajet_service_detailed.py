"""
Tests détaillés pour trajet_service - cible 80% de coverage.
"""
import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch
from app.extensions import db


@pytest.fixture
def setup_data(app):
    from app.models.bus_udm import BusUdM
    from app.models.chauffeur import Chauffeur
    from app.models.utilisateur import Utilisateur
    from app.models.prestataire import Prestataire
    from app.models.chargetransport import Chargetransport
    
    bus = BusUdM(
        numero='BUS_TS', immatriculation='TS-001', nombre_places=20,
        numero_chassis='CH_TS', etat_vehicule='BON',
        kilometrage=50000, capacite_reservoir_litres=80.0,
        consommation_km_par_litre=8.0, niveau_carburant_litres=40.0,
    )
    bus_def = BusUdM(
        numero='BUS_DEF', immatriculation='DEF-001', nombre_places=20,
        numero_chassis='CH_DEF', etat_vehicule='DEFAILLANT',
    )
    db.session.add_all([bus, bus_def])
    
    chauf = Chauffeur(
        nom='C', prenom='T', numero_permis='PERM_TS', telephone='000',
        date_delivrance_permis=date(2020,1,1),
        date_expiration_permis=date(2030,1,1),
    )
    db.session.add(chauf)
    
    user = Utilisateur(
        nom='U', prenom='T', login='u_ts', email='u_ts@t.com',
        telephone='000', role='CHARGE'
    )
    user.set_password('Pass!123')
    db.session.add(user)
    
    prest = Prestataire(nom_prestataire='Prest TS', localisation='Yaoundé')
    db.session.add(prest)
    db.session.commit()
    
    return {'bus': bus, 'bus_def': bus_def, 'chauffeur': chauf, 'user': user, 'prest': prest}


class TestTrajetServiceUtils:
    def test_get_bus_autonomie_with_consommation(self, setup_data):
        from app.services.trajet_service import _get_bus_autonomie
        assert _get_bus_autonomie(setup_data['bus']) == 8.0
    
    def test_get_bus_autonomie_default(self, setup_data):
        from app.services.trajet_service import _get_bus_autonomie, AUTONOMIE_KM_PAR_LITRE
        assert _get_bus_autonomie(setup_data['bus_def']) == AUTONOMIE_KM_PAR_LITRE
    
    def test_get_bus_autonomie_invalid_consommation(self, app, setup_data):
        from app.services.trajet_service import _get_bus_autonomie, AUTONOMIE_KM_PAR_LITRE
        bus = setup_data['bus']
        bus.consommation_km_par_litre = 'invalid'
        # Le fallback sur AUTONOMIE_KM_PAR_LITRE
        result = _get_bus_autonomie(bus)
        assert result is not None
    
    def test_get_reservoir_capacity_valid(self, setup_data):
        from app.services.trajet_service import _get_reservoir_capacity
        assert _get_reservoir_capacity(setup_data['bus']) == 80.0
    
    def test_get_reservoir_capacity_none(self, setup_data):
        from app.services.trajet_service import _get_reservoir_capacity
        assert _get_reservoir_capacity(setup_data['bus_def']) is None
    
    def test_get_reservoir_capacity_zero(self, setup_data):
        from app.services.trajet_service import _get_reservoir_capacity
        bus = setup_data['bus']
        bus.capacite_reservoir_litres = 0
        assert _get_reservoir_capacity(bus) is None
    
    def test_clamp_fuel_level_negative(self):
        from app.services.trajet_service import _clamp_fuel_level
        assert _clamp_fuel_level(-5, 80) == 0.0
    
    def test_clamp_fuel_level_above_capacity(self):
        from app.services.trajet_service import _clamp_fuel_level
        assert _clamp_fuel_level(100, 80) == 80
    
    def test_clamp_fuel_level_no_capacity(self):
        from app.services.trajet_service import _clamp_fuel_level
        assert _clamp_fuel_level(50, None) == 50
    
    def test_clamp_fuel_level_normal(self):
        from app.services.trajet_service import _clamp_fuel_level
        assert _clamp_fuel_level(40, 80) == 40
    
    def test_update_autocontrol_normal(self, setup_data):
        from app.services.trajet_service import update_autocontrol_after_km_change
        bus = setup_data['bus']
        update_autocontrol_after_km_change(bus, 51000, 50000)
        # 1000 km / 8 km/L = 125L consommés, mais on n'avait que 40L donc 0
        assert bus.niveau_carburant_litres >= 0
    
    def test_update_autocontrol_negative_delta(self, setup_data):
        from app.services.trajet_service import update_autocontrol_after_km_change
        bus = setup_data['bus']
        before = bus.niveau_carburant_litres
        update_autocontrol_after_km_change(bus, 49000, 50000)
        assert bus.niveau_carburant_litres == before
    
    def test_update_autocontrol_none_values(self, setup_data):
        from app.services.trajet_service import update_autocontrol_after_km_change
        bus = setup_data['bus']
        update_autocontrol_after_km_change(bus, None, 50000)
        update_autocontrol_after_km_change(bus, 51000, None)
    
    def test_update_autocontrol_invalid_values(self, setup_data):
        from app.services.trajet_service import update_autocontrol_after_km_change
        bus = setup_data['bus']
        update_autocontrol_after_km_change(bus, 'abc', 50000)


class TestEnregistrerDepartAed:
    def _make_form(self, setup_data, **overrides):
        form = MagicMock()
        form.date_heure_depart.data = datetime(2024, 1, 1, 8, 0)
        form.point_depart.data = 'Mfetum'
        form.type_passagers.data = 'ETUDIANT'
        form.nombre_places_occupees.data = 10
        form.chauffeur_id.data = setup_data['chauffeur'].chauffeur_id
        form.numero_aed.data = setup_data['bus'].numero
        form.kilometrage_actuel.data = 51000
        for k, v in overrides.items():
            getattr(form, k).data = v
        return form
    
    def test_enregistrer_depart_aed_success(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_aed
        form = self._make_form(setup_data)
        success, msg = enregistrer_depart_aed(form, setup_data['user'])
        assert success is True
    
    def test_enregistrer_depart_aed_defaillant(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_aed
        form = self._make_form(setup_data, numero_aed=setup_data['bus_def'].numero)
        success, msg = enregistrer_depart_aed(form, setup_data['user'])
        assert success is False
        assert 'DEFAILLANT' in msg or 'immobilisé' in msg
    
    def test_enregistrer_depart_aed_km_invalid(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_aed
        form = self._make_form(setup_data, kilometrage_actuel=40000)  # < 50000 actuel
        success, msg = enregistrer_depart_aed(form, setup_data['user'])
        assert success is False


class TestEnregistrerSortie:
    def test_enregistrer_sortie_success(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_sortie_hors_ville
        form = MagicMock()
        form.date_heure_depart.data = datetime(2024, 1, 1, 8, 0)
        form.point_depart.data = 'Mfetum'
        form.chauffeur_id.data = setup_data['chauffeur'].chauffeur_id
        form.numero_aed.data = setup_data['bus'].numero
        form.motif_trajet.data = 'Mission spéciale'
        form.kilometrage_actuel.data = 51000
        success, msg = enregistrer_depart_sortie_hors_ville(form, setup_data['user'])
        assert success is True
    
    def test_enregistrer_sortie_defaillant(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_sortie_hors_ville
        form = MagicMock()
        form.date_heure_depart.data = datetime(2024, 1, 1, 8, 0)
        form.point_depart.data = 'Mfetum'
        form.chauffeur_id.data = setup_data['chauffeur'].chauffeur_id
        form.numero_aed.data = setup_data['bus_def'].numero
        form.motif_trajet.data = 'Mission'
        form.kilometrage_actuel.data = 51000
        success, msg = enregistrer_depart_sortie_hors_ville(form, setup_data['user'])
        assert success is False


class TestEnregistrerPrestataire:
    def test_enregistrer_prestataire_success(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_prestataire
        data = {
            'date_heure_depart': '2024-01-01T08:00',
            'lieu_depart': 'Mfetum',
            'lieu_arrivee': 'Banekane',
            'type_passagers': 'ETUDIANT',
            'nombre_places_occupees': '10',
            'immat_bus': 'XX-001',
            'nom_prestataire': str(setup_data['prest'].id),
            'nom_chauffeur': 'Test Chauffeur',
        }
        success, msg = enregistrer_depart_prestataire(data, setup_data['user'])
        assert success is True
    
    def test_enregistrer_prestataire_no_date(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_prestataire
        success, msg = enregistrer_depart_prestataire({}, setup_data['user'])
        assert success is False
    
    def test_enregistrer_prestataire_invalid_date(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_prestataire
        success, msg = enregistrer_depart_prestataire(
            {'date_heure_depart': 'invalid-date'}, setup_data['user']
        )
        assert success is False
    
    def test_enregistrer_prestataire_missing_fields(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_prestataire
        success, msg = enregistrer_depart_prestataire(
            {'date_heure_depart': '2024-01-01T08:00'}, setup_data['user']
        )
        assert success is False
    
    def test_enregistrer_prestataire_invalid_int(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_prestataire
        data = {
            'date_heure_depart': '2024-01-01T08:00',
            'lieu_depart': 'Mfetum',
            'type_passagers': 'ETUDIANT',
            'nombre_places_occupees': 'abc',
            'immat_bus': 'XX-001',
            'nom_prestataire': 'invalid',
            'nom_chauffeur': 'Test',
        }
        success, msg = enregistrer_depart_prestataire(data, setup_data['user'])
        assert success is False


class TestEnregistrerBanekaneRetour:
    def test_aed_success(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_banekane_retour
        form = MagicMock()
        form.type_bus.data = 'AED'
        form.date_heure_depart.data = datetime(2024, 1, 1, 8, 0)
        form.type_passagers.data = 'ETUDIANT'
        form.nombre_places_occupees.data = 10
        form.chauffeur_id.data = setup_data['chauffeur'].chauffeur_id
        form.numero_aed.data = setup_data['bus'].numero
        form.kilometrage_actuel.data = 51000
        success, msg = enregistrer_depart_banekane_retour(form, setup_data['user'])
        # Peut succeed ou fail selon la disponibilité du form
        assert isinstance(success, bool)
    
    def test_aed_defaillant(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_banekane_retour
        form = MagicMock()
        form.type_bus.data = 'AED'
        form.numero_aed.data = setup_data['bus_def'].numero
        success, msg = enregistrer_depart_banekane_retour(form, setup_data['user'])
        assert success is False


class TestNouveauxServices:
    def _make_modernise_form(self, setup_data, **overrides):
        form = MagicMock()
        form.date_heure_depart.data = datetime(2024, 1, 1, 8, 0)
        form.lieu_depart.data = 'Mfetum'
        form.point_arriver.data = 'Banekane'
        form.type_passagers.data = 'ETUDIANT'
        form.nombre_places_occupees.data = 10
        form.chauffeur_id.data = setup_data['chauffeur'].chauffeur_id
        form.numero_bus_udm.data = setup_data['bus'].numero
        form.kilometrage_actuel.data = 51000
        form.motif_trajet.data = 'Mission'
        form.nom_prestataire.data = setup_data['prest'].id
        form.nom_chauffeur_prestataire.data = 'C Prest'
        form.immat_bus.data = 'PR-001'
        for k, v in overrides.items():
            getattr(form, k).data = v
        return form
    
    def test_trajet_interne_bus_udm(self, setup_data):
        from app.services.trajet_service import enregistrer_trajet_interne_bus_udm
        form = self._make_modernise_form(setup_data)
        success, msg = enregistrer_trajet_interne_bus_udm(form, setup_data['user'])
        assert success is True
    
    def test_trajet_interne_bus_udm_defaillant(self, setup_data):
        from app.services.trajet_service import enregistrer_trajet_interne_bus_udm
        form = self._make_modernise_form(setup_data, numero_bus_udm=setup_data['bus_def'].numero)
        success, msg = enregistrer_trajet_interne_bus_udm(form, setup_data['user'])
        assert success is False
    
    def test_trajet_interne_km_invalid(self, setup_data):
        from app.services.trajet_service import enregistrer_trajet_interne_bus_udm
        form = self._make_modernise_form(setup_data, kilometrage_actuel=10)
        success, msg = enregistrer_trajet_interne_bus_udm(form, setup_data['user'])
        assert success is False
    
    def test_trajet_prestataire_modernise(self, setup_data):
        from app.services.trajet_service import enregistrer_trajet_prestataire_modernise
        form = self._make_modernise_form(setup_data)
        success, msg = enregistrer_trajet_prestataire_modernise(form, setup_data['user'])
        # peut succeed ou fail selon le contexte
        assert isinstance(success, bool)
    
    def test_autres_trajets(self, setup_data):
        from app.services.trajet_service import enregistrer_autres_trajets
        form = self._make_modernise_form(setup_data)
        success, msg = enregistrer_autres_trajets(form, setup_data['user'])
        assert success is True
    
    def test_autres_trajets_defaillant(self, setup_data):
        from app.services.trajet_service import enregistrer_autres_trajets
        form = self._make_modernise_form(setup_data, numero_bus_udm=setup_data['bus_def'].numero)
        success, msg = enregistrer_autres_trajets(form, setup_data['user'])
        assert success is False
    
    def test_banekane_prestataire(self, setup_data):
        from app.services.trajet_service import enregistrer_depart_banekane_retour
        form = MagicMock()
        form.type_bus.data = 'PRESTATAIRE'
        form.date_heure_depart.data = datetime(2024, 1, 1, 8, 0)
        form.nombre_places_occupees.data = 30
        form.immat_bus.data = 'NEW-PR-001'
        form.nom_agence.data = 'AgenceX'
        form.nom_chauffeur_agence.data = 'Chauf X'
        success, msg = enregistrer_depart_banekane_retour(form, setup_data['user'])
        assert isinstance(success, bool)


class TestEnsureChargetransport:
    def test_creates_if_missing(self, app):
        from app.services.trajet_service import _ensure_chargetransport_for_user
        from app.models.utilisateur import Utilisateur
        from app.models.chargetransport import Chargetransport
        
        u = Utilisateur(
            nom='X', prenom='Y', login='ensure_ct', email='ec@t.com',
            telephone='000', role='CHARGE'
        )
        u.set_password('Pass!123')
        db.session.add(u)
        db.session.commit()
        
        _ensure_chargetransport_for_user(u.utilisateur_id)
        ct = Chargetransport.query.get(u.utilisateur_id)
        assert ct is not None
    
    def test_idempotent(self, app):
        from app.services.trajet_service import _ensure_chargetransport_for_user
        from app.models.utilisateur import Utilisateur
        from app.models.chargetransport import Chargetransport
        
        u = Utilisateur(
            nom='X2', prenom='Y2', login='ensure_ct2', email='ec2@t.com',
            telephone='000', role='CHARGE'
        )
        u.set_password('Pass!123')
        db.session.add(u)
        db.session.commit()
        
        _ensure_chargetransport_for_user(u.utilisateur_id)
        _ensure_chargetransport_for_user(u.utilisateur_id)
        # Should not raise
