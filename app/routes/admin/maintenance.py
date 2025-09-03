from flask import render_template, request, jsonify, url_for
from flask_login import current_user
from datetime import datetime
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.utilisateur import Utilisateur
from app.models.document_bus_udm import DocumentBusUdM
from app.database import db
from app.services.gestion_vidange import (
    get_vidange_history,
    build_bus_vidange_list,
    enregistrer_vidange_common,
)
from app.services.gestion_carburation import (
    get_carburation_history,
    build_bus_carburation_list,
    enregistrer_carburation_common,
)
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only
def admin_only(view):
    return role_required('ADMIN')(view)

# Route pour la page de Dépannage
@admin_only
@bp.route('/depanage')
def depanage():
    return render_template('depanage.html')

# Route pour enregistrer une déclaration de panne
@admin_only
@bp.route('/declarer_panne', methods=['POST'])
def declarer_panne():
    data = request.get_json(silent=True) or {}
    
    numero_aed = data.get('numero_aed')
    immatriculation = data.get('immatriculation')
    kilometrage = data.get('kilometrage')
    description = data.get('description')
    criticite = data.get('criticite')
    immobilisation = data.get('immobilisation', False)
    
    if not all([numero_aed, description, criticite]):
        return jsonify({'success': False, 'message': 'Champs obligatoires manquants.'}), 400
    
    if criticite not in ['FAIBLE', 'MOYENNE', 'HAUTE']:
        return jsonify({'success': False, 'message': 'Criticité invalide.'}), 400
    
    try:
        # Vérifier l'existence du bus et valider le kilométrage
        bus_existant = BusUdM.query.filter_by(numero=numero_aed).first()
        if not bus_existant:
            return jsonify({'success': False, 'message': "Numéro Bus UdM inconnu. Veuillez sélectionner un numéro existant."}), 400
        
        # Normaliser immobilisation (peut venir en bool, str, int)
        if isinstance(immobilisation, str):
            immobilisation_bool = immobilisation.strip().lower() in ('true', '1', 'oui', 'on')
        else:
            immobilisation_bool = bool(immobilisation)

        km_val = None
        if kilometrage not in (None, ''):
            try:
                km_val = float(kilometrage)
            except ValueError:
                return jsonify({'success': False, 'message': 'Kilométrage invalide.'}), 400
        
        if km_val is not None:
            km_bd = bus_existant.kilometrage or 0
            if km_val < km_bd:
                return jsonify({'success': False, 'message': f'Le kilométrage doit être supérieur ou égal à {km_bd}.'}), 400
            # Mettre à jour le kilométrage du bus si la valeur est valide
            bus_existant.kilometrage = km_val

        # Récupérer le nom complet de l'utilisateur connecté (défensif)
        nom = getattr(current_user, 'nom', None)
        prenom = getattr(current_user, 'prenom', None)
        full_name = " ".join([p for p in [nom, prenom] if p]) if (nom or prenom) else None
        login = getattr(current_user, 'login', None)
        enregistre_par = full_name or login or (getattr(current_user, 'get_id', lambda: None)() or 'Inconnu')
        
        nouvelle_panne = PanneBusUdM(
            bus_udm_id=bus_existant.id,
            numero_bus_udm=numero_aed,
            immatriculation=immatriculation,
            kilometrage=km_val if km_val is not None else None,
            description=description,
            criticite=criticite,
            immobilisation=immobilisation_bool,
            enregistre_par=enregistre_par
        )
        
        # Si immobilisation, mettre à jour l'état du bus
        if immobilisation_bool:
            bus_existant.etat_vehicule = 'DEFAILLANT'
        
        db.session.add(nouvelle_panne)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Panne déclarée avec succès.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour la page Vidange
@admin_only
@bp.route('/vidange')
def vidange():
    # --- Tableau d'état vidange (via service partagé) ---
    bus_vidange = build_bus_vidange_list()
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()

    # --- Historique des vidanges ---
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

    if selected_numero or date_debut or date_fin:
        historique_vidange = get_vidange_history(selected_numero, date_debut, date_fin)
    else:
        historique_vidange = get_vidange_history()

    return render_template(
        'vidange.html',
        active_page='vidange',
        bus_vidange=bus_vidange,
        historique_vidange=historique_vidange,
        numeros_aed=numeros_aed,
        selected_numero=selected_numero,
        post_url=url_for('admin.enregistrer_vidange'),
        selected_date_debut=date_debut_str,
        selected_date_fin=date_fin_str
    )

# Enregistrer une vidange 
@admin_only
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

# Route pour la page Carburation
@admin_only
@bp.route('/carburation')
def carburation():
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

    if selected_numero or date_debut or date_fin:
        historique_carburation = get_carburation_history(selected_numero, date_debut, date_fin)
    else:
        historique_carburation = get_carburation_history()

    return render_template(
        'carburation.html',
        active_page='carburation',
        bus_carburation=bus_carburation,
        historique_carburation=historique_carburation,
        numeros_aed=numeros_aed,
        selected_numero=selected_numero,
        post_url=url_for('admin.enregistrer_carburation'),
        selected_date_debut=date_debut_str,
        selected_date_fin=date_fin_str
    )

# Enregistrer une carburation
@admin_only
@bp.route('/enregistrer_carburation', methods=['POST'])
def enregistrer_carburation():
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

# Route du tableau de bord mécanicien
@admin_only
@bp.route('/dashboard_mecanicien')
def dashboard_mecanicien():
    bus_list = AED.query.order_by(AED.numero).all()
    return render_template('dashboard_mecanicien.html', bus_list=bus_list)
