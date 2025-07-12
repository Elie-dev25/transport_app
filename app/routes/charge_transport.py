from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.forms.trajet_depart_form import TrajetDepartForm
from app.forms.trajet_bus_agence_form import TrajetBusAgenceForm
from app.models.chauffeur import Chauffeur
from app.models.aed import AED
from app.models.busagence import Busagence
from app.models.trajet import Trajet
from app.database import db
from datetime import date

# Création du blueprint pour le chargé de transport
bp = Blueprint('charge_transport', __name__, url_prefix='/charge')

# Route du tableau de bord chargé de transport
@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    from app.models.trajet import Trajet
    today = date.today()
    # Nombre de trajets du jour enregistrés par CE chargé de transport
    trajets_jour_aed = Trajet.query.filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.enregistre_par == current_user.utilisateur_id,
        Trajet.numero_aed != None
    ).count()
    trajets_jour_bus_agence = Trajet.query.filter(
        db.func.date(Trajet.date_heure_depart) == today,
        Trajet.enregistre_par == current_user.utilisateur_id,
        Trajet.immat_bus != None
    ).count()
    # Exemple d'autres stats (à ajuster plus tard)
    stats = {
        'bus_actifs': AED.query.filter_by(etat_vehicule='BON').count(),
        'bus_en_maintenance': AED.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'bus_maintenance': AED.query.filter_by(etat_vehicule='DEFAILLANT').count(),
        'trajets_jour_aed': trajets_jour_aed,
        'trajets_jour_bus_agence': trajets_jour_bus_agence,
        'trajets_jour_change': 0,
        'chauffeurs_disponibles': 5
    }
    form = TrajetDepartForm()
    form_bus = TrajetBusAgenceForm()
    # Initialisation du formulaire Banekane retour
    from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm
    form_banekane_retour = TrajetBanekaneRetourForm()
    form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
    form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
    form_banekane_retour.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
    form_banekane_retour.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
    if form.validate_on_submit():
        from app.models.chargetransport import Chargetransport
        # Récupérer l'id du chargé de transport connecté
        chargeur = Chargetransport.query.get(current_user.utilisateur_id)
        if not chargeur:
            flash("Erreur: Aucun chargé de transport associé à cet utilisateur.", "danger")
            return redirect(url_for('charge_transport.dashboard'))
        trajet = Trajet(
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.point_depart.data,
            type_passagers=form.type_passagers.data,
            nombre_places_occupees=form.nombre_places_occupees.data,
            chauffeur_id=form.chauffeur_id.data,
            numero_aed=form.numero_aed.data,
            enregistre_par=chargeur.chargetransport_id
        )
        try:
            db.session.add(trajet)
            db.session.commit()
            flash('Départ AED enregistré avec succès.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'enregistrement du trajet : {e}', 'danger')
        return redirect(url_for('charge_transport.dashboard'))
    elif request.method == 'POST':
        flash('Erreur dans le formulaire. Veuillez vérifier les champs.', 'danger')
    chauffeurs_list = Chauffeur.query.all()
    bus_agence_list = Busagence.query.all()
    return render_template('dashboard_charge.html', stats=stats, form=form, form_bus=form_bus, form_banekane_retour=form_banekane_retour)

# Route pour la gestion des bus
@bp.route('/bus')
def bus():
    # Placeholder pour la page bus du chargé de transport
    return render_template('bus.html')

# Route pour la gestion des chauffeurs
@bp.route('/chauffeurs')
def chauffeurs():
    return render_template('chauffeurs.html') if 'chauffeurs.html' in globals() else "Page Chauffeurs (à implémenter)"

# Route pour la gestion des rapports
@bp.route('/rapports')
def rapports():
    return render_template('rapports.html') if 'rapports.html' in globals() else "Page Rapports (à implémenter)"

# Route pour les paramètres
@bp.route('/parametres')
def parametres():
    return render_template('parametres.html') if 'parametres.html' in globals() else "Page Paramètres (à implémenter)"

# Route pour le départ AED (Ajax)
@bp.route('/depart-aed', methods=['POST'])
def depart_aed():
    """Enregistrement d'un départ AED pour Banekane (AJAX, JSON)"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = TrajetDepartForm()
        # Actualiser les choix dépendants de la BD
        from app.models.chauffeur import Chauffeur
        from app.models.aed import AED
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]

        if form.validate_on_submit():
            try:
                chargeur = current_user  # alias
                trajet = Trajet(
                    date_heure_depart=form.date_heure_depart.data,
                    point_depart=form.point_depart.data,
                    type_passagers=form.type_passagers.data,
                    nombre_places_occupees=form.nombre_places_occupees.data,
                    chauffeur_id=form.chauffeur_id.data,
                    numero_aed=form.numero_aed.data,
                    immat_bus=None,
                    enregistre_par=chargeur.utilisateur_id
                )
                db.session.add(trajet)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Départ AED enregistré !'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Erreur : {e}'}), 500
        else:
            return jsonify({'success': False, 'message': 'Erreur dans le formulaire. Veuillez vérifier les champs.'}), 400
    return jsonify({'success': False, 'message': 'Requête non autorisée.'}), 400

# Route pour le départ AED Banekane
@bp.route('/depart-aed-banekane')
def depart_aed_banekane():
    # Placeholder pour la page de départ AED Banekane
    return "Page Départ AED Banekane (à implémenter)"

# Route pour le départ Bus Agence
@bp.route('/depart-bus-agence', methods=['POST'])
def depart_bus_agence():
    """Enregistrement d'un départ Bus Agence via soumission AJAX."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        date_heure_depart = request.form.get('date_heure_depart')
        point_depart = request.form.get('point_depart')
        nom_agence = request.form.get('nom_agence')
        immat_bus = request.form.get('immat_bus')
        nom_chauffeur = request.form.get('nom_chauffeur')
        places_occupees = request.form.get('nombre_places_occupees', type=int) or 0
        # Valeur par défaut pour la capacité du bus (plus saisie côté formulaire)
        nombre_places_bus = 50
        # Validation minimum
        if not all([date_heure_depart, point_depart, nom_agence, immat_bus, nom_chauffeur]):
            return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400
        try:
            from datetime import datetime as dt
            date_dt = dt.strptime(date_heure_depart, '%Y-%m-%dT%H:%M')
            from app.models.chargetransport import Chargetransport
            chargeur = Chargetransport.query.get(current_user.utilisateur_id)
            # Insérer ou mettre à jour Bus Agence
            bus = Busagence.query.get(immat_bus)
            if not bus:
                bus = Busagence(immatriculation=immat_bus, nom_agence=nom_agence,
                                 nombre_places=nombre_places_bus, nom_chauffeur=nom_chauffeur)
                db.session.add(bus)
            else:
                bus.nom_agence = nom_agence
                bus.nombre_places = nombre_places_bus
                bus.nom_chauffeur = nom_chauffeur

            trajet = Trajet(
                date_heure_depart=date_dt,
                point_depart=point_depart,
                type_passagers=request.form.get('type_passagers', 'ETUDIANT'),
                nombre_places_occupees=places_occupees,
                chauffeur_id=None,
                immat_bus=immat_bus,
                enregistre_par=chargeur.chargetransport_id
            )
            db.session.add(trajet)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Départ Bus Agence enregistré !'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erreur : {e}'}), 500
    # fallback
    return jsonify({'success': False, 'message': 'Erreur inconnue, veuillez réessayer.'}), 500

# Route pour le retour Banekane
from app.forms.trajet_banekane_retour_form import TrajetBanekaneRetourForm

@bp.route('/depart-banekane-retour', methods=['POST'])
def depart_banekane_retour():
    """Enregistrement d'un départ de Banekane (retour) via soumission AJAX."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = TrajetBanekaneRetourForm()
        # Remplir dynamiquement les choix
        from app.models.chauffeur import Chauffeur
        from app.models.aed import AED
        form.chauffeur_id.choices = [(c.chauffeur_id, f"{c.nom} {c.prenom}") for c in Chauffeur.query.all()]
        form.numero_aed.choices = [(a.numero, a.numero) for a in AED.query.all()]
        if form.validate_on_submit():
            from app.models.chargetransport import Chargetransport
            chargeur = Chargetransport.query.get(current_user.utilisateur_id)
            if not chargeur:
                return jsonify({'success': False, 'message': "Erreur: Aucun chargé de transport associé à cet utilisateur."}), 400
            # Préparation des champs selon le type de bus
            type_bus = form.type_bus.data
            if type_bus == 'AED':
                trajet = Trajet(
                    date_heure_depart=form.date_heure_depart.data,
                    point_depart='Banekane',
                    type_passagers=form.type_passagers.data,
                    nombre_places_occupees=form.nombre_places_occupees.data,
                    chauffeur_id=form.chauffeur_id.data,
                    numero_aed=form.numero_aed.data,
                    immat_bus=None,
                    enregistre_par=chargeur.chargetransport_id
                )
                try:
                    db.session.add(trajet)
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'Départ de Banekane (retour) enregistré !'})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'success': False, 'message': f'Erreur : {e}'}), 500
            else:  # Bus Agence
                immat = form.immat_bus.data.strip()
                if immat:
                    bus = Busagence.query.get(immat)
                    if not bus:
                        bus = Busagence(
                            immatriculation=immat,
                            nom_agence=form.nom_agence.data,
                            nombre_places=form.nombre_places_occupees.data or 50,
                            nom_chauffeur=form.nom_chauffeur_agence.data or ''
                        )
                        db.session.add(bus)
                    else:
                        bus.nom_agence = form.nom_agence.data
                        bus.nombre_places = form.nombre_places_occupees.data or bus.nombre_places
                        bus.nom_chauffeur = form.nom_chauffeur_agence.data or bus.nom_chauffeur
                    immat_bus_value = immat
                else:
                    immat_bus_value = None
                trajet = Trajet(
                    date_heure_depart=form.date_heure_depart.data,
                    point_depart='Banekane',
                    type_passagers='ETUDIANT',
                    nombre_places_occupees=form.nombre_places_occupees.data,
                    chauffeur_id=None,
                    numero_aed=None,
                    immat_bus=immat_bus_value,
                    enregistre_par=chargeur.chargetransport_id
                )
                try:
                    db.session.add(trajet)
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'Départ de Banekane (retour) enregistré !'})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'success': False, 'message': f'Erreur : {e}'}), 500
        else:
            return jsonify({'success': False, 'message': 'Erreur dans le formulaire. Veuillez vérifier les champs.'}), 400
    # fallback
    return jsonify({'success': False, 'message': 'Erreur inconnue, veuillez réessayer.'}), 500


# Route pour générer un rapport
@bp.route('/generer-rapport')
def generer_rapport():
    # Placeholder pour la génération de rapport
    return "Génération de rapport (à implémenter)"