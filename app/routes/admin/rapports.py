from flask import render_template, request, jsonify, make_response
from flask_login import login_required
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_

import json
from io import BytesIO
import base64

from app.database import db
from app.models.trajet import Trajet
from app.models.bus_udm import BusUdM
from app.models.carburation import Carburation
from app.models.prestataire import Prestataire
from app.models.chauffeur import Chauffeur
from app.models.vidange import Vidange
from app.routes.common import admin_only

from . import bp

# Routes pour les rapports détaillés
@bp.route('/rapport-noblesse')
def rapport_noblesse():
    """Rapport détaillé pour les trajets Noblesse (avec filtres)."""
    print("DEBUG: Route rapport_noblesse appelée!")
    try:
        # Filtres
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

        print(f"DEBUG: periode={periode}, date_debut={date_debut}, date_fin={date_fin}, start_date={start_date}, end_date={end_date}")
        # Récupérer les trajets prestataires Noblesse (via relation Prestataire)
        trajets = db.session.query(Trajet).join(Prestataire).filter(
            and_(
                Trajet.type_trajet == 'PRESTATAIRE',
                Prestataire.nom_prestataire == 'Noblesse',
                func.date(Trajet.date_heure_depart) >= start_date,
                func.date(Trajet.date_heure_depart) <= end_date
            )
        ).order_by(Trajet.date_heure_depart.desc()).all()

        print(f"DEBUG: Trouvé {len(trajets)} trajets Noblesse sur la période {start_date} -> {end_date}")

        # Statistiques
        total_trajets = len(trajets)
        total_passagers = sum([t.nombre_places_occupees or 0 for t in trajets])

        return render_template(
            'rapport_entity.html',
            entity_name='Noblesse',
            trajets=trajets,
            total_trajets=total_trajets,
            total_passagers=total_passagers,
            entity_type='prestataire'
        )
    except Exception as e:
        print(f"ERREUR rapport_noblesse: {e}")
        return f"Erreur: {e}", 500

@bp.route('/rapport-charter')
def rapport_charter():
    """Rapport détaillé pour les trajets Charter (avec filtres)."""
    try:
        # Filtres
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

        print(f"DEBUG: periode={periode}, date_debut={date_debut}, date_fin={date_fin}, start_date={start_date}, end_date={end_date}")
        # Récupérer les trajets prestataires Charter (via relation Prestataire)
        trajets = db.session.query(Trajet).join(Prestataire).filter(
            and_(
                Trajet.type_trajet == 'PRESTATAIRE',
                Prestataire.nom_prestataire == 'Charter',
                func.date(Trajet.date_heure_depart) >= start_date,
                func.date(Trajet.date_heure_depart) <= end_date
            )
        ).order_by(Trajet.date_heure_depart.desc()).all()

        # Statistiques
        total_trajets = len(trajets)
        total_passagers = sum([t.nombre_places_occupees or 0 for t in trajets])

        return render_template(
            'rapport_entity.html',
            entity_name='Charter',
            trajets=trajets,
            total_trajets=total_trajets,
            total_passagers=total_passagers,
            entity_type='prestataire'
        )
    except Exception as e:
        print(f"ERREUR rapport_charter: {e}")
        return f"Erreur: {e}", 500

@bp.route('/rapport-bus-udm')
def rapport_bus_udm():
    """Rapport détaillé pour les trajets Bus UdM (avec filtres)."""
    try:
        # Filtres
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

        print(f"DEBUG: periode={periode}, date_debut={date_debut}, date_fin={date_fin}, start_date={start_date}, end_date={end_date}")
        # Récupérer les trajets UdM sur période
        trajets = Trajet.query.filter(
            and_(
                Trajet.type_trajet == 'UDM_INTERNE',
                func.date(Trajet.date_heure_depart) >= start_date,
                func.date(Trajet.date_heure_depart) <= end_date
            )
        ).order_by(Trajet.date_heure_depart.desc()).all()

        # Statistiques
        total_trajets = len(trajets)
        total_passagers = sum([t.nombre_places_occupees or 0 for t in trajets])

        # Statistiques par type de passager
        etudiants = sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'ETUDIANT'])
        personnel = sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'PERSONNEL'])
        malades = sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'MALADE'])

        return render_template(
            'rapport_entity.html',
            entity_name='Bus UdM',
            trajets=trajets,
            total_trajets=total_trajets,
            total_passagers=total_passagers,
            entity_type='bus_udm',
            stats_passagers={
                'etudiants': etudiants,
                'personnel': personnel,
                'malades': malades
            }
        )
    except Exception as e:
        print(f"ERREUR rapport_bus_udm: {e}")
        return f"Erreur: {e}", 500

@bp.route('/rapports/')
def rapports():
    """Page principale des rapports"""
    # Données pour les rapports rapides
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Statistiques rapides
    stats = {
        'today': get_daily_stats(today),
        'week': get_period_stats(week_start, today),
        'month': get_period_stats(month_start, today),
        'fleet': get_fleet_stats()
    }

    return render_template('rapports.html', stats=stats)

@bp.route('/rapports/noblesse')
def rapport_noblesse_alias():
    """Alias redirigeant vers la route principale sans changer les templates existants."""
    return rapport_noblesse()

@bp.route('/rapports/charter')
def rapport_charter_alias():
    """Alias redirigeant vers la route principale sans changer les templates existants."""
    return rapport_charter()

@bp.route('/rapports/bus-udm')
def rapport_bus_udm_alias():
    """Alias redirigeant vers la route principale sans changer les templates existants."""
    return rapport_bus_udm()

@bp.route('/rapports/api/stats/<period>')
# @login_required  # Temp désactivé
# @admin_only      # Temp désactivé
def api_stats(period):
    """API pour récupérer les statistiques par période"""
    today = date.today()

    if period == 'today':
        data = get_daily_stats(today)
    elif period == 'week':
        week_start = today - timedelta(days=today.weekday())
        data = get_period_stats(week_start, today)
    elif period == 'month':
        month_start = today.replace(day=1)
        data = get_period_stats(month_start, today)
    elif period == 'fleet':
        data = get_fleet_stats()
    else:
        return jsonify({'error': 'Période invalide'}), 400

    return jsonify(data)

@bp.route('/rapports/api/chart/<chart_type>')
# @login_required  # Temp désactivé
# @admin_only      # Temp désactivé
def api_chart(chart_type):
    """API pour les données de graphiques"""
    if chart_type == 'trajets_evolution':
        return jsonify(get_trajets_evolution())
    elif chart_type == 'passagers_type':
        return jsonify(get_passagers_by_type())

    else:
        return jsonify({'error': 'Type de graphique invalide'}), 400

@bp.route('/api/bus-usage')
# @login_required  # Temp désactivé
# @admin_only      # Temp désactivé
def api_bus_usage():
    """API pour récupérer les données d'utilisation des bus UdM"""
    try:
        today = date.today()
        
        # Filtres
        periode = request.args.get('periode', 'jour')
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')

        # Calculer les dates de début et fin
        if date_debut and date_fin:
            start_date = datetime.strptime(date_debut, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_fin, '%Y-%m-%d').date()
        elif periode == 'mois':
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

        print(f"DEBUG BUS USAGE: periode={periode}, start_date={start_date}, end_date={end_date}")

        # Récupérer les trajets UdM par bus sur la période
        trajets_query = db.session.query(
            Trajet.numero_bus_udm,
            func.count(Trajet.trajet_id).label('nb_trajets')
        ).filter(
            and_(
                Trajet.type_trajet == 'UDM_INTERNE',
                Trajet.numero_bus_udm.isnot(None),
                func.date(Trajet.date_heure_depart) >= start_date,
                func.date(Trajet.date_heure_depart) <= end_date
            )
        ).group_by(Trajet.numero_bus_udm).order_by(func.count(Trajet.trajet_id).desc()).all()

        print(f"DEBUG BUS USAGE: Trouvé {len(trajets_query)} bus avec trajets")

        # Préparer les données pour le graphique circulaire
        labels = []
        data = []
        colors = ['#28a745', '#17a2b8', '#ffc107', '#fd7e14', '#6f42c1', '#e83e8c', '#6610f2', '#20c997', '#fd7e14', '#6c757d']
        
        for i, (numero_bus, nb_trajets) in enumerate(trajets_query):
            labels.append(f"Bus {numero_bus}")
            data.append(nb_trajets)
        
        # Générer des couleurs pour tous les bus
        background_colors = []
        border_colors = []
        for i in range(len(labels)):
            color = colors[i % len(colors)]
            background_colors.append(color)
            border_colors.append('#ffffff')

        # Informations sur la période pour l'affichage
        periode_info = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }

        response_data = {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': background_colors,
                'borderColor': border_colors,
                'borderWidth': 2
            }],
            'periode_info': periode_info,
            'total_trajets': sum(data)
        }

        print(f"DEBUG BUS USAGE: Retour {len(labels)} bus, {sum(data)} trajets total")
        return jsonify(response_data)

    except Exception as e:
        print(f"ERROR BUS USAGE: {e}")
        return jsonify({'error': str(e)}), 500



def get_daily_stats(target_date):
    """Statistiques pour une journée donnée"""
    trajets = Trajet.query.filter(func.date(Trajet.date_heure_depart) == target_date).all()

    stats = {
        'total_trajets': len(trajets),
        'trajets_udm': len([t for t in trajets if t.type_trajet == 'UDM_INTERNE']),
        'trajets_prestataire': len([t for t in trajets if t.type_trajet == 'PRESTATAIRE']),
        'trajets_autres': len([t for t in trajets if t.type_trajet == 'AUTRE']),
        'total_passagers': sum([t.nombre_places_occupees or 0 for t in trajets]),
        'passagers_etudiants': sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'ETUDIANT']),
        'passagers_personnel': sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'PERSONNEL']),
        'passagers_malades': sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'MALADE']),
    }

    return stats

def get_period_stats(start_date, end_date):
    """Statistiques pour une période donnée"""
    trajets = Trajet.query.filter(
        and_(
            func.date(Trajet.date_heure_depart) >= start_date,
            func.date(Trajet.date_heure_depart) <= end_date
        )
    ).all()

    stats = {
        'total_trajets': len(trajets),
        'trajets_udm': len([t for t in trajets if t.type_trajet == 'UDM_INTERNE']),
        'trajets_prestataire': len([t for t in trajets if t.type_trajet == 'PRESTATAIRE']),
        'trajets_autres': len([t for t in trajets if t.type_trajet == 'AUTRE']),
        'total_passagers': sum([t.nombre_places_occupees or 0 for t in trajets]),
        'moyenne_passagers_jour': round(sum([t.nombre_places_occupees or 0 for t in trajets]) / max(1, (end_date - start_date).days + 1), 1),
        'jours_periode': (end_date - start_date).days + 1
    }

    return stats

def get_fleet_stats():
    """Statistiques de la flotte"""
    bus_list = BusUdM.query.all()

    stats = {
        'total_bus': len(bus_list),
        'bus_actifs': len([b for b in bus_list if b.etat_vehicule != 'DEFAILLANT']),
        'bus_maintenance': len([b for b in bus_list if b.etat_vehicule == 'DEFAILLANT']),
        'km_total': sum([b.kilometrage or 0 for b in bus_list]),
        'moyenne_km': round(sum([b.kilometrage or 0 for b in bus_list]) / max(1, len(bus_list)), 0)
    }

    return stats

def get_trajets_evolution():
    """Données pour graphique d'évolution des trajets (7 derniers jours)"""
    today = date.today()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    data = {
        'labels': [d.strftime('%d/%m') for d in dates],
        'datasets': [
            {
                'label': 'Bus UdM',
                'data': [],
                'borderColor': '#28a745',
                'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                'tension': 0.4
            },
            {
                'label': 'Prestataires',
                'data': [],
                'borderColor': '#007bff',
                'backgroundColor': 'rgba(0, 123, 255, 0.1)',
                'tension': 0.4
            }
        ]
    }

    for d in dates:
        trajets_udm = Trajet.query.filter(
            and_(func.date(Trajet.date_heure_depart) == d, Trajet.type_trajet == 'UDM_INTERNE')
        ).count()
        trajets_prestataire = Trajet.query.filter(
            and_(func.date(Trajet.date_heure_depart) == d, Trajet.type_trajet == 'PRESTATAIRE')
        ).count()

        data['datasets'][0]['data'].append(trajets_udm)
        data['datasets'][1]['data'].append(trajets_prestataire)

    return data

def get_passagers_by_type():
    """Données pour graphique répartition des passagers"""
    today = date.today()
    month_start = today.replace(day=1)

    trajets = Trajet.query.filter(
        func.date(Trajet.date_heure_depart) >= month_start
    ).all()

    etudiants = sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'ETUDIANT'])
    personnel = sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'PERSONNEL'])
    malades = sum([t.nombre_places_occupees or 0 for t in trajets if t.type_passagers == 'MALADE'])

    return {
        'labels': ['Étudiants', 'Personnel', 'Malades'],
        'datasets': [{
            'data': [etudiants, personnel, malades],
            'backgroundColor': ['#28a745', '#17a2b8', '#ffc107'],
            'borderWidth': 2,
            'borderColor': '#fff'
        }]
    }

def get_prestataires_performance():
    """Données pour la section Performance des prestataires"""
    # Récupérer tous les prestataires
    prestataires = Prestataire.query.all()
    
    performance_data = []
    
    for prestataire in prestataires:
        # Récupérer les trajets de ce prestataire
        trajets = Trajet.query.filter(
            and_(
                Trajet.type_trajet == 'PRESTATAIRE',
                Trajet.immat_bus == prestataire.immatriculation
            )
        ).order_by(Trajet.date_heure_depart.desc()).all()
        
        performance_data.append({
            'nom_prestataire': prestataire.nom_prestataire,
            'immatriculation': prestataire.immatriculation,
            'nom_chauffeur': prestataire.nom_chauffeur,
            'trajets': trajets,
            'total_trajets': len(trajets),
            'total_passagers': sum([t.nombre_places_occupees or 0 for t in trajets])
        })
    
    return performance_data





@bp.route('/api/performances-chauffeurs')
def api_performances_chauffeurs():
    """API pour récupérer les données de performance des chauffeurs AED"""
    print("DEBUG: API performances-chauffeurs appelée!")
    # Définir today en amont pour l'utiliser en cas d'erreur
    _today = date.today()
    try:
        # Récupérer les paramètres de filtre
        periode = request.args.get('periode', 'jour')
        date_debut = request.args.get('date_debut')
        date_fin = request.args.get('date_fin')

        print(f"DEBUG API: periode={periode}, date_debut={date_debut}, date_fin={date_fin}")

        today = date.today()

        # Déterminer la période
        if date_debut and date_fin:
            try:
                start_date = datetime.strptime(date_debut, '%Y-%m-%d').date()
                end_date = datetime.strptime(date_fin, '%Y-%m-%d').date()
            except ValueError:
                start_date = today
                end_date = today
        elif periode == 'jour':
            start_date = today
            end_date = today
        elif periode == 'semaine':
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif periode == 'mois':
            start_date = today.replace(day=1)
            end_date = today
        else:
            start_date = today
            end_date = today

        # Récupérer les données des trajets avec chauffeurs (LEFT JOIN pour inclure tous les trajets)
        trajets_data = db.session.query(
            func.coalesce(Chauffeur.nom, 'Chauffeur').label('nom'),
            func.coalesce(Chauffeur.prenom, func.concat('ID-', Trajet.chauffeur_id)).label('prenom'),
            func.count(Trajet.trajet_id).label('nombre_trajets'),
            func.sum(Trajet.nombre_places_occupees).label('total_passagers')
        ).outerjoin(
            Chauffeur, Trajet.chauffeur_id == Chauffeur.chauffeur_id
        ).filter(
            and_(
                Trajet.type_trajet == 'UDM_INTERNE',
                func.date(Trajet.date_heure_depart) >= start_date,
                func.date(Trajet.date_heure_depart) <= end_date
            )
        ).group_by(
            Trajet.chauffeur_id, Chauffeur.nom, Chauffeur.prenom
        ).order_by(
            func.count(Trajet.trajet_id).desc()
        ).all()

        # Préparer les données pour le graphique
        chauffeurs = [f"{row.nom} {row.prenom}" for row in trajets_data]
        nombre_trajets = [row.nombre_trajets for row in trajets_data]

        # Couleurs distinctes par chauffeur (palette cyclique pour éviter des couleurs identiques)
        palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
            '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ac'
        ]
        colors = [palette[i % len(palette)] for i in range(len(chauffeurs))]

        print(f"DEBUG API: Trouvé {len(chauffeurs)} chauffeurs avec {sum(nombre_trajets)} trajets total")

        return jsonify({
            'labels': chauffeurs,
            'datasets': [{
                'label': 'Nombre de trajets',
                'data': nombre_trajets,
                'backgroundColor': colors,
                'borderColor': colors,
                'borderWidth': 2
            }],
            'periode_info': {
                'start_date': start_date.strftime('%d/%m/%Y'),
                'end_date': end_date.strftime('%d/%m/%Y'),
                'total_trajets': sum(nombre_trajets),
                'total_chauffeurs': len(chauffeurs)
            }
        })
    except Exception as e:
        print(f"ERREUR API performances-chauffeurs: {e}")
        return jsonify({
            'error': str(e),
            'labels': [],
            'datasets': [{
                'label': 'Nombre de trajets',
                'data': [],
                'backgroundColor': [],
                'borderColor': [],
                'borderWidth': 2
            }],
            'periode_info': {
                'start_date': _today.strftime('%d/%m/%Y'),
                'end_date': _today.strftime('%d/%m/%Y'),
                'total_trajets': 0,
                'total_chauffeurs': 0
            }
        }), 500