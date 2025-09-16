"""
Routes responsable - Dashboard distinct avec traçabilité
Toutes les autres actions utilisent les routes admin existantes
"""

from flask import Blueprint, render_template
from flask_login import current_user

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
    
    # RÉUTILISER EXACTEMENT le template admin avec paramètre responsable_mode
    return render_template(
        'roles/admin/dashboard_admin.html',  # Template admin identique
        stats=stats,
        trafic=trafic,
        form_trajet_interne=form_trajet_interne,
        form_bus=form_bus,
        form_autres_trajets=form_autres_trajets,
        responsable_mode=True  # Flag pour distinguer du mode admin
    )
