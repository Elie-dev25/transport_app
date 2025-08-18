import os

# Classe de configuration de l'application Flask
class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'  # Clé secrète pour la sécurité des sessions
    # Chaîne de connexion à la base de données MySQL (adapter user/motdepasse si besoin)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/transport_udm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactive le suivi des modifications SQLAlchemy (meilleure performance)

    # Configuration SMTP (lues exclusivement depuis les variables d'environnement)
    SMTP_HOST = os.environ.get('SMTP_HOST')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '0')) if os.environ.get('SMTP_PORT') else None
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', '').lower() in ('1', 'true', 'yes')
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', '').lower() in ('1', 'true', 'yes')
    MAIL_FROM = os.environ.get('MAIL_FROM')


class DevelopmentConfig(Config):
    """Configuration pour le développement."""
    DEBUG = True
    ENV = "development"


class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False
    ENV = "production"



