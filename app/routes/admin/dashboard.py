from flask import render_template, url_for, jsonify
from flask_login import current_user
from datetime import date, datetime

# Services centralisés (Phase 1 Refactoring)
from app.services.dashboard_service import DashboardService
from app.services.form_service import FormService

# Formulaires
from app.forms.trajet_depart_form import TrajetDepartForm
from app.forms.trajet_prestataire_form import TrajetPrestataireForm
from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm
from app.forms.trajet_sortie_hors_ville_form import TrajetSortieHorsVilleForm
from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
from app.forms.autres_trajets_form import AutresTrajetsForm

# Décorateurs et blueprint
from app.routes.common import role_required, superviseur_access, business_action_required
from . import bp

# Définition du décorateur admin_only (permet aussi superviseur en lecture seule)
def admin_only(view):
    return superviseur_access(view)

# Route du tableau de bord administrateur (accès complet + superviseur lecture seule)
@admin_only
@bp.route('/dashboard')
def dashboard():
    """
    Dashboard admin refactorisé - Phase 1
    Utilise DashboardService pour éliminer la duplication de code
    """
    # Utiliser le service centralisé au lieu du code dupliqué
    stats = DashboardService.get_common_stats()
    role_stats = DashboardService.get_role_specific_stats('ADMIN')

    # Fusionner les statistiques
    stats.update(role_stats)

    # Trafic temps réel (déjà inclus dans stats via DashboardService)
    trafic = stats.get('trafic', {})

    # Formulaires
    form_aed = TrajetDepartForm()
    form_bus = TrajetPrestataireForm()
    form_banekane_retour = TrajetBanekaneRetourForm()
    form_sortie = TrajetSortieHorsVilleForm()
    # Nouveaux formulaires modernisés
    form_trajet_interne = TrajetInterneBusUdMForm()
    form_autres_trajets = AutresTrajetsForm()

    # Utiliser FormService pour peupler tous les formulaires (élimine 30+ lignes dupliquées)
    try:
        FormService.populate_multiple_forms(
            form_aed, form_bus, form_banekane_retour, form_sortie,
            form_trajet_interne, form_autres_trajets,
            bus_filter='BON_ONLY'  # Admin peut voir tous les bus en bon état
        )
    except Exception as e:
        print(f"Erreur lors du remplissage des listes déroulantes: {e}")
        # FormService gère déjà les erreurs en interne
        form_trajet_interne.chauffeur_id.choices = []
        form_trajet_interne.numero_bus_udm.choices = []
        form_autres_trajets.chauffeur_id.choices = []
        form_autres_trajets.numero_bus_udm.choices = []

    return render_template(
        'roles/admin/dashboard_admin.html',
        stats=stats,
        trafic=trafic,
        form_aed=form_aed,
        form_bus=form_bus,
        form_banekane_retour=form_banekane_retour,
        form_sortie=form_sortie,
        form_trajet_interne=form_trajet_interne,
        form_autres_trajets=form_autres_trajets
    )

@bp.route('/stats', methods=['GET'])
@admin_only
def get_stats():
    """
    API pour récupérer les statistiques du dashboard en JSON
    Refactorisé - Phase 1 : utilise DashboardService
    """
    # Utiliser le service centralisé au lieu du code dupliqué
    stats = DashboardService.get_common_stats()
    role_stats = DashboardService.get_role_specific_stats('ADMIN')

    # Fusionner les statistiques
    stats.update(role_stats)

    # Extraire les données pour l'API
    trafic = stats.get('trafic', {})
    arrives = trafic.get('arrives', 0)
    partis = trafic.get('partis', 0)
    present = max(0, arrives - partis)
    
    return jsonify({
        'stats': {
            'bus_actifs': stats.get('bus_actifs', 0),
            'trajets_jour_aed': stats.get('trajets_jour_aed', 0),
            'trajets_jour_bus_agence': stats.get('trajets_jour_bus_agence', 0),
            'etudiants': stats.get('etudiants', 0),
            'bus_maintenance': stats.get('bus_maintenance', 0)
        },
        'trafic': {
            'arrives': arrives,
            'present': present,
            'partis': partis
        },
        'timestamp': datetime.now().isoformat()
    })

# Route de consultation pour superviseurs (lecture seule)
@superviseur_access
@bp.route('/consultation')
def consultation():
    """
    Dashboard en lecture seule pour les superviseurs
    Refactorisé - Phase 1 : utilise DashboardService
    """
    # Utiliser le service centralisé au lieu du code dupliqué
    stats = DashboardService.get_common_stats()
    role_stats = DashboardService.get_role_specific_stats('SUPERVISEUR')

    # Fusionner les statistiques
    stats.update(role_stats)
    trafic = stats.get('trafic', {})

    # Derniers trajets pour affichage (utiliser QueryService si nécessaire)
    from app.models.trajet import Trajet  # Import local pour éviter les erreurs
    derniers_trajets = Trajet.query.order_by(Trajet.date_heure_depart.desc()).limit(10).all()

    return render_template('roles/admin/consultation.html',
                         stats=stats,
                         trafic=trafic,
                         derniers_trajets=derniers_trajets,
                         active_page='consultation')
