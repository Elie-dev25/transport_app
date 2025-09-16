#!/usr/bin/env python3
"""
Vérification de la compatibilité entre les routes et les templates
après le refactoring - Phase finale
"""

import os
import re
from pathlib import Path

def extraire_routes_depuis_fichiers():
    """Extrait toutes les routes définies dans les fichiers de routes"""
    routes_definies = {}
    
    # Parcourir tous les fichiers de routes
    routes_dir = Path("app/routes")
    
    for route_file in routes_dir.rglob("*.py"):
        if route_file.name == "__init__.py":
            continue
            
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraire le blueprint
            blueprint_match = re.search(r"bp = Blueprint\(['\"]([^'\"]+)['\"]", content)
            if blueprint_match:
                blueprint_name = blueprint_match.group(1)
            else:
                # Déduire du chemin du fichier
                if "admin" in str(route_file):
                    blueprint_name = "admin"
                elif "charge_transport" in str(route_file):
                    blueprint_name = "charge_transport"
                elif "chauffeur" in str(route_file):
                    blueprint_name = "chauffeur"
                elif "superviseur" in str(route_file):
                    blueprint_name = "superviseur"
                elif "mecanicien" in str(route_file):
                    blueprint_name = "mecanicien"
                elif "auth" in str(route_file):
                    blueprint_name = "auth"
                else:
                    blueprint_name = "unknown"
            
            # Extraire toutes les routes @bp.route
            route_patterns = re.findall(r"@bp\.route\(['\"]([^'\"]+)['\"]", content)
            
            # Extraire les noms de fonctions
            function_patterns = re.findall(r"def ([a-zA-Z_][a-zA-Z0-9_]*)\(", content)
            
            # Associer routes et fonctions
            for i, route_pattern in enumerate(route_patterns):
                if i < len(function_patterns):
                    function_name = function_patterns[i]
                    full_route_name = f"{blueprint_name}.{function_name}"
                    routes_definies[full_route_name] = {
                        'blueprint': blueprint_name,
                        'function': function_name,
                        'pattern': route_pattern,
                        'file': str(route_file)
                    }
                    
        except Exception as e:
            print(f"Erreur lecture {route_file}: {e}")
    
    return routes_definies

def extraire_routes_depuis_templates():
    """Extrait toutes les routes utilisées dans les templates via url_for"""
    routes_utilisees = set()
    
    templates_dir = Path("app/templates")
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraire tous les url_for
            url_for_patterns = re.findall(r"url_for\(['\"]([^'\"]+)['\"]", content)
            
            for route in url_for_patterns:
                routes_utilisees.add(route)
                
        except Exception as e:
            print(f"Erreur lecture template {template_file}: {e}")
    
    return routes_utilisees

def verifier_compatibilite():
    """Vérifie la compatibilité entre routes définies et utilisées"""
    print("VERIFICATION COMPATIBILITE ROUTES <-> TEMPLATES")
    print("=" * 60)
    
    # Extraire les routes
    print("Extraction des routes definies...")
    routes_definies = extraire_routes_depuis_fichiers()
    print(f"   OK {len(routes_definies)} routes trouvees")

    print("\nExtraction des routes utilisees dans les templates...")
    routes_utilisees = extraire_routes_depuis_templates()
    print(f"   OK {len(routes_utilisees)} routes utilisees trouvees")

    # Vérification
    print("\nANALYSE DE COMPATIBILITE")
    print("-" * 40)
    
    routes_manquantes = []
    routes_orphelines = []
    routes_ok = []
    
    # Vérifier que toutes les routes utilisées existent
    for route_utilisee in routes_utilisees:
        if route_utilisee in routes_definies:
            routes_ok.append(route_utilisee)
        else:
            routes_manquantes.append(route_utilisee)
    
    # Identifier les routes définies mais non utilisées
    for route_definie in routes_definies:
        if route_definie not in routes_utilisees:
            routes_orphelines.append(route_definie)
    
    # Affichage des résultats
    print(f"\nROUTES COMPATIBLES: {len(routes_ok)}")
    for route in sorted(routes_ok):
        print(f"   OK {route}")

    if routes_manquantes:
        print(f"\nROUTES MANQUANTES: {len(routes_manquantes)}")
        for route in sorted(routes_manquantes):
            print(f"   ERREUR {route} - Utilisee dans template mais non definie")

    if routes_orphelines:
        print(f"\nROUTES ORPHELINES: {len(routes_orphelines)}")
        for route in sorted(routes_orphelines):
            print(f"   ATTENTION {route} - Definie mais non utilisee")
    
    # Résumé
    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)

    total_routes_utilisees = len(routes_utilisees)
    routes_compatibles = len(routes_ok)
    taux_compatibilite = (routes_compatibles / total_routes_utilisees * 100) if total_routes_utilisees > 0 else 0

    print(f"Routes utilisees dans templates: {total_routes_utilisees}")
    print(f"Routes compatibles: {routes_compatibles}")
    print(f"Routes manquantes: {len(routes_manquantes)}")
    print(f"Taux de compatibilite: {taux_compatibilite:.1f}%")

    if len(routes_manquantes) == 0:
        print("\nTOUTES LES ROUTES SONT COMPATIBLES!")
        print("Les templates utilisent uniquement des routes existantes.")
        return True
    else:
        print(f"\n{len(routes_manquantes)} route(s) manquante(s) detectee(s).")
        print("Veuillez creer ces routes ou corriger les templates.")
        return False

def afficher_routes_par_blueprint():
    """Affiche les routes organisées par blueprint"""
    print("\nROUTES PAR BLUEPRINT")
    print("=" * 40)
    
    routes_definies = extraire_routes_depuis_fichiers()
    
    # Organiser par blueprint
    blueprints = {}
    for route_name, route_info in routes_definies.items():
        blueprint = route_info['blueprint']
        if blueprint not in blueprints:
            blueprints[blueprint] = []
        blueprints[blueprint].append(route_info)
    
    # Afficher
    for blueprint_name, routes in sorted(blueprints.items()):
        print(f"\n{blueprint_name.upper()}")
        for route in sorted(routes, key=lambda x: x['function']):
            print(f"   OK {route['function']} -> {route['pattern']}")

if __name__ == "__main__":
    try:
        # Vérification principale
        compatibilite_ok = verifier_compatibilite()
        
        # Affichage détaillé
        afficher_routes_par_blueprint()
        
        # Conclusion
        print("\n" + "=" * 60)
        if compatibilite_ok:
            print("VERIFICATION TERMINEE - SUCCES COMPLET")
            print("Toutes les routes des templates sont compatibles avec le backend refactorise!")
        else:
            print("VERIFICATION TERMINEE - CORRECTIONS NECESSAIRES")
            print("Certaines routes doivent etre creees ou corrigees.")

    except Exception as e:
        print(f"\nERREUR GENERALE: {e}")
        import traceback
        traceback.print_exc()
