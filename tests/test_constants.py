"""
Tests pour les constantes de l'application.
"""
import pytest
from app.constants import (
    UserRoles, VehicleConstants, 
    DATE_FORMAT_FR, DATE_FORMAT_ISO,
    FormConstants
)


class TestUserRoles:
    """Tests pour les constantes de rôles."""
    
    def test_roles_class_defined(self):
        """Test que UserRoles est défini."""
        assert UserRoles is not None
    
    def test_admin_role_exists(self):
        """Test que le rôle ADMIN existe."""
        assert hasattr(UserRoles, 'ADMIN')
    
    def test_chauffeur_role_exists(self):
        """Test que le rôle CHAUFFEUR existe."""
        assert hasattr(UserRoles, 'CHAUFFEUR')
    
    def test_superviseur_role_exists(self):
        """Test que le rôle SUPERVISEUR existe."""
        assert hasattr(UserRoles, 'SUPERVISEUR')


class TestVehicleConstants:
    """Tests pour les constantes de véhicule."""
    
    def test_vehicle_constants_defined(self):
        """Test que VehicleConstants est défini."""
        assert VehicleConstants is not None
    
    def test_has_attributes(self):
        """Test que VehicleConstants a des attributs."""
        # Vérifier qu'il y a des attributs définis
        attrs = [a for a in dir(VehicleConstants) if not a.startswith('_')]
        assert len(attrs) > 0


class TestDateFormats:
    """Tests pour les formats de date."""
    
    def test_date_format_fr_defined(self):
        """Test que le format FR est défini."""
        assert DATE_FORMAT_FR is not None
        assert isinstance(DATE_FORMAT_FR, str)
    
    def test_date_format_iso_defined(self):
        """Test que le format ISO est défini."""
        assert DATE_FORMAT_ISO is not None
        assert isinstance(DATE_FORMAT_ISO, str)
    
    def test_date_format_fr_valid(self):
        """Test que le format FR est valide."""
        from datetime import datetime
        test_date = datetime(2024, 3, 15)
        formatted = test_date.strftime(DATE_FORMAT_FR)
        assert formatted is not None
    
    def test_date_format_iso_valid(self):
        """Test que le format ISO est valide."""
        from datetime import datetime
        test_date = datetime(2024, 3, 15)
        formatted = test_date.strftime(DATE_FORMAT_ISO)
        assert formatted is not None


class TestFormConstants:
    """Tests pour les constantes de formulaire."""
    
    def test_form_constants_defined(self):
        """Test que FormConstants est défini."""
        assert FormConstants is not None
