from flask import Flask
from app.config import Config
from app.database import db
from flask_login import LoginManager  # Ajout pour Flask-Login


# Fonction de création de l'application Flask
# Initialise l'application, la configuration et enregistre les blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Charge la configuration depuis le fichier config.py

    db.init_app(app)  # Initialise la base de données avec l'application

    # Initialisation de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    from app.models.utilisateur import Utilisateur
    @login_manager.user_loader
    def load_user(user_id):
        return Utilisateur.query.get(int(user_id))

    # Importation et enregistrement des blueprints (modules de routes)
    from app.routes import auth
    app.register_blueprint(auth.bp)
    from app.routes import admin
    app.register_blueprint(admin.bp)
    from app.routes import chauffeur, mecanicien, charge_transport
    app.register_blueprint(chauffeur.bp)
    app.register_blueprint(mecanicien.bp)
    app.register_blueprint(charge_transport.bp)
    from app.routes.admin_ajax import bp_ajax
    app.register_blueprint(bp_ajax, url_prefix='/admin')

    return app  # Retourne l'application Flask prête à l'emploi