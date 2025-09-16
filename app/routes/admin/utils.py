from flask import jsonify
from datetime import datetime, date
from app.models.bus_udm import BusUdM
from app.models.trajet import Trajet
from app.database import db
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only (ADMIN et RESPONSABLE avec traçabilité)
def admin_only(view):
    from app.routes.common import admin_or_responsable
    return admin_or_responsable(view)

# Route pour les alertes de documents
@admin_only
@bp.route('/documents_alerts_ajax', methods=['GET'])
def documents_alerts_ajax():
    """Retourne les documents dont l'expiration est comprise entre 20% et 30% du temps restant."""
    from app.models.document_aed import DocumentAED
    alerts = []
    today = datetime.utcnow().date()
    docs = DocumentAED.query.filter(DocumentAED.date_expiration != None).all()
    for d in docs:
        total_days = max((d.date_expiration - d.date_debut).days, 1)
        remaining_days = (d.date_expiration - today).days
        pct = remaining_days / total_days * 100
        if pct <= 30:
            status = 'RED' if pct<=10 else 'ORANGE'
            # construire durée lisible
            if remaining_days >= 60:
                reste = f"{round(remaining_days/30)} mois"
            elif remaining_days >= 14:
                reste = f"{round(remaining_days/7)} semaines"
            else:
                reste = f"{remaining_days} jours"
            alerts.append({
                'type_document': d.type_document,
                'numero_aed': d.numero_aed,
                'date_expiration': d.date_expiration.strftime('%d/%m/%Y'),
                'pourcentage_restant': round(pct,1),
                'reste': reste,
                'status': status
            })
    return jsonify({'success': True, 'alerts': alerts})

# Route pour les alertes de carburant
@admin_only
@bp.route('/fuel_alerts_ajax', methods=['GET'])
def fuel_alerts_ajax():
    """Retourne les alertes carburant selon les seuils 50%, 25%, 10%.
    Status: RED (<=10), ORANGE (<=25), YELLOW (<=50).
    """
    alerts = []
    buses = BusUdM.query.all()
    for bus in buses:
        cap = bus.capacite_reservoir_litres or 0
        niv = bus.niveau_carburant_litres or 0
        if cap <= 0:
            continue
        pct = (niv / cap) * 100
        status = None
        threshold = None
        if pct <= 10:
            status, threshold = 'RED', 10
        elif pct <= 25:
            status, threshold = 'ORANGE', 25
        elif pct <= 50:
            status, threshold = 'YELLOW', 50
        if status:
            alerts.append({
                'numero_aed': bus.numero,
                'pourcentage': round(pct, 1),
                'threshold': threshold,
                'status': status,
                'message': f"Niveau carburant {round(pct)}% (seuil {threshold}%)"
            })
    
    return jsonify({'success': True, 'alerts': alerts})
