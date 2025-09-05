from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user
from app.forms.login_form import LoginForm
from app.models.utilisateur import Utilisateur
from app.database import db

LDAP_SERVER = '192.168.21.131'
LDAP_DOMAIN = 'domaine.local'
BASE_DN = 'DC=domaine,DC=local'

# Fonction d'authentification MySQL (temporaire - remplace LDAP)
def authenticate_mysql(username, password):
    try:
        # Chercher l'utilisateur en base MySQL
        user = Utilisateur.query.filter_by(login=username).first()
        if user and user.check_password(password):
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
            
            print(f'MySQL Auth: Utilisateur {username} authentifié avec succès, rôle: {user.role}')
            return True, groups, None
        else:
            print(f'MySQL Auth: Échec authentification pour {username}')
            return False, [], 'Login ou mot de passe incorrect'
    except Exception as e:
        print(f'Erreur MySQL Auth: {e}')
        return False, [], str(e)

# Fonction d'authentification AD (SIMPLE bind via LDAPS, fallback StartTLS) - DÉSACTIVÉE
def authenticate_ad_disabled(username, password):
    # Utiliser le format UPN pour éviter NTLM/MD4
    user_upn = f"{username}@{LDAP_DOMAIN}"

    # Config TLS (validation désactivée en dev; sécuriser en prod)
    tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)

    # 1) Tentative LDAPS (port 636)
    server_ldaps = Server(LDAP_SERVER, port=636, use_ssl=True, tls=tls_config, get_info=ALL)
    try:
        conn = Connection(
            server_ldaps,
            user=user_upn,
            password=password,
            authentication=SIMPLE,
            auto_bind=True,
        )
        conn.search(BASE_DN, f'(sAMAccountName={username})', attributes=['memberOf'])
        if conn.entries:
            entry = conn.entries[0]
            groups = entry.memberOf.values if 'memberOf' in entry else []
            user_groups = [g.split(',')[0].replace('CN=', '') for g in groups]
            return True, user_groups, None
        print('LDAP: Utilisateur non trouvé dans AD.')
        return False, [], 'Utilisateur non trouvé dans AD.'
    except Exception as e_ldaps:
        # 2) Fallback: LDAP 389 + StartTLS
        try:
            server_ldap = Server(LDAP_SERVER, port=389, use_ssl=False, tls=tls_config, get_info=ALL)
            conn = Connection(
                server_ldap,
                user=user_upn,
                password=password,
                authentication=SIMPLE,
                auto_bind=False,
            )
            conn.open()
            conn.start_tls()
            if not conn.bind():
                raise Exception(conn.result)

            conn.search(BASE_DN, f'(sAMAccountName={username})', attributes=['memberOf'])
            if conn.entries:
                entry = conn.entries[0]
                groups = entry.memberOf.values if 'memberOf' in entry else []
                user_groups = [g.split(',')[0].replace('CN=', '') for g in groups]
                return True, user_groups, None
            print('LDAP: Utilisateur non trouvé dans AD.')
            return False, [], 'Utilisateur non trouvé dans AD.'
        except Exception as e_starttls:
            err = f"LDAPS 636 a échoué: {e_ldaps}; StartTLS 389 a échoué: {e_starttls}"
            print(f'Erreur LDAP: {err}')
            return False, [], err
    finally:
        try:
            conn.unbind()
        except Exception:
            pass

# Création du blueprint pour l'authentification
bp = Blueprint('auth', __name__)

# Route pour la page de connexion
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Instancie le formulaire de connexion
    if form.validate_on_submit():  # Vérifie si le formulaire est soumis et valide
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
            flash(f"Login ou mot de passe incorrect. Erreur: {auth_error}", "danger")  # Message d'erreur
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