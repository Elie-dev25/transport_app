from flask import Flask
from app.config import Config
from app.extensions import db, login_manager


# Fonction de création de l'application Flask
# Initialise l'application, la configuration et enregistre les blueprints

import os


def create_app():
    app = Flask(__name__)

    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        from app.config import ProductionConfig as CurrentConfig
    else:
        from app.config import DevelopmentConfig as CurrentConfig

    app.config.from_object(CurrentConfig)  # Charge la configuration adaptée

    db.init_app(app)  # Initialise la base de données avec l'application

    # Initialisation de Flask-Login
    login_manager.init_app(app)

    from flask import jsonify, request, redirect, url_for
    from flask_login import LoginManager
    # Handler pour AJAX : renvoie JSON au lieu de redirect si pas authentifié
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Session expirée ou non authentifié.'}), 401
        return redirect(url_for('auth.login'))

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

    # Filtre Jinja pour afficher les statuts avec mapping UI (sans changer la BD)
    def status_label(value: str) -> str:
        if value == 'DEFAILLANT':
            return 'HORS_SERVICE'
        return value
    app.jinja_env.filters['status_label'] = status_label

    @app.route('/')
    def accueil():
        from flask import render_template
        return render_template('welcome.html')

    return app  # Retourne l'application Flask prête à l'emploi