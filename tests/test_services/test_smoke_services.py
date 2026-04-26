"""
Tests smoke pour importer et invoquer les services basiques.
Augmente le coverage en exécutant les imports et signatures de fonctions.
"""
import pytest
from datetime import date, datetime


class TestServicesImports:
    """Test que tous les services s'importent correctement."""
    
    def test_import_alert_service(self):
        from app.services import alert_service
        assert alert_service is not None
    
    def test_import_bus_service(self):
        from app.services import bus_service
        assert bus_service is not None
    
    def test_import_dashboard_service(self):
        from app.services import dashboard_service
        assert dashboard_service is not None
    
    def test_import_form_service(self):
        from app.services import form_service
        assert form_service is not None
    
    def test_import_gestion_carburation(self):
        from app.services import gestion_carburation
        assert gestion_carburation is not None
    
    def test_import_gestion_vidange(self):
        from app.services import gestion_vidange
        assert gestion_vidange is not None
    
    def test_import_maintenance_service(self):
        from app.services import maintenance_service
        assert maintenance_service is not None
    
    def test_import_notification_service(self):
        from app.services import notification_service
        assert notification_service is not None
    
    def test_import_query_service(self):
        from app.services import query_service
        assert query_service is not None
    
    def test_import_rapport_service(self):
        from app.services import rapport_service
        assert rapport_service is not None
    
    def test_import_stats_service(self):
        from app.services import stats_service
        assert stats_service is not None
    
    def test_import_trajet_service(self):
        from app.services import trajet_service
        assert trajet_service is not None


class TestTrajetServiceFunctions:
    """Tests des fonctions utilitaires du trajet_service."""
    
    def test_get_bus_autonomie_default(self, app):
        from app.services.trajet_service import _get_bus_autonomie, AUTONOMIE_KM_PAR_LITRE
        from app.models.bus_udm import BusUdM
        from app.extensions import db
        
        bus = BusUdM(numero='BUS_AUTO', immatriculation='AUTO-1', nombre_places=20,
                     numero_chassis='CH_AUTO', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        
        autonomie = _get_bus_autonomie(bus)
        assert autonomie == AUTONOMIE_KM_PAR_LITRE
    
    def test_get_bus_autonomie_custom(self, app):
        from app.services.trajet_service import _get_bus_autonomie
        from app.models.bus_udm import BusUdM
        from app.extensions import db
        
        bus = BusUdM(numero='BUS_AUTO2', immatriculation='AUTO-2', nombre_places=20,
                     numero_chassis='CH_AUTO2', etat_vehicule='BON',
                     consommation_km_par_litre=10.0)
        db.session.add(bus)
        db.session.commit()
        
        autonomie = _get_bus_autonomie(bus)
        assert autonomie == 10.0
    
    def test_get_reservoir_capacity(self, app):
        from app.services.trajet_service import _get_reservoir_capacity
        from app.models.bus_udm import BusUdM
        from app.extensions import db
        
        bus = BusUdM(numero='BUS_RES', immatriculation='RES-1', nombre_places=20,
                     numero_chassis='CH_RES', etat_vehicule='BON',
                     capacite_reservoir_litres=80.0)
        db.session.add(bus)
        db.session.commit()
        
        cap = _get_reservoir_capacity(bus)
        assert cap == 80.0
    
    def test_get_reservoir_capacity_none(self, app):
        from app.services.trajet_service import _get_reservoir_capacity
        from app.models.bus_udm import BusUdM
        from app.extensions import db
        
        bus = BusUdM(numero='BUS_RES2', immatriculation='RES-2', nombre_places=20,
                     numero_chassis='CH_RES2', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        
        cap = _get_reservoir_capacity(bus)
        assert cap is None


class TestStatsService:
    """Tests pour le service de statistiques."""
    
    def test_stats_service_callable(self, app):
        from app.services import stats_service
        # Vérifier que le module a des fonctions
        funcs = [a for a in dir(stats_service) if not a.startswith('_') and callable(getattr(stats_service, a))]
        assert len(funcs) > 0


class TestQueryService:
    """Tests pour le service de requêtes."""
    
    def test_query_service_callable(self, app):
        from app.services import query_service
        funcs = [a for a in dir(query_service) if not a.startswith('_') and callable(getattr(query_service, a))]
        assert len(funcs) > 0


class TestNotificationService:
    """Tests pour le service de notifications."""
    
    def test_notification_service_callable(self, app):
        from app.services import notification_service
        funcs = [a for a in dir(notification_service) if not a.startswith('_') and callable(getattr(notification_service, a))]
        assert len(funcs) > 0


class TestBusService:
    """Tests pour le service bus."""
    
    def test_bus_service_callable(self, app):
        from app.services import bus_service
        funcs = [a for a in dir(bus_service) if not a.startswith('_') and callable(getattr(bus_service, a))]
        assert len(funcs) > 0


class TestDashboardService:
    """Tests pour le service dashboard."""
    
    def test_dashboard_service_callable(self, app):
        from app.services import dashboard_service
        funcs = [a for a in dir(dashboard_service) if not a.startswith('_') and callable(getattr(dashboard_service, a))]
        assert len(funcs) > 0


class TestFormService:
    """Tests pour le service de formulaires."""
    
    def test_form_service_callable(self, app):
        from app.services import form_service
        funcs = [a for a in dir(form_service) if not a.startswith('_') and callable(getattr(form_service, a))]
        assert len(funcs) > 0


class TestRapportService:
    """Tests pour le service de rapports."""
    
    def test_rapport_service_callable(self, app):
        from app.services import rapport_service
        funcs = [a for a in dir(rapport_service) if not a.startswith('_') and callable(getattr(rapport_service, a))]
        assert len(funcs) > 0


class TestAlertService:
    """Tests pour le service d'alertes."""
    
    def test_alert_service_callable(self, app):
        from app.services import alert_service
        funcs = [a for a in dir(alert_service) if not a.startswith('_') and callable(getattr(alert_service, a))]
        assert len(funcs) > 0


class TestMaintenanceService:
    """Tests pour le service de maintenance."""
    
    def test_maintenance_service_callable(self, app):
        from app.services import maintenance_service
        funcs = [a for a in dir(maintenance_service) if not a.startswith('_') and callable(getattr(maintenance_service, a))]
        assert len(funcs) > 0


class TestGestionVidange:
    """Tests pour gestion_vidange."""
    
    def test_module_callable(self, app):
        from app.services import gestion_vidange
        assert gestion_vidange is not None


class TestGestionCarburation:
    """Tests pour gestion_carburation."""
    
    def test_module_callable(self, app):
        from app.services import gestion_carburation
        assert gestion_carburation is not None
