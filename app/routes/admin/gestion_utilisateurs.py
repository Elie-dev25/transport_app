from flask import render_template, jsonify
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

# Route placeholder pour la page Ajouter Chauffeur
@admin_only
@bp.route('/ajouter_chauffeur')
def ajouter_chauffeur():
    return "Page Ajouter Chauffeur en construction."

# Route pour supprimer un chauffeur en AJAX via son id
@admin_only
@bp.route('/supprimer_chauffeur_ajax/<int:chauffeur_id>', methods=['POST'])
def supprimer_chauffeur_ajax(chauffeur_id):
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

# Route pour supprimer un utilisateur en AJAX via son id
@admin_only
@bp.route('/supprimer_utilisateur_ajax/<int:user_id>', methods=['POST'])
def supprimer_utilisateur_ajax(user_id):
    user = Utilisateur.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Utilisateur introuvable.'}), 404

    # Supprimer les enregistrements dépendants 
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
