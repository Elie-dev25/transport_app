# Common routes
from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import current_user

def role_required(*roles):
    """
    Décorateur unifié utilisant Flask-Login ET session pour double vérification
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérification Flask-Login
            if not current_user.is_authenticated:
                flash("Merci de vous connecter.", "warning")
                return redirect(url_for('auth.login'))

            # Vérification session (sécurité supplémentaire)
            if 'user_id' not in session or 'user_role' not in session:
                flash("Session expirée. Merci de vous reconnecter.", "warning")
                return redirect(url_for('auth.login'))

            # Vérification cohérence Flask-Login vs Session
            if str(current_user.utilisateur_id) != session['user_id']:
                flash("Incohérence de session détectée. Merci de vous reconnecter.", "warning")
                session.clear()
                return redirect(url_for('auth.login'))

            # Vérification du rôle
            if session['user_role'] not in roles:
                flash("Accès refusé.", "danger")
                return redirect(url_for('auth.login'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Décorateur spécifique pour les administrateurs
def admin_only(view):
    return role_required('ADMIN')(view)

# Décorateur pour les administrateurs et responsables (accès complet avec traçabilité)
def admin_or_responsable(view):
    """
    Décorateur pour ADMIN et RESPONSABLE avec traçabilité maintenue.
    Utilise le système unifié de vérification.
    """
    @wraps(view)
    def decorated_function(*args, **kwargs):
        # Vérification Flask-Login
        if not current_user.is_authenticated:
            flash("Merci de vous connecter.", "warning")
            return redirect(url_for('auth.login'))

        # Vérification session
        if 'user_id' not in session or 'user_role' not in session:
            flash("Session expirée. Merci de vous reconnecter.", "warning")
            return redirect(url_for('auth.login'))

        # Vérification cohérence
        if str(current_user.utilisateur_id) != session['user_id']:
            flash("Incohérence de session détectée. Merci de vous reconnecter.", "warning")
            session.clear()
            return redirect(url_for('auth.login'))

        # Vérifier les permissions
        if session['user_role'] not in ['ADMIN', 'RESPONSABLE']:
            flash("Accès refusé.", "danger")
            return redirect(url_for('auth.login'))

        # Log de l'action avec le rôle exact (pour traçabilité)
        from app.utils.audit_logger import log_user_action
        log_user_action('ACTION_ADMIN', view.__name__, f"Accès admin/responsable - Rôle: {session['user_role']}")

        return view(*args, **kwargs)
    return decorated_function

# Décorateur pour les rôles avec accès en lecture seule (consultation)
def read_only_access(*roles):
    """
    Décorateur pour les rôles qui ont accès en lecture seule.
    Utilisé pour les superviseurs et autres rôles de consultation.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or 'user_role' not in session:
                flash("Merci de vous connecter.", "warning")
                return redirect(url_for('auth.login'))
            if session['user_role'] not in roles:
                flash("Accès refusé.", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Décorateur spécifique pour les superviseurs (lecture seule)
def superviseur_access(view):
    """
    Décorateur pour accès en lecture seule : ADMIN, RESPONSABLE, SUPERVISEUR
    Utilise le système unifié de vérification.
    """
    @wraps(view)
    def decorated_function(*args, **kwargs):
        # Vérification Flask-Login
        if not current_user.is_authenticated:
            flash("Merci de vous connecter.", "warning")
            return redirect(url_for('auth.login'))

        # Vérification session
        if 'user_id' not in session or 'user_role' not in session:
            flash("Session expirée. Merci de vous reconnecter.", "warning")
            return redirect(url_for('auth.login'))

        # Vérification cohérence
        if str(current_user.utilisateur_id) != session['user_id']:
            flash("Incohérence de session détectée. Merci de vous reconnecter.", "warning")
            session.clear()
            return redirect(url_for('auth.login'))

        # Vérifier les permissions
        if session['user_role'] not in ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR']:
            flash("Accès refusé.", "danger")
            return redirect(url_for('auth.login'))

        # Log de l'action avec le rôle exact
        from app.utils.audit_logger import log_user_action
        log_user_action('CONSULTATION', view.__name__, f"Accès lecture seule - Rôle: {session['user_role']}")

        return view(*args, **kwargs)
    return decorated_function

# Décorateur spécifique pour les superviseurs uniquement
def superviseur_only(view):
    return role_required('SUPERVISEUR')(view)

# Décorateur pour les actions métier (excluant les superviseurs)
def business_action_required(*roles):
    """
    Décorateur pour les actions métier qui nécessitent des permissions d'écriture.
    Les superviseurs sont exclus de ces actions.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or 'user_role' not in session:
                flash("Merci de vous connecter.", "warning")
                return redirect(url_for('auth.login'))

            # Vérifier que l'utilisateur a un rôle autorisé ET n'est pas superviseur
            if session['user_role'] not in roles:
                flash("Accès refusé. Permissions insuffisantes.", "danger")
                return redirect(url_for('auth.login'))

            if session['user_role'] == 'SUPERVISEUR':
                flash("Action non autorisée. Les superviseurs ont un accès en lecture seule.", "warning")
                return redirect(url_for('auth.login'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Décorateur pour les administrateurs avec actions métier (avec traçabilité)
def admin_business_action(view):
    """
    Décorateur pour actions métier ADMIN et RESPONSABLE avec traçabilité complète
    """
    @wraps(view)
    def decorated_function(*args, **kwargs):
        # Vérifier l'authentification
        if 'user_id' not in session or 'user_role' not in session:
            flash("Merci de vous connecter.", "warning")
            return redirect(url_for('auth.login'))

        # Vérifier que l'utilisateur a un rôle autorisé
        if session['user_role'] not in ['ADMIN', 'RESPONSABLE']:
            flash("Accès refusé. Permissions insuffisantes.", "danger")
            return redirect(url_for('auth.login'))

        # Exclure explicitement les superviseurs (même si déjà filtré)
        if session['user_role'] == 'SUPERVISEUR':
            flash("Action non autorisée. Les superviseurs ont un accès en lecture seule.", "warning")
            return redirect(url_for('auth.login'))

        # Log détaillé de l'action métier
        from app.utils.audit_logger import log_user_action
        log_user_action('ACTION_METIER', view.__name__, f"Action métier critique")

        return view(*args, **kwargs)
    return decorated_function