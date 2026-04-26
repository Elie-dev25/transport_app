from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, logout_user
from app.forms.login_form import LoginForm
from app.models.utilisateur import Utilisateur
from app.database import db
from app.utils.audit_logger import (
    log_login_success, log_login_failed, log_logout,
    log_unauthorized_access, log_system_error
)
import os

# Configuration LDAP via variables d'environnement (OBLIGATOIRE en production)
# Les valeurs par défaut sont vides - doivent être définies dans .env
LDAP_SERVER = os.environ.get('LDAP_SERVER', '')
LDAP_DOMAIN = os.environ.get('LDAP_DOMAIN', '')
BASE_DN = os.environ.get('BASE_DN', '')

# Fonction d'authentification MySQL sécurisée
def authenticate_mysql(username, password):
    """Authentifie un utilisateur via la base de données MySQL.
    
    Args:
        username: Login de l'utilisateur
        password: Mot de passe en clair à vérifier
        
    Returns:
        Tuple (success: bool, groups: list, error: str|None)
    """
    try:
        # Chercher l'utilisateur en base MySQL
        user = Utilisateur.query.filter_by(login=username).first()
        if user:
            # Vérifier si le mot de passe est vide ou mal hashé
            if not user.mot_de_passe or user.mot_de_passe == '':
                print(f'MySQL Auth: Mot de passe vide pour {username}')
                return False, [], 'Mot de passe non configuré'

            # Vérifier le mot de passe
            if user.check_password(password):
                # Simuler les groupes AD selon le rôle
                groups = []
                if user.role == 'ADMIN':
                    groups = ['Administrateur']
                elif user.role == 'CHARGE':
                    groups = ['ChargeTransport']
                elif user.role == 'CHAUFFEUR':
                    groups = ['Chauffeurs']
                elif user.role == 'MECANICIEN':
                    groups = ['Mecanciens']
                elif user.role == 'SUPERVISEUR':
                    groups = ['Superviseurs']
                elif user.role == 'RESPONSABLE':
                    groups = ['Responsables']

                print(f'MySQL Auth: Utilisateur {username} authentifié avec succès, rôle: {user.role}')
                return True, groups, None
            else:
                print(f'MySQL Auth: Mot de passe incorrect pour {username}')
                return False, [], 'Mot de passe incorrect'
        else:
            print(f'MySQL Auth: Utilisateur {username} non trouvé')
            return False, [], 'Utilisateur non trouvé'
    except Exception as e:
        print(f'Erreur MySQL Auth: {e}')
        return False, [], str(e)

# Création du blueprint pour l'authentification
bp = Blueprint('auth', __name__)

# Route pour afficher le formulaire de connexion (GET)
@bp.route('/login', methods=['GET'])
def login_form():
    """Affiche le formulaire de connexion."""
    form = LoginForm()
    return render_template('auth/login.html', form=form)

# Route pour traiter la connexion (POST)
@bp.route('/login', methods=['POST'])
def login():
    """Traite la soumission du formulaire de connexion."""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.login.data
        password = form.mot_de_passe.data
        success, groups, auth_error = authenticate_mysql(username, password)
        if success:
            # Déterminer le rôle applicatif depuis les groupes AD
            role = None
            if 'Administrateur' in groups:
                role = 'ADMIN'
            elif 'ChargeTransport' in groups:
                role = 'CHARGE'
            elif 'Chauffeurs' in groups:
                role = 'CHAUFFEUR'
            elif 'Mecanciens' in groups:
                role = 'MECANICIEN'
            elif 'Superviseurs' in groups:
                role = 'SUPERVISEUR'
            elif 'Responsables' in groups:
                role = 'RESPONSABLE'

            # Synchroniser l'utilisateur local (création si absent)
            user = Utilisateur.query.filter_by(login=username).first()
            if not user:
                # Créer l'utilisateur avec un mot de passe temporaire sécurisé
                import secrets
                temp_password = secrets.token_urlsafe(16)
                user = Utilisateur(
                    nom=username.capitalize(),
                    prenom='Test',
                    login=username,
                    role=role,
                    email=f"{username}@udm.local",
                    telephone='000000000'
                )
                user.set_password(temp_password)
                # Note: L'utilisateur devra réinitialiser son mot de passe

                db.session.add(user)
                db.session.commit()
                print(f'Utilisateur {username} créé automatiquement')
            else:
                # Mettre à jour le rôle si nécessaire
                if role and user.role != role:
                    user.role = role
                    db.session.commit()
                    print(f'Rôle de {username} mis à jour vers {role}')

            # Connexion Flask-Login pour activer current_user et @login_required
            login_user(user)

            # SYNCHRONISATION CRITIQUE : Utiliser l'ID numérique pour la cohérence
            session['user_id'] = str(user.utilisateur_id)  # ID numérique en string pour cohérence
            session['user_login'] = username  # Login pour debug
            session['user_groups'] = groups
            if role:
                session['user_role'] = role

            # Debug pour traçabilité
            print(f'Session créée - ID: {user.utilisateur_id}, Login: {username}, Rôle: {role}')

            # AUDIT : Connexion réussie
            log_login_success(
                user_id=str(user.utilisateur_id),
                user_role=role,
                details=f"Login: {username} | Groups: {groups}"
            )

            # Affiche les groupes AD dans le message flash pour debug
            flash(f"Groupes AD détectés : {groups}", "info")
            flash('Connexion réussie.', 'success')  # Message de succès

            # Redirection selon le rôle
            if role == 'ADMIN':
                return redirect(url_for('admin.dashboard'))
            if role == 'RESPONSABLE':
                # Responsable a son propre dashboard pour la traçabilité
                return redirect(url_for('responsable.dashboard'))
            if role == 'CHARGE':
                return redirect(url_for('charge_transport.dashboard'))
            if role == 'CHAUFFEUR':
                return redirect(url_for('chauffeur.dashboard'))
            if role == 'MECANICIEN':
                return redirect(url_for('mecanicien.dashboard'))
            if role == 'SUPERVISEUR':
                # Superviseur utilise ses propres routes sécurisées
                return redirect(url_for('superviseur.dashboard'))
            # Si aucun rôle mappé, retourner à la page d'accueil ou login
            return redirect(url_for('auth.login'))
        else:
            # AUDIT : Connexion échouée
            log_login_failed(
                username=username,
                reason=auth_error or "Invalid credentials"
            )
            flash(f"Login ou mot de passe incorrect. Erreur: {auth_error}", "danger")  # Message d'erreur
    return render_template('auth/login.html', form=form)

# Route pour la déconnexion
@bp.route('/logout')
def logout():
    # Capturer les infos avant déconnexion pour l'audit
    user_id = session.get('user_id', 'UNKNOWN')
    user_role = session.get('user_role', 'UNKNOWN')
    user_login = session.get('user_login', 'UNKNOWN')

    # Debug avant déconnexion
    if 'user_login' in session:
        print(f'Déconnexion utilisateur: {session["user_login"]}')

    # AUDIT : Déconnexion
    log_logout(user_id=user_id, user_role=user_role)

    # Déconnexion Flask-Login et nettoyage session custom
    try:
        logout_user()
    except Exception as e:
        print(f'Erreur logout Flask-Login: {e}')
        log_system_error(
            error_type="Logout Error",
            error_message=str(e),
            context=f"User: {user_login}"
        )

    # Nettoyage complet de la session
    session.clear()

    flash('Déconnexion réussie.', 'info')
    return redirect(url_for('auth.login'))

# Route de diagnostic pour les problèmes d'authentification
@bp.route('/debug-session')
def debug_session():
    """Route de diagnostic pour identifier les problèmes d'authentification"""
    from flask_login import current_user
    from flask import jsonify

    debug_info = {
        'flask_login_authenticated': current_user.is_authenticated,
        'flask_login_user_id': getattr(current_user, 'utilisateur_id', None) if current_user.is_authenticated else None,
        'flask_login_login': getattr(current_user, 'login', None) if current_user.is_authenticated else None,
        'flask_login_role': getattr(current_user, 'role', None) if current_user.is_authenticated else None,
        'session_user_id': session.get('user_id'),
        'session_user_login': session.get('user_login'),
        'session_user_role': session.get('user_role'),
        'session_user_groups': session.get('user_groups'),
        'session_keys': list(session.keys()),
        'coherence_check': str(getattr(current_user, 'utilisateur_id', None)) == session.get('user_id') if current_user.is_authenticated else False
    }

    return jsonify(debug_info)