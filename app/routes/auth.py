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

# Mapping rôle applicatif -> groupes AD simulés (inverse de _AD_GROUP_TO_ROLE)
_ROLE_TO_AD_GROUPS = {
    'ADMIN': ['Administrateur'],
    'CHARGE': ['ChargeTransport'],
    'CHAUFFEUR': ['Chauffeurs'],
    'MECANICIEN': ['Mecanciens'],
    'SUPERVISEUR': ['Superviseurs'],
    'RESPONSABLE': ['Responsables'],
}

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
        user = Utilisateur.query.filter_by(login=username).first()
        if user is None:
            print(f'MySQL Auth: Utilisateur {username} non trouvé')
            return False, [], 'Utilisateur non trouvé'

        if not user.mot_de_passe:
            print(f'MySQL Auth: Mot de passe vide pour {username}')
            return False, [], 'Mot de passe non configuré'

        if not user.check_password(password):
            print(f'MySQL Auth: Mot de passe incorrect pour {username}')
            return False, [], 'Mot de passe incorrect'

        groups = _ROLE_TO_AD_GROUPS.get(user.role, [])
        print(f'MySQL Auth: Utilisateur {username} authentifié avec succès, rôle: {user.role}')
        return True, groups, None
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

# Mapping groupes AD -> rôle applicatif
_AD_GROUP_TO_ROLE = (
    ('Administrateur', 'ADMIN'),
    ('ChargeTransport', 'CHARGE'),
    ('Chauffeurs', 'CHAUFFEUR'),
    ('Mecanciens', 'MECANICIEN'),
    ('Superviseurs', 'SUPERVISEUR'),
    ('Responsables', 'RESPONSABLE'),
)

# Mapping rôle applicatif -> dashboard de redirection
_ROLE_TO_DASHBOARD = {
    'ADMIN': 'admin.dashboard',
    'RESPONSABLE': 'responsable.dashboard',
    'CHARGE': 'charge_transport.dashboard',
    'CHAUFFEUR': 'chauffeur.dashboard',
    'MECANICIEN': 'mecanicien.dashboard',
    'SUPERVISEUR': 'superviseur.dashboard',
}


def _role_from_groups(groups):
    """Retourne le premier rôle applicatif correspondant aux groupes AD."""
    for ad_group, role in _AD_GROUP_TO_ROLE:
        if ad_group in groups:
            return role
    return None


def _get_or_create_user(username, role):
    """Récupère l'utilisateur local ou le crée à partir des infos AD."""
    user = Utilisateur.query.filter_by(login=username).first()
    if user is None:
        import secrets
        user = Utilisateur(
            nom=username.capitalize(),
            prenom='Test',
            login=username,
            role=role,
            email=f"{username}@udm.local",
            telephone='000000000',
        )
        user.set_password(secrets.token_urlsafe(16))
        db.session.add(user)
        db.session.commit()
        print(f'Utilisateur {username} créé automatiquement')
        return user

    if role and user.role != role:
        user.role = role
        db.session.commit()
        print(f'Rôle de {username} mis à jour vers {role}')
    return user


def _setup_session_and_audit(user, username, role, groups):
    """Initialise la session Flask + Flask-Login et trace l'audit."""
    login_user(user)
    session['user_id'] = str(user.utilisateur_id)
    session['user_login'] = username
    session['user_groups'] = groups
    if role:
        session['user_role'] = role
    print(f'Session créée - ID: {user.utilisateur_id}, Login: {username}, Rôle: {role}')
    log_login_success(
        user_id=str(user.utilisateur_id),
        user_role=role,
        details=f"Login: {username} | Groups: {groups}",
    )
    flash(f"Groupes AD détectés : {groups}", "info")
    flash('Connexion réussie.', 'success')


def _redirect_after_login(role):
    """Renvoie la redirection appropriée selon le rôle, sinon retour login."""
    endpoint = _ROLE_TO_DASHBOARD.get(role, 'auth.login')
    return redirect(url_for(endpoint))


# Route pour traiter la connexion (POST)
@bp.route('/login', methods=['POST'])
def login():
    """Traite la soumission du formulaire de connexion."""
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('auth/login.html', form=form)

    username = form.login.data
    password = form.mot_de_passe.data
    success, groups, auth_error = authenticate_mysql(username, password)

    if not success:
        log_login_failed(username=username, reason=auth_error or "Invalid credentials")
        flash(f"Login ou mot de passe incorrect. Erreur: {auth_error}", "danger")
        return render_template('auth/login.html', form=form)

    role = _role_from_groups(groups)
    user = _get_or_create_user(username, role)
    _setup_session_and_audit(user, username, role, groups)
    return _redirect_after_login(role)

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