from flask import render_template, jsonify, request
from app.models.chauffeur import Chauffeur
from app.models.chauffeur_statut import ChauffeurStatut
from app.models.utilisateur import Utilisateur
from app.models.chargetransport import Chargetransport
from app.database import db
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only
def admin_only(view):
    return role_required('ADMIN')(view)

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
    
    return render_template('chauffeurs.html', chauffeur_list=chauffeur_list, active_page='chauffeurs')

# Route pour la page Utilisateurs qui affiche la liste des utilisateurs depuis la base
@admin_only
@bp.route('/utilisateurs')
def utilisateurs():
    user_list = Utilisateur.query.order_by(Utilisateur.nom, Utilisateur.prenom).all()
    return render_template('utilisateurs.html', user_list=user_list, active_page='utilisateurs')

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
