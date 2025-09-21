from flask import render_template, request, jsonify, url_for
from flask_login import current_user
from datetime import datetime
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.depannage import Depannage
from app.models.utilisateur import Utilisateur
from app.models.chauffeur import Chauffeur
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

# Définition du décorateur admin_only (ADMIN et RESPONSABLE avec traçabilité)
def admin_only(view):
    from app.routes.common import admin_or_responsable
    return admin_or_responsable(view)

# Route pour la page de Dépannage
@admin_only
@bp.route('/depanage')
def depanage():
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
    
    # Détecter si appelé par un responsable
    source = request.args.get('source', '')
    use_responsable_base = source == 'responsable' or (current_user.is_authenticated and current_user.role == 'RESPONSABLE')

    # Passer les pannes et dépannages au template
    return render_template('pages/depanage.html', pannes=pannes, depannages=depannages, unresolved_counts=unresolved_counts, use_responsable_base=use_responsable_base)

# Route pour enregistrer une déclaration de panne
@admin_only
@bp.route('/declarer_panne', methods=['POST'])
def declarer_panne():
    data = request.get_json(silent=True) or {}
    
    # Accepter les deux noms de champs pour compat compatibilité des templates
    numero_aed = data.get('numero_aed') or data.get('numero_bus_udm')
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
            enregistre_par=enregistre_par,
            resolue=False
        )
        
        # Dès qu'une panne est déclarée, le bus n'est plus BON
        bus_existant.etat_vehicule = 'DEFAILLANT'
        
        db.session.add(nouvelle_panne)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Panne déclarée avec succès.'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# Route pour enregistrer un dépannage (réparation)
@admin_only
@bp.route('/enregistrer_depannage', methods=['POST'])
def enregistrer_depannage():
    try:
        data = request.get_json(silent=True) or request.form or {}

        panne_id = data.get('panne_id')
        numero_bus_udm = data.get('numero_bus_udm')
        immatriculation = data.get('immatriculation')
        kilometrage = data.get('kilometrage')
        cout_reparation = data.get('cout_reparation')
        description_panne = data.get('description_panne')
        cause_panne = data.get('cause_panne')

        if not numero_bus_udm or not description_panne:
            return jsonify({'success': False, 'message': 'Champs obligatoires manquants.'}), 400

        # Casts
        km_val = None
        if kilometrage not in (None, ''):
            try:
                km_val = float(kilometrage)
            except ValueError:
                return jsonify({'success': False, 'message': 'Kilométrage invalide.'}), 400

        cout_val = None
        if cout_reparation not in (None, ''):
            try:
                cout_val = float(cout_reparation)
            except ValueError:
                return jsonify({'success': False, 'message': 'Coût de réparation invalide.'}), 400

        # Chercher le bus
        bus = BusUdM.query.filter_by(numero=numero_bus_udm).first()
        bus_id = bus.id if bus else None

        # Traçabilité: nom complet ou login
        nom = getattr(current_user, 'nom', None)
        prenom = getattr(current_user, 'prenom', None)
        full_name = " ".join([p for p in [nom, prenom] if p]) if (nom or prenom) else None
        login = getattr(current_user, 'login', None)
        repare_par = full_name or login or (getattr(current_user, 'get_id', lambda: None)() or 'Inconnu')

        dep = Depannage(
            panne_id=int(panne_id) if panne_id else None,
            bus_udm_id=bus_id,
            numero_bus_udm=numero_bus_udm,
            immatriculation=immatriculation,
            kilometrage=km_val,
            cout_reparation=cout_val,
            description_panne=description_panne,
            cause_panne=cause_panne,
            repare_par=repare_par,
        )
        db.session.add(dep)

        # Mettre à jour le kilométrage du bus si fourni
        if bus and km_val is not None:
            if bus.kilometrage is not None and km_val < float(bus.kilometrage):
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Le kilométrage doit être ≥ {bus.kilometrage}.'}), 400
            bus.kilometrage = km_val
            db.session.add(bus)

        # Si une panne est liée, la marquer comme résolue
        if panne_id:
            panne_obj = PanneBusUdM.query.get(int(panne_id))
            if panne_obj:
                panne_obj.resolue = True
                panne_obj.date_resolution = datetime.utcnow()
                db.session.add(panne_obj)

                # Déterminer le bus concerné par la panne si non trouvé plus haut
                if not bus and panne_obj.bus_udm_id:
                    bus = BusUdM.query.get(panne_obj.bus_udm_id)

        # Ne remettre le bus en état BON que si TOUTES les pannes déclarées sont résolues
        if bus:
            unresolved_count = db.session.query(PanneBusUdM).filter(
                PanneBusUdM.bus_udm_id == bus.id,
                PanneBusUdM.resolue == False
            ).count()
            if unresolved_count == 0:
                bus.etat_vehicule = 'BON'
            else:
                bus.etat_vehicule = 'DEFAILLANT'
            db.session.add(bus)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Réparation enregistrée avec succès.'})
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
        'pages/vidange.html',
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
    
    # --- Listes pour les formulaires ---
    chauffeurs = Chauffeur.query.order_by(Chauffeur.nom, Chauffeur.prenom).all()
    superviseurs = Utilisateur.query.filter(Utilisateur.role.in_(['ADMIN', 'CHARGE'])).order_by(Utilisateur.nom, Utilisateur.prenom).all()

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
        'pages/carburation.html',
        active_page='carburation',
        bus_carburation=bus_carburation,
        historique_carburation=historique_carburation,
        numeros_aed=numeros_aed,
        selected_numero=selected_numero,
        post_url=url_for('admin.enregistrer_carburation'),
        selected_date_debut=date_debut_str,
        selected_date_fin=date_fin_str,
        chauffeurs=chauffeurs,
        superviseurs=superviseurs
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
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()
    return render_template('roles/mecanicien/dashboard_mecanicien.html', bus_list=bus_list)
