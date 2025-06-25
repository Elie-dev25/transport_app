from flask import Blueprint, render_template

# Création du blueprint pour le chargé de transport
bp = Blueprint('charge_transport', __name__, url_prefix='/charge')

# Route du tableau de bord chargé de transport
@bp.route('/dashboard')
def dashboard():
    # Affiche un message de bienvenue pour le chargé de transport
    return "Bienvenue sur le tableau de bord chargé de transport."