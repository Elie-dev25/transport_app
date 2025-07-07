from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

"""Centralisation des extensions Flask.
Importe `db` et `login_manager` où tu en as besoin sans risque de circular import.
"""

db = SQLAlchemy()
login_manager = LoginManager()

# Vue de login par défaut
login_manager.login_view = "auth.login"
