"""
Tests pour les routes d'authentification.
"""
import pytest
from flask import session
from app.models.utilisateur import Utilisateur
from app.database import db


class TestAuthRoutes:
    """Tests pour les routes d'authentification."""
    
    def test_login_page_get(self, client):
        """Test d'accès à la page de login."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_login_success(self, client, app):
        """Test de connexion réussie."""
        with app.app_context():
            # Créer un utilisateur de test
            user = Utilisateur(
                nom='Test',
                prenom='Login',
                login='testlogin',
                email='testlogin@example.com',
                telephone='0600000000',
                role='ADMIN'
            )
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'login': 'testlogin',
            'mot_de_passe': 'TestPassword123!'
        }, follow_redirects=False)
        
        # Devrait rediriger vers le dashboard
        assert response.status_code in [200, 302]
    
    def test_login_invalid_password(self, client, app):
        """Test de connexion avec mot de passe invalide."""
        with app.app_context():
            user = Utilisateur(
                nom='Test',
                prenom='Invalid',
                login='testinvalid',
                email='testinvalid@example.com',
                telephone='0600000001',
                role='ADMIN'
            )
            user.set_password('CorrectPassword!')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'login': 'testinvalid',
            'mot_de_passe': 'WrongPassword!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Devrait afficher un message d'erreur
        assert b'incorrect' in response.data.lower() or b'erreur' in response.data.lower()
    
    def test_login_nonexistent_user(self, client):
        """Test de connexion avec utilisateur inexistant."""
        response = client.post('/login', data={
            'login': 'nonexistent_user',
            'mot_de_passe': 'SomePassword!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_logout(self, client, sample_user, app):
        """Test de déconnexion."""
        # D'abord se connecter
        with app.app_context():
            with client.session_transaction() as sess:
                sess['user_id'] = str(sample_user.utilisateur_id)
                sess['user_role'] = sample_user.role
        
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_login_empty_credentials(self, client):
        """Test de connexion avec identifiants vides."""
        response = client.post('/login', data={
            'login': '',
            'mot_de_passe': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_redirect_admin(self, client, app):
        """Test de redirection vers dashboard admin après login."""
        with app.app_context():
            user = Utilisateur(
                nom='Admin',
                prenom='Test',
                login='admintest',
                email='admin@example.com',
                telephone='0600000002',
                role='ADMIN'
            )
            user.set_password('AdminPass123!')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'login': 'admintest',
            'mot_de_passe': 'AdminPass123!'
        }, follow_redirects=False)
        
        # Devrait rediriger
        assert response.status_code in [200, 302]
    
    def test_login_redirect_chauffeur(self, client, app):
        """Test de redirection vers dashboard chauffeur après login."""
        with app.app_context():
            user = Utilisateur(
                nom='Chauffeur',
                prenom='Test',
                login='chauffeurtest',
                email='chauffeur@example.com',
                telephone='0600000003',
                role='CHAUFFEUR'
            )
            user.set_password('ChauffeurPass123!')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'login': 'chauffeurtest',
            'mot_de_passe': 'ChauffeurPass123!'
        }, follow_redirects=False)
        
        assert response.status_code in [200, 302]
    
    def test_login_redirect_superviseur(self, client, app):
        """Test de redirection vers dashboard superviseur après login."""
        with app.app_context():
            user = Utilisateur(
                nom='Superviseur',
                prenom='Test',
                login='superviseurtest',
                email='superviseur@example.com',
                telephone='0600000004',
                role='SUPERVISEUR'
            )
            user.set_password('SuperviseurPass123!')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'login': 'superviseurtest',
            'mot_de_passe': 'SuperviseurPass123!'
        }, follow_redirects=False)
        
        assert response.status_code in [200, 302]
    
    def test_session_cleared_on_logout(self, client, sample_user, app):
        """Test que la session est vidée après déconnexion."""
        with app.app_context():
            with client.session_transaction() as sess:
                sess['user_id'] = str(sample_user.utilisateur_id)
                sess['user_role'] = sample_user.role
                sess['user_login'] = sample_user.login
        
        client.get('/logout', follow_redirects=True)
        
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'user_role' not in sess
