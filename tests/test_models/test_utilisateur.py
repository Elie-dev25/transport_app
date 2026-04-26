"""
Tests pour le modèle Utilisateur.
"""
import pytest
from app.models.utilisateur import Utilisateur
from app.database import db


class TestUtilisateur:
    """Tests pour le modèle Utilisateur."""
    
    def test_create_utilisateur(self, app):
        """Test de création d'un utilisateur."""
        with app.app_context():
            user = Utilisateur(
                nom='Dupont',
                prenom='Jean',
                login='jdupont',
                email='jean.dupont@example.com',
                telephone='0612345678',
                role='ADMIN'
            )
            user.set_password('SecurePass123!')
            db.session.add(user)
            db.session.commit()
            
            assert user.utilisateur_id is not None
            assert user.nom == 'Dupont'
            assert user.prenom == 'Jean'
            assert user.login == 'jdupont'
            assert user.role == 'ADMIN'
    
    def test_set_password_hashes_password(self, app):
        """Test que set_password hash correctement le mot de passe."""
        with app.app_context():
            user = Utilisateur(
                nom='Test',
                prenom='User',
                login='testpwd',
                email='test@example.com',
                telephone='0600000000',
                role='CHAUFFEUR'
            )
            plain_password = 'MySecretPassword123!'
            user.set_password(plain_password)
            
            # Le mot de passe ne doit pas être stocké en clair
            assert user.mot_de_passe != plain_password
            # Le hash doit commencer par un préfixe werkzeug
            assert user.mot_de_passe.startswith('scrypt:') or user.mot_de_passe.startswith('pbkdf2:')
    
    def test_check_password_valid(self, app):
        """Test de vérification d'un mot de passe valide."""
        with app.app_context():
            user = Utilisateur(
                nom='Test',
                prenom='User',
                login='testcheck',
                email='test@example.com',
                telephone='0600000000',
                role='CHAUFFEUR'
            )
            password = 'CorrectPassword123!'
            user.set_password(password)
            
            assert user.check_password(password) is True
    
    def test_check_password_invalid(self, app):
        """Test de vérification d'un mot de passe invalide."""
        with app.app_context():
            user = Utilisateur(
                nom='Test',
                prenom='User',
                login='testinvalid',
                email='test@example.com',
                telephone='0600000000',
                role='CHAUFFEUR'
            )
            user.set_password('CorrectPassword123!')
            
            assert user.check_password('WrongPassword!') is False
    
    def test_get_id_returns_string(self, app):
        """Test que get_id retourne une chaîne."""
        with app.app_context():
            user = Utilisateur(
                nom='Test',
                prenom='User',
                login='testid',
                email='test@example.com',
                telephone='0600000000',
                role='ADMIN'
            )
            user.set_password('Password123!')
            db.session.add(user)
            db.session.commit()
            
            user_id = user.get_id()
            assert isinstance(user_id, str)
            assert user_id == str(user.utilisateur_id)
    
    def test_unique_login_constraint(self, app):
        """Test que le login doit être unique."""
        with app.app_context():
            user1 = Utilisateur(
                nom='User1',
                prenom='Test',
                login='unique_login',
                email='user1@example.com',
                telephone='0600000001',
                role='ADMIN'
            )
            user1.set_password('Password123!')
            db.session.add(user1)
            db.session.commit()
            
            user2 = Utilisateur(
                nom='User2',
                prenom='Test',
                login='unique_login',  # Même login
                email='user2@example.com',
                telephone='0600000002',
                role='CHAUFFEUR'
            )
            user2.set_password('Password456!')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
    
    def test_all_roles_valid(self, app):
        """Test que tous les rôles définis sont valides."""
        valid_roles = ['ADMIN', 'CHAUFFEUR', 'MECANICIEN', 'CHARGE', 'SUPERVISEUR', 'RESPONSABLE']
        
        with app.app_context():
            for i, role in enumerate(valid_roles):
                user = Utilisateur(
                    nom=f'User{i}',
                    prenom='Test',
                    login=f'user_role_{role.lower()}',
                    email=f'user{i}@example.com',
                    telephone=f'060000000{i}',
                    role=role
                )
                user.set_password('Password123!')
                db.session.add(user)
            
            db.session.commit()
            
            # Vérifier que tous les utilisateurs ont été créés
            count = Utilisateur.query.count()
            assert count == len(valid_roles)
    
    def test_user_mixin_is_authenticated(self, sample_user, app):
        """Test que UserMixin fournit is_authenticated."""
        with app.app_context():
            user = Utilisateur.query.get(sample_user.utilisateur_id)
            assert user.is_authenticated is True
    
    def test_user_mixin_is_active(self, sample_user, app):
        """Test que UserMixin fournit is_active."""
        with app.app_context():
            user = Utilisateur.query.get(sample_user.utilisateur_id)
            assert user.is_active is True
    
    def test_password_empty_check(self, app):
        """Test de vérification avec mot de passe vide."""
        with app.app_context():
            user = Utilisateur(
                nom='Test',
                prenom='Empty',
                login='testempty',
                email='empty@example.com',
                telephone='0600000000',
                role='CHAUFFEUR'
            )
            user.set_password('ValidPassword123!')
            
            # Un mot de passe vide ne doit pas correspondre
            assert user.check_password('') is False
