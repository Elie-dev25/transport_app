"""
Tests smoke pour les formulaires - imports et instanciation.
"""
import pytest


class TestFormsImports:
    """Test que tous les formulaires s'importent."""
    
    def test_import_login_form(self):
        from app.forms.login_form import LoginForm
        assert LoginForm is not None
    
    def test_import_bus_udm_form(self):
        from app.forms import bus_udm_form
        assert bus_udm_form is not None
    
    def test_import_panne_form(self):
        from app.forms.panne_form import PanneForm
        assert PanneForm is not None
    
    def test_import_autres_trajets_form(self):
        from app.forms import autres_trajets_form
        assert autres_trajets_form is not None
    
    def test_import_trajet_depart_form(self):
        from app.forms import trajet_depart_form
        assert trajet_depart_form is not None
    
    def test_import_trajet_prestataire_form(self):
        from app.forms import trajet_prestataire_form
        assert trajet_prestataire_form is not None
    
    def test_import_trajet_interne_form(self):
        from app.forms import trajet_interne_bus_udm_form
        assert trajet_interne_bus_udm_form is not None
    
    def test_import_trajet_sortie_form(self):
        from app.forms import trajet_sortie_hors_ville_form
        assert trajet_sortie_hors_ville_form is not None
    
    def test_import_trajet_banekane_form(self):
        from app.forms import trajet_banekane_retour_form
        assert trajet_banekane_retour_form is not None
    
    def test_import_validators(self):
        from app.forms import validators
        assert validators is not None
    
    def test_import_base_forms(self):
        from app.forms import base_forms
        assert base_forms is not None
    
    def test_import_constants(self):
        from app.forms import constants
        assert constants is not None


class TestLoginForm:
    """Tests pour LoginForm."""
    
    def test_login_form_instantiation(self, app):
        from app.forms.login_form import LoginForm
        with app.test_request_context():
            form = LoginForm()
            assert form is not None
    
    def test_login_form_validation_empty(self, app):
        from app.forms.login_form import LoginForm
        with app.test_request_context():
            form = LoginForm(data={'login': '', 'mot_de_passe': ''})
            assert not form.validate()
    
    def test_login_form_with_data(self, app):
        from app.forms.login_form import LoginForm
        with app.test_request_context():
            form = LoginForm(data={
                'login': 'testuser',
                'mot_de_passe': 'TestPass123!'
            })
            # Validation peut échouer si autres champs requis
            form.validate()
            assert form.login.data == 'testuser'


class TestPanneForm:
    """Tests pour PanneForm."""
    
    def test_panne_form_instantiation(self, app):
        from app.forms.panne_form import PanneForm
        with app.test_request_context():
            form = PanneForm()
            assert form is not None


class TestValidators:
    """Tests pour les validators custom."""
    
    def test_validators_module_attributes(self):
        from app.forms import validators
        # Vérifier qu'il y a des classes/fonctions définies
        attrs = [a for a in dir(validators) if not a.startswith('_')]
        assert len(attrs) > 0
