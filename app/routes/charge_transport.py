from flask import Blueprint, render_template

# Création du blueprint pour le chargé de transport
bp = Blueprint('charge_transport', __name__, url_prefix='/charge')

# Route du tableau de bord chargé de transport
@bp.route('/dashboard')
def dashboard():
    # Exemple de stats fictives pour affichage
    stats = {
        'bus_actifs': 12,
        'bus_en_maintenance': 2,
        'trajets_du_jour': 8,
        'chauffeurs_disponibles': 5
    }
    return render_template('dashboard_charge.html', stats=stats)

# Route pour la gestion des bus
@bp.route('/bus')
def bus():
    # Placeholder pour la page bus du chargé de transport
    return render_template('bus.html')

# Route pour la gestion des chauffeurs
@bp.route('/chauffeurs')
def chauffeurs():
    return render_template('chauffeurs.html') if 'chauffeurs.html' in globals() else "Page Chauffeurs (à implémenter)"

# Route pour la gestion des rapports
@bp.route('/rapports')
def rapports():
    return render_template('rapports.html') if 'rapports.html' in globals() else "Page Rapports (à implémenter)"

# Route pour les paramètres
@bp.route('/parametres')
def parametres():
    return render_template('parametres.html') if 'parametres.html' in globals() else "Page Paramètres (à implémenter)"

# Route pour le départ AED Banekane
@bp.route('/depart-aed-banekane')
def depart_aed_banekane():
    # Placeholder pour la page de départ AED Banekane
    return "Page Départ AED Banekane (à implémenter)"

# Route pour le départ Bus Agence
@bp.route('/depart-bus-agence')
def depart_bus_agence():
    # Placeholder pour la page de départ Bus Agence
    return "Page Départ Bus Agence (à implémenter)"

# Route pour le retour Banekane
@bp.route('/depart-banekane-retour')
def depart_banekane_retour():
    # Placeholder pour la page de retour Banekane
    return "Page Retour Banekane (à implémenter)"

# Route pour générer un rapport
@bp.route('/generer-rapport')
def generer_rapport():
    # Placeholder pour la génération de rapport
    return "Génération de rapport (à implémenter)"