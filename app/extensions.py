from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

"""Centralisation des extensions Flask.
Importe `db`, `login_manager` et `csrf` où tu en as besoin sans risque de circular import.
"""

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Vue de login par défaut
login_manager.login_view = "auth.login"
