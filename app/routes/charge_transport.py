from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.forms.trajet_depart_form import TrajetDepartForm
from app.models.chauffeur import Chauffeur
from app.models.aed import AED
from app.database import db

# Création du blueprint pour le chargé de transport
bp = Blueprint('charge_transport', __name__, url_prefix='/charge')

# Route du tableau de bord chargé de transport
@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Exemple de stats fictives pour affichage
    stats = {
        'bus_actifs': 12,
        'bus_en_maintenance': 2,
        'trajets_du_jour': 8,
        'chauffeurs_disponibles': 5
    }
    form = TrajetDepartForm()
    form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
    form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
    if form.validate_on_submit():
        from app.models.trajet import Trajet
        from app.models.chargetransport import Chargetransport
        # Récupérer l'id du chargé de transport connecté
        chargeur = Chargetransport.query.get(current_user.utilisateur_id)
        if not chargeur:
            flash("Erreur: Aucun chargé de transport associé à cet utilisateur.", "danger")
            return redirect(url_for('charge_transport.dashboard'))
        trajet = Trajet(
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.point_depart.data,
            type_passagers=form.type_passagers.data,
            nombre_places_occupees=form.nombre_places_occupees.data,
            chauffeur_id=form.chauffeur_id.data,
            numero_aed=form.numero_aed.data,
            enregistre_par=chargeur.chargetransport_id
        )
        try:
            db.session.add(trajet)
            db.session.commit()
            flash('Départ AED enregistré avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'enregistrement du trajet : {e}', 'danger')
        return redirect(url_for('charge_transport.dashboard'))
    elif request.method == 'POST':
        flash('Erreur dans le formulaire. Veuillez vérifier les champs.', 'danger')
    return render_template('dashboard_charge.html', stats=stats, form=form)

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