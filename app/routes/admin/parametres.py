from flask import render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import current_user
from app.routes.common import admin_or_responsable
from app.models.utilisateur import Utilisateur
from app.models.prestataire import Prestataire
from app.database import db
from app.utils.audit_logger import log_user_action, get_audit_logs, get_role_statistics, log_document_printed
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

# API - Audit d'impression
@bp.route('/api/audit/print', methods=['POST'])
@admin_responsable_superviseur_required
def audit_print_api():
    """API pour enregistrer l'audit d'impression de documents"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        document_type = data.get('document_type', 'unknown')
        document_id = data.get('document_id')
        details = data.get('details')
        page_url = data.get('page_url', '')

        # Construire les détails complets
        full_details = f"Page: {page_url}"
        if details:
            full_details += f" | {details}"

        # Enregistrer l'audit d'impression
        log_document_printed(
            document_type=document_type,
            document_id=document_id,
            details=full_details
        )

        return jsonify({'success': True, 'message': 'Print audit recorded'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API - Alertes critiques
@bp.route('/api/audit/alerts', methods=['GET'])
@admin_responsable_superviseur_required
def get_critical_alerts():
    """API pour récupérer les alertes critiques des dernières 24h"""
    try:
        from datetime import datetime, timedelta
        import os
        import re

        alerts = []
        yesterday = datetime.now() - timedelta(days=1)

        # Parcourir tous les fichiers d'audit
        audit_dir = os.path.join('logs', 'audit')
        if not os.path.exists(audit_dir):
            return jsonify([])

        for filename in os.listdir(audit_dir):
            if filename.startswith('audit_') and filename.endswith('.log'):
                role = filename.replace('audit_', '').replace('.log', '').upper()
                filepath = os.path.join(audit_dir, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Analyser les dernières lignes pour les alertes critiques
                    for line in reversed(lines[-100:]):  # Dernières 100 lignes
                        if 'LEVEL:CRITICAL' in line or 'UNAUTHORIZED_ACCESS' in line or 'SECURITY_VIOLATION' in line:
                            # Extraire la date
                            date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                            if date_match:
                                log_date = datetime.strptime(date_match.group(1), '%Y-%m-%d %H:%M:%S')
                                if log_date >= yesterday:
                                    alerts.append({
                                        'role': role,
                                        'timestamp': log_date.strftime('%d/%m %H:%M'),
                                        'log': line.strip()
                                    })

                except Exception as e:
                    continue

        # Trier par date décroissante
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify(alerts[:10])  # Limiter à 10 alertes

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API - Liste des utilisateurs
@bp.route('/api/users')
@admin_responsable_superviseur_required
def users_api():
    """API pour récupérer la liste des utilisateurs"""
    try:
        from datetime import datetime, timedelta
        import os
        import re

        users = Utilisateur.query.all()
        users_data = []

        # Fonction pour obtenir la dernière connexion depuis les logs d'audit
        def get_last_login(user_login):
            try:
                audit_dir = os.path.join('logs', 'audit')
                if not os.path.exists(audit_dir):
                    return None

                # Chercher dans tous les fichiers d'audit
                for filename in os.listdir(audit_dir):
                    if filename.startswith('audit_') and filename.endswith('.log'):
                        filepath = os.path.join(audit_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                lines = f.readlines()

                            # Chercher les connexions de cet utilisateur (en partant de la fin)
                            for line in reversed(lines):
                                if 'LOGIN_SUCCESS' in line and user_login in line:
                                    # Extraire la date
                                    date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                                    if date_match:
                                        return date_match.group(1)
                        except:
                            continue
                return None
            except:
                return None

        for user in users:
            # Obtenir la dernière connexion
            last_login = get_last_login(user.login)

            # Déterminer si l'utilisateur est actif (connecté dans les 30 derniers jours)
            is_active = False
            if last_login:
                try:
                    last_login_date = datetime.strptime(last_login, '%Y-%m-%d %H:%M:%S')
                    thirty_days_ago = datetime.now() - timedelta(days=30)
                    is_active = last_login_date >= thirty_days_ago
                except:
                    is_active = False

            # Formater la dernière connexion pour l'affichage
            formatted_last_login = "Jamais connecté"
            if last_login:
                try:
                    last_login_date = datetime.strptime(last_login, '%Y-%m-%d %H:%M:%S')
                    formatted_last_login = last_login_date.strftime('%d/%m/%Y %H:%M')
                except:
                    formatted_last_login = "Date invalide"

            users_data.append({
                'id': user.utilisateur_id,
                'login': user.login,
                'nom': user.nom or '',
                'prenom': user.prenom or '',
                'role': user.role,
                'active': is_active,
                'derniere_connexion': formatted_last_login
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

# ========================================
# ROUTES PRESTATAIRES
# ========================================

# API - Liste des prestataires
@bp.route('/api/prestataires')
@admin_responsable_superviseur_required
def prestataires_api():
    """API pour récupérer la liste des prestataires"""
    try:
        prestataires = Prestataire.query.all()
        prestataires_data = []

        for prestataire in prestataires:
            prestataires_data.append({
                'id': prestataire.id,
                'nom_prestataire': prestataire.nom_prestataire,
                'telephone': prestataire.telephone or '',
                'email': prestataire.email or '',
                'localisation': prestataire.localisation or ''
            })

        log_user_action('CONSULTATION', 'prestataires_list', f'Consultation liste prestataires ({len(prestataires_data)} prestataires)')

        return jsonify(prestataires_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API - Créer un prestataire
@bp.route('/api/prestataires', methods=['POST'])
@admin_or_responsable
def create_prestataire_api():
    """API pour créer un nouveau prestataire"""
    try:
        # Récupérer les données du formulaire (pas JSON)
        nom_prestataire = request.form.get('nom_prestataire', '').strip()
        telephone = request.form.get('telephone', '').strip()
        email = request.form.get('email', '').strip()
        localisation = request.form.get('localisation', '').strip()

        # Validation
        if not nom_prestataire:
            return jsonify({'success': False, 'message': 'Le nom du prestataire est requis'}), 400

        # Vérifier si le prestataire existe déjà
        if Prestataire.query.filter_by(nom_prestataire=nom_prestataire).first():
            return jsonify({'success': False, 'message': 'Ce nom de prestataire existe déjà'}), 400

        # Créer le prestataire
        prestataire = Prestataire(
            nom_prestataire=nom_prestataire,
            telephone=telephone if telephone else None,
            email=email if email else None,
            localisation=localisation if localisation else None
        )

        db.session.add(prestataire)
        db.session.commit()

        log_user_action('CREATION', 'create_prestataire', f'Création prestataire: {nom_prestataire}')

        return jsonify({
            'success': True,
            'message': 'Prestataire créé avec succès',
            'prestataire_id': prestataire.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API - Supprimer un prestataire
@bp.route('/api/prestataires/<int:prestataire_id>', methods=['DELETE'])
@admin_or_responsable
def delete_prestataire_api(prestataire_id):
    """API pour supprimer un prestataire"""
    try:
        prestataire = Prestataire.query.filter_by(id=prestataire_id).first_or_404()
        nom_prestataire = prestataire.nom_prestataire

        # Vérifier s'il y a des trajets associés
        from app.models.trajet import Trajet
        trajets_count = Trajet.query.filter_by(prestataire_id=prestataire_id).count()

        if trajets_count > 0:
            return jsonify({
                'error': f'Impossible de supprimer ce prestataire car il a {trajets_count} trajet(s) associé(s)'
            }), 400

        db.session.delete(prestataire)
        db.session.commit()

        log_user_action('SUPPRESSION', 'delete_prestataire', f'Suppression prestataire: {nom_prestataire}')

        return jsonify({
            'success': True,
            'message': 'Prestataire supprimé avec succès'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API - Supprimer un utilisateur (Admin et Responsable uniquement)
@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_or_responsable
def delete_user_api(user_id):
    """API pour supprimer un utilisateur"""
    try:
        from app.models import Utilisateur

        # Vérifier que l'utilisateur existe
        user = Utilisateur.query.filter_by(utilisateur_id=user_id).first_or_404()
        user_name = f"{user.nom} {user.prenom}"
        user_login = user.login

        # Empêcher la suppression de son propre compte
        if str(user.utilisateur_id) == str(session.get('user_id')):
            return jsonify({
                'error': 'Vous ne pouvez pas supprimer votre propre compte'
            }), 400

        # Vérifier s'il y a des données associées (trajets, etc.)
        # Ici vous pouvez ajouter des vérifications selon vos besoins

        # Supprimer l'utilisateur
        db.session.delete(user)
        db.session.commit()

        # Auditer la suppression
        log_user_action('SUPPRESSION', 'delete_user', f'Suppression utilisateur: {user_name} ({user_login})')

        return jsonify({
            'success': True,
            'message': f'Utilisateur {user_name} supprimé avec succès'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
