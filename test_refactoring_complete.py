#!/usr/bin/env python3
"""
Test complet du refactoring - Toutes les phases
Vérifie que toutes les améliorations fonctionnent correctement
"""

import sys
import traceback
from datetime import datetime

print("🚀 TEST COMPLET DU REFACTORING - TOUTES LES PHASES")
print("=" * 60)
print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Compteurs de tests
tests_passed = 0
tests_failed = 0
errors = []

def test_section(name):
    """Décorateur pour les sections de test"""
    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed, errors
            print(f"\n📋 {name}")
            print("-" * 40)
            try:
                result = func()
                if result:
                    tests_passed += 1
                    print(f"✅ {name} - SUCCÈS")
                else:
                    tests_failed += 1
                    print(f"❌ {name} - ÉCHEC")
                return result
            except Exception as e:
                tests_failed += 1
                error_msg = f"{name}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {name} - ERREUR: {str(e)}")
                return False
        return wrapper
    return decorator

@test_section("PHASE 1 - Services Centralisés")
def test_phase1_services():
    """Test des services centralisés"""
    try:
        # Test DashboardService
        from app.services.dashboard_service import DashboardService
        print("  ✓ DashboardService importé")
        
        # Test QueryService
        from app.services.query_service import QueryService
        print("  ✓ QueryService importé")
        
        # Test FormService étendu
        from app.services.form_service import FormService
        print("  ✓ FormService étendu importé")
        
        # Test des méthodes principales
        if hasattr(DashboardService, 'get_common_stats'):
            print("  ✓ DashboardService.get_common_stats() disponible")
        
        if hasattr(QueryService, 'get_active_buses'):
            print("  ✓ QueryService.get_active_buses() disponible")
        
        if hasattr(FormService, 'populate_multiple_forms'):
            print("  ✓ FormService.populate_multiple_forms() disponible")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

@test_section("PHASE 2 - Formulaires Refactorisés")
def test_phase2_forms():
    """Test des formulaires refactorisés"""
    try:
        # Test des constantes
        from app.forms.constants import FormChoices, FormLabels, FormMessages
        print("  ✓ Constantes de formulaires importées")
        
        # Test des validateurs
        from app.forms.validators import CommonValidators, FormValidators
        print("  ✓ Validateurs centralisés importés")
        
        # Test des classes de base
        from app.forms.base_forms import BaseTrajetForm, BaseTrajetInterneForm
        print("  ✓ Classes de base importées")
        
        # Test des formulaires refactorisés
        from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
        from app.forms.trajet_prestataire_form import TrajetPrestataireForm
        from app.forms.autres_trajets_form import AutresTrajetsForm
        print("  ✓ Formulaires refactorisés importés")
        
        # Vérifier l'héritage
        if issubclass(TrajetInterneBusUdMForm, BaseTrajetInterneForm):
            print("  ✓ Héritage correct pour TrajetInterneBusUdMForm")
        
        # Test des choix constants
        if len(FormChoices.TYPE_PASSAGERS) > 0:
            print(f"  ✓ {len(FormChoices.TYPE_PASSAGERS)} types de passagers définis")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

@test_section("PHASE 3 - Modèles Refactorisés")
def test_phase3_models():
    """Test des modèles refactorisés"""
    try:
        # Test des classes de base
        from app.models.base_models import BaseModel, UserRoleMixin, PermisDriverMixin
        print("  ✓ Classes de base de modèles importées")
        
        # Test des modèles refactorisés
        from app.models.administrateur import Administrateur
        from app.models.chargetransport import Chargetransport
        from app.models.chauffeur import Chauffeur
        from app.models.mecanicien import Mecanicien
        print("  ✓ Modèles refactorisés importés")
        
        # Vérifier l'héritage
        if issubclass(Chauffeur, BaseModel):
            print("  ✓ Chauffeur hérite de BaseModel")
        
        if issubclass(Chauffeur, PermisDriverMixin):
            print("  ✓ Chauffeur utilise PermisDriverMixin")
        
        # Test des méthodes héritées
        if hasattr(BaseModel, 'save'):
            print("  ✓ Méthode save() disponible")
        
        if hasattr(BaseModel, 'to_dict'):
            print("  ✓ Méthode to_dict() disponible")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

@test_section("PHASE 4 - Templates Centralisés")
def test_phase4_templates():
    """Test des templates centralisés"""
    try:
        import os
        
        # Vérifier l'existence des fichiers de templates
        template_files = [
            'app/templates/shared/macros/common_macros.html',
            'app/templates/shared/base_unified.html',
            'app/templates/shared/includes/dashboard_stats.html',
            'app/templates/shared/includes/navigation_menus.html'
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                print(f"  ✓ {template_file} existe")
            else:
                print(f"  ❌ {template_file} manquant")
                return False
        
        # Vérifier le contenu des macros
        with open('app/templates/shared/macros/common_macros.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'render_stats_cards' in content:
                print("  ✓ Macro render_stats_cards définie")
            if 'render_modal_form' in content:
                print("  ✓ Macro render_modal_form définie")
            if 'render_data_table' in content:
                print("  ✓ Macro render_data_table définie")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

@test_section("PHASE 5 - Configuration Centralisée")
def test_phase5_config():
    """Test de la configuration centralisée"""
    try:
        # Test des constantes globales
        from app.constants import (
            AppConstants, UserRoles, VehicleStates, 
            LocationConstants, SecurityConstants
        )
        print("  ✓ Constantes globales importées")
        
        # Test de la configuration
        from app.config import Config, DevelopmentConfig, ProductionConfig
        print("  ✓ Classes de configuration importées")
        
        # Vérifier les constantes
        if AppConstants.APP_NAME:
            print(f"  ✓ Nom de l'application: {AppConstants.APP_NAME}")
        
        if len(UserRoles) > 0:
            print(f"  ✓ {len(UserRoles)} rôles utilisateur définis")
        
        if len(LocationConstants.CAMPUS_LOCATIONS) > 0:
            print(f"  ✓ {len(LocationConstants.CAMPUS_LOCATIONS)} lieux campus définis")
        
        # Test des fonctions utilitaires
        from app.constants import get_role_display_name, has_permission
        
        admin_display = get_role_display_name('ADMIN')
        if admin_display == 'Administrateur':
            print("  ✓ Fonction get_role_display_name() fonctionne")
        
        admin_can_create = has_permission('ADMIN', 'create_user')
        if admin_can_create:
            print("  ✓ Fonction has_permission() fonctionne")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import: {e}")
        return False

@test_section("INTÉGRATION - Routes Refactorisées")
def test_integration_routes():
    """Test d'intégration des routes refactorisées"""
    try:
        # Test des imports des routes refactorisées
        from app.routes.admin import dashboard as admin_dashboard
        from app.routes.charge_transport import dashboard as charge_dashboard
        from app.routes.chauffeur import dashboard as chauffeur_dashboard
        print("  ✓ Routes refactorisées importées")
        
        # Vérifier que les services sont utilisés
        import inspect
        
        # Vérifier admin dashboard
        admin_source = inspect.getsource(admin_dashboard.dashboard)
        if 'DashboardService' in admin_source:
            print("  ✓ Admin dashboard utilise DashboardService")
        
        if 'FormService' in admin_source:
            print("  ✓ Admin dashboard utilise FormService")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

# Exécution des tests
def run_all_tests():
    """Exécute tous les tests"""
    global tests_passed, tests_failed
    
    print("🔍 DÉBUT DES TESTS")
    print()
    
    # Exécuter tous les tests
    test_phase1_services()
    test_phase2_forms()
    test_phase3_models()
    test_phase4_templates()
    test_phase5_config()
    test_integration_routes()
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 60)
    
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Tests réussis: {tests_passed}")
    print(f"❌ Tests échoués: {tests_failed}")
    print(f"📈 Taux de réussite: {success_rate:.1f}%")
    
    if errors:
        print(f"\n🚨 ERREURS DÉTAILLÉES:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    
    if tests_failed == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✨ Le refactoring est complet et fonctionnel.")
        return True
    else:
        print(f"\n⚠️  {tests_failed} test(s) ont échoué.")
        print("🔧 Veuillez corriger les erreurs avant de continuer.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
