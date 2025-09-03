from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user  # Ajouté logout_user
from ldap3 import Server, Connection, ALL, NTLM
from app.forms.login_form import LoginForm
from app.models.utilisateur import Utilisateur
from app.database import db

LDAP_SERVER = '192.168.21.131'
LDAP_DOMAIN = 'domaine.local'
BASE_DN = 'DC=domaine,DC=local'

# Fonction d'authentification AD

def authenticate_ad(username, password):
    user_dn = f"{LDAP_DOMAIN}\\{username}"
    server = Server(LDAP_SERVER, get_info=ALL)
    try:
        conn = Connection(server, user=user_dn, password=password, authentication=NTLM, auto_bind=True)
        conn.search(BASE_DN, f'(sAMAccountName={username})', attributes=['memberOf'])
        if conn.entries:
            entry = conn.entries[0]
            groups = entry.memberOf.values if 'memberOf' in entry else []
            user_groups = [g.split(',')[0].replace('CN=', '') for g in groups]
            return True, user_groups, None
        print('LDAP: Utilisateur non trouvé dans AD.')
        return False, [], 'Utilisateur non trouvé dans AD.'
    except Exception as e:
        print(f'Erreur LDAP: {e}')
        return False, [], str(e)

# Création du blueprint pour l'authentification
bp = Blueprint('auth', __name__)

# Route pour la page de connexion
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Instancie le formulaire de connexion
    if form.validate_on_submit():  # Vérifie si le formulaire est soumis et valide
        username = form.login.data
        password = form.mot_de_passe.data
        success, groups, ldap_error = authenticate_ad(username, password)
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

            # Synchroniser l'utilisateur local (création si absent)
            user = Utilisateur.query.filter_by(login=username).first()
            if not user:
                # Valeurs par défaut minimales pour respecter les contraintes NOT NULL
                user = Utilisateur(
                    nom=username,
                    prenom='',
                    login=username,
                    role=role,
                    email=f"{username}@domaine.local",
                    telephone=''  # inconnu pour LDAP
                )
                # Mot de passe placeholder (non utilisé car auth via LDAP)
                user.set_password('ldap')
                db.session.add(user)
                db.session.commit()
            else:
                # Mettre à jour le rôle si nécessaire
                if role and user.role != role:
                    user.role = role
                    db.session.commit()

            # Connexion Flask-Login pour activer current_user et @login_required
            login_user(user)

            # Conserver aussi la compatibilité avec le décorateur role_required basé session
            session['user_id'] = username
            session['user_groups'] = groups
            if role:
                session['user_role'] = role

            # Affiche les groupes AD dans le message flash pour debug
            flash(f"Groupes AD détectés : {groups}", "info")
            flash('Connexion réussie.', 'success')  # Message de succès

            # Redirection selon le rôle
            if role == 'ADMIN':
                return redirect(url_for('admin.dashboard'))
            if role == 'CHARGE':
                return redirect(url_for('charge_transport.dashboard'))
            if role == 'CHAUFFEUR':
                return redirect(url_for('chauffeur.dashboard'))
            if role == 'MECANICIEN':
                return redirect(url_for('mecanicien.dashboard'))
            # Si aucun rôle mappé, retourner à la page d'accueil ou login
            return redirect(url_for('auth.login'))
        else:
            flash(f"Login ou mot de passe incorrect. Erreur LDAP: {ldap_error}", "danger")  # Message d'erreur
    return render_template('login.html', form=form)  # Affiche la page de login

# Route pour la déconnexion
@bp.route('/logout')
def logout():
    # Déconnexion Flask-Login et nettoyage session custom
    try:
        logout_user()
    except Exception:
        pass
    session.clear()  # Vide aussi la session pour compatibilité décorateur role_required
    flash('Déconnexion réussie.', 'info')  # Message d'information
    return redirect(url_for('auth.login'))  # Redirige vers la page de login