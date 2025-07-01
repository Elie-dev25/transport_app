from flask import Blueprint, render_template, request, jsonify
from app.models.aed import AED
from app.database import db
import unicodedata

# Création du blueprint pour le mécanicien
bp = Blueprint('mecanicien', __name__, url_prefix='/mecanicien')

# Route du tableau de bord mécanicien
@bp.route('/dashboard')
def dashboard():
    bus_list = AED.query.order_by(AED.numero).all()
    bus_infos = []
    for bus in bus_list:
        niveau = bus.niveau_huile
        seuil = bus.seuil_critique_huile
        if niveau == seuil:
            color = '#ef4444'  # rouge
        elif seuil - 40 <= niveau < seuil:
            color = '#eab308'  # jaune
        else:
            color = '#22c55e'  # vert
        bus_infos.append({
            'id': bus.id,
            'numero': bus.numero,
            'etat_vehicule': bus.etat_vehicule,
            'niveau_huile': bus.niveau_huile,
            'seuil_critique_huile': bus.seuil_critique_huile,
            'color': color
        })
    return render_template('dashboard_mecanicien.html', bus_list=bus_infos)

# Route AJAX pour marquer comme défaillant
@bp.route('/aed/<int:aed_id>/defaillant', methods=['POST'])
def marquer_defaillant(aed_id):
    aed = AED.query.get(aed_id)
    if not aed:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    aed.etat_vehicule = 'Défaillant'
    db.session.commit()
    return jsonify({'success': True, 'etat': aed.etat_vehicule})

# Route AJAX pour marquer comme réparé
@bp.route('/aed/<int:aed_id>/repare', methods=['POST'])
def marquer_repare(aed_id):
    aed = AED.query.get(aed_id)
    if not aed:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    aed.etat_vehicule = 'En service'
    db.session.commit()
    return jsonify({'success': True, 'etat': aed.etat_vehicule})

def normalize_etat(etat):
    if etat is None:
        return ''
    return unicodedata.normalize('NFKD', str(etat)).encode('ASCII', 'ignore').decode('ASCII').lower()

# Route AJAX pour basculer l'état du véhicule
@bp.route('/aed/<int:aed_id>/toggle_etat', methods=['POST'])
def toggle_etat_aed(aed_id):
    aed = AED.query.get(aed_id)
    if not aed:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    etat_normalise = normalize_etat(aed.etat_vehicule)
    if 'defaillant' in etat_normalise:
        aed.etat_vehicule = 'BON'
    else:
        aed.etat_vehicule = 'DEFAILLANT'
    db.session.commit()
    return jsonify({'success': True, 'etat': aed.etat_vehicule})