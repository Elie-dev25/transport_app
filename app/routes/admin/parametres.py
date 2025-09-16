from flask import render_template
from app.routes.common import role_required
from . import bp

# Définition du décorateur admin_only (ADMIN et RESPONSABLE avec traçabilité)
def admin_only(view):
    from app.routes.common import admin_or_responsable
    return admin_or_responsable(view)

# Route pour la page Paramètres
@admin_only
@bp.route('/parametres')
def parametres():
    return render_template('pages/parametres.html', active_page='parametres')
