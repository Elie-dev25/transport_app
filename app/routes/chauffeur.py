from flask import Blueprint, render_template, session, request, url_for
from flask_login import current_user, login_required
from datetime import date, timedelta

# Services centralisés (Phase 1 Refactoring)
from app.services.dashboard_service import DashboardService

from app.routes.common import role_required

# Création du blueprint pour le chauffeur
bp = Blueprint('chauffeur', __name__, url_prefix='/chauffeur')

def get_chauffeur_statut_actuel():
    """
    Fonction utilitaire pour récupérer le statut actuel du chauffeur connecté
    Utilisée dans toutes les routes pour afficher le statut dans la topbar
    """
    try:
        from app.models.chauffeur import Chauffeur
        from app.models.chauffeur_statut import ChauffeurStatut

        # Récupérer les informations du chauffeur depuis la base de données
        chauffeur_db = Chauffeur.query.filter_by(
            nom=current_user.nom,
            prenom=current_user.prenom
        ).first()

        # Récupérer le statut actuel du chauffeur
        statut_actuel = "NON_SPECIFIE"
        if chauffeur_db:
            statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur_db.chauffeur_id)
            if statuts_actuels:
                statut_actuel = statuts_actuels[0].statut

        return statut_actuel

    except Exception as e:
        print(f"Erreur récupération statut chauffeur: {str(e)}")
        return "NON_SPECIFIE"

# Route du tableau de bord chauffeur
@bp.route('/dashboard')
@login_required
@role_required('CHAUFFEUR')
def dashboard():
    """
    Dashboard chauffeur refactorisé - Phase 1
    Utilise DashboardService pour éliminer la duplication de code
    """
    try:
        # Utiliser le service centralisé pour les statistiques générales
        stats_generales = DashboardService.get_common_stats()

        # Statistiques spécifiques au chauffeur connecté
        stats_personnelles = DashboardService.get_role_specific_stats('CHAUFFEUR', current_user.utilisateur_id)

        # Trafic temps réel (déjà inclus dans stats_generales)
        trafic = stats_generales.get('trafic', {})

        # Notifications réelles (à récupérer depuis la base)
        notifications = [
            {'type': 'info', 'icon': 'fas fa-info-circle', 'title': 'Départ prévu à 7h', 'time': 'Aujourd\'hui 06:00'},
            {'type': 'warning', 'icon': 'fas fa-exclamation-triangle', 'title': 'Maintenance demain', 'time': 'Hier 18:00'}
        ]

        # Récupérer le statut actuel du chauffeur pour la topbar
        statut_actuel = get_chauffeur_statut_actuel()

        return render_template(
            'roles/chauffeur/dashboard_chauffeur.html',
            stats_generales=stats_generales,
            stats_personnelles=stats_personnelles,
            trafic=trafic,
            notifications=notifications,
            current_user=current_user,
            statut_actuel=statut_actuel,
            active_page='dashboard'
        )

    except Exception as e:
        print(f"Erreur dashboard chauffeur: {str(e)}")
        # En cas d'erreur, afficher un dashboard minimal
        statut_actuel = get_chauffeur_statut_actuel()
        return render_template(
            'roles/chauffeur/dashboard_chauffeur_simple.html',
            current_user=current_user,
            error_message="Erreur lors du chargement du dashboard",
            statut_actuel=statut_actuel,
            active_page='dashboard'
        )

@bp.route('/trajets')
@login_required
@role_required('CHAUFFEUR')
def trajets():
    try:
        from app.models.chauffeur import Chauffeur
        from app.models.trajet import Trajet
        from app.database import db
        from datetime import datetime, timedelta
        from sqlalchemy import func, and_, or_
        
        chauffeur_db = Chauffeur.query.filter_by(
            nom=current_user.nom, 
            prenom=current_user.prenom
        ).first()
        
        if not chauffeur_db:
            statut_actuel = get_chauffeur_statut_actuel()
            return render_template(
                'roles/chauffeur/mes_trajets.html',
                current_user=current_user,
                error_message="Profil chauffeur non trouvé",
                statut_actuel=statut_actuel,
                active_page='trajets'
            )
        
        # Calculer les dates pour le mois en cours
        debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin_mois = datetime.now().replace(day=28) + timedelta(days=4)
        fin_mois = fin_mois - timedelta(days=fin_mois.day)
        fin_mois = fin_mois.replace(hour=23, minute=59, second=59)
        
        # Statistiques du mois en cours
        trajets_mois = Trajet.query.filter(
            Trajet.chauffeur_id == chauffeur_db.chauffeur_id,
            Trajet.date_heure_depart >= debut_mois,
            Trajet.date_heure_depart <= fin_mois
        ).all()
        
        # Compter les différents types de trajets
        vers_campus = 0
        du_campus = 0
        exceptionnels = 0
        
        destinations_campus = ['Banekane', 'banekane', 'BANEKANE']
        departs_campus = ['Mfetum', 'mfetum', 'MFETUM', 'Ancienne Mairie', 'ancienne mairie', 'ANCIENNE MAIRIE']
        
        for trajet in trajets_mois:
            # Vers le campus (destination = Banekane)
            if trajet.point_arrivee and any(dest in trajet.point_arrivee for dest in destinations_campus):
                vers_campus += 1
            # Du campus (départ = Mfetum ou Ancienne Mairie)
            elif trajet.point_depart and any(dep in trajet.point_depart for dep in departs_campus):
                du_campus += 1
            # Trajets exceptionnels (ni vers ni du campus)
            else:
                exceptionnels += 1
        
        stats_mois = {
            'total_trajets': len(trajets_mois),
            'vers_campus': vers_campus,
            'du_campus': du_campus,
            'exceptionnels': exceptionnels
        }
        
        # Récupérer l'historique complet des trajets (par défaut: ce mois)
        filtre = request.args.get('filtre', 'mois')
        date_debut_filtre = debut_mois
        date_fin_filtre = fin_mois
        
        if filtre == 'aujourd_hui':
            date_debut_filtre = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date_fin_filtre = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif filtre == 'semaine':
            # Début de la semaine (lundi)
            today = datetime.now()
            start_week = today - timedelta(days=today.weekday())
            date_debut_filtre = start_week.replace(hour=0, minute=0, second=0, microsecond=0)
            date_fin_filtre = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif filtre == 'plage':
            # Dates personnalisées depuis les paramètres
            date_debut_str = request.args.get('date_debut')
            date_fin_str = request.args.get('date_fin')
            if date_debut_str and date_fin_str:
                try:
                    date_debut_filtre = datetime.strptime(date_debut_str, '%Y-%m-%d')
                    date_fin_filtre = datetime.strptime(date_fin_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                except ValueError:
                    pass  # Garder les dates par défaut
        
        trajets_historique = Trajet.query.filter(
            Trajet.chauffeur_id == chauffeur_db.chauffeur_id,
            Trajet.date_heure_depart >= date_debut_filtre,
            Trajet.date_heure_depart <= date_fin_filtre
        ).order_by(Trajet.date_heure_depart.desc()).all()
        
        # Récupérer le statut actuel du chauffeur pour la topbar
        statut_actuel = get_chauffeur_statut_actuel()

        return render_template(
            'roles/chauffeur/mes_trajets.html',
            current_user=current_user,
            chauffeur_db=chauffeur_db,
            stats_mois=stats_mois,
            trajets_historique=trajets_historique,
            filtre_actuel=filtre,
            date_debut_filtre=date_debut_filtre,
            date_fin_filtre=date_fin_filtre,
            statut_actuel=statut_actuel,
            active_page='trajets'
        )
        
    except Exception as e:
        print(f"Erreur trajets chauffeur: {str(e)}")
        statut_actuel = get_chauffeur_statut_actuel()
        return render_template(
            'mes_trajets.html',
            current_user=current_user,
            error_message="Erreur lors du chargement des trajets",
            statut_actuel=statut_actuel,
            active_page='trajets'
        )

@bp.route('/profil')
@login_required
@role_required('CHAUFFEUR')
def profil():
    try:
        from app.models.chauffeur import Chauffeur
        from app.models.trajet import Trajet
        from app.models.chauffeur_statut import ChauffeurStatut
        from app.database import db
        from datetime import datetime, timedelta
        
        # Récupérer les informations du chauffeur depuis la base de données
        chauffeur_db = Chauffeur.query.filter_by(
            nom=current_user.nom, 
            prenom=current_user.prenom
        ).first()
        
        # Récupérer le statut actuel du chauffeur
        statut_actuel = "NON_SPECIFIE"
        if chauffeur_db:
            statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur_db.chauffeur_id)
            if statuts_actuels:
                statut_actuel = statuts_actuels[0].statut
        
        # Récupérer l'historique des trajets (30 derniers jours)
        trajets_historique = []
        if chauffeur_db:
            date_limite = datetime.now() - timedelta(days=30)
            trajets_historique = Trajet.query.filter(
                Trajet.chauffeur_id == chauffeur_db.chauffeur_id,
                Trajet.date_heure_depart >= date_limite
            ).order_by(Trajet.date_heure_depart.desc()).limit(50).all()
        
        # Statistiques du profil
        stats_profil = {}
        affectations_mois = []
        if chauffeur_db:
            # Total trajets effectués
            total_trajets = Trajet.query.filter_by(chauffeur_id=chauffeur_db.chauffeur_id).count()
            
            # Trajets ce mois-ci
            debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            trajets_mois = Trajet.query.filter(
                Trajet.chauffeur_id == chauffeur_db.chauffeur_id,
                Trajet.date_heure_depart >= debut_mois
            ).count()
            
            # Total passagers transportés
            total_passagers = db.session.query(
                db.func.sum(Trajet.nombre_places_occupees)
            ).filter(
                Trajet.chauffeur_id == chauffeur_db.chauffeur_id
            ).scalar() or 0
            
            stats_profil = {
                'total_trajets': total_trajets,
                'trajets_mois': trajets_mois,
                'total_passagers': total_passagers
            }
            
            # Affectations du mois (trajets groupés par jour)
            # Récupérer les statuts du chauffeur pour le mois en cours
            from app.models.chauffeur_statut import ChauffeurStatut
            fin_mois = datetime.now().replace(day=28) + timedelta(days=4)  # Fin approximative du mois
            fin_mois = fin_mois - timedelta(days=fin_mois.day)
            fin_mois = fin_mois.replace(hour=23, minute=59, second=59)
            
            statuts_mois = ChauffeurStatut.query.filter(
                ChauffeurStatut.chauffeur_id == chauffeur_db.chauffeur_id,
                db.or_(
                    db.and_(ChauffeurStatut.date_debut >= debut_mois, ChauffeurStatut.date_debut <= fin_mois),
                    db.and_(ChauffeurStatut.date_fin >= debut_mois, ChauffeurStatut.date_fin <= fin_mois),
                    db.and_(ChauffeurStatut.date_debut <= debut_mois, ChauffeurStatut.date_fin >= fin_mois)
                )
            ).order_by(ChauffeurStatut.date_debut.desc()).all()
            
            affectations_mois = []
            for statut in statuts_mois:
                # Calculer la durée
                duree_jours = (statut.date_fin - statut.date_debut).days + 1
                duree_str = f"{duree_jours} jour{'s' if duree_jours > 1 else ''}"
                
                # Déterminer l'état (actuel, passé, futur)
                maintenant = datetime.now()
                if statut.date_fin < maintenant:
                    etat = "Terminé"
                    etat_class = "success"
                elif statut.date_debut <= maintenant <= statut.date_fin:
                    etat = "En cours"
                    etat_class = "primary"
                else:
                    etat = "À venir"
                    etat_class = "warning"
                
                # Mapper les statuts pour un affichage plus lisible
                statut_display = {
                    'CONGE': 'Congé',
                    'PERMANENCE': 'Permanence',
                    'SERVICE_WEEKEND': 'Service Weekend',
                    'SERVICE_SEMAINE': 'Service Semaine'
                }.get(statut.statut, statut.statut)
                
                affectations_mois.append({
                    'date_debut': statut.date_debut,
                    'date_fin': statut.date_fin,
                    'statut': statut_display,
                    'statut_original': statut.statut,
                    'duree': duree_str,
                    'etat': etat,
                    'etat_class': etat_class
                })
        
        return render_template(
            'roles/chauffeur/profil_chauffeur.html',
            current_user=current_user,
            chauffeur_db=chauffeur_db,
            statut_actuel=statut_actuel,
            trajets_historique=trajets_historique,
            stats_profil=stats_profil,
            affectations_mois=affectations_mois,
            active_page='profil'
        )
        
    except Exception as e:
        print(f"Erreur profil chauffeur: {str(e)}")
        statut_actuel = get_chauffeur_statut_actuel()
        return render_template(
            'roles/chauffeur/profil_chauffeur.html',
            current_user=current_user,
            error_message="Erreur lors du chargement du profil",
            statut_actuel=statut_actuel,
            active_page='profil'
        )


@bp.route('/bus_udm')
@login_required
@role_required('CHAUFFEUR')
def bus_udm():
    try:
        from app.models.bus_udm import BusUdM
        
        # Récupérer tous les bus
        buses = BusUdM.query.all()
        
        # Récupérer le statut actuel du chauffeur pour la topbar
        statut_actuel = get_chauffeur_statut_actuel()

        return render_template(
            'pages/bus_udm.html',
            bus_list=buses,  # Le template attend bus_list, pas buses
            current_user=current_user,
            active_page='bus_udm',
            readonly=True,  # Mode lecture seule pour les chauffeurs
            statut_actuel=statut_actuel,
            base_template='roles/chauffeur/_base_chauffeur.html'
        )
    except Exception as e:
        print(f"Erreur lors du chargement des bus: {str(e)}")
        statut_actuel = get_chauffeur_statut_actuel()
        return render_template(
            'pages/bus_udm.html',
            bus_list=[],  # Le template attend bus_list, pas buses
            current_user=current_user,
            active_page='bus_udm',
            readonly=True,
            error_message="Erreur lors du chargement de la liste des bus",
            statut_actuel=statut_actuel,
            base_template='roles/chauffeur/_base_chauffeur.html'
        )

@bp.route('/trafic')
@login_required
@role_required('CHAUFFEUR')
def trafic():
    # Récupérer le statut actuel du chauffeur pour la topbar
    statut_actuel = get_chauffeur_statut_actuel()

    return render_template(
        'trafic_chauffeur.html',
        current_user=current_user,
        statut_actuel=statut_actuel,
        active_page='trafic'
    )

@bp.route('/carburation')
@login_required
@role_required('CHAUFFEUR')
def carburation():
    print("🚗 ROUTE CHAUFFEUR CARBURATION APPELÉE!")
    try:
        from app.models.bus_udm import BusUdM
        from app.models.chauffeur import Chauffeur
        from app.services.gestion_carburation import build_bus_carburation_list, get_carburation_history
        from app.database import db
        
        # Debug: vérifier les données
        print("=== DEBUG CHAUFFEUR CARBURATION ===")
        
        # Récupérer les données comme côté admin (utiliser le même service)
        bus_carburation = build_bus_carburation_list()
        print(f"Nombre de bus carburation: {len(bus_carburation)}")
        if bus_carburation:
            print(f"Premier bus: {bus_carburation[0]}")
        
        # Historique des carburations
        historique_carburation = get_carburation_history()
        print(f"Nombre historique carburation: {len(historique_carburation)}")
        
        # Liste des chauffeurs pour le formulaire
        chauffeurs = Chauffeur.query.all()
        print(f"Nombre de chauffeurs: {len(chauffeurs)}")
        
        # Numéros de bus pour les filtres
        numeros_aed = [bus['numero'] for bus in bus_carburation]
        print(f"Numéros AED: {numeros_aed}")
        print("=== FIN DEBUG ===")
        
        # Récupérer le statut actuel du chauffeur pour la topbar
        statut_actuel = get_chauffeur_statut_actuel()

        return render_template(
            'pages/carburation.html',
            bus_carburation=bus_carburation,
            historique_carburation=historique_carburation,
            chauffeurs=chauffeurs,
            numeros_aed=numeros_aed,
            current_user=current_user,
            active_page='carburation',
            readonly=True,  # Mode lecture seule pour chauffeur
            statut_actuel=statut_actuel,
            post_url=None  # Pas d'actions POST pour chauffeur (lecture seule)
        )
    except Exception as e:
        print(f"Erreur affichage carburation chauffeur: {str(e)}")
        statut_actuel = get_chauffeur_statut_actuel()
        return render_template(
            'pages/carburation.html',
            bus_carburation=[],
            historique_carburation=[],
            chauffeurs=[],
            numeros_aed=[],
            current_user=current_user,
            active_page='carburation',
            readonly=True,
            statut_actuel=statut_actuel,
            error_message="Erreur lors du chargement de la page carburation"
        )