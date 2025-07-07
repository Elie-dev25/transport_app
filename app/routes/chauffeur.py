from flask import Blueprint, render_template
from flask_login import current_user, login_required
from datetime import date, timedelta
from app.routes.common import role_required

# Création du blueprint pour le chauffeur
bp = Blueprint('chauffeur', __name__, url_prefix='/chauffeur')

# Route du tableau de bord chauffeur
@bp.route('/dashboard')
@login_required
@role_required('CHAUFFEUR')
def dashboard():
    print("DEBUG: dashboard chauffeur route called")
    # Affiche le vrai dashboard chauffeur
    # Préparer les stats et données fictives pour l'exemple (à remplacer par vraies requêtes)
    # Statistiques du jour et semaine (à adapter)
    stats = {
        'today_trips': 2,
        'today_vs_yesterday': 1,
        'people_transported': 40,
        'week_people': 120,
        'bus_code': 'AED-001',
        'status': 'En service'
    }
    # Notifications fictives
    notifications = [
        {'type': 'info', 'icon': 'fas fa-info-circle', 'title': 'Départ prévu à 7h', 'time': 'Aujourd\'hui 06:00'},
        {'type': 'warning', 'icon': 'fas fa-exclamation-triangle', 'title': 'Maintenance demain', 'time': 'Hier 18:00'}
    ]
    # Trajets fictifs
    trajets = [
        {'bus_code': 'AED-001', 'depart': 'Campus', 'arrivee': 'Gare', 'status': 'Terminé', 'status_class': 'done', 'heure': '07:15', 'date': '2025-07-07', 'etudiants': 23, 'places': 30},
        {'bus_code': 'AED-001', 'depart': 'Gare', 'arrivee': 'Campus', 'status': 'En cours', 'status_class': 'active', 'heure': '08:30', 'date': '2025-07-07', 'etudiants': 17, 'places': 30}
    ]
    # Semaine fictive
    semaine = []
    for i in range(7):
        jour = date.today() - timedelta(days=6-i)
        semaine.append({
            'nom': jour.strftime('%A'),
            'nb_trajets': 2,
            'trajets': [
                {'heure': '07:15', 'depart': 'Campus', 'arrivee': 'Gare'},
                {'heure': '08:30', 'depart': 'Gare', 'arrivee': 'Campus'}
            ]
        })
    # Trafic fictif
    trafic = {'arrives': 40, 'partis': 38, 'transit': 2, 'total': 78}
    return render_template(
        'dashboard_chauffeur.html',
        stats=stats, trajets=trajets, semaine=semaine, trafic=trafic,
        notifications=notifications, current_user=current_user, active_page='dashboard'
    )

@bp.route('/profil')
@login_required
@role_required('CHAUFFEUR')
def profil():
    # Affiche le profil du chauffeur connecté
    return render_template(
        'profil_chauffeur.html',
        current_user=current_user,
        active_page='profil'
    )

@bp.route('/trajets')
@login_required
@role_required('CHAUFFEUR')
def trajets():
    # Affiche la liste des trajets du chauffeur (exemple minimal)
    return render_template(
        'trajets_chauffeur.html',
        current_user=current_user,
        active_page='trajets'
    )

@bp.route('/semaine')
@login_required
@role_required('CHAUFFEUR')
def semaine():
    return render_template(
        'semaine_chauffeur.html',
        current_user=current_user,
        active_page='semaine'
    )

@bp.route('/trafic')
@login_required
@role_required('CHAUFFEUR')
def trafic():
    return render_template(
        'trafic_chauffeur.html',
        current_user=current_user,
        active_page='trafic'
    )