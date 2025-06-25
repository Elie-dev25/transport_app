from flask import Blueprint, render_template

# Création du blueprint pour l'administrateur
bp = Blueprint('admin', __name__, url_prefix='/admin')

# Route du tableau de bord administrateur
@bp.route('/dashboard')
def dashboard():
    # Exemple de stats fictives à adapter selon tes besoins
    stats = {
        'bus_actifs': 0,
        'bus_inactifs': 0,
        'chauffeurs': 0,
        'trajets': 0
    }
    # Affiche le template HTML du dashboard admin
    return render_template('dashboard_admin.html', stats=stats)

# Route placeholder pour la page Bus AED (pour éviter les erreurs de lien)
@bp.route('/bus')
def bus():
    # Affiche une page temporaire ou un message d'information
    return "Page Bus AED en construction."

# Route placeholder pour la page Chauffeurs (pour éviter les erreurs de lien)
@bp.route('/chauffeurs')
def chauffeurs():
    # Affiche une page temporaire ou un message d'information
    return "Page Chauffeurs en construction."

# Route placeholder pour la page Utilisateurs (pour éviter les erreurs de lien)
@bp.route('/utilisateurs')
def utilisateurs():
    # Affiche une page temporaire ou un message d'information
    return "Page Utilisateurs en construction."

# Route placeholder pour la page Rapports (pour éviter les erreurs de lien)
@bp.route('/rapports')
def rapports():
    # Affiche une page temporaire ou un message d'information
    return "Page Rapports en construction."

# Route placeholder pour la page Paramètres (pour éviter les erreurs de lien)
@bp.route('/parametres')
def parametres():
    # Affiche une page temporaire ou un message d'information
    return "Page Paramètres en construction."

# Route placeholder pour la page Ajouter Bus (pour éviter les erreurs de lien)
@bp.route('/ajouter_bus')
def ajouter_bus():
    # Affiche une page temporaire ou un message d'information
    return "Page Ajouter Bus en construction."

# Route placeholder pour la page Ajouter Chauffeur (pour éviter les erreurs de lien)
@bp.route('/ajouter_chauffeur')
def ajouter_chauffeur():
    # Affiche une page temporaire ou un message d'information
    return "Page Ajouter Chauffeur en construction."

# Route placeholder pour la page Planifier Trajet (pour éviter les erreurs de lien)
@bp.route('/planifier_trajet')
def planifier_trajet():
    # Affiche une page temporaire ou un message d'information
    return "Page Planifier Trajet en construction."

# Route placeholder pour la page Générer Rapport (pour éviter les erreurs de lien)
@bp.route('/generer_rapport')
def generer_rapport():
    # Affiche une page temporaire ou un message d'information
    return "Page Générer Rapport en construction."
