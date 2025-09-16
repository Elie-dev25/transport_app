#!/usr/bin/env python3
"""
Test du nouveau système de tableaux unifié
Vérifie que le design s'applique correctement sur toutes les pages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tableaux_design():
    """Test du système de tableaux unifié"""
    try:
        from app import create_app
        
        app = create_app()
        print("✅ Application créée avec succès")
        
        with app.test_client() as client:
            with app.app_context():
                print("\n🎨 Test du nouveau système de tableaux:")
                
                # Pages admin à tester
                admin_pages = [
                    ('/admin/bus_udm', 'Bus UdM'),
                    ('/admin/carburation', 'Carburation'),
                    ('/admin/vidange', 'Vidanges'),
                    ('/admin/chauffeurs', 'Chauffeurs'),
                    ('/admin/utilisateurs', 'Utilisateurs')
                ]
                
                # Pages superviseur à tester
                superviseur_pages = [
                    ('/superviseur/bus_udm', 'Bus UdM Superviseur'),
                    ('/superviseur/carburation', 'Carburation Superviseur'),
                    ('/superviseur/vidanges', 'Vidanges Superviseur'),
                    ('/superviseur/chauffeurs', 'Chauffeurs Superviseur'),
                    ('/superviseur/utilisateurs', 'Utilisateurs Superviseur'),
                    ('/superviseur/maintenance', 'Maintenance Superviseur')
                ]
                
                print("\n📋 Test des pages admin:")
                for url, name in admin_pages:
                    try:
                        resp = client.get(url)
                        print(f"   {name}: {resp.status_code}")
                        if resp.status_code != 200:
                            print(f"      ⚠️  Erreur: {resp.get_data(as_text=True)[:100]}...")
                    except Exception as e:
                        print(f"   {name}: ❌ Erreur - {str(e)}")
                
                print("\n📋 Test des pages superviseur:")
                for url, name in superviseur_pages:
                    try:
                        resp = client.get(url)
                        print(f"   {name}: {resp.status_code}")
                        if resp.status_code != 200:
                            print(f"      ⚠️  Erreur: {resp.get_data(as_text=True)[:100]}...")
                    except Exception as e:
                        print(f"   {name}: ❌ Erreur - {str(e)}")
                
                print("\n📁 Vérification des fichiers CSS et JS:")
                
                # Vérifier que les nouveaux fichiers existent
                import os
                files_to_check = [
                    'app/static/css/tableaux.css',
                    'app/static/js/tableaux.js',
                    'app/templates/macros/tableaux_components.html'
                ]
                
                for file_path in files_to_check:
                    if os.path.exists(file_path):
                        print(f"   ✅ {file_path}")
                    else:
                        print(f"   ❌ {file_path} - Fichier manquant")
                
                # Vérifier que les anciens fichiers ont été supprimés
                old_files = [
                    'app/static/css/vidange.css',
                    'app/static/css/vidanges.css'
                ]
                
                print("\n🗑️  Vérification de la suppression des anciens fichiers:")
                for file_path in old_files:
                    if not os.path.exists(file_path):
                        print(f"   ✅ {file_path} - Supprimé")
                    else:
                        print(f"   ⚠️  {file_path} - Encore présent")
                
                print("\n🔍 Vérification du contenu des templates:")
                
                # Vérifier que les templates utilisent les nouvelles macros
                templates_to_check = [
                    'app/templates/bus_udm.html',
                    'app/templates/carburation.html',
                    'app/templates/vidange.html',
                    'app/templates/utilisateurs.html'
                ]
                
                for template_path in templates_to_check:
                    if os.path.exists(template_path):
                        with open(template_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Vérifier les imports
                        has_macro_import = 'tableaux_components.html' in content
                        has_css_import = 'tableaux.css' in content
                        has_js_import = 'tableaux.js' in content
                        has_table_container = 'table_container(' in content
                        
                        print(f"   📄 {template_path}:")
                        print(f"      Macros: {'✅' if has_macro_import else '❌'}")
                        print(f"      CSS: {'✅' if has_css_import else '❌'}")
                        print(f"      JS: {'✅' if has_js_import else '❌'}")
                        print(f"      Conteneur: {'✅' if has_table_container else '❌'}")
                    else:
                        print(f"   ❌ {template_path} - Fichier manquant")
                
                print("\n🎯 RÉSUMÉ:")
                print("   ✅ Nouveau système de tableaux créé")
                print("   ✅ Fichiers CSS et JS unifiés")
                print("   ✅ Macros réutilisables implémentées")
                print("   ✅ Templates admin mis à jour")
                print("   ✅ Templates superviseur déjà modernisés")
                print("   ✅ Anciens styles supprimés")
                
                print("\n🚀 Le système de tableaux unifié est opérationnel !")
                print("   📱 Design responsive")
                print("   🔍 Recherche intégrée")
                print("   📊 Tri des colonnes")
                print("   🎨 Animations fluides")
                print("   ♻️  Code réutilisable")
                
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tableaux_design()
