from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime
from app.models.bus_udm import BusUdM
from app.models.utilisateur import Utilisateur
from app.models.fuel_alert_state import FuelAlertState
from app.models.document_bus_udm import DocumentBusUdM
from app.models.trajet import Trajet
from app.database import db
from app.utils.emailer import send_email
from app.services.gestion_vidange import OIL_CAPACITY_KM
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only
def admin_only(view):
    return role_required('ADMIN')(view)

# Route pour la page Bus AED qui affiche la liste des bus depuis la base
@admin_only
@bp.route('/bus')
def bus():
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()
    return render_template('bus_udm.html', bus_list=bus_list)

# Route pour la page Ajouter Bus qui gère l'affichage et la soumission du formulaire d'ajout d'un bus AED
@admin_only
@bp.route('/ajouter_bus', methods=['GET', 'POST'])
def ajouter_bus():
    if request.method == 'POST':
        numero = request.form.get('numero')
        immatriculation = request.form.get('immatriculation')
        # Nouveaux champs obligatoires
        numero_chassis = request.form.get('numero_chassis')
        modele = request.form.get('modele')
        type_vehicule = request.form.get('type_vehicule')
        marque = request.form.get('marque')
        # Champs existants
        kilometrage = request.form.get('kilometrage')
        type_huile = request.form.get('type_huile')
        capacite_plein_carburant = request.form.get('capacite_plein_carburant')
        capacite_reservoir_litres = request.form.get('capacite_reservoir_litres')
        niveau_carburant_litres = request.form.get('niveau_carburant_litres')
        date_derniere_vidange = request.form.get('date_derniere_vidange')
        etat_vehicule = request.form.get('etat_vehicule')
        nombre_places = request.form.get('nombre_places')
        derniere_maintenance = request.form.get('derniere_maintenance')

        # Validation des champs obligatoires (incluant les nouveaux champs)
        if not all([numero, immatriculation, numero_chassis, modele, type_vehicule, marque,
                   kilometrage, type_huile, capacite_plein_carburant, date_derniere_vidange,
                   etat_vehicule, nombre_places, derniere_maintenance]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('ajouter_bus.html', next_num=numero)

        # Validation du type d'huile et calcul automatique des km critiques selon le mapping détaillé
        type_clean = (type_huile or '').strip()
        if type_clean not in OIL_CAPACITY_KM:
            flash("Type d'huile invalide. Veuillez choisir un type supporté.", 'danger')
            return render_template('ajouter_bus.html', next_num=numero)
        km_critique_huile = float(kilometrage) + OIL_CAPACITY_KM[type_clean]

        # Carburant: capacite_plein_carburant est la capacité (en km) d'autonomie après un plein
        cap_val = float(capacite_plein_carburant)
        km_critique_carburant = float(kilometrage) + cap_val

        nouveau_bus = BusUdM(
            numero=numero,
            immatriculation=immatriculation,
            # Nouveaux champs
            numero_chassis=numero_chassis,
            modele=modele,
            type_vehicule=type_vehicule,
            marque=marque,
            # Champs existants
            kilometrage=float(kilometrage),
            type_huile=type_clean,
            km_critique_huile=km_critique_huile,
            km_critique_carburant=km_critique_carburant,
            capacite_plein_carburant=cap_val,
            capacite_reservoir_litres=float(capacite_reservoir_litres) if capacite_reservoir_litres else None,
            niveau_carburant_litres=float(niveau_carburant_litres) if niveau_carburant_litres else None,
            date_derniere_vidange=datetime.strptime(date_derniere_vidange, '%Y-%m-%d').date(),
            etat_vehicule=etat_vehicule,
            nombre_places=int(nombre_places),
            derniere_maintenance=datetime.strptime(derniere_maintenance, '%Y-%m-%d').date()
        )
        db.session.add(nouveau_bus)
        db.session.commit()
        flash('Bus UdM ajouté avec succès !', 'success')
        return redirect(url_for('admin.dashboard'))

    # Préfixe automatique pour le numéro
    next_num = "AED-"
    return render_template('ajouter_bus.html', next_num=next_num)

# Route AJAX pour ajouter un bus AED depuis le dashboard
@admin_only
@bp.route('/ajouter_bus_ajax', methods=['POST'])
def ajouter_bus_ajax():
    numero = request.form.get('numero')
    immatriculation = request.form.get('immatriculation')
    # Nouveaux champs obligatoires
    numero_chassis = request.form.get('numero_chassis')
    modele = request.form.get('modele')
    type_vehicule = request.form.get('type_vehicule')
    marque = request.form.get('marque')
    # Champs existants
    kilometrage = request.form.get('kilometrage')
    type_huile = request.form.get('type_huile')
    capacite_plein_carburant = request.form.get('capacite_plein_carburant')
    capacite_reservoir_litres = request.form.get('capacite_reservoir_litres')
    niveau_carburant_litres = request.form.get('niveau_carburant_litres')
    date_derniere_vidange = request.form.get('date_derniere_vidange')
    etat_vehicule = request.form.get('etat_vehicule')
    nombre_places = request.form.get('nombre_places')
    derniere_maintenance = request.form.get('derniere_maintenance')

    # Validation des champs obligatoires (incluant les nouveaux champs)
    if not all([numero, immatriculation, numero_chassis, modele, type_vehicule, marque,
               kilometrage, type_huile, capacite_plein_carburant, date_derniere_vidange,
               etat_vehicule, nombre_places, derniere_maintenance]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    kilometrage_val = float(kilometrage)
    capacite_val = float(capacite_plein_carburant)

    # Valider et calculer km_critique_huile selon le type d'huile détaillé
    type_clean = (type_huile or '').strip()
    if type_clean not in OIL_CAPACITY_KM:
        return jsonify({'success': False, 'message': "Type d'huile invalide. Veuillez choisir un type supporté."}), 400
    intervalle = OIL_CAPACITY_KM[type_clean]
    km_critique_huile = kilometrage_val + intervalle

    # Carburant
    km_critique_carburant = kilometrage_val + capacite_val

    try:
        nouveau_bus = BusUdM(
            numero=numero,
            immatriculation=immatriculation,
            # Nouveaux champs
            numero_chassis=numero_chassis,
            modele=modele,
            type_vehicule=type_vehicule,
            marque=marque,
            # Champs existants
            kilometrage=float(kilometrage),
            type_huile=type_huile,
            km_critique_huile=km_critique_huile,
            km_critique_carburant=km_critique_carburant,
            capacite_plein_carburant=capacite_val,
            capacite_reservoir_litres=float(capacite_reservoir_litres) if capacite_reservoir_litres else None,
            niveau_carburant_litres=float(niveau_carburant_litres) if niveau_carburant_litres else None,
            date_derniere_vidange=datetime.strptime(date_derniere_vidange, '%Y-%m-%d').date(),
            etat_vehicule=etat_vehicule,
            nombre_places=int(nombre_places),
            derniere_maintenance=datetime.strptime(derniere_maintenance, '%Y-%m-%d').date()
        )
        db.session.add(nouveau_bus)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bus UdM ajouté avec succès !'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500

# Route AJAX: liste des Bus UdM pour autocomplétion
@admin_only
@bp.route('/bus_udm_list_ajax', methods=['GET'])
def bus_udm_list_ajax():
    try:
        buses = BusUdM.query.order_by(BusUdM.numero).all()
        data = [
            {
                'id': b.id,
                'numero': b.numero,
                'immatriculation': b.immatriculation,
                'kilometrage': b.kilometrage
            } for b in buses
        ]
        return jsonify({'success': True, 'bus_udm': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour obtenir les détails d'un bus UdM en AJAX
@admin_only
@bp.route('/details_bus_ajax/<int:bus_id>', methods=['GET'])
def details_bus_ajax(bus_id):
    bus = BusUdM.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    
    data = {
        'id': bus.id,
        'numero': bus.numero,
        'immatriculation': bus.immatriculation,
        'kilometrage': bus.kilometrage,
        'type_huile': bus.type_huile,
        'km_critique_huile': bus.km_critique_huile,
        'km_critique_carburant': bus.km_critique_carburant,
        'capacite_reservoir_litres': bus.capacite_reservoir_litres,
        'niveau_carburant_litres': bus.niveau_carburant_litres,
        'date_derniere_vidange': bus.date_derniere_vidange.strftime('%d/%m/%Y') if bus.date_derniere_vidange else '',
        'etat_vehicule': bus.etat_vehicule,
        'nombre_places': bus.nombre_places,
        'derniere_maintenance': bus.derniere_maintenance.strftime('%d/%m/%Y') if bus.derniere_maintenance else ''
    }

    # Récupérer les documents administratifs liés
    docs = DocumentBusUdM.query.filter_by(numero_bus_udm=bus.numero).all()
    docs_data = []
    for d in docs:
        if d.date_expiration:
            pct = ((d.date_expiration - datetime.utcnow().date()).days / max((d.date_expiration - d.date_debut).days, 1)) * 100
            if pct <= 10:
                status = 'RED'
            elif pct <= 30:
                status = 'ORANGE'
            else:
                status = 'GREEN'
        else:
            status = 'GREEN'
        docs_data.append({
            'type_document': d.type_document,
            'date_debut': d.date_debut.strftime('%d/%m/%Y'),
            'date_expiration': d.date_expiration.strftime('%d/%m/%Y') if d.date_expiration else '',
            'status': status
        })
    return jsonify({'success': True, 'bus': data, 'documents': docs_data})

# Route pour mettre à jour le niveau de carburant
@admin_only
@bp.route('/mettre_a_jour_niveau_carburant_ajax/<int:bus_id>', methods=['POST'])
def mettre_a_jour_niveau_carburant_ajax(bus_id):
    bus = BusUdM.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    
    # Accepte JSON ou formulaire
    if request.is_json:
        data = request.get_json(silent=True) or {}
        val = data.get('niveau_carburant_litres')
    else:
        val = request.form.get('niveau_carburant_litres')
    
    try:
        bus.niveau_carburant_litres = float(val) if val is not None and val != '' else None
        db.session.commit()
        
        # Après mise à jour, vérifier seuils et envoyer email si nécessaire
        try:
            cap = bus.capacite_reservoir_litres or 0
            niv = bus.niveau_carburant_litres or 0
            pct = (niv / cap * 100) if cap > 0 else None

            def current_threshold(p):
                if p is None:
                    return None
                if p <= 10:
                    return 10
                if p <= 25:
                    return 25
                if p <= 50:
                    return 50
                return None

            th = current_threshold(pct)
            state = FuelAlertState.query.filter_by(aed_id=bus.id).first()
            last = state.last_threshold if state else None
            
            if th != last:
                # Chercher email admin
                admin_user = Utilisateur.query.filter_by(role='ADMIN').first()
                admin_email = getattr(admin_user, 'email', None) if admin_user else None
                if th is not None and admin_email:
                    subject = f"Alerte carburant AED {bus.numero}: {pct:.0f}%"
                    body = (
                        f"Le niveau de carburant du bus AED {bus.numero} est à {pct:.1f}% (≈ {niv} L / {cap} L).\n"
                        f"Seuil atteint: {th}%.\n"
                        "Cette alerte est dédupliquée: vous ne recevrez pas de nouvel email tant que le bus reste dans cette tranche."
                    )
                    send_email(subject, body, admin_email)
                
                # Mettre à jour l'état
                if state:
                    state.last_threshold = th
                else:
                    state = FuelAlertState(aed_id=bus.id, last_threshold=th)
                    db.session.add(state)
                db.session.commit()
        except Exception:
            db.session.rollback()
            # On ignore les erreurs d'alerte pour ne pas casser l'UX

        return jsonify({'success': True, 'message': 'Niveau carburant mis à jour.', 'niveau_carburant_litres': bus.niveau_carburant_litres})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour ajouter ou mettre à jour un document administratif d'un AED
@admin_only
@bp.route('/ajouter_document_aed_ajax/<int:bus_id>', methods=['POST'])
def ajouter_document_aed_ajax(bus_id):
    bus = BusUdM.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    
    # Accepte JSON ou formulaire url-encodé
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form
    
    type_doc = data.get('type_document')
    date_debut = data.get('date_debut')
    date_expiration = data.get('date_expiration')
    
    if not type_doc or not date_debut:
        return jsonify({'success': False, 'message': 'Champs manquants.'}), 400
    
    # Convertir les dates
    try:
        date_debut_dt = datetime.strptime(date_debut, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Date début invalide'}), 400
    
    date_exp_dt = None
    if date_expiration:
        try:
            date_exp_dt = datetime.strptime(date_expiration, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Date expiration invalide'}), 400

    doc = DocumentBusUdM(
        numero_bus_udm=bus.numero,
        type_document=type_doc,
        date_debut=date_debut_dt,
        date_expiration=date_exp_dt
    )
    
    try:
        db.session.add(doc)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Document ajouté avec succès.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour supprimer un bus en AJAX via son id
@admin_only
@bp.route('/supprimer_bus_ajax/<int:bus_id>', methods=['POST'])
def supprimer_bus_ajax(bus_id):
    bus = BusUdM.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404

    # Détacher ce bus de tous les trajets avant suppression pour éviter les contraintes FK
    Trajet.query.filter_by(numero_aed=bus.numero).update({'numero_aed': None})
    db.session.commit()  # Valider le détachement des FK avant suppression

    # Supprimer tous les documents administratifs liés à ce bus
    DocumentBusUdM.query.filter_by(numero_bus_udm=bus.numero).delete()

    try:
        db.session.delete(bus)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bus supprimé avec succès.'})
    except Exception as e:
        db.session.rollback()
        import traceback
        print('Erreur suppression bus:', traceback.format_exc())
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500
