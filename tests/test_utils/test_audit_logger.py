"""
Tests pour le système d'audit.
"""
import pytest
from app.utils.audit_logger import (
    AuditActionType, AuditLevel,
    is_critical_action, get_action_level,
    log_login_success, log_login_failed, log_logout,
    log_creation, log_modification, log_suppression,
    log_system_error, log_unauthorized_access
)


class TestAuditActionType:
    """Tests pour l'enum AuditActionType."""
    
    def test_login_success_exists(self):
        """Test que LOGIN_SUCCESS existe."""
        assert AuditActionType.LOGIN_SUCCESS is not None
        assert AuditActionType.LOGIN_SUCCESS.value == "LOGIN_SUCCESS"
    
    def test_login_failed_exists(self):
        """Test que LOGIN_FAILED existe."""
        assert AuditActionType.LOGIN_FAILED is not None
        assert AuditActionType.LOGIN_FAILED.value == "LOGIN_FAILED"
    
    def test_crud_actions_exist(self):
        """Test que les actions CRUD existent."""
        assert AuditActionType.CREATE is not None
        assert AuditActionType.UPDATE is not None
        assert AuditActionType.DELETE is not None
    
    def test_system_error_exists(self):
        """Test que SYSTEM_ERROR existe."""
        assert AuditActionType.SYSTEM_ERROR is not None


class TestAuditLevel:
    """Tests pour l'enum AuditLevel."""
    
    def test_all_levels_exist(self):
        """Test que tous les niveaux existent."""
        assert AuditLevel.LOW is not None
        assert AuditLevel.MEDIUM is not None
        assert AuditLevel.HIGH is not None
        assert AuditLevel.CRITICAL is not None
    
    def test_level_values(self):
        """Test des valeurs des niveaux."""
        assert AuditLevel.LOW.value == "LOW"
        assert AuditLevel.CRITICAL.value == "CRITICAL"


class TestIsCriticalAction:
    """Tests pour la fonction is_critical_action."""
    
    def test_login_success_is_critical(self):
        """Test que LOGIN_SUCCESS est critique."""
        assert is_critical_action(AuditActionType.LOGIN_SUCCESS) is True
    
    def test_login_failed_is_critical(self):
        """Test que LOGIN_FAILED est critique."""
        assert is_critical_action(AuditActionType.LOGIN_FAILED) is True
    
    def test_create_is_critical(self):
        """Test que CREATE est critique."""
        assert is_critical_action(AuditActionType.CREATE) is True
    
    def test_update_is_critical(self):
        """Test que UPDATE est critique."""
        assert is_critical_action(AuditActionType.UPDATE) is True
    
    def test_delete_is_critical(self):
        """Test que DELETE est critique."""
        assert is_critical_action(AuditActionType.DELETE) is True
    
    def test_system_error_is_critical(self):
        """Test que SYSTEM_ERROR est critique."""
        assert is_critical_action(AuditActionType.SYSTEM_ERROR) is True
    
    def test_string_action_type(self):
        """Test avec un type d'action en string."""
        assert is_critical_action("LOGIN_SUCCESS") is True
    
    def test_invalid_string_action(self):
        """Test avec un type d'action invalide."""
        assert is_critical_action("INVALID_ACTION") is False


class TestGetActionLevel:
    """Tests pour la fonction get_action_level."""
    
    def test_login_failed_is_critical_level(self):
        """Test que LOGIN_FAILED a un niveau CRITICAL."""
        level = get_action_level(AuditActionType.LOGIN_FAILED)
        assert level == AuditLevel.CRITICAL
    
    def test_login_success_is_high_level(self):
        """Test que LOGIN_SUCCESS a un niveau HIGH."""
        level = get_action_level(AuditActionType.LOGIN_SUCCESS)
        assert level == AuditLevel.HIGH
    
    def test_create_is_medium_level(self):
        """Test que CREATE a un niveau MEDIUM."""
        level = get_action_level(AuditActionType.CREATE)
        assert level == AuditLevel.MEDIUM
    
    def test_system_error_is_critical_level(self):
        """Test que SYSTEM_ERROR a un niveau CRITICAL."""
        level = get_action_level(AuditActionType.SYSTEM_ERROR)
        assert level == AuditLevel.CRITICAL
    
    def test_invalid_action_returns_low(self):
        """Test qu'une action invalide retourne LOW."""
        level = get_action_level("INVALID")
        assert level == AuditLevel.LOW


class TestAuditFunctions:
    """Tests pour les fonctions d'audit spécialisées."""
    
    def test_log_login_success_no_error(self, app):
        """Test que log_login_success ne lève pas d'erreur."""
        with app.app_context():
            # Ne devrait pas lever d'exception
            log_login_success(user_id="1", user_role="ADMIN", details="Test login")
    
    def test_log_login_failed_no_error(self, app):
        """Test que log_login_failed ne lève pas d'erreur."""
        with app.app_context():
            log_login_failed(username="testuser", reason="Invalid password")
    
    def test_log_logout_no_error(self, app):
        """Test que log_logout ne lève pas d'erreur."""
        with app.app_context():
            log_logout(user_id="1", user_role="ADMIN")
    
    def test_log_creation_no_error(self, app):
        """Test que log_creation ne lève pas d'erreur."""
        with app.app_context():
            log_creation(entity_type="bus", entity_id="123", details="New bus created")
    
    def test_log_modification_no_error(self, app):
        """Test que log_modification ne lève pas d'erreur."""
        with app.app_context():
            log_modification(
                entity_type="bus",
                entity_id="123",
                old_values={"kilometrage": 50000},
                new_values={"kilometrage": 51000}
            )
    
    def test_log_suppression_no_error(self, app):
        """Test que log_suppression ne lève pas d'erreur."""
        with app.app_context():
            log_suppression(entity_type="bus", entity_id="123", details="Bus deleted")
    
    def test_log_system_error_no_error(self, app):
        """Test que log_system_error ne lève pas d'erreur."""
        with app.app_context():
            log_system_error(
                error_type="DatabaseError",
                error_message="Connection failed",
                context="During user query"
            )
    
    def test_log_unauthorized_access_no_error(self, app):
        """Test que log_unauthorized_access ne lève pas d'erreur."""
        with app.app_context():
            log_unauthorized_access(
                attempted_resource="admin_dashboard",
                attempted_action="view"
            )
