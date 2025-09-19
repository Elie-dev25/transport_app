from flask import render_template, jsonify, request
from app.models.chauffeur import Chauffeur
from app.models.chauffeur_statut import ChauffeurStatut
from app.models.utilisateur import Utilisateur
from app.models.chargetransport import Chargetransport
from app.database import db
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only (ADMIN et RESPONSABLE avec traçabilité)
def admin_only(view):
    from app.routes.common import admin_or_responsable
    return admin_or_responsable(view)

# Route pour la page Chauffeurs qui affiche la liste des chauffeurs depuis la base
@admin_only
@bp.route('/chauffeurs')
def chauffeurs():
    chauffeur_list = Chauffeur.query.order_by(Chauffeur.nom).all()
    
    # Ajouter les statuts actuels pour chaque chauffeur
    for chauffeur in chauffeur_list:
        chauffeur.statuts_actuels = ChauffeurStatut.get_current_statuts(chauffeur.chauffeur_id)
        # Debug temporaire
        print(f"DEBUG: Chauffeur {chauffeur.nom} {chauffeur.prenom} (ID: {chauffeur.chauffeur_id}) - {len(chauffeur.statuts_actuels)} statuts actuels")
        for statut in chauffeur.statuts_actuels:
            print(f"  - {statut.statut}: {statut.date_debut} -> {statut.date_fin}")
    
    return render_template(
        'legacy/chauffeurs.html',
        chauffeur_list=chauffeur_list,
        active_page='chauffeurs',
        base_template='roles/admin/_base_admin.html'
    )

# Route pour la page Utilisateurs qui affiche la liste des utilisateurs depuis la base
@admin_only
@bp.route('/utilisateurs')
def utilisateurs():
    user_list = Utilisateur.query.order_by(Utilisateur.nom, Utilisateur.prenom).all()
    return render_template('pages/utilisateurs.html', user_list=user_list, active_page='utilisateurs')

# Route pour supprimer un chauffeur en AJAX
@admin_only
@bp.route('/supprimer_chauffeur_ajax/<int:chauffeur_id>', methods=['POST'])
def supprimer_chauffeur_ajax(chauffeur_id):
    from app.models.chauffeur import Chauffeur
    chauffeur = Chauffeur.query.get(chauffeur_id)
    if not chauffeur:
        return jsonify({'success': False, 'message': 'Chauffeur introuvable.'}), 404
    
    try:
        db.session.delete(chauffeur)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Chauffeur supprimé avec succès.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500

# Route pour ajouter un utilisateur en AJAX
@admin_only
@bp.route('/ajouter_utilisateur_ajax', methods=['POST'])
def ajouter_utilisateur_ajax():
    try:
        # Récupérer les données du formulaire
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        login = request.form.get('login', '').strip()
        role = request.form.get('role', '').strip()
        mot_de_passe = request.form.get('mot_de_passe', '').strip()
        email = request.form.get('email', '').strip()
        telephone = request.form.get('telephone', '').strip()

        # Validation des champs obligatoires
        if not all([nom, prenom, login, role, mot_de_passe, email, telephone]):
            return jsonify({'success': False, 'message': 'Tous les champs obligatoires doivent être remplis.'}), 400

        # Vérifier si le login existe déjà
        existing_user = Utilisateur.query.filter_by(login=login).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Ce login existe déjà.'}), 400

        # Vérifier si l'email existe déjà
        existing_email = Utilisateur.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'success': False, 'message': 'Cet email existe déjà.'}), 400

        # Créer le nouvel utilisateur
        new_user = Utilisateur(
            nom=nom,
            prenom=prenom,
            login=login,
            role=role,
            email=email,
            telephone=telephone
        )
        new_user.set_password(mot_de_passe)

        # Ajouter à la base de données
        db.session.add(new_user)
        db.session.commit()

        # Créer les enregistrements spécifiques selon le rôle
        if role == 'CHAUFFEUR':
            from app.models.chauffeur import Chauffeur
            numero_permis = request.form.get('numero_permis', '').strip()
            date_delivrance_permis = request.form.get('date_delivrance_permis')
            date_expiration_permis = request.form.get('date_expiration_permis')

            # Pour les chauffeurs, les champs permis sont obligatoires
            if not numero_permis or not date_delivrance_permis or not date_expiration_permis:
                db.session.rollback()
                return jsonify({'success': False, 'message': 'Pour un chauffeur, le numéro de permis et les dates sont obligatoires.'}), 400

            chauffeur = Chauffeur(
                chauffeur_id=new_user.utilisateur_id,
                nom=nom,
                prenom=prenom,
                numero_permis=numero_permis,
                telephone=telephone,
                date_delivrance_permis=date_delivrance_permis,
                date_expiration_permis=date_expiration_permis
            )
            db.session.add(chauffeur)

        elif role == 'MECANICIEN':
            from app.models.mecanicien import Mecanicien
            numero_permis = request.form.get('numero_permis', '').strip()
            date_delivrance_permis = request.form.get('date_delivrance_permis')
            date_expiration_permis = request.form.get('date_expiration_permis')

            # Pour les mécaniciens, les champs permis sont obligatoires
            if not numero_permis or not date_delivrance_permis or not date_expiration_permis:
                db.session.rollback()
                return jsonify({'success': False, 'message': 'Pour un mécanicien, le numéro de permis et les dates sont obligatoires.'}), 400

            mecanicien = Mecanicien(
                mecanicien_id=new_user.utilisateur_id,
                numero_permis=numero_permis,
                date_delivrance_permis=date_delivrance_permis,
                date_expiration_permis=date_expiration_permis
            )
            db.session.add(mecanicien)

        elif role == 'CHARGE':
            charge_transport = Chargetransport(
                chargetransport_id=new_user.utilisateur_id
            )
            db.session.add(charge_transport)

        elif role == 'ADMIN':
            from app.models.administrateur import Administrateur
            administrateur = Administrateur(
                administrateur_id=new_user.utilisateur_id
            )
            db.session.add(administrateur)

        # RESPONSABLE et SUPERVISEUR n'ont pas de tables personnelles spécifiques
        # Ils utilisent seulement la table utilisateur

        db.session.commit()

        return jsonify({'success': True, 'message': f'Utilisateur {nom} {prenom} ajouté avec succès.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500

# Route pour supprimer un utilisateur en AJAX
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
        return jsonify({'success': True, 'message': 'Utilisateur supprimé avec succès.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur serveur : {str(e)}'}), 500

# Route placeholder pour la page Ajouter Chauffeur
@admin_only
@bp.route('/ajouter_chauffeur')
def ajouter_chauffeur():
    return "Page Ajouter Chauffeur en construction."

# Créer/ajouter un statut pour un chauffeur (utilisé par la modale "Modifier le statut")
@admin_only
@bp.route('/modifier_statut_chauffeur_ajax', methods=['POST'])
def modifier_statut_chauffeur_ajax():
    try:
        chauffeur_id = request.form.get('chauffeur_id')
        statut = request.form.get('statut')
        date_debut_raw = request.form.get('date_debut')
        date_fin_raw = request.form.get('date_fin')

        if not chauffeur_id or not statut or not date_debut_raw or not date_fin_raw:
            return jsonify({'success': False, 'message': 'Champs requis manquants.'}), 400

        from datetime import datetime
        # Le champ vient d'un input datetime-local: AAAA-MM-JJTHH:MM
        try:
            date_debut = datetime.strptime(date_debut_raw, '%Y-%m-%dT%H:%M')
            date_fin = datetime.strptime(date_fin_raw, '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'success': False, 'message': 'Format de date invalide (attendu AAAA-MM-JJTHH:MM).'}), 400

        if date_fin <= date_debut:
            return jsonify({'success': False, 'message': 'La date de fin doit être postérieure à la date de début.'}), 400

        # Vérifier le chauffeur
        ch = Chauffeur.query.get(chauffeur_id)
        if not ch:
            return jsonify({'success': False, 'message': 'Chauffeur introuvable.'}), 404

        # Vérifier chevauchements
        overlaps = ChauffeurStatut.check_overlap(int(chauffeur_id), date_debut, date_fin, statut)
        if overlaps:
            return jsonify({'success': False, 'message': 'Chevauchement avec un autre statut existant.'}), 400

        # Créer le statut
        new_statut = ChauffeurStatut(
            chauffeur_id=int(chauffeur_id),
            statut=statut,
            date_debut=date_debut,
            date_fin=date_fin,
        )
        db.session.add(new_statut)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Statut enregistré avec succès.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Récupérer tous les statuts d'un chauffeur (pour la modale de détails)
@admin_only
@bp.route('/get_statuts_chauffeur_ajax/<int:chauffeur_id>', methods=['GET'])
def get_statuts_chauffeur_ajax(chauffeur_id: int):
    try:
        ch = Chauffeur.query.get(chauffeur_id)
        if not ch:
            return jsonify({'success': False, 'message': 'Chauffeur introuvable.'}), 404
        from datetime import datetime
        now = datetime.now()
        # Ne renvoyer que les statuts encore valides: date_fin >= maintenant
        statuts = (
            ChauffeurStatut.query
            .filter(
                ChauffeurStatut.chauffeur_id == chauffeur_id,
                ChauffeurStatut.date_fin >= now
            )
            .order_by(ChauffeurStatut.date_debut.desc())
            .all()
        )
        data = [s.to_dict() for s in statuts]
        return jsonify({'success': True, 'statuts': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour récupérer la planification complète des chauffeurs (pour impression)
@admin_only
@bp.route('/get_chauffeurs_planning_ajax', methods=['GET'])
def get_chauffeurs_planning_ajax():
    try:
        from datetime import datetime, timedelta

        # Récupérer tous les chauffeurs avec leurs statuts actuels et futurs
        chauffeurs = Chauffeur.query.order_by(Chauffeur.nom).all()
        planning_data = []

        for chauffeur in chauffeurs:
            # Récupérer tous les statuts (actuels et futurs) pour ce chauffeur
            now = datetime.now()
            statuts = (
                ChauffeurStatut.query
                .filter(
                    ChauffeurStatut.chauffeur_id == chauffeur.chauffeur_id,
                    ChauffeurStatut.date_fin >= now  # Statuts actuels et futurs
                )
                .order_by(ChauffeurStatut.date_debut)
                .all()
            )

            if statuts:
                for statut in statuts:
                    # Calculer la durée
                    duree_jours = (statut.date_fin - statut.date_debut).days + 1
                    duree_str = f"{duree_jours} jour{'s' if duree_jours > 1 else ''}"

                    # Mapper les statuts pour un affichage plus lisible
                    statut_display = {
                        'CONGE': 'Congé',
                        'PERMANENCE': 'Permanence',
                        'SERVICE_WEEKEND': 'Service Week-end',
                        'SERVICE_SEMAINE': 'Service Semaine'
                    }.get(statut.statut, statut.statut)

                    planning_data.append({
                        'chauffeur': f"{chauffeur.nom} {chauffeur.prenom}",
                        'statut': statut_display,
                        'date_debut': statut.date_debut.strftime('%d/%m/%Y'),
                        'date_fin': statut.date_fin.strftime('%d/%m/%Y'),
                        'duree': duree_str
                    })
            else:
                # Chauffeur sans statut spécifique
                planning_data.append({
                    'chauffeur': f"{chauffeur.nom} {chauffeur.prenom}",
                    'statut': 'Disponible',
                    'date_debut': '-',
                    'date_fin': '-',
                    'duree': '-'
                })

        return jsonify({'success': True, 'planning': planning_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
