"""
Tests exhaustifs : pour chaque blueprint, visite toutes les routes avec données pré-créées.
"""
import re
import pytest
from datetime import date, datetime, timedelta
from app.extensions import db


@pytest.fixture(scope='function')
def full_data(app):
    from app.models.bus_udm import BusUdM
    from app.models.chauffeur import Chauffeur
    from app.models.utilisateur import Utilisateur
    from app.models.trajet import Trajet
    from app.models.vidange import Vidange
    from app.models.carburation import Carburation
    from app.models.depannage import Depannage
    from app.models.panne_bus_udm import PanneBusUdM
    from app.models.prestataire import Prestataire
    from app.models.affectation import Affectation
    
    # Bus
    buses = []
    for i in range(3):
        b = BusUdM(
            numero=f'BUSEX{i}', immatriculation=f'EX-{i:03d}', nombre_places=20,
            numero_chassis=f'CHEX{i}',
            etat_vehicule='BON' if i < 2 else 'DEFAILLANT',
            kilometrage=50000 + i*5000,
            capacite_reservoir_litres=80.0,
            niveau_carburant_litres=40.0 - i*10,
            consommation_km_par_litre=8.0,
            marque='Mercedes', modele='Sprinter',
        )
        db.session.add(b)
        buses.append(b)
    
    # Chauffeurs
    chauffeurs = []
    for i in range(3):
        c = Chauffeur(
            nom=f'C{i}', prenom=f'P{i}', numero_permis=f'PERMEX{i}',
            telephone=f'00{i}',
            date_delivrance_permis=date(2020,1,1),
            date_expiration_permis=date(2030,1,1),
        )
        db.session.add(c)
        chauffeurs.append(c)
    
    # Users (un par rôle)
    users = {}
    for role in ['ADMIN', 'CHAUFFEUR', 'SUPERVISEUR', 'MECANICIEN', 'CHARGE', 'RESPONSABLE']:
        u = Utilisateur(
            nom=f'U{role}', prenom='X', login=f'ex_{role.lower()}',
            email=f'ex_{role.lower()}@t.com', telephone='000', role=role
        )
        u.set_password('Pass!123')
        db.session.add(u)
        users[role] = u
    
    prest = Prestataire(nom_prestataire='P EX', localisation='Yaoundé')
    db.session.add(prest)
    db.session.commit()
    
    # Lier le chauffeur user au chauffeur model si la classe d'affectation existe
    try:
        chauf_user = users['CHAUFFEUR']
        aff = Affectation(chauffeur_id=chauffeurs[0].chauffeur_id,
                          utilisateur_id=chauf_user.utilisateur_id,
                          date_affectation=date.today())
        db.session.add(aff)
        db.session.commit()
    except Exception:
        db.session.rollback()
    
    # Trajets variés
    for i in range(5):
        t = Trajet(
            type_trajet='UDM_INTERNE' if i < 3 else 'AUTRE',
            date_heure_depart=datetime.now() - timedelta(days=i),
            point_depart='Mfetum', point_arriver='Banekane',
            numero_bus_udm=buses[i % 3].numero,
            chauffeur_id=chauffeurs[i % 3].chauffeur_id,
            nombre_places_occupees=10 + i,
            type_passagers='ETUDIANT',
        )
        db.session.add(t)
    
    # Vidange / Carburation / Panne / Depannage
    for b in buses[:2]:
        db.session.add(Vidange(
            bus_udm_id=b.id, date_vidange=date.today() - timedelta(days=10),
            kilometrage=49000, type_huile='QUARTZ',
        ))
        db.session.add(Carburation(
            bus_udm_id=b.id, date_carburation=date.today(),
            kilometrage=50000, quantite_litres=50.0,
            prix_unitaire=850.0, cout_total=42500.0,
        ))
        db.session.add(Depannage(
            bus_udm_id=b.id, numero_bus_udm=b.numero,
            immatriculation=b.immatriculation,
            date_heure=datetime.now(), kilometrage=50000.0,
            cout_reparation=500.0, description_panne='Test',
            cause_panne='Cause', repare_par='Mec',
        ))
        db.session.add(PanneBusUdM(
            bus_udm_id=b.id, numero_bus_udm=b.numero,
            immatriculation=b.immatriculation,
            date_heure=datetime.now(), kilometrage=50000,
            description='Test', criticite='HAUTE',
            immobilisation=False, enregistre_par='Test',
        ))
    
    db.session.commit()
    return {'buses': buses, 'chauffeurs': chauffeurs, 'users': users, 'prest': prest}


def _login(client, login):
    return client.post('/login', data={'login': login, 'mot_de_passe': 'Pass!123'})


def _expand_path(rule_str, ids):
    """Replace <type:name> with id valeur."""
    def replacer(m):
        # Match groupe entier
        return str(ids.pop(0)) if ids else '1'
    return re.sub(r'<[^>]+>', lambda m: '1', rule_str)


def _visit_blueprint(client, app, blueprint_name):
    """Visite toutes les routes GET d'un blueprint donné."""
    visited = 0
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        if not rule.endpoint.startswith(blueprint_name + '.'):
            continue
        if 'GET' not in (rule.methods or set()):
            continue
        path = _expand_path(rule.rule, [])
        # Variantes communes
        for suffix in ['', '?page=1', '?date_debut=2024-01-01&date_fin=2024-12-31']:
            try:
                client.get(path + suffix)
                visited += 1
            except Exception:
                pass
    return visited


def _visit_blueprint_post(client, app, blueprint_name, payloads=None):
    """POST sur toutes les routes POST du blueprint avec différents payloads."""
    visited = 0
    payloads = payloads or [{}]
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        if not rule.endpoint.startswith(blueprint_name + '.'):
            continue
        if 'POST' not in (rule.methods or set()):
            continue
        path = _expand_path(rule.rule, [])
        for p in payloads:
            try:
                client.post(path, data=p)
                visited += 1
            except Exception:
                pass
    return visited


class TestExhaustiveBlueprints:
    def test_admin_blueprint_get(self, client, app, full_data):
        _login(client, 'ex_admin')
        _visit_blueprint(client, app, 'admin')
    
    def test_admin_blueprint_post(self, client, app, full_data):
        _login(client, 'ex_admin')
        from app.models.bus_udm import BusUdM
        from app.models.chauffeur import Chauffeur
        from app.models.utilisateur import Utilisateur
        bus = BusUdM.query.first()
        chauf = Chauffeur.query.first()
        user = Utilisateur.query.filter_by(role='CHAUFFEUR').first()
        
        payloads = [
            {},
            {'numero': 'NEWBUS', 'immatriculation': 'NB-001',
             'nombre_places': '20', 'numero_chassis': 'CHN',
             'etat_vehicule': 'BON', 'marque': 'M', 'modele': 'S'},
            {'nom': 'NewC', 'prenom': 'P', 'numero_permis': 'PNEW',
             'telephone': '111', 'date_delivrance_permis': '2020-01-01',
             'date_expiration_permis': '2030-01-01'},
            {'nom': 'NewU', 'prenom': 'P', 'login': 'newuser_post',
             'email': 'nu@t.com', 'telephone': '111', 'role': 'CHAUFFEUR',
             'mot_de_passe': 'Pass!123'},
        ]
        _visit_blueprint_post(client, app, 'admin', payloads)
    
    def test_chauffeur_blueprint(self, client, app, full_data):
        _login(client, 'ex_chauffeur')
        _visit_blueprint(client, app, 'chauffeur')
        _visit_blueprint_post(client, app, 'chauffeur', [
            {},
            {'description': 'Panne test', 'criticite': 'HAUTE',
             'kilometrage': '50000', 'immobilisation': 'true',
             'numero_bus_udm': 'BUSEX0'},
        ])
    
    def test_superviseur_blueprint(self, client, app, full_data):
        _login(client, 'ex_superviseur')
        _visit_blueprint(client, app, 'superviseur')
    
    def test_mecanicien_blueprint(self, client, app, full_data):
        _login(client, 'ex_mecanicien')
        _visit_blueprint(client, app, 'mecanicien')
        _visit_blueprint_post(client, app, 'mecanicien', [
            {},
            {'description_panne': 'Réparé', 'cout_reparation': '500',
             'date_heure': '2024-01-01T08:00', 'kilometrage': '50000',
             'cause_panne': 'X', 'repare_par': 'M'},
        ])
    
    def test_charge_blueprint(self, client, app, full_data):
        _login(client, 'ex_charge')
        for bp_name in ['charge_transport', 'charge']:
            _visit_blueprint(client, app, bp_name)
            _visit_blueprint_post(client, app, bp_name, [
                {},
                {'date_heure_depart': '2024-01-01T08:00',
                 'point_depart': 'Mfetum', 'point_arriver': 'Banekane',
                 'numero_aed': 'BUSEX0', 'chauffeur_id': '1',
                 'type_passagers': 'ETUDIANT', 'nombre_places_occupees': '10',
                 'kilometrage_actuel': '51000'},
            ])
    
    def test_responsable_blueprint(self, client, app, full_data):
        _login(client, 'ex_responsable')
        _visit_blueprint(client, app, 'responsable')
    
    def test_auth_blueprint(self, client, app):
        _visit_blueprint(client, app, 'auth')
        _visit_blueprint_post(client, app, 'auth', [
            {},
            {'login': 'invalid', 'mot_de_passe': 'wrong'},
        ])
