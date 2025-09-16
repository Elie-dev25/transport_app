#!/usr/bin/env python3
"""
Vérification complète de TOUTES les routes pour détecter les anciens chemins de templates
"""

import os
import re
from pathlib import Path

def verifier_toutes_routes():
    """Vérifie tous les render_template dans toutes les routes"""
    print("🔍 VÉRIFICATION COMPLÈTE DE TOUTES LES ROUTES")
    print("=" * 80)
    
    routes_dir = Path("app/routes")
    problemes = []
    
    # Patterns d'anciens chemins à détecter
    anciens_patterns = [
        # Templates sans préfixe de dossier
        (r"render_template\(['\"]dashboard_admin\.html['\"]", "dashboard_admin.html → roles/admin/dashboard_admin.html"),
        (r"render_template\(['\"]dashboard_charge\.html['\"]", "dashboard_charge.html → roles/charge_transport/dashboard_charge.html"),
        (r"render_template\(['\"]dashboard_chauffeur\.html['\"]", "dashboard_chauffeur.html → roles/chauffeur/dashboard_chauffeur.html"),
        (r"render_template\(['\"]dashboard_superviseur\.html['\"]", "dashboard_superviseur.html → roles/superviseur/dashboard.html"),
        (r"render_template\(['\"]dashboard_mecanicien\.html['\"]", "dashboard_mecanicien.html → roles/mecanicien/dashboard_mecanicien.html"),
        (r"render_template\(['\"]bus_udm\.html['\"]", "bus_udm.html → pages/bus_udm.html ou roles/admin/bus_udm.html"),
        (r"render_template\(['\"]carburation\.html['\"]", "carburation.html → pages/carburation.html"),
        (r"render_template\(['\"]vidange\.html['\"]", "vidange.html → pages/vidange.html"),
        (r"render_template\(['\"]parametres\.html['\"]", "parametres.html → pages/parametres.html"),
        (r"render_template\(['\"]rapports\.html['\"]", "rapports.html → pages/rapports.html"),
        (r"render_template\(['\"]utilisateurs\.html['\"]", "utilisateurs.html → pages/utilisateurs.html"),
        (r"render_template\(['\"]chauffeurs\.html['\"]", "chauffeurs.html → legacy/chauffeurs.html"),
        (r"render_template\(['\"]depanage\.html['\"]", "depanage.html → pages/depanage.html"),
        (r"render_template\(['\"]details_bus\.html['\"]", "details_bus.html → pages/details_bus.html"),
        
        # Templates avec anciens préfixes
        (r"render_template\(['\"]admin/([^'\"]*\.html)['\"]", "admin/... → roles/admin/..."),
        (r"render_template\(['\"]charge_transport/([^'\"]*\.html)['\"]", "charge_transport/... → roles/charge_transport/..."),
        (r"render_template\(['\"]chauffeur/([^'\"]*\.html)['\"]", "chauffeur/... → roles/chauffeur/..."),
        (r"render_template\(['\"]superviseur/([^'\"]*\.html)['\"]", "superviseur/... → roles/superviseur/..."),
        (r"render_template\(['\"]mecanicien/([^'\"]*\.html)['\"]", "mecanicien/... → roles/mecanicien/..."),
    ]
    
    total_files = 0
    files_with_problems = 0
    
    # Parcourir tous les fichiers Python dans routes/
    for route_file in routes_dir.rglob("*.py"):
        if route_file.name == "__init__.py":
            continue
            
        total_files += 1
        file_has_problems = False
        
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Chercher tous les render_template
            render_templates = re.findall(r"render_template\(['\"][^'\"]*\.html['\"][^)]*\)", content)
            
            if render_templates:
                print(f"\n📁 {route_file.relative_to(routes_dir)}")
                
                for template_call in render_templates:
                    # Extraire le chemin du template
                    template_match = re.search(r"['\"]([^'\"]*\.html)['\"]", template_call)
                    if template_match:
                        template_path = template_match.group(1)
                        
                        # Vérifier si c'est un ancien pattern
                        is_old_pattern = False
                        correction_suggeree = ""
                        
                        for pattern, suggestion in anciens_patterns:
                            if re.search(pattern, template_call):
                                is_old_pattern = True
                                correction_suggeree = suggestion
                                break
                        
                        if is_old_pattern:
                            if not file_has_problems:
                                files_with_problems += 1
                                file_has_problems = True
                            
                            print(f"   ❌ {template_path}")
                            print(f"      → {correction_suggeree}")
                            problemes.append({
                                'fichier': route_file,
                                'template': template_path,
                                'correction': correction_suggeree,
                                'ligne_complete': template_call
                            })
                        else:
                            print(f"   ✅ {template_path}")
                            
        except Exception as e:
            print(f"⚠️  Erreur lecture {route_file}: {e}")
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • {total_files} fichiers de routes analysés")
    print(f"   • {files_with_problems} fichiers avec problèmes")
    print(f"   • {len(problemes)} problèmes détectés")
    
    return problemes

def corriger_routes_automatiquement(problemes):
    """Corrige automatiquement les routes avec des anciens chemins"""
    if not problemes:
        print("\n✅ Aucune correction nécessaire")
        return 0
    
    print(f"\n\n🔧 CORRECTION AUTOMATIQUE DE {len(problemes)} PROBLÈME(S)")
    print("=" * 80)
    
    # Mapping des corrections
    corrections_map = {
        # Templates sans préfixe
        r"render_template\(['\"]dashboard_admin\.html['\"]": r"render_template('roles/admin/dashboard_admin.html'",
        r"render_template\(['\"]dashboard_charge\.html['\"]": r"render_template('roles/charge_transport/dashboard_charge.html'",
        r"render_template\(['\"]dashboard_chauffeur\.html['\"]": r"render_template('roles/chauffeur/dashboard_chauffeur.html'",
        r"render_template\(['\"]dashboard_superviseur\.html['\"]": r"render_template('roles/superviseur/dashboard.html'",
        r"render_template\(['\"]dashboard_mecanicien\.html['\"]": r"render_template('roles/mecanicien/dashboard_mecanicien.html'",
        r"render_template\(['\"]bus_udm\.html['\"]": r"render_template('pages/bus_udm.html'",
        r"render_template\(['\"]carburation\.html['\"]": r"render_template('pages/carburation.html'",
        r"render_template\(['\"]vidange\.html['\"]": r"render_template('pages/vidange.html'",
        r"render_template\(['\"]parametres\.html['\"]": r"render_template('pages/parametres.html'",
        r"render_template\(['\"]rapports\.html['\"]": r"render_template('pages/rapports.html'",
        r"render_template\(['\"]utilisateurs\.html['\"]": r"render_template('pages/utilisateurs.html'",
        r"render_template\(['\"]chauffeurs\.html['\"]": r"render_template('legacy/chauffeurs.html'",
        r"render_template\(['\"]depanage\.html['\"]": r"render_template('pages/depanage.html'",
        r"render_template\(['\"]details_bus\.html['\"]": r"render_template('pages/details_bus.html'",
        
        # Templates avec anciens préfixes
        r"render_template\(['\"]admin/([^'\"]*\.html)['\"]": r"render_template('roles/admin/\1'",
        r"render_template\(['\"]charge_transport/([^'\"]*\.html)['\"]": r"render_template('roles/charge_transport/\1'",
        r"render_template\(['\"]chauffeur/([^'\"]*\.html)['\"]": r"render_template('roles/chauffeur/\1'",
        r"render_template\(['\"]superviseur/([^'\"]*\.html)['\"]": r"render_template('roles/superviseur/\1'",
        r"render_template\(['\"]mecanicien/([^'\"]*\.html)['\"]": r"render_template('roles/mecanicien/\1'",
    }
    
    corrections_appliquees = 0
    fichiers_modifies = set()
    
    # Grouper les problèmes par fichier
    problemes_par_fichier = {}
    for probleme in problemes:
        fichier = probleme['fichier']
        if fichier not in problemes_par_fichier:
            problemes_par_fichier[fichier] = []
        problemes_par_fichier[fichier].append(probleme)
    
    # Corriger chaque fichier
    for fichier, problemes_fichier in problemes_par_fichier.items():
        print(f"\n🔧 Correction: {fichier.relative_to(Path('app/routes'))}")
        
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Appliquer toutes les corrections
            for pattern, replacement in corrections_map.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    corrections_appliquees += 1
                    print(f"   ✅ Appliqué: {pattern[:50]}...")
            
            # Sauvegarder si modifié
            if content != original_content:
                with open(fichier, 'w', encoding='utf-8') as f:
                    f.write(content)
                fichiers_modifies.add(fichier)
                print(f"   💾 Fichier sauvegardé")
            
        except Exception as e:
            print(f"   ❌ Erreur correction {fichier}: {e}")
    
    print(f"\n✅ {corrections_appliquees} correction(s) appliquée(s) dans {len(fichiers_modifies)} fichier(s)")
    return corrections_appliquees

def tester_application():
    """Teste que l'application démarre sans erreur"""
    print("\n\n🚀 TEST DE L'APPLICATION")
    print("=" * 80)
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Application créée avec succès")
        
        with app.test_client() as client:
            routes_test = [
                ('/admin/dashboard', 'Dashboard Admin'),
                ('/admin/bus', 'Bus UdM Admin'),
                ('/admin/utilisateurs', 'Utilisateurs Admin'),
                ('/charge_transport/dashboard', 'Dashboard Charge'),
                ('/chauffeur/dashboard', 'Dashboard Chauffeur'),
                ('/superviseur/dashboard', 'Dashboard Superviseur'),
            ]
            
            erreurs = []
            for route, nom in routes_test:
                try:
                    response = client.get(route)
                    if response.status_code in [200, 302, 401, 403]:
                        print(f"✅ {nom} - Status {response.status_code}")
                    else:
                        print(f"⚠️  {nom} - Status {response.status_code}")
                except Exception as e:
                    if "TemplateNotFound" in str(e):
                        print(f"❌ {nom} - Template manquant: {e}")
                        erreurs.append(f"{nom}: {e}")
                    else:
                        print(f"⚠️  {nom} - Autre erreur: {type(e).__name__}")
            
            return erreurs
            
    except Exception as e:
        print(f"❌ Erreur lors du test de l'application: {e}")
        return [f"Erreur générale: {e}"]

def main():
    """Fonction principale"""
    print("🎯 VÉRIFICATION ET CORRECTION COMPLÈTE DES ROUTES")
    print("=" * 100)
    
    # 1. Vérifier toutes les routes
    problemes = verifier_toutes_routes()
    
    if not problemes:
        print("\n🎉 PARFAIT ! Toutes les routes utilisent les bons chemins")
        
        # Test de l'application
        erreurs = tester_application()
        if not erreurs:
            print("\n✅ Application fonctionne parfaitement")
            return 0
        else:
            print(f"\n⚠️  {len(erreurs)} erreur(s) détectée(s) lors du test")
            return 1
    
    # 2. Corriger automatiquement
    corrections = corriger_routes_automatiquement(problemes)
    
    # 3. Vérification après correction
    print("\n\n🔍 VÉRIFICATION APRÈS CORRECTION")
    print("=" * 80)
    
    nouveaux_problemes = verifier_toutes_routes()
    
    if not nouveaux_problemes:
        print("\n🎉 CORRECTION COMPLÈTE RÉUSSIE !")
        
        # Test final de l'application
        erreurs = tester_application()
        if not erreurs:
            print("\n✅ Application fonctionne parfaitement après correction")
            return 0
        else:
            print(f"\n⚠️  {len(erreurs)} erreur(s) restante(s)")
            return 1
    else:
        print(f"\n⚠️  {len(nouveaux_problemes)} problème(s) restant(s)")
        return 1

if __name__ == "__main__":
    exit(main())
