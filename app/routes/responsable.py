"""
Routes responsable - Dashboard distinct avec traçabilité
Toutes les autres actions utilisent les routes admin existantes
"""

from flask import Blueprint, render_template

# Réutilisation des services existants
from app.services.dashboard_service import DashboardService
from app.services.form_service import FormService

# Réutilisation des décorateurs de sécurité existants
from app.routes.common import admin_or_responsable

# Réutilisation des formulaires existants
from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
from app.forms.trajet_prestataire_form import TrajetPrestataireForm
from app.forms.autres_trajets_form import AutresTrajetsForm

# Création du blueprint responsable (juste pour le dashboard)
bp = Blueprint('responsable', __name__, url_prefix='/responsable')

@bp.route('/dashboard', methods=['GET', 'POST'])
@admin_or_responsable
def dashboard():
    """
    Dashboard responsable distinct - Réutilise les services admin
    Toutes les autres actions redirigent vers les routes admin
    """
    # Réutiliser le service centralisé (même logique que admin)
    stats = DashboardService.get_common_stats()
    role_stats = DashboardService.get_role_specific_stats('RESPONSABLE')
    
    # Fusionner les statistiques
    stats.update(role_stats)
    
    # Trafic temps réel
    trafic = stats.get('trafic', {})
    
    # Réutiliser FormService pour les formulaires
    form_trajet_interne = TrajetInterneBusUdMForm()
    form_bus = TrajetPrestataireForm()
    form_autres_trajets = AutresTrajetsForm()
    
    # Peupler les formulaires avec le service existant (même logique que admin)
    try:
        FormService.populate_multiple_forms(
            form_trajet_interne, form_bus, form_autres_trajets,
            bus_filter='BON_ONLY'  # Responsable peut voir tous les bus en bon état
        )
    except Exception as e:
        print(f"Erreur lors du remplissage des listes déroulantes: {e}")
        # FormService gère déjà les erreurs en interne
        form_trajet_interne.chauffeur_id.choices = []
        form_trajet_interne.numero_bus_udm.choices = []
        form_autres_trajets.chauffeur_id.choices = []
        form_autres_trajets.numero_bus_udm.choices = []
    
    # UTILISER le template responsable spécifique pour la traçabilité
    return render_template(
        'roles/responsable/dashboard_responsable.html',  # Template responsable distinct
        stats=stats,
        trafic=trafic,
        form_trajet_interne=form_trajet_interne,
        form_bus=form_bus,
        form_autres_trajets=form_autres_trajets
    )


# Routes de redirection avec traçabilité pour le responsable
@bp.route('/bus')
@admin_or_responsable
def bus():
    """Redirection vers gestion des bus avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.bus', source='responsable'))


@bp.route('/trajets')
@admin_or_responsable
def trajets():
    """Redirection vers gestion des trajets avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.trajets', source='responsable'))


@bp.route('/chauffeurs')
@admin_or_responsable
def chauffeurs():
    """Redirection vers gestion des chauffeurs avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.chauffeurs', source='responsable'))


@bp.route('/depanage')
@admin_or_responsable
def depanage():
    """Redirection vers dépannage avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.depanage', source='responsable'))


@bp.route('/carburation')
@admin_or_responsable
def carburation():
    """Redirection vers carburation avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.carburation', source='responsable'))


@bp.route('/rapports')
@admin_or_responsable
def rapports():
    """Redirection vers rapports avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.rapports', source='responsable'))


@bp.route('/utilisateurs')
@admin_or_responsable
def utilisateurs():
    """Redirection vers gestion des utilisateurs avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.utilisateurs', source='responsable'))


@bp.route('/parametres')
@admin_or_responsable
def parametres():
    """Redirection vers paramètres avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.parametres', source='responsable'))


@bp.route('/bus/details/<int:bus_id>')
@admin_or_responsable
def details_bus(bus_id):
    """Redirection vers détails bus avec traçabilité responsable"""
    from flask import redirect, url_for
    return redirect(url_for('admin.details_bus', bus_id=bus_id, source='responsable'))
