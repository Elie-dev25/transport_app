from flask import Blueprint, request, jsonify
import logging
from sqlalchemy.exc import IntegrityError
from app.models.aed import AED
from app.models.chauffeur import Chauffeur
from app.models.utilisateur import Utilisateur
from app.models.mecanicien import Mecanicien
from app.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash

bp_ajax = Blueprint('admin_ajax', __name__)

@bp_ajax.route('/ajouter_bus_ajax', methods=['POST'])
def ajouter_bus_ajax():
    numero = request.form.get('numero')
    kilometrage = request.form.get('kilometrage')
    type_huile = request.form.get('type_huile')
    km_critique_huile = request.form.get('km_critique_huile')
    km_critique_carburant = request.form.get('km_critique_carburant')
    date_derniere_vidange = request.form.get('date_derniere_vidange')
    etat_vehicule = request.form.get('etat_vehicule')
    nombre_places = request.form.get('nombre_places')
    derniere_maintenance = request.form.get('derniere_maintenance')

    # Tous les champs du formulaire sont requis
    if not all([
        numero, kilometrage, type_huile, km_critique_huile, km_critique_carburant,
        date_derniere_vidange, etat_vehicule, nombre_places, derniere_maintenance
    ]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    nouveau_aed = AED(
        numero=numero,
        kilometrage=int(kilometrage),
        type_huile=type_huile,
        km_critique_huile=int(km_critique_huile),
        km_critique_carburant=int(km_critique_carburant),
        date_derniere_vidange=datetime.strptime(date_derniere_vidange, '%Y-%m-%d').date(),
        etat_vehicule=etat_vehicule,
        nombre_places=int(nombre_places),
        derniere_maintenance=datetime.strptime(derniere_maintenance, '%Y-%m-%d').date()
    )
    db.session.add(nouveau_aed)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Bus AED ajouté avec succès !'})

# Endpoint obsolète supprimé: '/ajouter_chauffeur_ajax' (remplacé par '/ajouter_utilisateur_ajax' avec rôle CHAUFFEUR)

@bp_ajax.route('/ajouter_mecanicien_ajax', methods=['POST'])
def ajouter_mecanicien_ajax():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    login = request.form.get('login')
    telephone = request.form.get('telephone')
    email = request.form.get('email')
    mot_de_passe = request.form.get('mot_de_passe')
    numero_permis = request.form.get('numero_permis')
    date_delivrance_permis = request.form.get('date_delivrance_permis')
    date_expiration_permis = request.form.get('date_expiration_permis')

    if not all([nom, prenom, login, email, telephone, mot_de_passe, numero_permis, date_delivrance_permis, date_expiration_permis]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    # Vérifier unicité du login
    if Utilisateur.query.filter_by(login=login).first():
        return jsonify({'success': False, 'message': 'Ce login existe déjà.'}), 400

    # Création de l'utilisateur associé
    nouvel_utilisateur = Utilisateur(
        nom=nom,
        prenom=prenom,
        login=login,
        mot_de_passe=generate_password_hash(mot_de_passe),
        role='MECANICIEN',
        email=email,
        telephone=telephone
    )
    db.session.add(nouvel_utilisateur)
    db.session.flush()  # Pour récupérer l'ID
    # Validation des dates
    try:
        d_delivrance = datetime.strptime(date_delivrance_permis, '%Y-%m-%d').date()
        d_expiration = datetime.strptime(date_expiration_permis, '%Y-%m-%d').date()
    except ValueError:
        db.session.rollback()
        return jsonify({'success': False, 'message': "Format de date invalide. Utilisez 'YYYY-MM-DD'."}), 400
    if d_expiration <= d_delivrance:
        db.session.rollback()
        return jsonify({'success': False, 'message': "La date d'expiration doit être postérieure à la date de délivrance."}), 400

    # Création du mécanicien lié à l'utilisateur avec champs permis
    nouveau_mecanicien = Mecanicien(
        mecanicien_id=nouvel_utilisateur.utilisateur_id,
        numero_permis=numero_permis,
        date_delivrance_permis=d_delivrance,
        date_expiration_permis=d_expiration
    )
    db.session.add(nouveau_mecanicien)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Mécanicien ajouté avec succès !'})

@bp_ajax.route('/ajouter_utilisateur_ajax', methods=['POST'])
def ajouter_utilisateur_ajax():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    login = request.form.get('login')
    mot_de_passe = request.form.get('mot_de_passe')
    email = request.form.get('email')
    telephone = request.form.get('telephone')
    role = request.form.get('role')
    # Champs permis (affichés conditionnellement côté UI pour CHAUFFEUR et MECANICIEN)
    numero_permis = request.form.get('numero_permis')
    date_delivrance_permis = request.form.get('date_delivrance_permis')
    date_expiration_permis = request.form.get('date_expiration_permis')

    if not all([nom, prenom, login, mot_de_passe, email, telephone, role]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    if Utilisateur.query.filter_by(login=login).first():
        return jsonify({'success': False, 'message': 'Ce login existe déjà.'}), 400

    nouvel_utilisateur = Utilisateur(
        nom=nom,
        prenom=prenom,
        login=login,
        mot_de_passe=generate_password_hash(mot_de_passe),
        role=role,
        email=email,
        telephone=telephone
    )
    db.session.add(nouvel_utilisateur)
    db.session.flush()  # Pour avoir l'ID
    logging.debug(f"[ajouter_utilisateur_ajax] nouvel_utilisateur.utilisateur_id = {nouvel_utilisateur.utilisateur_id}")
    # Si rôle nécessite permis (CHAUFFEUR, MECANICIEN): exiger et valider dates
    if role in ('CHAUFFEUR', 'MECANICIEN'):
        if not all([numero_permis, date_delivrance_permis, date_expiration_permis]):
            db.session.rollback()
            return jsonify({'success': False, 'message': "Pour le rôle %s, numéro de permis, date de délivrance et date d'expiration sont obligatoires." % role}), 400
        try:
            d_delivrance = datetime.strptime(date_delivrance_permis, '%Y-%m-%d').date()
            d_expiration = datetime.strptime(date_expiration_permis, '%Y-%m-%d').date()
        except ValueError:
            db.session.rollback()
            return jsonify({'success': False, 'message': "Format de date invalide. Utilisez 'YYYY-MM-DD'."}), 400
        if d_expiration <= d_delivrance:
            db.session.rollback()
            return jsonify({'success': False, 'message': "La date d'expiration doit être postérieure à la date de délivrance."}), 400

        if role == 'CHAUFFEUR':
            # Unicité du numéro de permis chez Chauffeur
            if Chauffeur.query.filter_by(numero_permis=numero_permis).first():
                db.session.rollback()
                return jsonify({'success': False, 'message': 'Ce numéro de permis existe déjà.'}), 400
            nouveau_chauffeur = Chauffeur(
                nom=nom,
                prenom=prenom,
                numero_permis=numero_permis,
                telephone=telephone,
                date_delivrance_permis=d_delivrance,
                date_expiration_permis=d_expiration
            )
            db.session.add(nouveau_chauffeur)
        elif role == 'MECANICIEN':
            # Respecter la contrainte PK=FK: mecanicien_id doit correspondre à utilisateur.utilisateur_id
            # Laisser MySQL garantir l'unicité (PK=FK) sans pré-vérification côté app
            nouveau_mecanicien = Mecanicien(
                mecanicien_id=nouvel_utilisateur.utilisateur_id,
                numero_permis=numero_permis,
                date_delivrance_permis=d_delivrance,
                date_expiration_permis=d_expiration
            )
            db.session.add(nouveau_mecanicien)
    # Insertion automatique dans la table chargetransport si role == 'CHARGE'
    if role == 'CHARGE':
        from app.models.chargetransport import Chargetransport
        nouveau_charge = Chargetransport(chargetransport_id=nouvel_utilisateur.utilisateur_id)
        db.session.add(nouveau_charge)
    # Insertion automatique dans la table administrateur si role == 'ADMIN'
    if role == 'ADMIN':
        from app.models.administrateur import Administrateur
        nouveau_admin = Administrateur(administrateur_id=nouvel_utilisateur.utilisateur_id)
        db.session.add(nouveau_admin)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.exception("[ajouter_utilisateur_ajax] IntegrityError lors du commit")
        # Extraire les infos MySQL si disponibles
        err_code = None
        err_msg = None
        try:
            if hasattr(e.orig, 'args') and len(e.orig.args) >= 2:
                err_code = e.orig.args[0]
                err_msg = e.orig.args[1]
        except Exception:
            pass
        payload = {
            'success': False,
            'message': "Erreur d'intégrité en base.",
        }
        if err_code is not None:
            payload['mysql_code'] = err_code
        if err_msg is not None:
            payload['mysql_message'] = err_msg
        return jsonify(payload), 400
    return jsonify({'success': True, 'message': 'Utilisateur ajouté avec succès !'})
