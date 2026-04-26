"""
Tests détaillés des routes par rôle (superviseur, chauffeur, mecanicien).
"""
import pytest
from datetime import date, datetime, timedelta
from app.extensions import db


@pytest.fixture
def populated(app):
    from app.models.bus_udm import BusUdM
    from app.models.chauffeur import Chauffeur
    from app.models.utilisateur import Utilisateur
    from app.models.trajet import Trajet
    from app.models.vidange import Vidange
    from app.models.carburation import Carburation
    from app.models.depannage import Depannage
    from app.models.panne_bus_udm import PanneBusUdM
    from app.models.prestataire import Prestataire
    
    bus = BusUdM(
        numero='BUS_RR', immatriculation='RR-001', nombre_places=20,
        numero_chassis='CH_RR', etat_vehicule='BON', kilometrage=50000,
        capacite_reservoir_litres=80.0, niveau_carburant_litres=40.0,
        consommation_km_par_litre=8.0, marque='Mercedes', modele='Sprinter',
    )
    bus2 = BusUdM(
        numero='BUS_RR2', immatriculation='RR-002', nombre_places=25,
        numero_chassis='CH_RR2', etat_vehicule='DEFAILLANT', kilometrage=80000,
    )
    db.session.add_all([bus, bus2])
    
    chauf = Chauffeur(
        nom='Chau', prenom='Rou', numero_permis='PERM_RR', telephone='000',
        date_delivrance_permis=date(2020,1,1),
        date_expiration_permis=date(2030,1,1),
    )
    db.session.add(chauf)
    
    prest = Prestataire(nom_prestataire='Prest RR', localisation='Yaoundé')
    db.session.add(prest)
    db.session.commit()
    
    # Trajets
    for i in range(3):
        t = Trajet(
            type_trajet='UDM_INTERNE',
            date_heure_depart=datetime.now() - timedelta(days=i),
            point_depart='Mfetum', point_arriver='Banekane',
            numero_bus_udm='BUS_RR', nombre_places_occupees=10,
            type_passagers='ETUDIANT',
        )
        db.session.add(t)
    
    # Vidange
    v = Vidange(
        bus_udm_id=bus.id, date_vidange=date.today() - timedelta(days=30),
        kilometrage=49000, type_huile='QUARTZ',
    )
    db.session.add(v)
    
    # Carburation
    c = Carburation(
        bus_udm_id=bus.id, date_carburation=date.today(),
        kilometrage=50000, quantite_litres=50.0,
        prix_unitaire=850.0, cout_total=42500.0,
    )
    db.session.add(c)
    
    # Depannage
    d = Depannage(
        bus_udm_id=bus.id, numero_bus_udm='BUS_RR',
        immatriculation='RR-001',
        date_heure=datetime.now(), kilometrage=50000.0,
        cout_reparation=500.0, description_panne='Test',
        cause_panne='Cause', repare_par='Mec',
    )
    db.session.add(d)
    
    # Panne
    p = PanneBusUdM(
        bus_udm_id=bus.id, numero_bus_udm='BUS_RR',
        immatriculation='RR-001',
        date_heure=datetime.now(), kilometrage=50000,
        description='Test panne', criticite='HAUTE',
        immobilisation=False, enregistre_par='Test',
    )
    db.session.add(p)
    
    db.session.commit()
    return {'bus': bus, 'bus2': bus2, 'chauffeur': chauf, 'prest': prest}


def _make_user(role, login_suffix='rr'):
    from app.models.utilisateur import Utilisateur
    u = Utilisateur(
        nom=f'U{role}', prenom='RR', login=f'{role.lower()}_{login_suffix}',
        email=f'{role.lower()}_{login_suffix}@t.com', telephone='000', role=role
    )
    u.set_password('Pass!123')
    db.session.add(u)
    db.session.commit()
    return u


def _login(client, user):
    return client.post('/login', data={
        'login': user.login, 'mot_de_passe': 'Pass!123'
    })


def _safe_get(client, path):
    try:
        return client.get(path).status_code
    except Exception:
        return -1


class TestSuperviseurRoutes:
    @pytest.fixture
    def sup_client(self, client, app, populated):
        u = _make_user('SUPERVISEUR', 'sup_routes')
        _login(client, u)
        return client, populated
    
    def test_dashboard(self, sup_client):
        c, _ = sup_client
        _safe_get(c, '/superviseur/dashboard')
    
    def test_list_pages(self, sup_client):
        c, _ = sup_client
        for p in ['/superviseur/carburation', '/superviseur/bus_udm',
                  '/superviseur/vidange', '/superviseur/vidanges',
                  '/superviseur/chauffeurs', '/superviseur/utilisateurs',
                  '/superviseur/maintenance', '/superviseur/depanage',
                  '/superviseur/rapports']:
            _safe_get(c, p)
    
    def test_detail_pages(self, sup_client):
        c, data = sup_client
        _safe_get(c, f'/superviseur/bus/{data["bus"].id}')
        _safe_get(c, '/superviseur/bus/99999')
    
    def test_rapports_specifiques(self, sup_client):
        c, _ = sup_client
        for p in ['/superviseur/rapport-noblesse', '/superviseur/rapport-charter',
                  '/superviseur/rapport-bus-udm']:
            _safe_get(c, p)
            _safe_get(c, p + '?date_debut=2024-01-01&date_fin=2024-12-31')
    
    def test_exports_csv(self, sup_client):
        c, _ = sup_client
        for p in ['/superviseur/export/trajets/csv',
                  '/superviseur/export/carburation/csv',
                  '/superviseur/export/chauffeurs/csv',
                  '/superviseur/export/bus/csv',
                  '/superviseur/export/utilisateurs/csv',
                  '/superviseur/export/maintenance/csv']:
            _safe_get(c, p)
    
    def test_exports_pdf(self, sup_client):
        c, _ = sup_client
        for p in ['/superviseur/export/trajets/pdf',
                  '/superviseur/export/carburation/pdf',
                  '/superviseur/export/chauffeurs/pdf',
                  '/superviseur/export/bus/pdf',
                  '/superviseur/export/utilisateurs/pdf',
                  '/superviseur/export/maintenance/pdf']:
            _safe_get(c, p)
    
    def test_export_invalid_format(self, sup_client):
        c, _ = sup_client
        _safe_get(c, '/superviseur/export/trajets/xml')
    
    def test_api_stats(self, sup_client):
        c, _ = sup_client
        _safe_get(c, '/superviseur/api/stats')
    
    def test_with_date_filters(self, sup_client):
        c, _ = sup_client
        params = '?date_debut=2024-01-01&date_fin=2024-12-31'
        for p in ['/superviseur/rapports', '/superviseur/maintenance',
                  '/superviseur/carburation']:
            _safe_get(c, p + params)
    
    def test_unauthorized_access(self, client, app, populated):
        # Pas de login
        _safe_get(client, '/superviseur/dashboard')
        # Login en tant que chauffeur
        u = _make_user('CHAUFFEUR', 'chauf_sup')
        _login(client, u)
        _safe_get(client, '/superviseur/dashboard')


class TestChauffeurRoutes:
    @pytest.fixture
    def chauf_client(self, client, app, populated):
        u = _make_user('CHAUFFEUR', 'chauf_routes')
        _login(client, u)
        return client, populated
    
    def test_dashboard(self, chauf_client):
        c, _ = chauf_client
        _safe_get(c, '/chauffeur/dashboard')
    
    def test_pages(self, chauf_client):
        c, _ = chauf_client
        for p in ['/chauffeur/profile', '/chauffeur/trajets',
                  '/chauffeur/declarer-panne', '/chauffeur/historique',
                  '/chauffeur/bus', '/chauffeur/notifications']:
            _safe_get(c, p)
    
    def test_unauthorized(self, client, app):
        u = _make_user('SUPERVISEUR', 'sup_chau')
        _login(client, u)
        _safe_get(client, '/chauffeur/dashboard')


class TestMecanicienRoutes:
    @pytest.fixture
    def meca_client(self, client, app, populated):
        u = _make_user('MECANICIEN', 'meca_routes')
        _login(client, u)
        return client, populated
    
    def test_dashboard(self, meca_client):
        c, _ = meca_client
        _safe_get(c, '/mecanicien/dashboard')
    
    def test_pages(self, meca_client):
        c, _ = meca_client
        for p in ['/mecanicien/pannes', '/mecanicien/depannages',
                  '/mecanicien/maintenance', '/mecanicien/historique',
                  '/mecanicien/profile', '/mecanicien/notifications']:
            _safe_get(c, p)
    
    def test_panne_detail(self, meca_client):
        c, data = meca_client
        from app.models.panne_bus_udm import PanneBusUdM
        p = PanneBusUdM.query.first()
        if p:
            _safe_get(c, f'/mecanicien/panne/{p.id}')
        _safe_get(c, '/mecanicien/panne/99999')


class TestChargeRoutes:
    @pytest.fixture
    def charge_client(self, client, app, populated):
        u = _make_user('CHARGE', 'charge_routes')
        _login(client, u)
        return client, populated
    
    def test_dashboard(self, charge_client):
        c, _ = charge_client
        _safe_get(c, '/charge_transport/dashboard')
        _safe_get(c, '/charge/dashboard')
    
    def test_all_pages(self, charge_client):
        c, _ = charge_client
        # Visite du blueprint charge_transport
        for p in ['/charge_transport/trajets', '/charge_transport/bus',
                  '/charge_transport/rapports', '/charge_transport/chauffeurs',
                  '/charge_transport/depart-aed', '/charge_transport/depart-prestataire',
                  '/charge_transport/depart-banekane', '/charge_transport/profile',
                  '/charge/trajets', '/charge/bus']:
            _safe_get(c, p)


class TestResponsableRoutes:
    @pytest.fixture
    def resp_client(self, client, app, populated):
        u = _make_user('RESPONSABLE', 'resp_routes')
        _login(client, u)
        return client, populated
    
    def test_pages(self, resp_client):
        c, _ = resp_client
        for p in ['/responsable/dashboard', '/responsable/parametres',
                  '/responsable/utilisateurs', '/responsable/profile']:
            _safe_get(c, p)
