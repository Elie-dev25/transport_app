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
    niveau_carburant = request.form.get('niveau_carburant')
    niveau_huile = request.form.get('niveau_huile')
    seuil_critique_huile = request.form.get('seuil_critique_huile')
    etat_vehicule = request.form.get('etat_vehicule')
    nombre_places = request.form.get('nombre_places')
    derniere_maintenance = request.form.get('derniere_maintenance')

    if not all([numero, niveau_carburant, niveau_huile, seuil_critique_huile, etat_vehicule, nombre_places, derniere_maintenance]):
        return jsonify({'success': False, 'message': 'Tous les champs sont obligatoires.'}), 400

    nouveau_aed = AED(
        numero=numero,
        niveau_carburant=float(niveau_carburant),
        niveau_huile=float(niveau_huile),
        seuil_critique_huile=float(seuil_critique_huile),
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
    db.session.commit()
    return jsonify({'success': True, 'message': 'Utilisateur ajouté avec succès !'})
