# Common routes
from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(*roles):
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