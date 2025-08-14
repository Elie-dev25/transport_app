from flask import Blueprint, render_template, request, jsonify
from app.models.aed import AED
from app.models.vidange import Vidange
from app.services.gestion_vidange import get_vidange_history
from app.database import db
from datetime import datetime
import unicodedata

# Création du blueprint pour le mécanicien
bp = Blueprint('mecanicien', __name__, url_prefix='/mecanicien')

# Route du tableau de bord mécanicien
@bp.route('/dashboard')
def dashboard():
    bus_list = AED.query.order_by(AED.numero).all()
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