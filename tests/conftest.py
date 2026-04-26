"""
Configuration pytest pour les tests TransportUdM.
Utilise create_app() pour maximiser le coverage.
"""
import pytest
import os
import sys

# Définir les variables d'environnement AVANT tout import
os.environ['FLASK_ENV'] = 'testing'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only-12345678'
os.environ['LDAP_SERVER'] = 'ldap://test-server'
os.environ['LDAP_DOMAIN'] = 'test.local'
os.environ['BASE_DN'] = 'dc=test,dc=local'

# Path racine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='function')
def app():
    """Crée l'application Flask via la factory pour les tests."""
    # Patcher Config AVANT l'import de create_app pour désactiver les options pool incompatibles SQLite
    from app.config import Config
    Config.SQLALCHEMY_ENGINE_OPTIONS = {}
    Config.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    Config.WTF_CSRF_ENABLED = False
    Config.TESTING = True
    
    from app import create_app
    from app.extensions import db
    
    flask_app = create_app()
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False,
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Client de test Flask."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Session de base de données."""
    from app.extensions import db
    yield db.session
    db.session.rollback()


@pytest.fixture
def sample_user(app):
    """Utilisateur de test."""
    from app.models.utilisateur import Utilisateur
    from app.extensions import db
    
    user = Utilisateur(
        nom='Test',
        prenom='User',
        login='testuser',
        email='test@example.com',
        telephone='0123456789',
        role='ADMIN'
    )
    user.set_password('TestPassword123!')
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user


@pytest.fixture
def sample_chauffeur(app):
    """Chauffeur de test."""
    from datetime import date
    from app.models.chauffeur import Chauffeur
    from app.extensions import db
    
    chauffeur = Chauffeur(
        nom='Chauffeur',
        prenom='Test',
        numero_permis='PERM123456',
        telephone='0123456780',
        date_delivrance_permis=date(2020, 1, 1),
        date_expiration_permis=date(2030, 1, 1)
    )
    db.session.add(chauffeur)
    db.session.commit()
    return chauffeur


@pytest.fixture
def sample_bus(app):
    """Bus de test."""
    from app.models.bus_udm import BusUdM
    from app.extensions import db
    
    bus = BusUdM(
        numero='BUS001',
        immatriculation='AB-123-CD',
        marque='Mercedes',
        modele='Sprinter',
        nombre_places=20,
        numero_chassis='CHASSIS001',
        etat_vehicule='BON'
    )
    db.session.add(bus)
    db.session.commit()
    return bus


@pytest.fixture
def authenticated_client(client, sample_user, app):
    """Client authentifié."""
    with client.session_transaction() as sess:
        sess['user_id'] = str(sample_user.utilisateur_id)
        sess['user_role'] = sample_user.role
        sess['user_login'] = sample_user.login
    return client
