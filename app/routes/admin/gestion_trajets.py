from flask import request, jsonify
from flask_login import current_user
from app.models.chauffeur import Chauffeur
from app.models.aed import AED
from app.forms.trajet_depart_form import TrajetDepartForm
from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm
from app.forms.trajet_sortie_hors_ville_form import TrajetSortieHorsVilleForm
from app.services.trajet_service import (
    enregistrer_depart_aed,
    enregistrer_depart_prestataire,
    enregistrer_depart_banekane_retour,
    enregistrer_depart_sortie_hors_ville,
)
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only
def admin_only(view):
    return role_required('ADMIN')(view)

# --- Endpoints Admin pour enregistrements de trajets ---
@admin_only
@bp.route('/depart_aed', methods=['POST'])
def depart_aed():
    form = TrajetDepartForm(request.form)
    # Peupler les choix dynamiques avant validation
    try:
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
    except Exception:
        form.chauffeur_id.choices = []
        form.numero_aed.choices = []
    
    if not form.validate():
        return jsonify({'success': False, 'message': 'Formulaire invalide', 'errors': form.errors}), 400
    
    ok, msg = enregistrer_depart_aed(form, current_user)
    status = 200 if ok else 400
    return jsonify({'success': ok, 'message': msg}), status

@admin_only
@bp.route('/depart_prestataire', methods=['POST'])
def depart_prestataire():
    ok, msg = enregistrer_depart_prestataire(request.form, current_user)
    status = 200 if ok else 400
    return jsonify({'success': ok, 'message': msg}), status

@admin_only
@bp.route('/depart_banekane_retour', methods=['POST'])
def depart_banekane_retour():
    form = TrajetBanekaneRetourForm(request.form)
    # Peupler les choix dynamiques avant validation
    try:
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
    except Exception:
        form.chauffeur_id.choices = []
        form.numero_aed.choices = []
    
    if not form.validate():
        return jsonify({'success': False, 'message': 'Formulaire invalide', 'errors': form.errors}), 400
    
    ok, msg = enregistrer_depart_banekane_retour(form, current_user)
    status = 200 if ok else 400
    return jsonify({'success': ok, 'message': msg}), status

@admin_only
@bp.route('/depart_sortie_hors_ville', methods=['POST'])
def depart_sortie_hors_ville():
    form = TrajetSortieHorsVilleForm(request.form)
    # Peupler les choix dynamiques avant validation
    try:
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
    except Exception:
        form.chauffeur_id.choices = []
        form.numero_aed.choices = []
    
    # Debug: afficher les données reçues et erreurs de validation
    print(f"DEBUG - Form data: {dict(request.form)}")
    print(f"DEBUG - Form errors: {form.errors}")
    print(f"DEBUG - Form validate: {form.validate()}")
    
    if not form.validate():
        return jsonify({'success': False, 'message': 'Formulaire invalide', 'errors': form.errors}), 400
    
    ok, msg = enregistrer_depart_sortie_hors_ville(form, current_user)
    status = 200 if ok else 400
    return jsonify({'success': ok, 'message': msg}), status
