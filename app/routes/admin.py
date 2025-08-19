from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.models.aed import AED
from app.models.vidange import Vidange
from app.models.utilisateur import Utilisateur
from app.models.fuel_alert_state import FuelAlertState
from app.models.panne_aed import PanneAED
from app.utils.emailer import send_email
from app.services.gestion_vidange import (
    get_vidange_history,
    build_bus_vidange_list,
    enregistrer_vidange_common,
    OIL_CAPACITY_KM,
)
from app.services.gestion_carburation import (
    get_carburation_history,
    build_bus_carburation_list,
    enregistrer_carburation_common,
)
from app.database import db  # Ajout de l'import manquant
from datetime import datetime
from app.forms.trajet_depart_form import TrajetDepartForm
from app.forms.trajet_prestataire_form import TrajetPrestataireForm
from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm
from app.forms.trajet_sortie_hors_ville_form import TrajetSortieHorsVilleForm
from app.models.chauffeur import Chauffeur
from app.models.aed import AED
from app.services.trajet_service import (
    enregistrer_depart_aed,
    enregistrer_depart_prestataire,
    enregistrer_depart_banekane_retour,
    enregistrer_depart_sortie_hors_ville,
)

# Création du blueprint pour l'administrateur
bp = Blueprint('admin', __name__, url_prefix='/admin')


from app.routes.common import role_required

# Définition du décorateur admin_only avant toute utilisation
def admin_only(view):
    return role_required('ADMIN')(view)

bp.before_request(lambda: None)  # Placeholder pour pouvoir ajouter le décorateur via dispatch


# Route AJAX pour ajouter un bus AED depuis le dashboard (après les imports et la déclaration du blueprint)
@admin_only
@bp.route('/ajouter_bus_ajax', methods=['POST'])
def ajouter_bus_ajax():
    numero = request.form.get('numero')
    immatriculation = request.form.get('immatriculation')
    kilometrage = request.form.get('kilometrage')
    type_huile = request.form.get('type_huile')
    capacite_plein_carburant = request.form.get('capacite_plein_carburant')
    # Nouveau champ optionnel: capacité du réservoir en litres
    capacite_reservoir_litres = request.form.get('capacite_reservoir_litres')
    # Nouveau champ optionnel: niveau actuel de carburant en litres
    niveau_carburant_litres = request.form.get('niveau_carburant_litres')
    date_derniere_vidange = request.form.get('date_derniere_vidange')
    etat_vehicule = request.form.get('etat_vehicule')
    nombre_places = request.form.get('nombre_places')
    derniere_maintenance = request.form.get('derniere_maintenance')

    if not all([numero, immatriculation, kilometrage, type_huile, capacite_plein_carburant, date_derniere_vidange, etat_vehicule, nombre_places, derniere_maintenance]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400


    kilometrage_val = float(kilometrage)
    capacite_val = float(capacite_plein_carburant)

    # Valider et calculer km_critique_huile selon le type d'huile détaillé
    type_clean = (type_huile or '').strip()
    if type_clean not in OIL_CAPACITY_KM:
        return jsonify({'success': False, 'message': "Type d'huile invalide. Veuillez choisir un type supporté."}), 400
    intervalle = OIL_CAPACITY_KM[type_clean]
    km_critique_huile = kilometrage_val + intervalle

    # Carburant:
    # - capacite_plein_carburant: capacité (en km) d'autonomie après un plein
    # - km_critique_carburant: kilométrage critique = kilometrage actuel + capacité
    km_critique_carburant = kilometrage_val + capacite_val

    try:
        nouveau_aed = AED(
            numero=numero,
            immatriculation=immatriculation,
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

    # Instancier les formulaires pour inclure les modales correspondantes dans le template
    form = TrajetDepartForm()
    form_bus = TrajetPrestataireForm()
    form_banekane_retour = TrajetBanekaneRetourForm()
    form_sortie = TrajetSortieHorsVilleForm()

    # Renseigner les choix dynamiques dépendants de la BD
    try:
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
        form_banekane_retour.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form_banekane_retour.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
        form_sortie.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form_sortie.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
    except Exception:
        # En cas d'erreur DB, laisser les choix vides pour ne pas casser le rendu
        form.chauffeur_id.choices = []
        form.numero_aed.choices = []
        form_banekane_retour.chauffeur_id.choices = []
        form_banekane_retour.numero_aed.choices = []
        form_sortie.chauffeur_id.choices = []
        form_sortie.numero_aed.choices = []

    # Affiche le template HTML du dashboard admin en fournissant les formulaires
    return render_template(
        'dashboard_admin.html',
        stats=stats,
        trafic=trafic,
        form=form,
        form_bus=form_bus,
        form_banekane_retour=form_banekane_retour,
        form_sortie=form_sortie,
        depart_aed_url=url_for('admin.depart_aed'),
        depart_prestataire_url=url_for('admin.depart_prestataire'),
        depart_banekane_retour_url=url_for('admin.depart_banekane_retour'),
        depart_sortie_hors_ville_url=url_for('admin.depart_sortie_hors_ville'),
    )


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

# Route pour la page Bus AED qui affiche la liste des bus depuis la base
@admin_only
@bp.route('/bus')
def bus():
    bus_list = AED.query.order_by(AED.numero).all()
    return render_template('bus_aed.html', bus_list=bus_list)

# Route AJAX: liste des AED pour autocomplétion (numero, immatriculation, kilometrage)
@admin_only
@bp.route('/aed_list_ajax', methods=['GET'])
def aed_list_ajax():
    try:
        buses = AED.query.order_by(AED.numero).all()
        data = [
            {
                'id': b.id,
                'numero': b.numero,
                'immatriculation': b.immatriculation,
                'kilometrage': b.kilometrage
            } for b in buses
        ]
        return jsonify({'success': True, 'aed': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
    user_list = Utilisateur.query.order_by(Utilisateur.nom, Utilisateur.prenom).all()
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
        # Nouveau champ optionnel
        capacite_reservoir_litres = request.form.get('capacite_reservoir_litres')
        # Nouveau champ optionnel
        niveau_carburant_litres = request.form.get('niveau_carburant_litres')
        date_derniere_vidange = request.form.get('date_derniere_vidange')
        etat_vehicule = request.form.get('etat_vehicule')
        nombre_places = request.form.get('nombre_places')
        derniere_maintenance = request.form.get('derniere_maintenance')

        if not all([numero, kilometrage, type_huile, capacite_plein_carburant, date_derniere_vidange, etat_vehicule, nombre_places, derniere_maintenance]):
            flash('Tous les champs sont obligatoires.', 'danger')
            return render_template('ajouter_bus.html', next_num=numero)

        # Validation du type d'huile et calcul automatique des km critiques selon le mapping détaillé
        type_clean = (type_huile or '').strip()
        if type_clean not in OIL_CAPACITY_KM:
            flash("Type d'huile invalide. Veuillez choisir un type supporté.", 'danger')
            return render_template('ajouter_bus.html', next_num=numero)
        km_critique_huile = float(kilometrage) + OIL_CAPACITY_KM[type_clean]

        # Carburant:
        # - capacite_plein_carburant est la capacité (en km) d'autonomie après un plein
        # - km_critique_carburant = kilometrage actuel + capacité
        cap_val = float(capacite_plein_carburant)
        km_critique_carburant = float(kilometrage) + cap_val

        nouveau_aed = AED(
            numero=numero,
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
        'capacite_reservoir_litres': bus.capacite_reservoir_litres,
        'niveau_carburant_litres': bus.niveau_carburant_litres,
        'date_derniere_vidange': bus.date_derniere_vidange.strftime('%d/%m/%Y') if bus.date_derniere_vidange else '',
        'etat_vehicule': bus.etat_vehicule,
        'nombre_places': bus.nombre_places,
        'derniere_maintenance': bus.derniere_maintenance.strftime('%d/%m/%Y') if bus.derniere_maintenance else ''
    }

@admin_only
@bp.route('/mettre_a_jour_niveau_carburant_ajax/<int:bus_id>', methods=['POST'])
def mettre_a_jour_niveau_carburant_ajax(bus_id):
    bus = AED.query.get(bus_id)
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
        # Après mise à jour, vérifier seuils et envoyer email si nécessaire (déduplication)
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
                # Mettre à jour l'état (même si pas d'email, pour stabiliser la tranche)
                if state:
                    state.last_threshold = th
                else:
                    state = FuelAlertState(aed_id=bus.id, last_threshold=th)
                    db.session.add(state)
                db.session.commit()
        except Exception:
            db.session.rollback()
            # On ignore les erreurs d'alerte pour ne pas casser l'UX de mise à jour

        return jsonify({'success': True, 'message': 'Niveau carburant mis à jour.', 'niveau_carburant_litres': bus.niveau_carburant_litres})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


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
        bus_existant = AED.query.filter_by(numero=numero_aed).first()
        if not bus_existant:
            return jsonify({'success': False, 'message': "Numéro AED inconnu. Veuillez sélectionner un numéro existant."}), 400
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
        
        nouvelle_panne = PanneAED(
            aed_id=bus_existant.id,
            numero_aed=numero_aed,
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


@admin_only
@bp.route('/fuel_alerts_ajax', methods=['GET'])
def fuel_alerts_ajax():
    """Retourne les alertes carburant selon les seuils 50%, 25%, 10%.
    Status: RED (<=10), ORANGE (<=25), YELLOW (<=50).
    """
    alerts = []
    buses = AED.query.all()
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


def dashboard_mecanicien():
    from app.models.aed import AED
    bus_list = AED.query.order_by(AED.numero).all()
    return render_template('dashboard_mecanicien.html', bus_list=bus_list)



@admin_only
@bp.route('/vidange')
def vidange():
    # --- Tableau d'état vidange (via service partagé) ---
    bus_vidange = build_bus_vidange_list()
    bus_list = AED.query.order_by(AED.numero).all()

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
    bus_list = AED.query.order_by(AED.numero).all()

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
