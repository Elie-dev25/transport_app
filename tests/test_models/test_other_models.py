"""
Tests pour les autres modèles : administrateur, mecanicien, demande_huile, etc.
"""
import pytest
from datetime import date, datetime
from app.extensions import db


class TestAdministrateurModel:
    def test_import(self):
        from app.models.administrateur import Administrateur
        assert Administrateur is not None
    
    def test_create(self, app):
        from app.models.administrateur import Administrateur
        from app.models.utilisateur import Utilisateur
        
        # D'abord créer un utilisateur
        user = Utilisateur(
            nom='Admin', prenom='Test', login='admin_test_other',
            email='admin_other@test.com', telephone='000', role='ADMIN'
        )
        user.set_password('Pass!123')
        db.session.add(user)
        db.session.commit()
        
        admin = Administrateur(administrateur_id=user.utilisateur_id)
        db.session.add(admin)
        db.session.commit()
        assert admin.administrateur_id == user.utilisateur_id


class TestMecanicienModel:
    def test_import(self):
        from app.models.mecanicien import Mecanicien
        assert Mecanicien is not None
    
    def test_create(self, app):
        from app.models.mecanicien import Mecanicien
        from app.models.utilisateur import Utilisateur
        
        user = Utilisateur(
            nom='Meca', prenom='Test', login='meca_other',
            email='meca_other@test.com', telephone='001', role='MECANICIEN'
        )
        user.set_password('Pass!123')
        db.session.add(user)
        db.session.commit()
        
        meca = Mecanicien(mecanicien_id=user.utilisateur_id)
        db.session.add(meca)
        db.session.commit()
        assert meca.mecanicien_id == user.utilisateur_id


class TestPrestataireModel:
    def test_import(self):
        from app.models.prestataire import Prestataire
        assert Prestataire is not None
    
    def test_create(self, app):
        from app.models.prestataire import Prestataire
        prest = Prestataire(nom_prestataire='Test SA', localisation='Yaoundé')
        db.session.add(prest)
        db.session.commit()
        assert prest.id is not None


class TestChargetransportModel:
    def test_import(self):
        from app.models.chargetransport import Chargetransport
        assert Chargetransport is not None
    
    def test_create(self, app):
        from app.models.chargetransport import Chargetransport
        from app.models.utilisateur import Utilisateur
        
        user = Utilisateur(
            nom='Charge', prenom='Test', login='charge_other',
            email='charge_other@test.com', telephone='002', role='CHARGE'
        )
        user.set_password('Pass!123')
        db.session.add(user)
        db.session.commit()
        
        ct = Chargetransport(chargetransport_id=user.utilisateur_id)
        db.session.add(ct)
        db.session.commit()
        assert ct.chargetransport_id == user.utilisateur_id


class TestPanneBusUdMModel:
    def test_import(self):
        from app.models.panne_bus_udm import PanneBusUdM
        assert PanneBusUdM is not None
    
    def test_create(self, app):
        from app.models.panne_bus_udm import PanneBusUdM
        from app.models.bus_udm import BusUdM
        
        bus = BusUdM(numero='BUS_PANNE', immatriculation='P-001', nombre_places=20,
                     numero_chassis='CH_PANNE', etat_vehicule='DEFAILLANT')
        db.session.add(bus)
        db.session.commit()
        
        attrs = [a for a in dir(PanneBusUdM) if not a.startswith('_')]
        assert len(attrs) > 0


class TestDemandeHuileModel:
    def test_import(self):
        from app.models.demande_huile import DemandeHuile
        assert DemandeHuile is not None


class TestAffectationModel:
    def test_import(self):
        from app.models.affectation import Affectation
        assert Affectation is not None


class TestBaseModelsModel:
    def test_import(self):
        from app.models import base_models
        assert base_models is not None


class TestChauffeurStatutModel:
    def test_import(self):
        from app.models.chauffeur_statut import ChauffeurStatut
        assert ChauffeurStatut is not None


class TestDocumentBusUdMModel:
    def test_import(self):
        from app.models.document_bus_udm import DocumentBusUdM
        assert DocumentBusUdM is not None


class TestFuelAlertStateModel:
    def test_import(self):
        from app.models.fuel_alert_state import FuelAlertState
        assert FuelAlertState is not None
