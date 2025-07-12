from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.aed import AED
from app.database import db  # Ajout de l'import manquant
from datetime import datetime

# Création du blueprint pour l'administrateur
bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.routes.common import role_required

# Appliquer le décorateur rôle ADMIN à toutes les routes du blueprint

def admin_only(view):
    return role_required('ADMIN')(view)

bp.before_request(lambda: None)  # Placeholder pour pouvoir ajouter le décorateur via dispatch


# Route du tableau de bord administrateur
@admin_only
@bp.route('/dashboard')
def dashboard():
    from datetime import date
    from app.models.trajet import Trajet
    today = date.today()
    trajets_jour_aed = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.numero_aed != None).count()
    trajets_jour_bus_agence = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.immat_bus != None).count()

    from app.models.chauffeur import Chauffeur
    stats = {
        'bus_actifs': AED.query.filter_by(etat_vehicule='BON').count(),
        'bus_actifs_change': 0,
        'bus_inactifs': AED.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'chauffeurs': Chauffeur.query.count(),
        'trajets_jour_aed': trajets_jour_aed,
        'trajets_jour_bus_agence': trajets_jour_bus_agence,
        'trajets_jour_change': 0,
        'bus_maintenance': AED.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'bus_maintenance_info': '',
        'etudiants': 0,
        'etudiants_change': 0
    }
    from app.utils.trafic import daily_student_trafic
    trafic = daily_student_trafic()
    stats['etudiants'] = trafic.get('present', 0)
    # Affiche le template HTML du dashboard admin
    return render_template('dashboard_admin.html', stats=stats, trafic=trafic)

# Route pour la page Bus AED qui affiche la liste des bus depuis la base
@admin_only
@bp.route('/bus')
def bus():
    bus_list = AED.query.order_by(AED.numero).all()
    return render_template('bus_aed.html', bus_list=bus_list)

# Route pour la page Chauffeurs qui affiche la liste des chauffeurs depuis la base
@admin_only
@bp.route('/chauffeurs')
def chauffeurs():
    from app.models.chauffeur import Chauffeur
    chauffeur_list = Chauffeur.query.order_by(Chauffeur.nom).all()
    return render_template('chauffeurs.html', chauffeur_list=chauffeur_list, active_page='chauffeurs')

# Route pour la page Utilisateurs qui affiche la liste des utilisateurs depuis la base
@admin_only
@bp.route('/utilisateurs')
def utilisateurs():
    from app.models.utilisateur import Utilisateur
    user_list = Utilisateur.query.order_by(Utilisateur.nom_utilisateur).all()
    return render_template('utilisateurs.html', user_list=user_list, active_page='utilisateurs')

# Route placeholder pour la page Rapports (pour éviter les erreurs de lien)
@admin_only
@bp.route('/rapports')
def rapports():
    # Affiche une page temporaire ou un message d'information
    return "Page Rapports en construction."

# Route placeholder pour la page Paramètres (pour éviter les erreurs de lien)
@admin_only
@bp.route('/parametres')
def parametres():
    # Affiche une page temporaire ou un message d'information
    return "Page Paramètres en construction."

# Route pour la page Ajouter Bus qui gère l'affichage et la soumission du formulaire d'ajout d'un bus AED
@admin_only
@bp.route('/ajouter_bus', methods=['GET', 'POST'])
def ajouter_bus():
    if request.method == 'POST':
        numero = request.form.get('numero')
        niveau_carburant = request.form.get('niveau_carburant')
        niveau_huile = request.form.get('niveau_huile')
        seuil_critique_huile = request.form.get('seuil_critique_huile')
        etat_vehicule = request.form.get('etat_vehicule')
        nombre_places = request.form.get('nombre_places')
        derniere_maintenance = request.form.get('derniere_maintenance')

        if not all([numero, niveau_carburant, niveau_huile, seuil_critique_huile, etat_vehicule, nombre_places, derniere_maintenance]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('ajouter_bus.html', next_num=numero)

        nouveau_aed = AED(
            numero=numero,
            niveau_carburant=float(niveau_carburant),
            niveau_huile=float(niveau_huile),
            seuil_critique_huile=float(seuil_critique_huile),
            etat_vehicule=etat_vehicule,
            nombre_places=int(nombre_places),
            derniere_maintenance=datetime.strptime(derniere_maintenance, '%Y-%m-%d').date()
        )
        db.session.add(nouveau_aed)
        db.session.commit()
        flash('Bus AED ajouté avec succès !', 'success')
        return redirect(url_for('admin.dashboard'))

    # Préfixe automatique pour le numéro
    next_num = "AED-"
    return render_template('ajouter_bus.html', next_num=next_num)

# Route placeholder pour la page Ajouter Chauffeur (pour éviter les erreurs de lien)
@admin_only
@bp.route('/ajouter_chauffeur')
def ajouter_chauffeur():
    # Affiche une page temporaire ou un message d'information
    return "Page Ajouter Chauffeur en construction."

# Route placeholder pour la page Planifier Trajet (pour éviter les erreurs de lien)
@admin_only
@bp.route('/planifier_trajet')
def planifier_trajet():
    # Affiche une page temporaire ou un message d'information
    return "Page Planifier Trajet en construction."

# Route placeholder pour la page Générer Rapport (pour éviter les erreurs de lien)
@admin_only
@bp.route('/generer_rapport')
def generer_rapport():
    # Affiche une page temporaire ou un message d'information
    return "Page Générer Rapport en construction."

# Route pour supprimer un bus en AJAX via son id
@admin_only
@bp.route('/supprimer_bus_ajax/<int:bus_id>', methods=['POST'])
def supprimer_bus_ajax(bus_id):
    bus = AED.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    db.session.delete(bus)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bus supprimé avec succès.'})

# Route pour supprimer un chauffeur en AJAX via son id
@admin_only
@bp.route('/supprimer_chauffeur_ajax/<int:chauffeur_id>', methods=['POST'])
def supprimer_chauffeur_ajax(chauffeur_id):
    from app.models.chauffeur import Chauffeur
    chauffeur = Chauffeur.query.get(chauffeur_id)
    if not chauffeur:
        return jsonify({'success': False, 'message': 'Chauffeur introuvable.'}), 404
    db.session.delete(chauffeur)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Chauffeur supprimé avec succès.'})

# Route pour supprimer un utilisateur en AJAX via son id
@admin_only
@bp.route('/supprimer_utilisateur_ajax/<int:user_id>', methods=['POST'])
def supprimer_utilisateur_ajax(user_id):
    from app.models.utilisateur import Utilisateur
    user = Utilisateur.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable.'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Utilisateur supprimé avec succès.'})

# Route du tableau de bord mécanicien
@admin_only
@bp.route('/dashboard_mecanicien')
def dashboard_mecanicien():
    from app.models.aed import AED
    bus_list = AED.query.order_by(AED.numero).all()
    return render_template('dashboard_mecanicien.html', bus_list=bus_list)
