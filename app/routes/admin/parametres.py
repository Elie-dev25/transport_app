from flask import render_template
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only
def admin_only(view):
    return role_required('ADMIN')(view)

# Route pour la page Paramètres
@admin_only
@bp.route('/parametres')
def parametres():
    return render_template('parametres.html', active_page='parametres')
