import os

# Classe de configuration de l'application Flask
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'  # Clé secrète pour la sécurité des sessions
    # Chaîne de connexion à la base de données MySQL (adapter user/motdepasse si besoin)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/transport_udm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactive le suivi des modifications SQLAlchemy (meilleure performance)