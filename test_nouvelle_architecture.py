#!/usr/bin/env python3
"""
Script de test pour vérifier la nouvelle architecture unifiée
Teste que les formulaires et modales sont correctement partagés entre les rôles
"""

import os
import sys
import subprocess
from pathlib import Path

def test_imports():
    """Teste que tous les imports fonctionnent correctement"""
    print("🔍 Test des imports...")
    
    try:
        # Test des nouveaux formulaires
        from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
        from app.forms.trajet_prestataire_form import TrajetPrestataireForm
        from app.forms.autres_trajets_form import AutresTrajetsForm
        print("✅ Formulaires modernisés importés avec succès")
        
        # Test du service centralisé
        from app.services.form_service import FormService
        print("✅ Service FormService importé avec succès")
        
        # Test des services de trajets
        from app.services.trajet_service import (
            enregistrer_trajet_interne_bus_udm,
            enregistrer_trajet_prestataire_modernise,
            enregistrer_autres_trajets
        )
        print("✅ Services de trajets modernisés importés avec succès")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_templates_exist():
    """Vérifie que les nouveaux templates partagés existent"""
    print("\n🔍 Test de l'existence des templates...")
    
    templates_to_check = [
        "app/templates/shared/modals/trajet_interne_modal.html",
        "app/templates/shared/modals/trajet_prestataire_modal.html", 
        "app/templates/shared/modals/autres_trajets_modal.html",
        "app/templates/shared/macros/trajet_modals.html"
    ]
    
    all_exist = True
    for template in templates_to_check:
        if os.path.exists(template):
            print(f"✅ {template}")
        else:
            print(f"❌ {template} - MANQUANT")
            all_exist = False
    
    return all_exist

def test_routes_syntax():
    """Teste la syntaxe des routes modifiées"""
    print("\n🔍 Test de la syntaxe des routes...")
    
    try:
        # Test de la syntaxe Python des routes
        result = subprocess.run([
            sys.executable, "-m", "py_compile", 
            "app/routes/charge_transport.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Route charge_transport.py - syntaxe OK")
        else:
            print(f"❌ Route charge_transport.py - erreur de syntaxe: {result.stderr}")
            return False
            
        # Test de la route admin
        result = subprocess.run([
            sys.executable, "-m", "py_compile", 
            "app/routes/admin/dashboard.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Route admin/dashboard.py - syntaxe OK")
        else:
            print(f"❌ Route admin/dashboard.py - erreur de syntaxe: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de syntaxe: {e}")
        return False

def test_form_service():
    """Teste le service FormService"""
    print("\n🔍 Test du service FormService...")
    
    try:
        from app.forms.trajet_interne_bus_udm_form import TrajetInterneBusUdMForm
        from app.services.form_service import FormService
        
        # Créer un formulaire de test
        form = TrajetInterneBusUdMForm()
        
        # Tester les méthodes du service
        bus_choices = FormService.get_bus_choices()
        chauffeur_choices = FormService.get_chauffeur_choices()
        prestataire_choices = FormService.get_prestataire_choices()
        
        print("✅ FormService.get_bus_choices() fonctionne")
        print("✅ FormService.get_chauffeur_choices() fonctionne")
        print("✅ FormService.get_prestataire_choices() fonctionne")
        
        # Tester le peuplement des formulaires
        FormService.populate_trajet_form_choices(form)
        print("✅ FormService.populate_trajet_form_choices() fonctionne")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans FormService: {e}")
        return False

def test_template_syntax():
    """Teste la syntaxe des templates modifiés"""
    print("\n🔍 Test de la syntaxe des templates...")
    
    templates_to_check = [
        "app/templates/dashboard_charge.html",
        "app/templates/dashboard_admin.html"
    ]
    
    all_ok = True
    for template in templates_to_check:
        if os.path.exists(template):
            # Vérification basique de la syntaxe Jinja2
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Vérifications basiques
            if '{% from' in content and 'import' in content:
                print(f"✅ {template} - contient des imports de macros")
            else:
                print(f"⚠️  {template} - pas d'imports de macros détectés")
                
            if 'include_all_trajet_modals' in content:
                print(f"✅ {template} - utilise les nouvelles macros")
            else:
                print(f"⚠️  {template} - n'utilise pas les nouvelles macros")
        else:
            print(f"❌ {template} - MANQUANT")
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale de test"""
    print("🚀 Test de la nouvelle architecture unifiée")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Templates", test_templates_exist),
        ("Syntaxe des routes", test_routes_syntax),
        ("Service FormService", test_form_service),
        ("Syntaxe des templates", test_template_syntax)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'architecture unifiée est prête.")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
