from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.utilisateur import Utilisateur
from app.models.fuel_alert_state import FuelAlertState
from app.models.document_bus_udm import DocumentBusUdM
from app.models.trajet import Trajet
from app.database import db
from app.utils.emailer import send_email
from app.services.gestion_vidange import OIL_CAPACITY_KM
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only (ADMIN et RESPONSABLE avec traçabilité)
def admin_only(view):
    from app.routes.common import admin_or_responsable
    return admin_or_responsable(view)

@admin_only
@bp.route('/ajouter_document_udm_ajax/<int:bus_id>', methods=['POST'])
def ajouter_document_udm_ajax(bus_id):
    try:
        bus = BusUdM.query.get(bus_id)
        if not bus:
            return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404

        type_document = request.form.get('type_document')
        date_debut = request.form.get('date_debut')
        date_expiration = request.form.get('date_expiration')

        if not type_document or not date_debut or not date_expiration:
            return jsonify({'success': False, 'message': 'Veuillez renseigner tous les champs requis.'}), 400

        # Valider le type contre l’Enum du modèle
        allowed = {
            'VISITE_TECHNIQUE',
            'ASSURANCE_VIGNETTE',
            'TAXE_STATIONNEMENT',
            'TAXE_PUBLICITAIRE',
            'CARTE_GRISE',
        }
        if type_document not in allowed:
            return jsonify({'success': False, 'message': 'Type de document invalide.'}), 400

        from datetime import datetime
        try:
            d_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            d_exp = datetime.strptime(date_expiration, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Format de date invalide. Utilisez AAAA-MM-JJ.'}), 400

        if d_exp < d_debut:
            return jsonify({'success': False, 'message': "La date d'expiration doit être postérieure à la date de début."}), 400

        doc = DocumentBusUdM(
            numero_bus_udm=bus.numero,
            type_document=type_document,
            date_debut=d_debut,
            date_expiration=d_exp,
        )
        db.session.add(doc)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Document enregistré avec succès.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_only
@bp.route('/modifier_document_udm_ajax/<int:document_id>', methods=['POST'])
def modifier_document_udm_ajax(document_id):
    try:
        doc = DocumentBusUdM.query.get(document_id)
        if not doc:
            return jsonify({'success': False, 'message': 'Document introuvable.'}), 404

        date_debut = request.form.get('date_debut')
        date_expiration = request.form.get('date_expiration')
        if not date_debut or not date_expiration:
            return jsonify({'success': False, 'message': 'Veuillez renseigner les dates.'}), 400

        from datetime import datetime
        try:
            d_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            d_exp = datetime.strptime(date_expiration, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Format de date invalide. Utilisez AAAA-MM-JJ.'}), 400

        if d_exp < d_debut:
            return jsonify({'success': False, 'message': "La date d'expiration doit être postérieure à la date de production."}), 400

        # Mettre à jour uniquement la validité
        doc.date_debut = d_debut
        doc.date_expiration = d_exp
        db.session.commit()
        return jsonify({'success': True, 'message': 'Validité mise à jour avec succès.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_only
@bp.route('/bus')
def bus():
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()

    # Calculer les pannes non résolues par bus pour ajuster l'état affiché
    from app.database import db as _db
    unresolved_counts = dict(
        _db.session.query(PanneBusUdM.bus_udm_id, _db.func.count(PanneBusUdM.id))
        .filter((PanneBusUdM.resolue == False) | (PanneBusUdM.resolue.is_(None)))
        .group_by(PanneBusUdM.bus_udm_id)
        .all()
    )

    for b in bus_list:
        count = unresolved_counts.get(b.id, 0)
        if count and b.etat_vehicule != 'DEFAILLANT':
            # Forcer l'affichage comme défaillant s'il y a des pannes ouvertes
            b.etat_vehicule = 'DEFAILLANT'
        elif not count and not b.etat_vehicule:
            # Si pas de panne ouverte et état NULL, afficher 'BON'
            b.etat_vehicule = 'BON'

    # Utiliser l'utilitaire pour gérer le contexte de rôle
    from app.utils.route_utils import add_role_context_to_template_vars

    template_vars = add_role_context_to_template_vars(bus_list=bus_list)
    return render_template('roles/admin/bus_udm.html', **template_vars)

@admin_only
@bp.route('/bus/ajouter', methods=['GET', 'POST'])
def ajouter_bus():
    if request.method == 'POST':
        numero = request.form['numero']
        marque = request.form['marque']
        modele = request.form['modele']
        annee = int(request.form['annee'])
        capacite = int(request.form['capacite'])
        kilometrage = int(request.form['kilometrage'])
        etat_vehicule = request.form['etat_vehicule']
        
        # Vérifier si le numéro existe déjà
        existing_bus = BusUdM.query.filter_by(numero=numero).first()
        if existing_bus:
            flash('Un bus avec ce numéro existe déjà.', 'error')
            return redirect(url_for('admin.ajouter_bus'))
        
        nouveau_bus = BusUdM(
            numero=numero,
            marque=marque,
            modele=modele,
            annee=annee,
            capacite=capacite,
            kilometrage=kilometrage,
            etat_vehicule=etat_vehicule
        )
        
        try:
            db.session.add(nouveau_bus)
            db.session.commit()
            flash('Bus ajouté avec succès!', 'success')
            return redirect(url_for('admin.bus'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du bus: {str(e)}", 'error')
    
    return render_template('ajouter_bus.html')

@admin_only
@bp.route('/bus/modifier/<int:bus_id>', methods=['GET', 'POST'])
def modifier_bus(bus_id):
    bus = BusUdM.query.get_or_404(bus_id)
    
    if request.method == 'POST':
        bus.numero = request.form['numero']
        bus.marque = request.form['marque']
        bus.modele = request.form['modele']
        bus.annee = int(request.form['annee'])
        bus.capacite = int(request.form['capacite'])
        bus.kilometrage = int(request.form['kilometrage'])
        bus.etat_vehicule = request.form['etat_vehicule']
        
        try:
            db.session.commit()
            flash('Bus modifié avec succès!', 'success')
            return redirect(url_for('admin.bus'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('modifier_bus.html', bus=bus)

@admin_only
@bp.route('/bus/supprimer/<int:bus_id>', methods=['POST'])
def supprimer_bus(bus_id):
    bus = BusUdM.query.get_or_404(bus_id)
    
    try:
        # Vérifier s'il y a des trajets associés
        trajets_associes = Trajet.query.filter_by(numero_bus_udm=bus.numero).count()
        if trajets_associes > 0:
            flash(f"Impossible de supprimer ce bus. Il y a {trajets_associes} trajets associés.", 'error')
            return redirect(url_for('admin.bus'))
        
        db.session.delete(bus)
        db.session.commit()
        flash('Bus supprimé avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('admin.bus'))

@admin_only
@bp.route('/bus/details/<int:bus_id>')
def details_bus(bus_id):
    bus = BusUdM.query.get_or_404(bus_id)

    # Récupérer l'historique complet du bus
    from app.models.trajet import Trajet
    from app.models.carburation import Carburation
    from app.models.vidange import Vidange

    # Historique des trajets
    trajets = Trajet.query.filter_by(numero_bus_udm=bus.numero).order_by(Trajet.date_heure_depart.desc()).all()

    # Historique des carburations
    carburations = Carburation.query.filter_by(bus_udm_id=bus.id).order_by(Carburation.date_carburation.desc()).all()

    # Historique des vidanges
    vidanges = Vidange.query.filter_by(bus_udm_id=bus.id).order_by(Vidange.date_vidange.desc()).all()

    # Historique des pannes
    pannes = PanneBusUdM.query.filter_by(bus_udm_id=bus.id).order_by(PanneBusUdM.date_heure.desc()).all()

    # Historique des dépannages
    from app.models.depannage import Depannage
    depannages = Depannage.query.filter_by(bus_udm_id=bus.id).order_by(Depannage.date_heure.desc()).all()

    # Récupérer les documents liés à ce bus via le numéro (FK: DocumentBusUdM.numero_bus_udm -> BusUdM.numero)
    documents = DocumentBusUdM.query.filter_by(numero_bus_udm=bus.numero).all()

    # Calculer un statut de validité par document
    from datetime import date
    today = date.today()
    documents_vm = []
    for d in documents:
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

        documents_vm.append({
            'document_id': d.document_id,
            'type_document': d.type_document,
            'date_debut': d.date_debut,
            'date_expiration': d.date_expiration,
            'status': status,
            'percent_left': percent_left,
        })

    # Utiliser l'utilitaire pour gérer le contexte de rôle
    from app.utils.route_utils import add_role_context_to_template_vars

    template_vars = add_role_context_to_template_vars(
        bus=bus,
        trajets=trajets,
        carburations=carburations,
        vidanges=vidanges,
        pannes=pannes,
        depannages=depannages,
        documents=documents_vm
    )

    return render_template('pages/details_bus.html', **template_vars)

@admin_only
@bp.route('/bus/<int:bus_id>/details')
def bus_details_ajax(bus_id):
    """Route AJAX pour récupérer les détails d'un bus"""
    try:
        bus = BusUdM.query.get_or_404(bus_id)

        bus_data = {
            'id': bus.id,
            'numero': bus.numero,
            'immatriculation': bus.immatriculation,
            'marque': bus.marque,
            'modele': bus.modele,
            'capacite': bus.nombre_places,
            'kilometrage': bus.kilometrage,
            'etat_vehicule': bus.etat_vehicule,
            'numero_chassis': bus.numero_chassis,
            'type_vehicule': bus.type_vehicule
        }

        return jsonify({
            'success': True,
            'bus': bus_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du chargement des détails: {str(e)}'
        })

@admin_only
@bp.route('/bus/mettre_a_jour_kilometrage', methods=['POST'])
def mettre_a_jour_kilometrage():
    bus_id = request.form.get('bus_id')
    nouveau_kilometrage = request.form.get('kilometrage')
    
    if not bus_id or not nouveau_kilometrage:
        return jsonify({'success': False, 'message': 'Données manquantes'})
    
    try:
        bus = BusUdM.query.get(bus_id)
        if not bus:
            return jsonify({'success': False, 'message': 'Bus non trouvé'})
        
        ancien_kilometrage = bus.kilometrage
        bus.kilometrage = int(nouveau_kilometrage)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Kilométrage mis à jour de {ancien_kilometrage} à {nouveau_kilometrage} km'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@admin_only
@bp.route('/bus/changer_etat', methods=['POST'])
def changer_etat_bus():
    bus_id = request.form.get('bus_id')
    nouvel_etat = request.form.get('etat')
    
    if not bus_id or not nouvel_etat:
        return jsonify({'success': False, 'message': 'Données manquantes'})
    
    try:
        bus = BusUdM.query.get(bus_id)
        if not bus:
            return jsonify({'success': False, 'message': 'Bus non trouvé'})
        
        bus.etat_vehicule = nouvel_etat
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f"État du bus {bus.numero} changé à {nouvel_etat}",
            'etat': nouvel_etat
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@admin_only
@bp.route('/bus/statistiques')
def statistiques_bus():
    # Statistiques générales
    total_bus = BusUdM.query.count()
    bus_actifs = BusUdM.query.filter_by(etat_vehicule='BON').count()
    bus_maintenance = BusUdM.query.filter_by(etat_vehicule='DEFAILLANT').count()
    
    # Kilométrage total
    km_total = db.session.query(db.func.sum(BusUdM.kilometrage)).scalar() or 0
    km_moyen = km_total / total_bus if total_bus > 0 else 0
    
    # Bus les plus utilisés (basé sur les trajets)
    bus_utilises = db.session.query(
        BusUdM.numero,
        db.func.count(Trajet.trajet_id).label('nb_trajets')
    ).join(Trajet, BusUdM.numero == Trajet.numero_bus_udm) \
     .group_by(BusUdM.numero) \
     .order_by(db.func.count(Trajet.trajet_id).desc()) \
     .limit(5).all()
    
    stats = {
        'total_bus': total_bus,
        'bus_actifs': bus_actifs,
        'bus_maintenance': bus_maintenance,
        'km_total': km_total,
        'km_moyen': round(km_moyen, 0),
        'bus_utilises': bus_utilises
    }
    
    return render_template('statistiques_bus.html', stats=stats)

@admin_only
@bp.route('/bus/export')
def export_bus():
    """Export de la liste des bus en CSV"""
    import csv
    from io import StringIO
    from flask import Response
    
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow(['Numéro', 'Marque', 'Modèle', 'Année', 'Capacité', 'Kilométrage', 'État'])
    
    # Données
    for bus in bus_list:
        writer.writerow([
            bus.numero,
            bus.marque,
            bus.modele,
            bus.annee,
            bus.capacite,
            bus.kilometrage,
            bus.etat_vehicule
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=bus_udm.csv'}
    )

# Route AJAX: liste des bus pour autocomplétion
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

# Route pour mettre à jour le niveau de carburant
@admin_only
@bp.route('/mettre_a_jour_niveau_carburant_ajax/<int:bus_id>', methods=['POST'])
def mettre_a_jour_niveau_carburant_ajax(bus_id):
    from app.models.fuel_alert_state import FuelAlertState
    from app.models.utilisateur import Utilisateur
    from app.utils.emailer import send_email
    
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
        
        # Vérifier seuils et envoyer email si nécessaire
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
            state = FuelAlertState.query.filter_by(bus_udm_id=bus.id).first()
            last = state.last_threshold if state else None
            
            if th != last:
                # Chercher email admin
                admin_user = Utilisateur.query.filter_by(role='ADMIN').first()
                admin_email = getattr(admin_user, 'email', None) if admin_user else None
                
                if th is not None and admin_email:
                    subject = f"Alerte carburant Bus UdM {bus.numero}: {pct:.0f}%"
                    body = (
                        f"Le niveau de carburant du bus {bus.numero} est à {pct:.1f}% (≈ {niv} L / {cap} L).\n"
                        f"Seuil atteint: {th}%.\n"
                        "Cette alerte est dédupliquée: vous ne recevrez pas de nouvel email tant que le bus reste dans cette tranche."
                    )
                    send_email(subject, body, admin_email)
                
                # Mettre à jour l'état
                if state:
                    state.last_threshold = th
                else:
                    state = FuelAlertState(bus_udm_id=bus.id, last_threshold=th)
                    db.session.add(state)
                db.session.commit()
        except Exception:
            db.session.rollback()
            # Ignorer les erreurs d'alerte pour ne pas casser l'UX

        return jsonify({
            'success': True, 
            'message': 'Niveau carburant mis à jour.', 
            'niveau_carburant_litres': bus.niveau_carburant_litres
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour supprimer un bus
@admin_only
@bp.route('/supprimer_bus_ajax/<int:bus_id>', methods=['POST'])
def supprimer_bus_ajax(bus_id):
    bus = BusUdM.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404

    # Détacher ce bus de tous les trajets avant suppression
    from app.models.trajet import Trajet
    Trajet.query.filter_by(numero_bus_udm=bus.numero).update({'numero_bus_udm': None})
    db.session.commit()

    # Supprimer tous les documents administratifs liés
    from app.models.document_aed import DocumentAED
    DocumentAED.query.filter_by(numero_aed=bus.numero).delete()

    try:
        db.session.delete(bus)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bus supprimé avec succès.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500
