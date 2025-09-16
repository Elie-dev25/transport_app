"""
Configuration centralisée de l'application
Phase 5 - Configuration unifiée pour tous les environnements
"""

import os
from datetime import timedelta
from .constants import AppConstants


class Config:
    """Configuration de base de l'application Flask"""

    # Informations de l'application
    APP_NAME = AppConstants.APP_NAME
    APP_VERSION = AppConstants.APP_VERSION
    APP_DESCRIPTION = AppConstants.APP_DESCRIPTION

    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_change_in_production'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 heure

    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/transport_udm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=AppConstants.SESSION_TIMEOUT)
    SESSION_COOKIE_SECURE = False  # True en production avec HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Upload de fichiers
    MAX_CONTENT_LENGTH = AppConstants.MAX_UPLOAD_SIZE
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}

    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = AppConstants.CACHE_TIMEOUT

    # Pagination
    POSTS_PER_PAGE = AppConstants.DEFAULT_PAGE_SIZE
    MAX_SEARCH_RESULTS = 50

    # Configuration SMTP
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'true').lower() in ('1', 'true', 'yes')
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', 'false').lower() in ('1', 'true', 'yes')
    MAIL_FROM = os.environ.get('MAIL_FROM') or 'noreply@transport-udm.com'

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

    # Fonctionnalités
    ENABLE_LDAP = os.environ.get('ENABLE_LDAP', 'false').lower() in ('1', 'true', 'yes')
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() in ('1', 'true', 'yes')
    ENABLE_SMS_NOTIFICATIONS = os.environ.get('ENABLE_SMS_NOTIFICATIONS', 'false').lower() in ('1', 'true', 'yes')

    @staticmethod
    def init_app(app):
        """Initialise la configuration de l'application"""
        # Créer le dossier d'upload s'il n'existe pas
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder and not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Configuration du logging
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')

            file_handler = RotatingFileHandler(
                f'logs/{app.config.get("LOG_FILE")}',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
            app.logger.addHandler(file_handler)

            app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
            app.logger.info(f'{AppConstants.APP_NAME} startup')


class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    ENV = "development"

    # Base de données de développement (utilise la même DB que production pour l'instant)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:@localhost/transport_udm'

    # Sécurité relâchée pour le développement
    WTF_CSRF_ENABLED = False  # Désactivé pour faciliter les tests
    SESSION_COOKIE_SECURE = False

    # Logging verbeux
    LOG_LEVEL = 'DEBUG'

    # Cache désactivé
    CACHE_TYPE = 'null'

    # Email en mode debug (affichage console)
    MAIL_SUPPRESS_SEND = True

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Configuration spécifique au développement
        import logging
        logging.basicConfig(level=logging.DEBUG)
        app.logger.info('Mode développement activé')


class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DEBUG = True
    ENV = "testing"

    # Base de données en mémoire pour les tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Sécurité désactivée pour les tests
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

    # Cache désactivé
    CACHE_TYPE = 'null'

    # Email désactivé
    MAIL_SUPPRESS_SEND = True

    # Session courte pour les tests
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('Mode test activé')


class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    ENV = "production"

    # Sécurité renforcée
    SESSION_COOKIE_SECURE = True  # HTTPS requis
    WTF_CSRF_ENABLED = True

    # Base de données de production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:@localhost/transport_udm'

    # Logging en production
    LOG_LEVEL = 'WARNING'

    # Cache Redis en production
    CACHE_TYPE = 'redis' if os.environ.get('REDIS_URL') else 'simple'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')

    # Email activé
    MAIL_SUPPRESS_SEND = False

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Configuration spécifique à la production
        import logging
        from logging.handlers import SMTPHandler

        # Envoi d'emails pour les erreurs critiques
        if app.config.get('SMTP_HOST'):
            auth = None
            if app.config.get('SMTP_USERNAME'):
                auth = (app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])

            secure = None
            if app.config.get('SMTP_USE_TLS'):
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config['SMTP_HOST'], app.config['SMTP_PORT']),
                fromaddr=app.config['MAIL_FROM'],
                toaddrs=['admin@transport-udm.com'],
                subject=f'{AppConstants.APP_NAME} - Erreur Critique',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        app.logger.info('Mode production activé')


# Configuration par défaut selon l'environnement
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Retourne la configuration selon l'environnement"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config.get(config_name, config['default'])



