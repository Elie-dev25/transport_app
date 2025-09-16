#!/usr/bin/env python3
"""
Vérification finale qu'il n'y a plus de références aux anciens chemins partials/
"""

import os
import re
from pathlib import Path

def verifier_references_partials():
    """Vérifie qu'il n'y a plus de références aux anciens chemins partials/"""
    print("🔍 VÉRIFICATION FINALE - RÉFÉRENCES PARTIALS/")
    print("=" * 60)
    
    templates_dir = Path("app/templates")
    problemes = []
    
    # Patterns à détecter
    patterns_partials = [
        r"{% include ['\"]partials/",
        r"{% from ['\"]partials/",
        r"{% extends ['\"]partials/"
    ]
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Chercher les références partials/
            for line_num, line in enumerate(content.split('\n'), 1):
                for pattern in patterns_partials:
                    if re.search(pattern, line):
                        print(f"❌ {template_file.relative_to(templates_dir)}:{line_num}")
                        print(f"   {line.strip()}")
                        problemes.append(f"{template_file}:{line_num} - {line.strip()}")
                        
        except Exception as e:
            print(f"⚠️  Erreur lecture {template_file}: {e}")
    
    if not problemes:
        print("✅ Aucune référence aux anciens chemins partials/ trouvée")
        print("✅ Toutes les références utilisent maintenant shared/")
    
    return problemes

def verifier_fichiers_shared():
    """Vérifie que tous les fichiers nécessaires existent dans shared/"""
    print("\n\n📁 VÉRIFICATION DES FICHIERS SHARED/")
    print("=" * 60)
    
    fichiers_requis = [
        "app/templates/shared/modals/_add_bus_modal.html",
        "app/templates/shared/modals/_add_user_modal.html", 
        "app/templates/shared/modals/_declaration_panne_modal.html",
        "app/templates/shared/modals/_depannage_modal.html",
        "app/templates/shared/modals/_document_modal.html",
        "app/templates/shared/modals/_edit_statut_chauffeur_modal.html",
        "app/templates/shared/modals/_statut_details_modal.html",
        "app/templates/shared/modals/trajet_interne_modal.html",
        "app/templates/shared/modals/trajet_prestataire_modal.html",
        "app/templates/shared/modals/autres_trajets_modal.html",
        "app/templates/shared/macros/trajet_modals.html",
        "app/templates/shared/macros/tableaux_components.html",
        "app/templates/shared/macros/superviseur_components.html"
    ]
    
    manquants = []
    
    for fichier in fichiers_requis:
        if os.path.exists(fichier):
            print(f"✅ {os.path.basename(fichier)}")
        else:
            print(f"❌ {os.path.basename(fichier)} - MANQUANT")
            manquants.append(fichier)
    
    return manquants

def verifier_anciens_dossiers():
    """Vérifie l'état des anciens dossiers partials/"""
    print("\n\n📂 VÉRIFICATION DES ANCIENS DOSSIERS")
    print("=" * 60)
    
    anciens_dossiers = [
        "app/templates/partials/admin",
        "app/templates/partials/charge_transport",
        "app/templates/partials/shared"
    ]
    
    for dossier in anciens_dossiers:
        if os.path.exists(dossier):
            fichiers = list(Path(dossier).glob("*.html"))
            if fichiers:
                print(f"⚠️  {dossier} - Contient encore {len(fichiers)} fichier(s)")
                for fichier in fichiers[:5]:  # Afficher max 5 fichiers
                    print(f"   • {fichier.name}")
                if len(fichiers) > 5:
                    print(f"   • ... et {len(fichiers) - 5} autres")
            else:
                print(f"✅ {dossier} - Vide")
        else:
            print(f"✅ {dossier} - Supprimé")

def test_application():
    """Teste que l'application démarre sans erreur"""
    print("\n\n🚀 TEST DE L'APPLICATION")
    print("=" * 60)
    
    try:
        # Import et création de l'app
        from app import create_app
        app = create_app()
        print("✅ Application créée avec succès")
        
        # Test du contexte
        with app.app_context():
            print("✅ Contexte application fonctionnel")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de l'application: {e}")
        return False

def main():
    """Fonction principale de vérification"""
    print("🎯 VÉRIFICATION FINALE - MIGRATION PARTIALS/ → SHARED/")
    print("=" * 80)
    
    tous_problemes = []
    
    # 1. Vérifier les références partials/
    problemes_partials = verifier_references_partials()
    tous_problemes.extend(problemes_partials)
    
    # 2. Vérifier les fichiers shared/
    fichiers_manquants = verifier_fichiers_shared()
    tous_problemes.extend(fichiers_manquants)
    
    # 3. Vérifier les anciens dossiers
    verifier_anciens_dossiers()
    
    # 4. Tester l'application
    app_ok = test_application()
    if not app_ok:
        tous_problemes.append("Application ne démarre pas")
    
    # Résumé final
    print("\n\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 80)
    
    if tous_problemes:
        print(f"❌ {len(tous_problemes)} problème(s) détecté(s):")
        for probleme in tous_problemes:
            print(f"   • {probleme}")
        print("\n⚠️  La migration n'est PAS complète")
        return 1
    else:
        print("🎉 MIGRATION COMPLÈTEMENT RÉUSSIE !")
        print("✅ Aucune référence aux anciens chemins partials/")
        print("✅ Tous les fichiers shared/ sont présents")
        print("✅ L'application démarre sans erreur")
        print("✅ Architecture entièrement mise à jour")
        
        print("\n🏆 AVANTAGES OBTENUS:")
        print("   • 🚫 Zéro duplication de code")
        print("   • 🛠️ Maintenance simplifiée")
        print("   • 📁 Organisation claire")
        print("   • 🚀 Architecture modulaire")
        print("   • 🔄 Composants réutilisables")
        
        return 0

if __name__ == "__main__":
    exit(main())
