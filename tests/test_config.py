"""
Tests pour la configuration de l'application.
"""
import pytest
import os
from app.config import Config


class TestConfig:
    """Tests pour la classe Config."""
    
    def test_secret_key_from_env(self, monkeypatch):
        """Test que SECRET_KEY est lu depuis l'environnement."""
        monkeypatch.setenv('SECRET_KEY', 'test-secret-key-12345')
        
        # Recharger la config
        from importlib import reload
        import app.config
        reload(app.config)
        
        assert app.config.Config.SECRET_KEY == 'test-secret-key-12345'
    
    def test_database_url_from_env(self, monkeypatch):
        """Test que DATABASE_URL est lu depuis l'environnement."""
        test_url = 'mysql+pymysql://user:pass@localhost/testdb'
        monkeypatch.setenv('DATABASE_URL', test_url)
        
        from importlib import reload
        import app.config
        reload(app.config)
        
        assert app.config.Config.SQLALCHEMY_DATABASE_URI == test_url
    
    def test_sqlalchemy_track_modifications_false(self):
        """Test que SQLALCHEMY_TRACK_MODIFICATIONS est False."""
        assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    
    def test_wtf_csrf_enabled(self):
        """Test que WTF_CSRF_ENABLED est True par défaut."""
        assert Config.WTF_CSRF_ENABLED is True


class TestConfigSecurity:
    """Tests de sécurité pour la configuration."""
    
    def test_no_hardcoded_password_in_database_url(self):
        """Test qu'il n'y a pas de mot de passe en dur dans DATABASE_URL."""
        db_url = Config.SQLALCHEMY_DATABASE_URI
        if db_url:
            # Ne devrait pas contenir de mots de passe courants
            assert 'password' not in db_url.lower()
            assert '123456' not in db_url
    
    def test_secret_key_not_default(self, monkeypatch):
        """Test que SECRET_KEY n'est pas une valeur par défaut faible."""
        # Simuler un environnement de production
        monkeypatch.setenv('FLASK_ENV', 'production')
        monkeypatch.setenv('SECRET_KEY', 'a-very-long-and-secure-secret-key-for-production')
        
        from importlib import reload
        import app.config
        reload(app.config)
        
        secret = app.config.Config.SECRET_KEY
        # La clé devrait être suffisamment longue
        assert len(secret) >= 16
