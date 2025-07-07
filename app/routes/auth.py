from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user  # Ajouté en haut
from app.forms.login_form import LoginForm
from app.models.utilisateur import Utilisateur
from app.database import db

# Création du blueprint pour l'authentification
bp = Blueprint('auth', __name__)

# Route pour la page de connexion
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Instancie le formulaire de connexion
    if form.validate_on_submit():  # Vérifie si le formulaire est soumis et valide
        user = Utilisateur.query.filter_by(login=form.login.data).first()  # Recherche l'utilisateur par login
        if user and user.check_password(form.mot_de_passe.data):  # Vérifie le mot de passe
            login_user(user)  # Authentifie l'utilisateur avec Flask-Login
            session['user_id'] = user.utilisateur_id  # Stocke l'ID utilisateur en session
            session['user_role'] = user.role  # Stocke le rôle utilisateur en session (plus de .value)
            if user.role != 'CHARGE':
                flash('Connexion réussie.', 'success')  # Message de succès
            # Redirection selon le rôle de l'utilisateur
            if user.role == "ADMIN":
                return redirect(url_for('admin.dashboard'))
            elif user.role == "CHAUFFEUR":
                return redirect(url_for('chauffeur.dashboard'))
            elif user.role == "MECANICIEN":
                return redirect(url_for('mecanicien.dashboard'))
            elif user.role == "CHARGE":
                return redirect(url_for('charge_transport.dashboard'))
        else:
            flash("Login ou mot de passe incorrect", "danger")  # Message d'erreur
    return render_template('login.html', form=form)  # Affiche la page de login

# Route pour la déconnexion
@bp.route('/logout')
def logout():
    session.clear()  # Vide la session
    flash('Déconnexion réussie.', 'info')  # Message d'information
    return redirect(url_for('auth.login'))  # Redirige vers la page de login

# Route pour la page d'accueil
@bp.route('/')
def home():
    return "Bienvenue sur la page d'accueil"