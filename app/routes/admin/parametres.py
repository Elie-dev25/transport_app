from flask import render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import current_user
from app.routes.common import admin_or_responsable
from app.models.utilisateur import Utilisateur
from app.database import db
from app.utils.audit_logger import log_user_action, get_audit_logs, get_role_statistics
from werkzeug.security import generate_password_hash
from functools import wraps
from . import bp

# Décorateur personnalisé pour Admin, Responsable, Superviseur
def admin_responsable_superviseur_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'user_role' not in session:
            flash("Merci de vous connecter.", "warning")
            return redirect(url_for('auth.login'))

        allowed_roles = ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR']
        if session['user_role'] not in allowed_roles:
            flash("Accès refusé. Cette page est réservée aux administrateurs, responsables et superviseurs.", "danger")
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function

# Décorateur personnalisé pour Admin uniquement
def admin_only_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'user_role' not in session:
            flash("Merci de vous connecter.", "warning")
            return redirect(url_for('auth.login'))

        if session['user_role'] != 'ADMIN':
            flash("Accès refusé. Cette fonctionnalité est réservée aux administrateurs.", "danger")
            return redirect(url_for('admin.parametres'))

        return f(*args, **kwargs)
    return decorated_function

# Route pour la page Paramètres (Admin, Responsable, Superviseur)
@bp.route('/parametres')
@admin_responsable_superviseur_required
def parametres():
    # Détecter si appelé par un responsable
    source = request.args.get('source', '')
    use_responsable_base = source == 'responsable' or (session.get('user_role') == 'RESPONSABLE')

    return render_template('pages/parametres.html', active_page='parametres', use_responsable_base=use_responsable_base)

# API - Statistiques d'audit (pour paramètres)
@bp.route('/parametres/api/audit/stats')
@admin_responsable_superviseur_required
def parametres_audit_stats_api():
    """API pour récupérer les statistiques d'audit depuis les paramètres"""
    try:
        stats = get_role_statistics()
        log_user_action('CONSULTATION', 'audit_stats', 'Consultation statistiques audit')
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API - Logs d'audit (pour paramètres)
@bp.route('/parametres/api/audit/logs')
@admin_responsable_superviseur_required
def parametres_audit_logs_api():
    """API pour récupérer les logs d'audit depuis les paramètres"""
    try:
        role_filter = request.args.get('role')
        action_filter = request.args.get('action')
        limit = int(request.args.get('limit', 50))

        logs = get_audit_logs(
            limit=limit,
            role_filter=role_filter,
            action_filter=action_filter
        )

        log_user_action('CONSULTATION', 'audit_logs', f'Consultation logs (limite: {limit})')

        return jsonify({
            'logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API - Liste des utilisateurs
@bp.route('/api/users')
@admin_or_responsable
def users_api():
    """API pour récupérer la liste des utilisateurs"""
    try:
        users = Utilisateur.query.all()
        users_data = []

        for user in users:
            users_data.append({
                'id': user.utilisateur_id,
                'login': user.login,
                'nom': user.nom or '',
                'prenom': user.prenom or '',
                'role': user.role,
                'active': True,  # À adapter selon votre modèle
                'derniere_connexion': None  # Le modèle n'a pas ce champ
            })

        log_user_action('CONSULTATION', 'users_list', f'Consultation liste utilisateurs ({len(users_data)} utilisateurs)')

        return jsonify(users_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API - Créer un utilisateur
@bp.route('/api/users', methods=['POST'])
@admin_or_responsable
def create_user_api():
    """API pour créer un nouvel utilisateur"""
    try:
        data = request.get_json()

        # Validation
        required_fields = ['login', 'password', 'confirm_password', 'nom', 'prenom', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        if data['password'] != data['confirm_password']:
            return jsonify({'error': 'Les mots de passe ne correspondent pas'}), 400

        # Vérifier si l'utilisateur existe déjà
        if Utilisateur.query.filter_by(login=data['login']).first():
            return jsonify({'error': 'Ce login existe déjà'}), 400

        # Créer l'utilisateur
        user = Utilisateur(
            login=data['login'],
            nom=data['nom'],
            prenom=data['prenom'],
            role=data['role'],
            mot_de_passe=generate_password_hash(data['password']),
            email=data.get('email', f"{data['login']}@transportudm.local"),  # Email par défaut
            telephone=data.get('telephone', '0000000000')  # Téléphone par défaut
        )

        db.session.add(user)
        db.session.commit()

        log_user_action('CREATION', 'create_user', f'Création utilisateur: {data["login"]} (rôle: {data["role"]})')

        return jsonify({
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'user_id': user.utilisateur_id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API - Modifier le rôle d'un utilisateur
@bp.route('/api/users/<int:user_id>/role', methods=['PUT'])
@admin_or_responsable
def edit_user_role_api(user_id):
    """API pour modifier le rôle d'un utilisateur"""
    try:
        data = request.get_json()
        new_role = data.get('new_role')

        if not new_role:
            return jsonify({'error': 'Le nouveau rôle est requis'}), 400

        user = Utilisateur.query.filter_by(utilisateur_id=user_id).first_or_404()
        old_role = user.role

        user.role = new_role
        db.session.commit()

        log_user_action('MODIFICATION', 'edit_user_role',
                       f'Modification rôle utilisateur {user.login}: {old_role} → {new_role}')

        return jsonify({
            'success': True,
            'message': 'Rôle modifié avec succès'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API - Modifier les identifiants (Admin uniquement)
@bp.route('/api/users/<int:user_id>/credentials', methods=['PUT'])
@admin_only_required
def update_credentials_api(user_id):
    """API pour modifier les identifiants d'un utilisateur (Admin uniquement)"""
    try:
        data = request.get_json()

        new_login = data.get('new_login')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not all([new_login, new_password, confirm_password]):
            return jsonify({'error': 'Tous les champs sont requis'}), 400

        if new_password != confirm_password:
            return jsonify({'error': 'Les mots de passe ne correspondent pas'}), 400

        user = Utilisateur.query.filter_by(utilisateur_id=user_id).first_or_404()
        old_login = user.login

        # Vérifier si le nouveau login existe déjà
        if new_login != old_login and Utilisateur.query.filter_by(login=new_login).first():
            return jsonify({'error': 'Ce login existe déjà'}), 400

        user.login = new_login
        user.mot_de_passe = generate_password_hash(new_password)
        db.session.commit()

        log_user_action('MODIFICATION', 'update_credentials',
                       f'Modification identifiants utilisateur: {old_login} → {new_login}')

        return jsonify({
            'success': True,
            'message': 'Identifiants modifiés avec succès'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API - Rechercher un utilisateur pour modification d'identifiants
@bp.route('/api/users/search')
@admin_only_required
def search_user_api():
    """API pour rechercher un utilisateur"""
    try:
        query = request.args.get('q', '').strip()

        if len(query) < 2:
            return jsonify({'error': 'La recherche doit contenir au moins 2 caractères'}), 400

        users = Utilisateur.query.filter(
            db.or_(
                Utilisateur.login.ilike(f'%{query}%'),
                Utilisateur.nom.ilike(f'%{query}%'),
                Utilisateur.prenom.ilike(f'%{query}%')
            )
        ).limit(10).all()

        users_data = []
        for user in users:
            users_data.append({
                'id': user.utilisateur_id,
                'login': user.login,
                'nom': user.nom or '',
                'prenom': user.prenom or '',
                'role': user.role,
                'display_name': f"{user.nom} {user.prenom} ({user.login})"
            })

        log_user_action('CONSULTATION', 'search_user', f'Recherche utilisateur: {query}')

        return jsonify(users_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
