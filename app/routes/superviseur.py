"""
Routes superviseur - Accès en lecture seule utilisant les services réutilisables
Sécurisé avec des URLs dédiées /superviseur/*
"""

from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta

from app.routes.common import superviseur_only, superviseur_access
from app.services import StatsService, BusService, MaintenanceService, RapportService
from app.models.prestataire import Prestataire

# Création du blueprint superviseur
bp = Blueprint('superviseur', __name__, url_prefix='/superviseur')


@bp.route('/dashboard')
@superviseur_only
def dashboard():
    """
    Dashboard superviseur - Réutilise la logique admin avec interface superviseur
    """
    try:
        # Vérifier l'existence des services requis
        if not all([StatsService, BusService, MaintenanceService, RapportService]):
            raise ImportError("Services requis non disponibles")
            
        # Récupérer les données via les services
        from datetime import date
        from app.models.bus_udm import BusUdM
        from app.models.trajet import Trajet
        from app.models.chauffeur import Chauffeur
        from app.database import db
        from app.utils.trafic import daily_student_trafic

        today = date.today()
        trajets_jour_aed = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.numero_bus_udm != None).count()
        trajets_jour_bus_agence = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.immat_bus != None).count()

        # Calcul des étudiants présents sur le campus
        arrives = db.session.query(db.func.sum(Trajet.nombre_places_occupees)).filter(
            db.func.date(Trajet.date_heure_depart) == today,
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart.in_(['Mfetum', 'Ancienne Mairie'])
        ).scalar() or 0

        departs = db.session.query(db.func.sum(Trajet.nombre_places_occupees)).filter(
            db.func.date(Trajet.date_heure_depart) == today,
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart == 'Banekane'
        ).scalar() or 0

        etudiants = arrives - departs

        # Statistiques identiques à l'admin
        stats = {
            'bus_actifs': BusUdM.query.filter(BusUdM.etat_vehicule != 'DEFAILLANT').count(),
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

        # Utiliser le template superviseur dédié
        return render_template(
            'roles/superviseur/dashboard.html',  # Template superviseur
            stats=stats,
            trafic=trafic,
            readonly=True,
            superviseur_mode=True
        )

    except ImportError as e:
        return render_template(
            'superviseur/error.html',
            message="Services non disponibles. Contactez l'administrateur.",
            readonly=True
        )
    except Exception as e:
        return render_template(
            'superviseur/error.html',
            message=f"Erreur lors du chargement du dashboard: {str(e)}",
            readonly=True
        )


@bp.route('/carburation')
@superviseur_only
def carburation():
    """
    Gestion des carburations - Supervision
    """
    try:
        from app.services.gestion_carburation import build_bus_carburation_list, get_carburation_history
        from app.models.bus_udm import BusUdM
        from app.models.chauffeur import Chauffeur
        from app.models.utilisateur import Utilisateur

        # --- Tableau d'état carburation (via service partagé) ---
        bus_carburation = build_bus_carburation_list()
        bus_list = BusUdM.query.order_by(BusUdM.numero).all()

        # --- Historique des carburations ---
        # Récupérer tous les numéros AED distincts pour le filtre
        numeros_aed = [bus.numero for bus in bus_list]
        selected_numero = request.args.get('numero_aed')
        date_debut_str = request.args.get('date_debut')
        date_fin_str = request.args.get('date_fin')
        date_debut = None
        date_fin = None

        try:
            if date_debut_str:
                date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            if date_fin_str:
                date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            date_debut = None
            date_fin = None

        if selected_numero:
            historique_carburation = get_carburation_history(selected_numero, date_debut, date_fin)
        else:
            historique_carburation = get_carburation_history(None, date_debut, date_fin)

        # --- Récupérer les chauffeurs et utilisateurs pour les modals ---
        chauffeurs = Chauffeur.query.all()
        utilisateurs = Utilisateur.query.filter(Utilisateur.role.in_(['ADMIN', 'RESPONSABLE', 'MECANICIEN'])).all()

        return render_template(
            'pages/carburation.html',
            bus_carburation=bus_carburation,
            bus_list=bus_list,
            historique_carburation=historique_carburation,
            numeros_aed=numeros_aed,
            selected_numero=selected_numero,
            date_debut=date_debut,
            date_fin=date_fin,
            chauffeurs=chauffeurs,
            utilisateurs=utilisateurs,
            readonly=True,
            superviseur_mode=True,
            base_template='roles/superviseur/_base_superviseur.html'
        )

    except Exception as e:
        return render_template(
            'roles/superviseur/error.html',
            message=f"Erreur lors du chargement: {str(e)}",
            readonly=True
        )


@bp.route('/bus_udm')
@superviseur_only
def bus_udm():
    """
    Gestion des bus UdM - Supervision
    """
    try:
        from app.models.bus_udm import BusUdM

        # Récupérer tous les bus
        buses = BusUdM.query.all()

        return render_template(
            'pages/bus_udm.html',
            bus_list=buses,  # Le template attend bus_list
            readonly=True,
            superviseur_mode=True,
            base_template='roles/superviseur/_base_superviseur.html'
        )

    except Exception as e:
        return render_template(
            'superviseur/error.html',
            message=f"Erreur lors du chargement: {str(e)}",
            readonly=True
        )


@bp.route('/vidange')
@bp.route('/vidanges')  # Alias pour compatibilité
@superviseur_only
def vidanges():
    """
    Gestion des vidanges - Supervision
    """
    try:
        from app.services.gestion_vidange import get_vidange_history, build_bus_vidange_list
        from app.models.bus_udm import BusUdM

        # --- Tableau d'état vidange (via service partagé) ---
        bus_vidange = build_bus_vidange_list()
        bus_list = BusUdM.query.order_by(BusUdM.numero).all()

        # --- Historique des vidanges ---
        # Récupérer tous les numéros AED distincts pour le filtre
        numeros_bus_udm = [bus.numero for bus in bus_list]
        selected_numero = request.args.get('numero_aed')
        date_debut_str = request.args.get('date_debut')
        date_fin_str = request.args.get('date_fin')
        date_debut = None
        date_fin = None

        try:
            if date_debut_str:
                date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            if date_fin_str:
                date_fin = datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            date_debut = None
            date_fin = None

        if selected_numero:
            historique_vidange = get_vidange_history(selected_numero, date_debut, date_fin)
        else:
            historique_vidange = get_vidange_history(None, date_debut, date_fin)

        return render_template(
            'pages/vidange.html',
            bus_vidange=bus_vidange,
            bus_list=bus_list,
            historique_vidange=historique_vidange,
            numeros_bus_udm=numeros_bus_udm,
            selected_numero=selected_numero,
            date_debut=date_debut,
            date_fin=date_fin,
            readonly=True,
            superviseur_mode=True,
            base_template='roles/superviseur/_base_superviseur.html'
        )

    except Exception as e:
        return render_template(
            'roles/superviseur/error.html',
            message=f"Erreur lors du chargement: {str(e)}",
            readonly=True
        )


@bp.route('/chauffeurs')
@superviseur_only
def chauffeurs():
    """
    Gestion des chauffeurs - Supervision
    """
    try:
        from app.models.chauffeur import Chauffeur

        # Récupérer tous les chauffeurs
        chauffeurs = Chauffeur.query.all()

        return render_template(
            'legacy/chauffeurs.html',
            chauffeur_list=chauffeurs,
            readonly=True,
            superviseur_mode=True,
            base_template='roles/superviseur/_base_superviseur.html'
        )

    except Exception as e:
        return render_template(
            'superviseur/error.html',
            message=f"Erreur lors du chargement: {str(e)}",
            readonly=True
        )


@bp.route('/utilisateurs')
@superviseur_only
def utilisateurs():
    """
    Gestion des utilisateurs - Supervision
    """
    try:
        from app.models.utilisateur import Utilisateur

        # Récupérer tous les utilisateurs
        utilisateurs = Utilisateur.query.all()

        return render_template(
            'pages/utilisateurs.html',
            utilisateurs=utilisateurs,
            readonly=True,
            superviseur_mode=True,
            base_template='roles/superviseur/_base_superviseur.html'
        )

    except Exception as e:
        return render_template(
            'superviseur/error.html',
            message=f"Erreur lors du chargement: {str(e)}",
            readonly=True
        )


@bp.route('/bus/<int:bus_id>')
@superviseur_only
def bus_detail(bus_id):
    """
    Détail d'un bus en lecture seule
    Utilise BusService pour récupérer les données
    """
    try:
        # Vérifier la disponibilité des services
        if not BusService or not MaintenanceService:
            return render_template('roles/superviseur/error.html',
                                 message="Services non disponibles", readonly=True)
        
        # Récupérer les détails du bus
        bus = BusService.get_bus_by_id(bus_id, include_stats=True)
        if not bus:
            return render_template('roles/superviseur/error.html',
                                 message="Bus non trouvé", readonly=True)
        
        # Récupérer l'historique de maintenance
        pannes = MaintenanceService.get_pannes_by_bus(bus_id)
        vidanges = MaintenanceService.get_vidanges_by_bus(bus_id)
        
        return render_template(
            'superviseur/bus_detail.html',
            bus=bus,
            pannes=pannes[:10],      # Limiter à 10
            vidanges=vidanges[:10],  # Limiter à 10
            readonly=True
        )
        
    except Exception as e:
        return render_template('roles/superviseur/error.html',
                             message=f"Erreur: {str(e)}", readonly=True)


@bp.route('/maintenance')
@superviseur_only
def maintenance():
    """
    Vue d'ensemble de la maintenance en lecture seule
    Utilise MaintenanceService pour récupérer les données
    """
    try:
        # Vérifier la disponibilité des services
        if not MaintenanceService or not StatsService:
            raise ImportError("Services de maintenance non disponibles")

        # Récupérer les données de maintenance
        pannes_recentes = MaintenanceService.get_all_pannes(limit=20, include_resolved=False)
        vidanges_recentes = MaintenanceService.get_all_vidanges(limit=10)
        carburations_recentes = MaintenanceService.get_all_carburations(limit=10)

        # Statistiques de maintenance
        today = date.today()
        maintenance_stats = StatsService.get_maintenance_stats(today)

        return render_template(
            'superviseur/maintenance.html',
            pannes_recentes=pannes_recentes,
            vidanges_recentes=vidanges_recentes,
            carburations_recentes=carburations_recentes,
            maintenance_stats=maintenance_stats,
            readonly=True
        )

    except Exception as e:
        return render_template('roles/superviseur/error.html',
                             message=f"Erreur: {str(e)}", readonly=True)


@bp.route('/depanage')
@superviseur_only
def depanage():
    """
    Vue dépannage en lecture seule pour superviseur
    """
    try:
        from app.models.panne_bus_udm import PanneBusUdM
        from app.models.depannage import Depannage
        from app.models.bus_udm import BusUdM
        from app.database import db

        # Récupérer les pannes non résolues, plus récentes en premier
        pannes = (
            db.session.query(PanneBusUdM, BusUdM)
            .outerjoin(BusUdM, PanneBusUdM.bus_udm_id == BusUdM.id)
            .filter((PanneBusUdM.resolue == False) | (PanneBusUdM.resolue.is_(None)))
            .order_by(PanneBusUdM.date_heure.desc())
            .all()
        )

        # Récupérer l'historique des dépannages
        depannages = (
            db.session.query(Depannage, BusUdM)
            .outerjoin(BusUdM, Depannage.bus_udm_id == BusUdM.id)
            .order_by(Depannage.date_heure.desc())
            .all()
        )

        # Utiliser le template superviseur dédié
        return render_template('roles/superviseur/depanage.html',
                             pannes=pannes,
                             depannages=depannages,
                             active_page='depanage',
                             readonly=True)

    except Exception as e:
        return render_template('roles/superviseur/error.html',
                             message=f"Erreur: {str(e)}", readonly=True)


@bp.route('/rapports')
@superviseur_only
def rapports():
    """
    Page des rapports superviseur - Utilise les services pour récupérer les données
    """
    try:
        from datetime import date, timedelta
        from sqlalchemy import func, and_
        from app.models.trajet import Trajet
        from app.models.bus_udm import BusUdM

        # Données pour les rapports rapides
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Statistiques du jour
        trajets_today = Trajet.query.filter(func.date(Trajet.date_heure_depart) == today).all()
        stats_today = {
            'total_trajets': len(trajets_today),
            'total_passagers': sum([t.nombre_places_occupees or 0 for t in trajets_today]),
            'passagers_etudiants': sum([t.nombre_places_occupees or 0 for t in trajets_today if t.type_passagers == 'ETUDIANT']),
            'passagers_personnel': sum([t.nombre_places_occupees or 0 for t in trajets_today if t.type_passagers == 'PERSONNEL']),
            'passagers_malades': sum([t.nombre_places_occupees or 0 for t in trajets_today if t.type_passagers == 'MALADE']),
        }

        # Statistiques de la semaine
        trajets_week = Trajet.query.filter(
            and_(
                func.date(Trajet.date_heure_depart) >= week_start,
                func.date(Trajet.date_heure_depart) <= today
            )
        ).all()
        stats_week = {
            'total_trajets': len(trajets_week),
            'total_passagers': sum([t.nombre_places_occupees or 0 for t in trajets_week]),
            'passagers_etudiants': sum([t.nombre_places_occupees or 0 for t in trajets_week if t.type_passagers == 'ETUDIANT']),
            'passagers_personnel': sum([t.nombre_places_occupees or 0 for t in trajets_week if t.type_passagers == 'PERSONNEL']),
            'passagers_malades': sum([t.nombre_places_occupees or 0 for t in trajets_week if t.type_passagers == 'MALADE']),
            'jours_periode': (today - week_start).days + 1
        }

        # Statistiques du mois
        trajets_month = Trajet.query.filter(
            and_(
                func.date(Trajet.date_heure_depart) >= month_start,
                func.date(Trajet.date_heure_depart) <= today
            )
        ).all()
        stats_month = {
            'total_trajets': len(trajets_month),
            'total_passagers': sum([t.nombre_places_occupees or 0 for t in trajets_month]),
            'passagers_etudiants': sum([t.nombre_places_occupees or 0 for t in trajets_month if t.type_passagers == 'ETUDIANT']),
            'passagers_personnel': sum([t.nombre_places_occupees or 0 for t in trajets_month if t.type_passagers == 'PERSONNEL']),
            'passagers_malades': sum([t.nombre_places_occupees or 0 for t in trajets_month if t.type_passagers == 'MALADE']),
            'jours_periode': (today - month_start).days + 1
        }

        # Statistiques de la flotte (noms harmonisés avec admin)
        bus_list = BusUdM.query.all()
        stats_fleet = {
            'total_bus': len(bus_list),
            'bus_actifs': len([b for b in bus_list if b.etat_vehicule != 'DEFAILLANT']),
            'bus_maintenance': len([b for b in bus_list if b.etat_vehicule == 'DEFAILLANT']),
            'km_total': sum([b.kilometrage or 0 for b in bus_list]),
            'moyenne_km': round(sum([b.kilometrage or 0 for b in bus_list]) / max(1, len(bus_list)), 0)
        }

        # Regrouper toutes les statistiques
        stats = {
            'today': stats_today,
            'week': stats_week,
            'month': stats_month,
            'fleet': stats_fleet
        }

        # Utiliser le template admin avec mode superviseur
        return render_template(
            'pages/rapports.html',  # Template admin existant
            stats=stats,
            readonly=True,
            superviseur_mode=True
        )

    except Exception as e:
        return render_template('roles/superviseur/error.html',
                             message=f"Erreur lors du chargement des rapports: {str(e)}", readonly=True)


@bp.route('/rapport-noblesse')
@superviseur_only
def rapport_noblesse():
    """
    Rapport Noblesse - Wrapper de la route admin
    """
    try:
        # Importer et utiliser la fonction admin
        from app.routes.admin.rapports import rapport_noblesse as admin_rapport

        # Exécuter la logique admin dans le contexte superviseur
        # Note: Nous devons adapter cela car c'est une fonction de route
        from flask import request
        from datetime import date, datetime, timedelta
        from app.models.trajet import Trajet
        from app.database import db

        # Logique identique à l'admin
        today = date.today()
        start_date = today.replace(day=1)
        end_date = today

        periode = request.args.get('periode', 'mois')
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')

        if date_debut and date_fin:
            try:
                start_date = datetime.strptime(date_debut, '%Y-%m-%d').date()
                end_date = datetime.strptime(date_fin, '%Y-%m-%d').date()
            except ValueError:
                start_date = today.replace(day=1)
                end_date = today
        elif periode == 'jour':
            start_date = today
            end_date = today
        elif periode == 'semaine':
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif periode == 'annee':
            start_date = today.replace(month=1, day=1)
            end_date = today

        # Requête des trajets Noblesse (via relation Prestataire)
        from app.models.prestataire import Prestataire
        from sqlalchemy import and_, func

        trajets = db.session.query(Trajet).join(Prestataire).filter(
            and_(
                Trajet.type_trajet == 'PRESTATAIRE',
                Prestataire.nom_prestataire == 'Noblesse',
                func.date(Trajet.date_heure_depart) >= start_date,
                func.date(Trajet.date_heure_depart) <= end_date
            )
        ).order_by(Trajet.date_heure_depart.desc()).all()

        # Calculer les statistiques
        total_trajets = len(trajets)
        total_passagers = sum([t.nombre_places_occupees or 0 for t in trajets])

        # Formatage de la date pour l'affichage
        from datetime import datetime
        mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        date_actuelle = datetime.now()
        mois_actuel = mois_noms[date_actuelle.month - 1]
        periode_formatee = f"{mois_actuel} {date_actuelle.year}"

        # Récupérer les informations du prestataire Noblesse
        prestataire_info = Prestataire.query.filter_by(nom_prestataire='Noblesse').first()

        return render_template(
            'legacy/rapport_entity.html',  # Template admin existant
            trajets=trajets,
            start_date=start_date,
            end_date=end_date,
            periode=periode,
            entity_name='Noblesse',
            entity_type='prestataire',
            prestataire_info=prestataire_info,
            total_trajets=total_trajets,
            total_passagers=total_passagers,
            readonly=True,
            superviseur_mode=True,
            periode_formatee=periode_formatee
        )

    except Exception as e:
        return render_template('roles/superviseur/error.html',
                             message=f"Erreur: {str(e)}", readonly=True)


@bp.route('/rapport-charter')
@superviseur_only
def rapport_charter():
    """
    Rapport Charter - Wrapper de la route admin
    """
    try:
        from flask import request
        from datetime import date, datetime, timedelta
        from app.models.trajet import Trajet
        from app.database import db

        # Logique identique à l'admin
        today = date.today()
        start_date = today.replace(day=1)
        end_date = today

        periode = request.args.get('periode', 'mois')
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')

        if date_debut and date_fin:
            try:
                start_date = datetime.strptime(date_debut, '%Y-%m-%d').date()
                end_date = datetime.strptime(date_fin, '%Y-%m-%d').date()
            except ValueError:
                start_date = today.replace(day=1)
                end_date = today
        elif periode == 'jour':
            start_date = today
            end_date = today
        elif periode == 'semaine':
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif periode == 'annee':
            start_date = today.replace(month=1, day=1)
            end_date = today

        # Requête des trajets Charter (via relation Prestataire)
        from app.models.prestataire import Prestataire
        from sqlalchemy import and_, func

        trajets = db.session.query(Trajet).join(Prestataire).filter(
            and_(
                Trajet.type_trajet == 'PRESTATAIRE',
                Prestataire.nom_prestataire == 'Charter',
                func.date(Trajet.date_heure_depart) >= start_date,
                func.date(Trajet.date_heure_depart) <= end_date
            )
        ).order_by(Trajet.date_heure_depart.desc()).all()

        # Calculer les statistiques
        total_trajets = len(trajets)
        total_passagers = sum([t.nombre_places_occupees or 0 for t in trajets])

        # Formatage de la date pour l'affichage
        mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        date_actuelle = datetime.now()
        mois_actuel = mois_noms[date_actuelle.month - 1]
        periode_formatee = f"{mois_actuel} {date_actuelle.year}"

        # Récupérer les informations du prestataire Charter
        prestataire_info = Prestataire.query.filter_by(nom_prestataire='Charter').first()

        return render_template(
            'legacy/rapport_entity.html',
            trajets=trajets,
            start_date=start_date,
            end_date=end_date,
            periode=periode,
            entity_name='Charter',
            entity_type='prestataire',
            prestataire_info=prestataire_info,
            total_trajets=total_trajets,
            total_passagers=total_passagers,
            readonly=True,
            superviseur_mode=True,
            periode_formatee=periode_formatee
        )

    except Exception as e:
        return render_template('roles/superviseur/error.html',
                             message=f"Erreur: {str(e)}", readonly=True)


@bp.route('/rapport-bus-udm')
@superviseur_only
def rapport_bus_udm():
    """
    Rapport Bus UdM - Wrapper de la route admin
    """
    try:
        from flask import request
        from datetime import date, datetime, timedelta
        from app.models.trajet import Trajet
        from app.database import db

        # Logique identique à l'admin
        today = date.today()
        start_date = today.replace(day=1)
        end_date = today

        periode = request.args.get('periode', 'mois')
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')

        if date_debut and date_fin:
            try:
                start_date = datetime.strptime(date_debut, '%Y-%m-%d').date()
                end_date = datetime.strptime(date_fin, '%Y-%m-%d').date()
            except ValueError:
                start_date = today.replace(day=1)
                end_date = today
        elif periode == 'jour':
            start_date = today
            end_date = today
        elif periode == 'semaine':
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif periode == 'annee':
            start_date = today.replace(month=1, day=1)
            end_date = today

        # Requête des trajets Bus UdM (type_trajet UDM_INTERNE)
        from sqlalchemy import func

        trajets = Trajet.query.filter(
            Trajet.type_trajet == 'UDM_INTERNE',
            func.date(Trajet.date_heure_depart) >= start_date,
            func.date(Trajet.date_heure_depart) <= end_date
        ).order_by(Trajet.date_heure_depart.desc()).all()

        # Calculer les statistiques
        total_trajets = len(trajets)
        total_passagers = sum([t.nombre_places_occupees or 0 for t in trajets])

        # Formatage de la date pour l'affichage
        mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        date_actuelle = datetime.now()
        mois_actuel = mois_noms[date_actuelle.month - 1]
        periode_formatee = f"{mois_actuel} {date_actuelle.year}"

        return render_template(
            'legacy/rapport_entity.html',
            trajets=trajets,
            start_date=start_date,
            end_date=end_date,
            periode=periode,
            entity_name='Bus UdM',
            entity_type='bus_udm',
            total_trajets=total_trajets,
            total_passagers=total_passagers,
            readonly=True,
            superviseur_mode=True,
            periode_formatee=periode_formatee
        )

    except Exception as e:
        return render_template('roles/superviseur/error.html',
                             message=f"Erreur: {str(e)}", readonly=True)


@bp.route('/export/trajets/<format>')
@superviseur_only
def export_trajets(format):
    """
    Export des trajets en CSV ou PDF
    Utilise RapportService pour générer les exports
    """
    try:
        # Paramètres de période
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        
        # Récupérer les données
        rapport = RapportService.get_rapport_trajets(date_debut, date_fin)
        
        if format.lower() == 'csv':
            content, filename = RapportService.export_trajets_csv(rapport['trajets'])
            
            response = make_response(content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        elif format.lower() == 'pdf':
            content, filename = RapportService.export_trajets_pdf(rapport['trajets'])
            
            response = make_response(content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        else:
            return jsonify({'error': 'Format non supporté'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500


@bp.route('/export/carburation/<format>')
@superviseur_only
def export_carburation(format):
    """
    Export des données de carburation en CSV
    Utilise RapportService pour générer les exports
    """
    try:
        # Paramètres de période
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        
        # Récupérer les données de carburation
        from app.models.carburation import Carburation
        query = Carburation.query
        
        if date_debut:
            query = query.filter(Carburation.date_carburation >= date_debut)
        if date_fin:
            query = query.filter(Carburation.date_carburation <= date_fin)
            
        carburations = query.order_by(Carburation.date_carburation.desc()).all()
        
        if format.lower() == 'csv':
            # Générer le CSV
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # En-têtes
            writer.writerow(['Date', 'Bus N°', 'Kilométrage', 'Quantité (L)', 'Prix Unitaire', 'Coût Total', 'Remarques'])
            
            # Données
            for carb in carburations:
                writer.writerow([
                    carb.date_carburation.strftime('%d/%m/%Y') if carb.date_carburation else '',
                    carb.bus_udm.numero if carb.bus_udm else '',
                    carb.kilometrage or '',
                    carb.quantite_litres or '',
                    carb.prix_unitaire or '',
                    carb.cout_total or '',
                    carb.remarque or ''
                ])
            
            content = output.getvalue()
            output.close()
            
            filename = f'carburations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            response = make_response(content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        else:
            return jsonify({'error': 'Format non supporté'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500


@bp.route('/export/chauffeurs/<format>')
@superviseur_only
def export_chauffeurs(format):
    """
    Export des données des chauffeurs en CSV
    """
    try:
        from app.models.chauffeur import Chauffeur
        
        chauffeurs = Chauffeur.query.all()
        
        if format.lower() == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # En-têtes
            writer.writerow(['Nom', 'Prénom', 'Téléphone', 'Email', 'Permis', 'Date Embauche', 'Statut'])

            # Données
            from app.models.utilisateur import Utilisateur
            from app.models.chauffeur_statut import ChauffeurStatut
            for chauffeur in chauffeurs:
                # Email pris depuis la table utilisateur (même identifiant)
                user = Utilisateur.query.get(chauffeur.chauffeur_id)
                email = user.email if user else ''

                # Statut courant (si disponible)
                statuts = ChauffeurStatut.get_current_statuts(chauffeur.chauffeur_id)
                statut = statuts[0].statut if statuts else ''

                # Date d'embauche non disponible dans la table chauffeur -> vide
                writer.writerow([
                    chauffeur.nom or '',
                    chauffeur.prenom or '',
                    chauffeur.telephone or '',
                    email,
                    chauffeur.numero_permis or '',
                    '',  # date_embauche non disponible
                    statut
                ])
            
            content = output.getvalue()
            output.close()
            
            filename = f'chauffeurs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            response = make_response(content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        else:
            return jsonify({'error': 'Format non supporté'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500


@bp.route('/export/bus/<format>')
@superviseur_only
def export_bus(format):
    """
    Export des données des bus en CSV
    """
    try:
        from app.models.bus_udm import BusUdM
        
        buses = BusUdM.query.all()
        
        if format.lower() == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # En-têtes
            writer.writerow(['Numéro', 'Immatriculation', 'Marque', 'Modèle', 'Année', 'Capacité', 'État', 'Kilométrage'])
            
            # Données
            for bus in buses:
                writer.writerow([
                    bus.numero or '',
                    bus.immatriculation or '',
                    bus.marque or '',
                    bus.modele or '',
                    bus.annee or '',
                    bus.capacite or '',
                    bus.etat_vehicule or '',
                    bus.kilometrage or ''
                ])
            
            content = output.getvalue()
            output.close()
            
            filename = f'bus_udm_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            response = make_response(content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        else:
            return jsonify({'error': 'Format non supporté'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500


@bp.route('/export/utilisateurs/<format>')
@superviseur_only
def export_utilisateurs(format):
    """
    Export des données des utilisateurs en CSV
    """
    try:
        from app.models.utilisateur import Utilisateur
        
        utilisateurs = Utilisateur.query.all()
        
        if format.lower() == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # En-têtes
            writer.writerow(['Nom', 'Prénom', 'Login', 'Email', 'Téléphone', 'Rôle'])
            
            # Données
            for user in utilisateurs:
                writer.writerow([
                    user.nom or '',
                    user.prenom or '',
                    user.login or '',
                    user.email or '',
                    user.telephone or '',
                    user.role or ''
                ])
            
            content = output.getvalue()
            output.close()
            
            filename = f'utilisateurs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            response = make_response(content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        else:
            return jsonify({'error': 'Format non supporté'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500


@bp.route('/export/maintenance/<format>')
@superviseur_only
def export_maintenance(format):
    """
    Export des données de maintenance en CSV
    Utilise RapportService pour générer les exports
    """
    try:
        # Paramètres de période
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')
        
        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        
        # Récupérer les données
        rapport = RapportService.get_rapport_maintenance(date_debut, date_fin)
        
        if format.lower() == 'csv':
            content, filename = RapportService.export_maintenance_csv(rapport)
            
            response = make_response(content)
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        else:
            return jsonify({'error': 'Format non supporté'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'export: {str(e)}'}), 500


@bp.route('/api/stats')
@superviseur_only
def api_stats():
    """
    API pour récupérer les statistiques en JSON
    Utilisable pour les graphiques dynamiques
    """
    try:
        # Vérifier la disponibilité du service
        if not StatsService:
            return jsonify({
                'success': False,
                'error': 'Service de statistiques non disponible'
            }), 503
            
        stats = StatsService.get_dashboard_stats()
        trends = StatsService.get_monthly_trends(6)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'trends': trends
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Gestionnaire d'erreur pour le blueprint superviseur
@bp.errorhandler(403)
def forbidden(error):
    """Gestionnaire d'erreur 403 - Accès interdit"""
    return render_template('roles/superviseur/error.html',
                         message="Accès interdit. Permissions insuffisantes.",
                         readonly=True), 403


@bp.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404 - Page non trouvée"""
    return render_template('roles/superviseur/error.html',
                         message="Page non trouvée.",
                         readonly=True), 404
