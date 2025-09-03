from flask import render_template, url_for, jsonify
from flask_login import current_user
from datetime import date, datetime
from app.models.bus_udm import BusUdM
from app.models.trajet import Trajet
from app.models.chauffeur import Chauffeur
from app.database import db
from app.utils.trafic import daily_student_trafic
from app.forms.trajet_depart_form import TrajetDepartForm
from app.forms.trajet_prestataire_form import TrajetPrestataireForm
from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm
from app.forms.trajet_sortie_hors_ville_form import TrajetSortieHorsVilleForm
# Nouveaux formulaires modernisés
from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
from app.forms.autres_trajets_form import AutresTrajetsForm
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only
def admin_only(view):
    return role_required('ADMIN')(view)

# Route du tableau de bord administrateur
@admin_only
@bp.route('/dashboard')
def dashboard():
    today = date.today()
    trajets_jour_aed = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.numero_bus_udm != None).count()
    trajets_jour_bus_agence = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.immat_bus != None).count()

    stats = {
        'bus_actifs': BusUdM.query.filter_by(etat_vehicule='BON').count(),
        'bus_actifs_change': 0,
        'bus_inactifs': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'chauffeurs': Chauffeur.query.count(),
        'trajets_jour_aed': trajets_jour_aed,
        'trajets_jour_bus_agence': trajets_jour_bus_agence,
        'trajets_jour_change': 0,
        'bus_maintenance': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'bus_maintenance_info': '',
        'etudiants': 0,
        'etudiants_change': 0
    }
    
    trafic = daily_student_trafic()
    stats['etudiants'] = trafic.get('present', 0)

    # Instancier les formulaires pour inclure les modales correspondantes dans le template
    form = TrajetDepartForm()
    form_bus = TrajetPrestataireForm()
    form_banekane_retour = TrajetBanekaneRetourForm()
    form_sortie = TrajetSortieHorsVilleForm()
    # Nouveaux formulaires modernisés
    form_trajet_interne = TrajetInterneBusUdMForm()
    form_autres_trajets = AutresTrajetsForm()

    # Renseigner les choix dynamiques dépendants de la BD
    try:
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
        form_banekane_retour.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form_banekane_retour.numero_aed.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
        form_sortie.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form_sortie.numero_aed.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
        # Nouveaux formulaires modernisés
        form_trajet_interne.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form_trajet_interne.numero_bus_udm.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
        form_autres_trajets.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form_autres_trajets.numero_bus_udm.choices = [(a.numero, a.numero) for a in BusUdM.query.all()]
    except Exception:
        # En cas d'erreur DB, laisser les choix vides pour ne pas casser le rendu
        form.chauffeur_id.choices = []
        form.numero_aed.choices = []
        form_banekane_retour.chauffeur_id.choices = []
        form_banekane_retour.numero_aed.choices = []
        form_sortie.chauffeur_id.choices = []
        form_sortie.numero_aed.choices = []
        # Nouveaux formulaires modernisés
        form_trajet_interne.chauffeur_id.choices = []
        form_trajet_interne.numero_bus_udm.choices = []
        form_autres_trajets.chauffeur_id.choices = []
        form_autres_trajets.numero_bus_udm.choices = []

    # Affiche le template HTML du dashboard admin en fournissant les formulaires
    return render_template(
        'dashboard_admin.html',
        stats=stats,
        trafic=trafic,
        form=form,
        form_bus=form_bus,
        form_banekane_retour=form_banekane_retour,
        form_sortie=form_sortie,
        # Nouveaux formulaires modernisés
        form_trajet_interne=form_trajet_interne,
        form_autres_trajets=form_autres_trajets,
        # URLs existantes
        depart_aed_url=url_for('admin.depart_aed'),
        depart_prestataire_url=url_for('admin.depart_prestataire'),
        depart_banekane_retour_url=url_for('admin.depart_banekane_retour'),
        depart_sortie_hors_ville_url=url_for('admin.depart_sortie_hors_ville'),
        # Nouvelles URLs modernisées
        trajet_interne_bus_udm_url=url_for('admin.trajet_interne_bus_udm'),
        trajet_prestataire_modernise_url=url_for('admin.trajet_prestataire_modernise'),
        autres_trajets_url=url_for('admin.autres_trajets'),
    )


@bp.route('/stats', methods=['GET'])
@admin_only
def get_stats():
    """API pour récupérer les statistiques du dashboard en JSON"""
    today = datetime.now().date()

    # Statistiques principales
    bus_actifs = BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count()
    trajets_jour_aed = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.numero_bus_udm != None).count()
    trajets_jour_bus_agence = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.immat_bus != None).count()

    # Calcul des étudiants transportés aujourd'hui
    etudiants = db.session.query(db.func.sum(Trajet.nombre_places_occupees)).filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.type_passagers == 'ETUDIANT'
    ).scalar() or 0

    # Bus en maintenance
    bus_maintenance = BusUdM.query.filter(BusUdM.etat_vehicule == 'DEFAILLANT').count()

    # Trafic temps réel (logique simplifiée)
    arrives = trajets_jour_aed + trajets_jour_bus_agence
    present = max(0, etudiants - (arrives // 2))  # Estimation
    partis = arrives // 2  # Estimation

    return jsonify({
        'stats': {
            'bus_actifs': bus_actifs,
            'trajets_jour_aed': trajets_jour_aed,
            'trajets_jour_bus_agence': trajets_jour_bus_agence,
            'etudiants': etudiants,
            'bus_maintenance': bus_maintenance
        },
        'trafic': {
            'arrives': arrives,
            'present': present,
            'partis': partis
        }
    })

# Route rapports supprimée - maintenant dans rapports.py

# Route placeholder pour la page Paramètres
@admin_only
@bp.route('/parametres')
def parametres():
    return "Page Paramètres en construction."

# Route placeholder pour la page Planifier Trajet
@admin_only
@bp.route('/planifier_trajet')
def planifier_trajet():
    return "Page Planifier Trajet en construction."

# Route placeholder pour la page Générer Rapport
@admin_only
@bp.route('/generer_rapport')
def generer_rapport():
    return "Page Générer Rapport en construction."
