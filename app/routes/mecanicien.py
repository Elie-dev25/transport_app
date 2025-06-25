from flask import Blueprint, render_template

# Création du blueprint pour le mécanicien
bp = Blueprint('mecanicien', __name__, url_prefix='/mecanicien')

# Route du tableau de bord mécanicien
@bp.route('/dashboard')
def dashboard():
    # Affiche un message de bienvenue pour le mécanicien
    return "Bienvenue sur le tableau de bord mécanicien."