from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required
from app.models.bus_udm import BusUdM
from app.database import db
from app.routes.common import role_required
from app.services.gestion_vidange import (
    get_vidange_history,
    build_bus_vidange_list,
    enregistrer_vidange_common,
)
import unicodedata

# Création du blueprint pour le mécanicien
bp = Blueprint('mecanicien', __name__, url_prefix='/mecanicien')

# Route du tableau de bord mécanicien
@bp.route('/dashboard')
@login_required
@role_required('MECANICIEN')
def dashboard():
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()

    # Calculer les statistiques pour les cards
    bus_total = len(bus_list)
    bus_bon_etat = 0
    bus_en_panne = 0
    bus_vidange_urgente = 0

    for bus in bus_list:
        # Compter les bus en bon état et en panne
        etat_normalise = normalize_etat(bus.etat_vehicule)
        if 'defaillant' in etat_normalise or 'hors' in etat_normalise or 'panne' in etat_normalise:
            bus_en_panne += 1
        else:
            bus_bon_etat += 1

        # Compter les vidanges urgentes
        niveau = bus.kilometrage or 0
        seuil = bus.km_critique_huile or 0
        if seuil > 0 and niveau >= seuil:
            bus_vidange_urgente += 1

    stats = {
        'bus_total': bus_total,
        'bus_bon_etat': bus_bon_etat,
        'bus_en_panne': bus_en_panne,
        'bus_vidange_urgente': bus_vidange_urgente
    }

    return render_template('roles/mecanicien/dashboard_mecanicien.html', stats=stats)

# Route pour la page Bus UdM (accessible aux mécaniciens)
@bp.route('/bus_udm')
@login_required
@role_required('MECANICIEN')
def bus_udm():
    buses = BusUdM.query.order_by(BusUdM.numero).all()
    return render_template(
        'pages/bus_udm.html',
        bus_list=buses,
        active_page='bus_udm',
        readonly=False,  # Mécaniciens peuvent modifier les bus
        base_template='roles/mecanicien/_base_mecanicien.html'
    )

# Route pour les détails d'un bus (accessible aux mécaniciens)
@bp.route('/bus/details/<int:bus_id>')
@login_required
@role_required('MECANICIEN')
def details_bus(bus_id):
    bus = BusUdM.query.get_or_404(bus_id)

    # Récupérer l'historique complet du bus
    from app.models.trajet import Trajet
    from app.models.carburation import Carburation
    from app.models.vidange import Vidange
    from app.models.panne_bus_udm import PanneBusUdM
    from app.models.depannage import Depannage
    from app.models.document_bus_udm import DocumentBusUdM

    # Historique des trajets
    trajets = Trajet.query.filter_by(numero_bus_udm=bus.numero).order_by(Trajet.date_heure_depart.desc()).limit(10).all()

    # Historique des carburations
    carburations = Carburation.query.filter_by(bus_udm_id=bus.id).order_by(Carburation.date_carburation.desc()).limit(10).all()

    # Historique des vidanges
    vidanges = Vidange.query.filter_by(bus_udm_id=bus.id).order_by(Vidange.date_vidange.desc()).limit(10).all()

    # Historique des pannes
    pannes = PanneBusUdM.query.filter_by(bus_udm_id=bus.id).order_by(PanneBusUdM.date_heure.desc()).limit(10).all()

    # Historique des dépannages
    depannages = Depannage.query.filter_by(bus_udm_id=bus.id).order_by(Depannage.date_heure.desc()).limit(10).all()

    # Documents administratifs avec calcul des statuts
    documents_raw = DocumentBusUdM.query.filter_by(numero_bus_udm=bus.numero).order_by(DocumentBusUdM.date_debut.desc()).all()

    # Calculer un statut de validité par document
    from datetime import date
    today = date.today()
    documents = []
    for d in documents_raw:
        status = 'BLEU'
        percent_left = None
        try:
            total_days = (d.date_expiration - d.date_debut).days if d.date_expiration and d.date_debut else None
            left_days = (d.date_expiration - today).days if d.date_expiration else None
            if d.date_expiration and today > d.date_expiration:
                status = 'ROUGE'
                percent_left = 0
            elif total_days and total_days > 0 and left_days is not None:
                ratio = max(0, left_days) / total_days
                percent_left = round(ratio * 100)
                if ratio <= 0.10:
                    status = 'ORANGE'
                else:
                    status = 'BLEU'
            else:
                status = 'BLEU'
        except Exception:
            status = 'BLEU'
            percent_left = None

        documents.append({
            'document_id': d.document_id,
            'numero_bus_udm': d.numero_bus_udm,
            'type_document': d.type_document,
            'date_debut': d.date_debut,
            'date_expiration': d.date_expiration,
            'status': status,
            'percent_left': percent_left,
        })

    return render_template(
        'pages/details_bus.html',
        bus=bus,
        trajets=trajets,
        carburations=carburations,
        vidanges=vidanges,
        pannes=pannes,
        depannages=depannages,
        documents=documents,
        active_page='bus_udm',
        base_template='roles/mecanicien/_base_mecanicien.html'
    )

# Route pour la page Carburation (accessible aux mécaniciens)
@bp.route('/carburation')
@login_required
@role_required('MECANICIEN')
def carburation():
    from app.services.gestion_carburation import build_bus_carburation_list, get_carburation_history
    from app.models.chauffeur import Chauffeur
    from app.models.utilisateur import Utilisateur
    from datetime import datetime

    # --- Tableau d'état carburation (via service partagé) ---
    bus_carburation = build_bus_carburation_list()
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()

    # --- Listes pour les formulaires ---
    chauffeurs = Chauffeur.query.order_by(Chauffeur.nom, Chauffeur.prenom).all()
    superviseurs = Utilisateur.query.filter(Utilisateur.role.in_(['ADMIN', 'CHARGE', 'MECANICIEN'])).order_by(Utilisateur.nom, Utilisateur.prenom).all()

    # --- Historique des carburations ---
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

    if selected_numero or date_debut or date_fin:
        historique_carburation = get_carburation_history(selected_numero, date_debut, date_fin)
    else:
        historique_carburation = get_carburation_history()

    return render_template(
        'pages/carburation.html',
        active_page='carburation',
        bus_carburation=bus_carburation,
        historique_carburation=historique_carburation,
        numeros_aed=numeros_aed,
        selected_numero=selected_numero,
        post_url=url_for('mecanicien.enregistrer_carburation'),
        selected_date_debut=date_debut_str,
        selected_date_fin=date_fin_str,
        chauffeurs=chauffeurs,
        superviseurs=superviseurs
    )

# Route pour enregistrer une carburation (accessible aux mécaniciens)
@bp.route('/enregistrer_carburation', methods=['POST'])
@login_required
@role_required('MECANICIEN')
def enregistrer_carburation():
    from app.services.gestion_carburation import enregistrer_carburation_common
    data = request.get_json() or {}
    try:
        payload = enregistrer_carburation_common(data)
        return jsonify(payload)
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(ve)}), 400
    except LookupError as le:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(le)}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour la page Déclaration Panne (accessible aux mécaniciens)
@bp.route('/declaration_panne')
@login_required
@role_required('MECANICIEN')
def declaration_panne():
    from app.models.panne_bus_udm import PanneBusUdM
    from app.models.depannage import Depannage

    # Récupérer les pannes, plus récentes en premier
    pannes = (
        db.session.query(PanneBusUdM, BusUdM)
        .outerjoin(BusUdM, PanneBusUdM.bus_udm_id == BusUdM.id)
        .filter((PanneBusUdM.resolue == False) | (PanneBusUdM.resolue.is_(None)))
        .order_by(PanneBusUdM.date_heure.desc())
        .all()
    )
    # Récupérer l'historique des dépannages pour l'onglet
    depannages = (
        db.session.query(Depannage, BusUdM)
        .outerjoin(BusUdM, Depannage.bus_udm_id == BusUdM.id)
        .order_by(Depannage.date_heure.desc())
        .all()
    )
    # Compter les pannes non résolues par bus pour l'état opérationnel
    unresolved_counts = dict(
        db.session.query(PanneBusUdM.bus_udm_id, db.func.count(PanneBusUdM.id))
        .filter(PanneBusUdM.resolue == False)
        .group_by(PanneBusUdM.bus_udm_id)
        .all()
    )

    return render_template('pages/depanage.html',
                         active_page='declaration_panne',
                         pannes=pannes,
                         depannages=depannages,
                         unresolved_counts=unresolved_counts)

# Route pour la page Dépannage (accessible aux mécaniciens)
@bp.route('/depannage')
@login_required
@role_required('MECANICIEN')
def depannage():
    from app.models.panne_bus_udm import PanneBusUdM
    from app.models.depannage import Depannage

    # Récupérer les pannes, plus récentes en premier
    pannes = (
        db.session.query(PanneBusUdM, BusUdM)
        .outerjoin(BusUdM, PanneBusUdM.bus_udm_id == BusUdM.id)
        .filter((PanneBusUdM.resolue == False) | (PanneBusUdM.resolue.is_(None)))
        .order_by(PanneBusUdM.date_heure.desc())
        .all()
    )
    # Récupérer l'historique des dépannages pour l'onglet
    depannages = (
        db.session.query(Depannage, BusUdM)
        .outerjoin(BusUdM, Depannage.bus_udm_id == BusUdM.id)
        .order_by(Depannage.date_heure.desc())
        .all()
    )
    # Compter les pannes non résolues par bus pour l'état opérationnel
    unresolved_counts = dict(
        db.session.query(PanneBusUdM.bus_udm_id, db.func.count(PanneBusUdM.id))
        .filter(PanneBusUdM.resolue == False)
        .group_by(PanneBusUdM.bus_udm_id)
        .all()
    )

    return render_template('pages/depanage.html',
                         active_page='depannage',
                         pannes=pannes,
                         depannages=depannages,
                         unresolved_counts=unresolved_counts)

# Route AJAX pour marquer comme défaillant
@bp.route('/bus_udm/<int:bus_udm_id>/defaillant', methods=['POST'])
def marquer_defaillant(bus_udm_id):
    bus_udm = BusUdM.query.get(bus_udm_id)
    if not bus_udm:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    bus_udm.etat_vehicule = 'Défaillant'
    db.session.commit()
    return jsonify({'success': True, 'etat': bus_udm.etat_vehicule})

# Route pour la page Vidange (accessible aux mécaniciens)
@bp.route('/vidange')
@login_required
@role_required('MECANICIEN')
def vidange():
    # --- Tableau d'état vidange (via service partagé) ---
    bus_vidange = build_bus_vidange_list()
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()

    # --- Historique des vidanges ---
    numeros_bus_udm = [bus.numero for bus in bus_list]
    selected_numero = request.args.get('numero_aed')
    if selected_numero:
        historique_vidange = get_vidange_history(selected_numero)
    else:
        historique_vidange = get_vidange_history()

    return render_template(
        'pages/vidange.html',
        active_page='vidange',
        bus_vidange=bus_vidange,
        historique_vidange=historique_vidange,
        numeros_aed=numeros_bus_udm,
        selected_numero=selected_numero,
        post_url=url_for('mecanicien.enregistrer_vidange')
    )

# Route pour enregistrer une vidange (accessible aux mécaniciens)
@bp.route('/enregistrer_vidange', methods=['POST'])
@login_required
@role_required('MECANICIEN')
def enregistrer_vidange():
    data = request.get_json() or {}
    try:
        payload = enregistrer_vidange_common(data)
        return jsonify(payload)
    except ValueError as ve:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(ve)}), 400
    except LookupError as le:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(le)}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route AJAX pour marquer comme réparé
@bp.route('/bus_udm/<int:bus_udm_id>/repare', methods=['POST'])
def marquer_repare(bus_udm_id):
    bus_udm = BusUdM.query.get(bus_udm_id)
    if not bus_udm:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    bus_udm.etat_vehicule = 'En service'
    db.session.commit()
    return jsonify({'success': True, 'etat': bus_udm.etat_vehicule})

def normalize_etat(etat):
    if etat is None:
        return ''
    return unicodedata.normalize('NFKD', str(etat)).encode('ASCII', 'ignore').decode('ASCII').lower()

# Route AJAX pour basculer l'état du véhicule
@bp.route('/bus_udm/<int:bus_udm_id>/toggle_etat', methods=['POST'])
def toggle_etat_bus_udm(bus_udm_id):
    bus_udm = BusUdM.query.get(bus_udm_id)
    if not bus_udm:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    etat_normalise = normalize_etat(bus_udm.etat_vehicule)
    if 'defaillant' in etat_normalise:
        bus_udm.etat_vehicule = 'BON'
    else:
        bus_udm.etat_vehicule = 'DEFAILLANT'
    db.session.commit()
    return jsonify({'success': True, 'etat': bus_udm.etat_vehicule})