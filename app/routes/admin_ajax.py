from flask import Blueprint, request, jsonify
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

@bp_ajax.route('/ajouter_chauffeur_ajax', methods=['POST'])
def ajouter_chauffeur_ajax():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    numero_permis = request.form.get('numero_permis')
    telephone = request.form.get('telephone')

    if not all([nom, prenom, numero_permis, telephone]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    # Vérifier unicité du numéro de permis
    if Chauffeur.query.filter_by(numero_permis=numero_permis).first():
        return jsonify({'success': False, 'message': 'Ce numéro de permis existe déjà.'}), 400

    nouveau_chauffeur = Chauffeur(
        nom=nom,
        prenom=prenom,
        numero_permis=numero_permis,
        telephone=telephone
    )
    db.session.add(nouveau_chauffeur)
    # Création de l'utilisateur associé
    nom_utilisateur = f"{nom} {prenom}"
    login = numero_permis
    mot_de_passe = generate_password_hash(numero_permis)
    nouvel_utilisateur = Utilisateur(
        nom_utilisateur=nom_utilisateur,
        login=login,
        mot_de_passe=mot_de_passe,
        role='CHAUFFEUR'
    )
    db.session.add(nouvel_utilisateur)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Chauffeur ajouté avec succès !'})

@bp_ajax.route('/ajouter_mecanicien_ajax', methods=['POST'])
def ajouter_mecanicien_ajax():
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    login = request.form.get('login')
    telephone = request.form.get('telephone')
    mot_de_passe = request.form.get('mot_de_passe')

    if not all([nom, prenom, login, telephone, mot_de_passe]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    # Vérifier unicité du login
    if Utilisateur.query.filter_by(login=login).first():
        return jsonify({'success': False, 'message': 'Ce login existe déjà.'}), 400

    # Création de l'utilisateur associé
    nom_utilisateur = f"{nom} {prenom}"
    nouvel_utilisateur = Utilisateur(
        nom_utilisateur=nom_utilisateur,
        login=login,
        mot_de_passe=generate_password_hash(mot_de_passe),
        role='MECANICIEN'
    )
    db.session.add(nouvel_utilisateur)
    db.session.flush()  # Pour récupérer l'ID
    # Création du mécanicien lié à l'utilisateur
    nouveau_mecanicien = Mecanicien(mecanicien_id=nouvel_utilisateur.utilisateur_id)
    db.session.add(nouveau_mecanicien)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Mécanicien ajouté avec succès !'})

@bp_ajax.route('/ajouter_utilisateur_ajax', methods=['POST'])
def ajouter_utilisateur_ajax():
    nom_utilisateur = request.form.get('nom_utilisateur')
    login = request.form.get('login')
    mot_de_passe = request.form.get('mot_de_passe')
    role = request.form.get('role')

    if not all([nom_utilisateur, login, mot_de_passe, role]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    if Utilisateur.query.filter_by(login=login).first():
        return jsonify({'success': False, 'message': 'Ce login existe déjà.'}), 400

    nouvel_utilisateur = Utilisateur(
        nom_utilisateur=nom_utilisateur,
        login=login,
        mot_de_passe=generate_password_hash(mot_de_passe),
        role=role
    )
    db.session.add(nouvel_utilisateur)
    db.session.flush()  # Pour avoir l'ID
    # Insertion automatique dans la table chargetransport si role == 'CHARGE'
    if role == 'CHARGE':
        from app.models.chargetransport import Chargetransport
        nouveau_charge = Chargetransport(chargetransport_id=nouvel_utilisateur.utilisateur_id)
        db.session.add(nouveau_charge)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Utilisateur ajouté avec succès !'})
