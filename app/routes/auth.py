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
        # Authentification de test pour le superviseur
        if username == "superviseur" and password == "superviseur123":
            print('Auth Test: Connexion superviseur réussie')
            return True, ['Superviseurs'], None

        # Authentification de test pour l'admin
        if username == "admin" and password == "admin123":
            print('Auth Test: Connexion admin réussie')
            return True, ['Administrateur'], None

        # Authentification de test pour le responsable
        if username == "responsable" and password == "responsable123":
            print('Auth Test: Connexion responsable réussie')
            return True, ['Responsables'], None

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
            elif 'Superviseurs' in groups:
                role = 'SUPERVISEUR'
            elif 'Responsables' in groups:
                role = 'RESPONSABLE'

            # Synchroniser l'utilisateur local (création si absent)
            user = Utilisateur.query.filter_by(login=username).first()
            if not user:
                # Créer l'utilisateur avec le bon mot de passe
                user = Utilisateur(
                    nom=username.capitalize(),
                    prenom='Test',
                    login=username,
                    role=role,
                    email=f"{username}@udm.local",
                    telephone='000000000'
                )
                # Définir le mot de passe selon l'utilisateur
                if username == "superviseur":
                    user.set_password('superviseur123')
                elif username == "admin":
                    user.set_password('admin123')
                elif username == "responsable":
                    user.set_password('responsable123')
                else:
                    user.set_password('password123')

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
            flash(f"Login ou mot de passe incorrect. Erreur: {auth_error}", "danger")  # Message d'erreur
    return render_template('auth/login.html', form=form)  # Affiche la page de login

# Route pour la déconnexion
@bp.route('/logout')
def logout():
    # Debug avant déconnexion
    if 'user_login' in session:
        print(f'Déconnexion utilisateur: {session["user_login"]}')

    # Déconnexion Flask-Login et nettoyage session custom
    try:
        logout_user()
    except Exception as e:
        print(f'Erreur logout Flask-Login: {e}')

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