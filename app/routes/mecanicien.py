from flask import Blueprint, render_template, request, jsonify, url_for
from app.models.bus_udm import BusUdM
from app.database import db
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
def dashboard():
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()
    bus_infos = []
    for bus in bus_list:
        niveau = bus.kilometrage or 0
        seuil = bus.km_critique_huile or 0
        if seuil > 0:
            if niveau >= seuil:
                color = '#ef4444'  # rouge
            elif seuil - 500 <= niveau < seuil:
                color = '#eab308'  # jaune
            else:
                color = '#22c55e'  # vert
        else:
            color = '#22c55e'  # vert par défaut si pas de seuil
        km_restant = (bus.km_critique_huile or 0) - (bus.kilometrage or 0)
        bus_infos.append({
            'id': bus.id,
            'numero': bus.numero,
            'etat_vehicule': bus.etat_vehicule,
            'kilometrage': bus.kilometrage,
            'km_critique_huile': bus.km_critique_huile,
            'km_restant': km_restant,
            'color': color
        })
    return render_template('dashboard_mecanicien.html', bus_list=bus_infos)

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
        'vidange.html',
        active_page='vidange',
        bus_vidange=bus_vidange,
        historique_vidange=historique_vidange,
        numeros_aed=numeros_bus_udm,
        selected_numero=selected_numero,
        post_url=url_for('mecanicien.enregistrer_vidange')
    )

# Route pour enregistrer une vidange (accessible aux mécaniciens)
@bp.route('/enregistrer_vidange', methods=['POST'])
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