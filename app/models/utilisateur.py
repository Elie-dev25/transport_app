from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin  # Ajout pour Flask-Login
from sqlalchemy import Enum

# Modèle représentant un utilisateur dans la base de données
class Utilisateur(UserMixin, db.Model):  # Hérite de UserMixin pour Flask-Login
    __tablename__ = "utilisateur"

    utilisateur_id = db.Column(db.Integer, primary_key=True)  # Identifiant unique
    nom = db.Column(db.String(100), nullable=False)  # Nom
    prenom = db.Column(db.String(100), nullable=False)  # Prénom
    login = db.Column(db.String(50), unique=True, nullable=False)  # Login unique
    mot_de_passe = db.Column(db.String(255), nullable=False)  # Mot de passe hashé
    reset_token = db.Column(db.String(255), nullable=True)
    reset_expires = db.Column(db.DateTime, nullable=True)
    role = db.Column(Enum('ADMIN', 'CHAUFFEUR', 'MECANICIEN', 'CHARGE', name='role_enum'), nullable=True)
    # Email et téléphone désormais obligatoires pour tous les utilisateurs
    email = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        # Hash le mot de passe et le stocke
        self.mot_de_passe = generate_password_hash(password)
    def check_password(self, password):
        # Vérifie si le mot de passe fourni correspond au hash stocké
        return check_password_hash(self.mot_de_passe, password)

    def get_id(self):
        # Retourne l'identifiant unique pour Flask-Login
        return str(self.utilisateur_id)