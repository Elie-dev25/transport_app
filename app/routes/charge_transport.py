from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.forms.trajet_depart_form import TrajetDepartForm
from app.forms.trajet_prestataire_form import TrajetPrestataireForm
from app.models.chauffeur import Chauffeur
from app.models.bus_udm import BusUdM
from app.models.prestataire import Prestataire
from app.models.trajet import Trajet
from app.database import db
from app.utils.trafic import daily_student_trafic
from datetime import date
from app.services.trajet_service import (
    enregistrer_depart_aed,
    enregistrer_depart_prestataire,
    enregistrer_depart_banekane_retour,
)

# Création du blueprint pour le chargé de transport
bp = Blueprint('charge_transport', __name__, url_prefix='/charge')

# Route du tableau de bord chargé de transport
@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    from app.models.trajet import Trajet
    today = date.today()
    # Nombre total de trajets du jour (aligné avec le dashboard admin)
    trajets_jour_aed = Trajet.query.filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.numero_aed != None
    ).count()
    trajets_jour_prestataire = Trajet.query.filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.immat_bus != None
    ).count()
    # Statistiques trafic étudiants temps réel
    trafic = daily_student_trafic()

    # Exemple d'autres stats (à ajuster plus tard)
    stats = {
        'bus_actifs': BusUdM.query.filter_by(etat_vehicule='BON').count(),
        'bus_en_maintenance': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'bus_maintenance': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'trajets_jour_aed': trajets_jour_aed,
        'trajets_jour_prestataire': trajets_jour_prestataire,
        'trajets_jour_change': 0,
        'chauffeurs_disponibles': 5,
        'etudiants': trafic['present']
    }
    form = TrajetDepartForm()
    form_bus = TrajetPrestataireForm()
    # Initialisation du formulaire Banekane retour
    from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm
    form_banekane_retour = TrajetBanekaneRetourForm()
    form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
    form.numero_aed.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
    form_banekane_retour.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
    form_banekane_retour.numero_aed.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
    if form.validate_on_submit():
        ok, msg = enregistrer_depart_aed(form, current_user)
        flash(msg, 'success' if ok else 'danger')
        return redirect(url_for('charge_transport.dashboard'))

    elif request.method == 'POST':
        flash('Erreur dans le formulaire. Veuillez vérifier les champs.', 'danger')
    chauffeurs_list = Chauffeur.query.all()
    prestataire_list = Prestataire.query.all()
    return render_template('dashboard_charge.html', stats=stats, trafic=trafic, form=form, form_bus=form_bus, form_banekane_retour=form_banekane_retour)

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

# Route pour le départ AED (Ajax)
@bp.route('/depart-aed', methods=['POST'])
def depart_aed():
    """Enregistrement d'un départ AED pour Banekane (AJAX, JSON)"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = TrajetDepartForm()
        # Actualiser les choix dépendants de la BD
        from app.models.chauffeur import Chauffeur
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
        if form.validate_on_submit():
            ok, msg = enregistrer_depart_aed(form, current_user)
            return jsonify({'success': ok, 'message': msg}), (200 if ok else 500)
        else:
            return jsonify({'success': False, 'message': 'Erreur dans le formulaire. Veuillez vérifier les champs.'}), 400
    return jsonify({'success': False, 'message': 'Requête non autorisée.'}), 400

# Route pour le départ AED Banekane
@bp.route('/depart-aed-banekane')
def depart_aed_banekane():
    # Placeholder pour la page de départ AED Banekane
    return "Page Départ AED Banekane (à implémenter)"

# Route pour le départ Bus Agence
@bp.route('/depart-prestataire', methods=['POST'])
def depart_prestataire():
    """Enregistrement d'un départ Bus Agence via soumission AJAX."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        ok, msg = enregistrer_depart_prestataire(request.form, current_user)
        return jsonify({'success': ok, 'message': msg}), (200 if ok else 400)
    # fallback
    return jsonify({'success': False, 'message': 'Erreur inconnue, veuillez réessayer.'}), 500

# Route pour le retour Banekane
from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm

@bp.route('/depart-banekane-retour', methods=['POST'])
def depart_banekane_retour():
    """Enregistrement d'un départ de Banekane (retour) via soumission AJAX."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = TrajetBanekaneRetourForm()
        # Remplir dynamiquement les choix
        from app.models.chauffeur import Chauffeur
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
        if form.validate_on_submit():
            ok, msg = enregistrer_depart_banekane_retour(form, current_user)
            return jsonify({'success': ok, 'message': msg}), (200 if ok else 500)
        else:
            return jsonify({'success': False, 'message': 'Erreur dans le formulaire. Veuillez vérifier les champs.'}), 400
    # fallback
    return jsonify({'success': False, 'message': 'Erreur inconnue, veuillez réessayer.'}), 500

# Route pour générer un rapport
@bp.route('/generer-rapport')
def generer_rapport():
    # Placeholder pour la génération de rapport
    return "Génération de rapport (à implémenter)"