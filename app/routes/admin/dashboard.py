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
from app.models.prestataire import Prestataire
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

    # Calcul des étudiants présents sur le campus (arrivées - départs)
    # Arrivées : départs depuis Mfetum/Ancienne mairie vers le campus
    arrives = db.session.query(db.func.sum(Trajet.nombre_places_occupees)).filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.type_passagers == 'ETUDIANT',
        Trajet.point_depart.in_(['Mfetum', 'Ancienne mairie'])
    ).scalar() or 0
    
    # Départs : départs depuis Banekane (campus) vers l'extérieur
    departs = db.session.query(db.func.sum(Trajet.nombre_places_occupees)).filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.type_passagers == 'ETUDIANT',
        Trajet.point_depart == 'Banekane'
    ).scalar() or 0
    
    # Étudiants présents = arrivées - départs
    etudiants = arrives - departs

    stats = {
        'bus_actifs': BusUdM.query.filter_by(etat_vehicule='BON').count(),
        'bus_actifs_change': 0,
        'bus_inactifs': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'chauffeurs': Chauffeur.query.count(),
        'trajets_jour_aed': trajets_jour_aed,
        'trajets_jour_bus_agence': trajets_jour_bus_agence,
        'trajets_jour_change': 0,
        'bus_maintenance': BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'etudiants': etudiants
    }

    # Trafic temps réel
    trafic = daily_student_trafic()

    # Formulaires
    form_aed = TrajetDepartForm()
    form_bus = TrajetPrestataireForm()
    form_banekane_retour = TrajetBanekaneRetourForm()
    form_sortie = TrajetSortieHorsVilleForm()
    # Nouveaux formulaires modernisés
    form_trajet_interne = TrajetInterneBusUdMForm()
    form_autres_trajets = AutresTrajetsForm()

    # Renseigner les choix dynamiques dépendants de la BD
    try:
        # Récupérer les chauffeurs, bus et prestataires
        chauffeurs = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        bus_udm = [(b.numero, b.numero) for b in BusUdM.query.all()]
        prestataires = [(p.id, p.nom_prestataire) for p in Prestataire.query.all()]

        # Anciens formulaires
        form_aed.chauffeur_id.choices = chauffeurs
        form_aed.numero_aed.choices = bus_udm  # Note: utilise encore numero_aed
        form_bus.nom_prestataire.choices = prestataires
        form_banekane_retour.chauffeur_id.choices = chauffeurs
        form_banekane_retour.numero_aed.choices = bus_udm
        form_sortie.chauffeur_id.choices = chauffeurs
        form_sortie.numero_aed.choices = bus_udm

        # Nouveaux formulaires modernisés
        form_trajet_interne.chauffeur_id.choices = chauffeurs
        form_trajet_interne.numero_bus_udm.choices = bus_udm
        form_autres_trajets.chauffeur_id.choices = chauffeurs
        form_autres_trajets.numero_bus_udm.choices = bus_udm

    except Exception as e:
        print(f"Erreur lors du remplissage des listes déroulantes: {e}")
        # En cas d'erreur DB, laisser les choix vides pour ne pas casser le rendu
        form_aed.chauffeur_id.choices = []
        form_aed.numero_aed.choices = []
        form_bus.nom_prestataire.choices = []
        form_banekane_retour.chauffeur_id.choices = []
        form_banekane_retour.numero_aed.choices = []
        form_sortie.chauffeur_id.choices = []
        form_sortie.numero_aed.choices = []
        form_trajet_interne.chauffeur_id.choices = []
        form_trajet_interne.numero_bus_udm.choices = []
        form_autres_trajets.chauffeur_id.choices = []
        form_autres_trajets.numero_bus_udm.choices = []

    return render_template(
        'dashboard_admin.html',
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
    """API pour récupérer les statistiques du dashboard en JSON"""
    today = datetime.now().date()
    
    # Statistiques principales
    bus_actifs = BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count()
    trajets_jour_aed = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.numero_bus_udm != None).count()
    trajets_jour_bus_agence = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.immat_bus != None).count()
    
    # Calcul des étudiants présents sur le campus (arrivées - départs)
    # Arrivées : départs depuis Mfetum/Ancienne mairie vers le campus
    arrives_api = db.session.query(db.func.sum(Trajet.nombre_places_occupees)).filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.type_passagers == 'ETUDIANT',
        Trajet.point_depart.in_(['Mfetum', 'Ancienne mairie'])
    ).scalar() or 0
    
    # Départs : départs depuis Banekane (campus) vers l'extérieur
    departs_api = db.session.query(db.func.sum(Trajet.nombre_places_occupees)).filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.type_passagers == 'ETUDIANT',
        Trajet.point_depart == 'Banekane'
    ).scalar() or 0
    
    # Étudiants présents = arrivées - départs
    etudiants = arrives_api - departs_api
    
    # Bus en maintenance
    bus_maintenance = BusUdM.query.filter(BusUdM.etat_vehicule == 'DEFAILLANT').count()
    
    # Trafic temps réel - utiliser la même logique que trafic.py
    # Arrivées = étudiants venus sur le campus (depuis Mfetum/Ancienne mairie)
    arrives = arrives_api
    # Départs = étudiants partis du campus (depuis Banekane)  
    partis = departs_api
    # Présents = arrivées - départs
    present = max(0, arrives - partis)
    
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
