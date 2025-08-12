


from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.aed import AED
from app.models.vidange import Vidange
from app.services.gestion_vidange import get_vidange_history
from app.database import db  # Ajout de l'import manquant
from datetime import datetime

# Création du blueprint pour l'administrateur
bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.routes.common import role_required

# Appliquer le décorateur rôle ADMIN à toutes les routes du blueprint

def admin_only(view):
    return role_required('ADMIN')(view)


bp.before_request(lambda: None)  # Placeholder pour pouvoir ajouter le décorateur via dispatch


# Route AJAX pour ajouter un bus AED depuis le dashboard (après les imports et la déclaration du blueprint)
@admin_only
@bp.route('/ajouter_bus_ajax', methods=['POST'])
def ajouter_bus_ajax():
    numero = request.form.get('numero')
    kilometrage = request.form.get('kilometrage')
    type_huile = request.form.get('type_huile')
    capacite_plein_carburant = request.form.get('capacite_plein_carburant')
    date_derniere_vidange = request.form.get('date_derniere_vidange')
    etat_vehicule = request.form.get('etat_vehicule')
    nombre_places = request.form.get('nombre_places')
    derniere_maintenance = request.form.get('derniere_maintenance')

    if not all([numero, kilometrage, type_huile, capacite_plein_carburant, date_derniere_vidange, etat_vehicule, nombre_places, derniere_maintenance]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400


    kilometrage_val = float(kilometrage)
    capacite_val = float(capacite_plein_carburant)

    # Calculs selon la nouvelle règle
    if type_huile.upper() == 'QUARTZ':
        km_critique_huile = kilometrage_val + 700
    elif type_huile.upper() == 'RUBIA':
        km_critique_huile = kilometrage_val + 600
    else:
        km_critique_huile = kilometrage_val

    km_critique_carburant = kilometrage_val + capacite_val

    try:
        nouveau_aed = AED(
            numero=numero,
            kilometrage=float(kilometrage),
            type_huile=type_huile,
            km_critique_huile=km_critique_huile,
            km_critique_carburant=km_critique_carburant,
            capacite_plein_carburant=km_critique_carburant,
            date_derniere_vidange=datetime.strptime(date_derniere_vidange, '%Y-%m-%d').date(),
            etat_vehicule=etat_vehicule,
            nombre_places=int(nombre_places),
            derniere_maintenance=datetime.strptime(derniere_maintenance, '%Y-%m-%d').date()
        )
        db.session.add(nouveau_aed)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Bus AED ajouté avec succès !'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500


# Route du tableau de bord administrateur
@admin_only
@bp.route('/dashboard')
def dashboard():
    from datetime import date
    from app.models.trajet import Trajet
    today = date.today()
    trajets_jour_aed = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.numero_aed != None).count()
    trajets_jour_bus_agence = Trajet.query.filter(db.func.date(Trajet.date_heure_depart) == today, Trajet.immat_bus != None).count()

    from app.models.chauffeur import Chauffeur
    stats = {
        'bus_actifs': AED.query.filter_by(etat_vehicule='BON').count(),
        'bus_actifs_change': 0,
        'bus_inactifs': AED.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'chauffeurs': Chauffeur.query.count(),
        'trajets_jour_aed': trajets_jour_aed,
        'trajets_jour_bus_agence': trajets_jour_bus_agence,
        'trajets_jour_change': 0,
        'bus_maintenance': AED.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'bus_maintenance_info': '',
        'etudiants': 0,
        'etudiants_change': 0
    }
    from app.utils.trafic import daily_student_trafic
    trafic = daily_student_trafic()
    stats['etudiants'] = trafic.get('present', 0)
    # Affiche le template HTML du dashboard admin
    return render_template('dashboard_admin.html', stats=stats, trafic=trafic)

# Route pour la page Bus AED qui affiche la liste des bus depuis la base
@admin_only
@bp.route('/bus')
def bus():
    bus_list = AED.query.order_by(AED.numero).all()
    return render_template('bus_aed.html', bus_list=bus_list)

# Route pour la page Chauffeurs qui affiche la liste des chauffeurs depuis la base
@admin_only
@bp.route('/chauffeurs')
def chauffeurs():
    from app.models.chauffeur import Chauffeur
    chauffeur_list = Chauffeur.query.order_by(Chauffeur.nom).all()
    return render_template('chauffeurs.html', chauffeur_list=chauffeur_list, active_page='chauffeurs')

# Route pour la page Utilisateurs qui affiche la liste des utilisateurs depuis la base
@admin_only
@bp.route('/utilisateurs')
def utilisateurs():
    from app.models.utilisateur import Utilisateur
    user_list = Utilisateur.query.order_by(Utilisateur.nom_utilisateur).all()
    return render_template('utilisateurs.html', user_list=user_list, active_page='utilisateurs')

# Route placeholder pour la page Rapports (pour éviter les erreurs de lien)
@admin_only
@bp.route('/rapports')
def rapports():
    # Affiche une page temporaire ou un message d'information
    return "Page Rapports en construction."

# Route placeholder pour la page Paramètres (pour éviter les erreurs de lien)
@admin_only
@bp.route('/parametres')
def parametres():
    # Affiche une page temporaire ou un message d'information
    return "Page Paramètres en construction."

# Route pour la page Ajouter Bus qui gère l'affichage et la soumission du formulaire d'ajout d'un bus AED
@admin_only
@bp.route('/ajouter_bus', methods=['GET', 'POST'])
def ajouter_bus():

    if request.method == 'POST':
        numero = request.form.get('numero')
        kilometrage = request.form.get('kilometrage')
        type_huile = request.form.get('type_huile')
        capacite_plein_carburant = request.form.get('capacite_plein_carburant')
        date_derniere_vidange = request.form.get('date_derniere_vidange')
        etat_vehicule = request.form.get('etat_vehicule')
        nombre_places = request.form.get('nombre_places')
        derniere_maintenance = request.form.get('derniere_maintenance')

        if not all([numero, kilometrage, type_huile, capacite_plein_carburant, date_derniere_vidange, etat_vehicule, nombre_places, derniere_maintenance]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('ajouter_bus.html', next_num=numero)

        # Calcul automatique des km critiques
        if type_huile.upper() == 'QUARTZ':
            km_critique_huile = 700
        elif type_huile.upper() == 'RUBIA':
            km_critique_huile = 600
        else:
            km_critique_huile = 0

        km_critique_carburant = float(capacite_plein_carburant)

        nouveau_aed = AED(
            numero=numero,
            kilometrage=float(kilometrage),
            type_huile=type_huile,
            km_critique_huile=km_critique_huile,
            km_critique_carburant=km_critique_carburant,
            date_derniere_vidange=datetime.strptime(date_derniere_vidange, '%Y-%m-%d').date(),
            etat_vehicule=etat_vehicule,
            nombre_places=int(nombre_places),
            derniere_maintenance=datetime.strptime(derniere_maintenance, '%Y-%m-%d').date()
        )
        db.session.add(nouveau_aed)
        db.session.commit()
        flash('Bus AED ajouté avec succès !', 'success')
        return redirect(url_for('admin.dashboard'))

    # Préfixe automatique pour le numéro
    next_num = "AED-"
    return render_template('ajouter_bus.html', next_num=next_num)

# Route placeholder pour la page Ajouter Chauffeur (pour éviter les erreurs de lien)
@admin_only
@bp.route('/ajouter_chauffeur')
def ajouter_chauffeur():
    # Affiche une page temporaire ou un message d'information
    return "Page Ajouter Chauffeur en construction."

# Route placeholder pour la page Planifier Trajet (pour éviter les erreurs de lien)
@admin_only
@bp.route('/planifier_trajet')
def planifier_trajet():
    # Affiche une page temporaire ou un message d'information
    return "Page Planifier Trajet en construction."

# Route placeholder pour la page Générer Rapport (pour éviter les erreurs de lien)
@admin_only
@bp.route('/generer_rapport')
def generer_rapport():
    # Affiche une page temporaire ou un message d'information
    return "Page Générer Rapport en construction."

# Route pour obtenir les détails d'un bus AED en AJAX
@admin_only
@bp.route('/details_bus_ajax/<int:bus_id>', methods=['GET'])
def details_bus_ajax(bus_id):
    bus = AED.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404
    data = {
        'id': bus.id,
        'numero': bus.numero,
        'kilometrage': bus.kilometrage,
        'type_huile': bus.type_huile,
        'km_critique_huile': bus.km_critique_huile,
        'km_critique_carburant': bus.km_critique_carburant,
        'date_derniere_vidange': bus.date_derniere_vidange.strftime('%d/%m/%Y') if bus.date_derniere_vidange else '',
        'etat_vehicule': bus.etat_vehicule,
        'nombre_places': bus.nombre_places,
        'derniere_maintenance': bus.derniere_maintenance.strftime('%d/%m/%Y') if bus.derniere_maintenance else ''
    }
    # Récupérer les documents administratifs liés
    from app.models.document_aed import DocumentAED
    docs = DocumentAED.query.filter_by(numero_aed=bus.numero).all()
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

# Route pour ajouter ou mettre à jour un document administratif d'un AED
@admin_only
@bp.route('/ajouter_document_aed_ajax/<int:bus_id>', methods=['POST'])
def ajouter_document_aed_ajax(bus_id):
    from app.models.document_aed import DocumentAED
    bus = AED.query.get(bus_id)
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
    from datetime import datetime
    if not type_doc or not date_debut:
        return jsonify({'success': False, 'message': 'Champs manquants.'}), 400
    # convert date strings to date objects
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

    doc = DocumentAED(
        numero_aed=bus.numero,
        type_document=type_doc,
        date_debut=date_debut_dt,
        date_expiration=date_exp_dt
    )
    try:
        db.session.add(doc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    return jsonify({'success': True, 'message': 'Document ajouté.'})

# Route pour supprimer un bus en AJAX via son id
@admin_only
@bp.route('/supprimer_bus_ajax/<int:bus_id>', methods=['POST'])
def supprimer_bus_ajax(bus_id):
    bus = AED.query.get(bus_id)
    if not bus:
        return jsonify({'success': False, 'message': 'Bus introuvable.'}), 404

    # Détacher ce bus de tous les trajets avant suppression pour éviter les contraintes FK.
    from app.models.trajet import Trajet

    Trajet.query.filter_by(numero_aed=bus.numero).update({'numero_aed': None})
    db.session.commit()  # Valider le détachement des FK avant suppression

    # Supprimer tous les documents administratifs liés à ce bus
    from app.models.document_aed import DocumentAED
    DocumentAED.query.filter_by(numero_aed=bus.numero).delete()

    try:
        db.session.delete(bus)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        import traceback
        print('Erreur suppression bus:', traceback.format_exc())
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500

    return jsonify({'success': True, 'message': 'Bus supprimé avec succès.'})

# Route pour supprimer un chauffeur en AJAX via son id
@admin_only
@bp.route('/supprimer_chauffeur_ajax/<int:chauffeur_id>', methods=['POST'])
def supprimer_chauffeur_ajax(chauffeur_id):
    from app.models.chauffeur import Chauffeur
    chauffeur = Chauffeur.query.get(chauffeur_id)
    if not chauffeur:
        return jsonify({'success': False, 'message': 'Chauffeur introuvable.'}), 404
    db.session.delete(chauffeur)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Chauffeur supprimé avec succès.'})

# Route pour supprimer un utilisateur en AJAX via son id
@admin_only
@bp.route('/supprimer_utilisateur_ajax/<int:user_id>', methods=['POST'])
def supprimer_utilisateur_ajax(user_id):
    from app.models.utilisateur import Utilisateur
    user = Utilisateur.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable.'}), 404

    # Supprimer les enregistrements dépendants 
    from app.models.chargetransport import Chargetransport
    ct = Chargetransport.query.get(user_id)
    if ct:
        db.session.delete(ct)

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500

    return jsonify({'success': True, 'message': 'Utilisateur supprimé avec succès.'})

# Route du tableau de bord mécanicien
@admin_only
@bp.route('/documents_alerts_ajax', methods=['GET'])
@admin_only
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


def dashboard_mecanicien():
    from app.models.aed import AED
    bus_list = AED.query.order_by(AED.numero).all()
    return render_template('dashboard_mecanicien.html', bus_list=bus_list)



@admin_only
@bp.route('/vidange')
def vidange():
    # --- Tableau d'état vidange ---
    bus_list = AED.query.order_by(AED.numero).all()
    bus_vidange = []
    for bus in bus_list:
        voyant = 'green'
        if bus.kilometrage is not None and bus.km_critique_huile is not None:
            seuil = 0.1 * (bus.km_critique_huile - (bus.kilometrage or 0))
            reste = (bus.km_critique_huile or 0) - (bus.kilometrage or 0)
            if reste <= 0:
                voyant = 'red'
            elif reste <= seuil:
                voyant = 'orange'
        bus_vidange.append({
            'id': bus.id,
            'numero': bus.numero,
            'kilometrage': bus.kilometrage,
            'km_critique_huile': bus.km_critique_huile,
            'date_derniere_vidange': bus.date_derniere_vidange,
            'voyant': voyant
        })

    # --- Historique des vidanges ---
    # Récupérer tous les numéros AED distincts pour le filtre
    numeros_aed = [bus.numero for bus in bus_list]
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
        numeros_aed=numeros_aed,
        selected_numero=selected_numero
    )

# Route pour la page Carburation
@admin_only
@bp.route('/carburation')
def carburation():
    return render_template('carburation.html', active_page='carburation')
