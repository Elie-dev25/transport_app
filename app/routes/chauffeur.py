from flask import Blueprint, render_template

# Création du blueprint pour le chauffeur
bp = Blueprint('chauffeur', __name__, url_prefix='/chauffeur')

# Route du tableau de bord chauffeur
@bp.route('/dashboard')
def dashboard():
    # Affiche un message de bienvenue pour le chauffeur
    return "Bienvenue sur le tableau de bord chauffeur."