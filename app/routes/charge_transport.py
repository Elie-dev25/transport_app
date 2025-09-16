from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import date

# Services centralisés (Phase 1 Refactoring)
from app.services.dashboard_service import DashboardService
from app.services.form_service import FormService
from app.services.trajet_service import (
    enregistrer_trajet_interne_bus_udm,
    enregistrer_trajet_prestataire_modernise,
    enregistrer_autres_trajets,
)

# Formulaires
from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
from app.forms.trajet_prestataire_form import TrajetPrestataireForm
from app.forms.autres_trajets_form import AutresTrajetsForm

# Modèles (imports locaux pour éviter les erreurs)
from app.models.bus_udm import BusUdM

# Création du blueprint pour le chargé de transport
bp = Blueprint('charge_transport', __name__, url_prefix='/charge')

# Route du tableau de bord chargé de transport
@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    Dashboard chargé de transport refactorisé - Phase 1
    Utilise DashboardService pour éliminer la duplication de code
    """
    # Utiliser le service centralisé au lieu du code dupliqué
    stats = DashboardService.get_common_stats()
    role_stats = DashboardService.get_role_specific_stats('CHARGE')

    # Fusionner les statistiques
    stats.update(role_stats)

    # Trafic temps réel (déjà inclus dans stats via DashboardService)
    trafic = stats.get('trafic', {})
    # Nouveaux formulaires modernisés (identiques à ceux de l'admin)
    form_trajet_interne = TrajetInterneBusUdMForm()
    form_bus = TrajetPrestataireForm()
    form_autres_trajets = AutresTrajetsForm()

    # Utiliser FormService pour peupler tous les formulaires (élimine duplication)
    FormService.populate_multiple_forms(
        form_trajet_interne, form_bus, form_autres_trajets,
        bus_filter='BON_ONLY'  # Chargé transport voit les bus en bon état
    )

    return render_template(
        'roles/charge_transport/dashboard_charge.html',
        stats=stats,
        trafic=trafic,
        form_trajet_interne=form_trajet_interne,
        form_bus=form_bus,
        form_autres_trajets=form_autres_trajets
    )

# Route pour la gestion des bus
@bp.route('/bus')
def bus():
    # Page Bus pour le chargé de transport avec le bon sidebar
    buses = BusUdM.query.all()
    return render_template(
        'pages/bus_udm.html',
        bus_list=buses,
        current_user=current_user,
        active_page='bus_udm',
        readonly=False,
        base_template='roles/charge_transport/_base_charge.html'
    )

# Route pour la gestion des chauffeurs
@bp.route('/chauffeurs')
def chauffeurs():
    from app.models.chauffeur import Chauffeur
    from app.models.chauffeur_statut import ChauffeurStatut

    chauffeur_list = Chauffeur.query.order_by(Chauffeur.nom).all()

    # Ajouter les statuts actuels pour chaque chauffeur
    for chauffeur in chauffeur_list:
        chauffeur.statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur.chauffeur_id)

    return render_template('legacy/chauffeurs.html', chauffeur_list=chauffeur_list, active_page='chauffeurs')

# Route pour la gestion des rapports
@bp.route('/rapports')
def rapports():
    return render_template('pages/rapports.html') if 'rapports.html' in globals() else "Page Rapports (à implémenter)"

# Route pour les paramètres
@bp.route('/parametres')
def parametres():
    return render_template('pages/parametres.html') if 'parametres.html' in globals() else "Page Paramètres (à implémenter)"

# Nouvelles routes AJAX modernisées (identiques à l'admin)

@bp.route('/trajet_interne_bus_udm', methods=['POST'])
def trajet_interne_bus_udm():
    """Route pour les trajets internes avec bus UdM (remplace depart_aed)"""
    form = TrajetInterneBusUdMForm(request.form)

    # Peupler les choix dynamiques avant validation
    FormService.populate_trajet_form_choices(form)

    if not form.validate():
        return jsonify({'success': False, 'message': 'Formulaire invalide', 'errors': form.errors}), 400

    ok, msg = enregistrer_trajet_interne_bus_udm(form, current_user)
    status = 200 if ok else 400
    return jsonify({'success': ok, 'message': msg}), status

# Route pour le départ AED Banekane
@bp.route('/depart-aed-banekane')
def depart_aed_banekane():
    # Placeholder pour la page de départ AED Banekane
    return "Page Départ AED Banekane (à implémenter)"

@bp.route('/trajet_prestataire_modernise', methods=['POST'])
def trajet_prestataire_modernise():
    """Route pour les trajets prestataires modernisés"""
    form = TrajetPrestataireForm(request.form)

    # Peupler les choix dynamiques avant validation
    FormService.populate_trajet_form_choices(form)

    if not form.validate():
        return jsonify({'success': False, 'message': 'Formulaire invalide', 'errors': form.errors}), 400

    ok, msg = enregistrer_trajet_prestataire_modernise(form, current_user)
    status = 200 if ok else 400
    return jsonify({'success': ok, 'message': msg}), status

@bp.route('/autres_trajets', methods=['POST'])
def autres_trajets():
    """Route pour les autres trajets (remplace sortie hors ville et banekane retour)"""
    form = AutresTrajetsForm(request.form)

    # Peupler les choix dynamiques avant validation
    FormService.populate_trajet_form_choices(form)

    if not form.validate():
        return jsonify({'success': False, 'message': 'Formulaire invalide', 'errors': form.errors}), 400

    ok, msg = enregistrer_autres_trajets(form, current_user)
    status = 200 if ok else 400
    return jsonify({'success': ok, 'message': msg}), status

# Route pour générer un rapport
@bp.route('/generer-rapport')
def generer_rapport():
    # Placeholder pour la génération de rapport
    return "Génération de rapport (à implémenter)"