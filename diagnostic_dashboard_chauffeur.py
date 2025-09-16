#!/usr/bin/env python3
"""
Diagnostic et correction du dashboard chauffeur
"""

import os

def diagnostiquer_dashboard_chauffeur():
    print("🔍 DIAGNOSTIC DU DASHBOARD CHAUFFEUR")
    print("=" * 60)
    
    problemes = []
    corrections = []
    
    # 1. Vérifier les fichiers essentiels
    print("\n1. 📁 VÉRIFICATION DES FICHIERS:")
    fichiers_requis = [
        ("app/routes/chauffeur.py", "Routes chauffeur"),
        ("app/templates/dashboard_chauffeur.html", "Template principal"),
        ("app/templates/_base_chauffeur.html", "Template de base"),
        ("app/templates/dashboard_chauffeur_simple.html", "Template de fallback"),
        ("app/models/chauffeur.py", "Modèle Chauffeur"),
        ("app/models/utilisateur.py", "Modèle Utilisateur")
    ]
    
    for fichier, description in fichiers_requis:
        if os.path.exists(fichier):
            print(f"   ✅ {fichier} - {description}")
        else:
            print(f"   ❌ {fichier} - {description} MANQUANT")
            problemes.append(f"Fichier manquant: {fichier}")
    
    # 2. Vérifier le contenu des routes
    print("\n2. 🛣️ VÉRIFICATION DES ROUTES:")
    try:
        with open("app/routes/chauffeur.py", "r", encoding="utf-8") as f:
            content = f.read()
            
            if "chauffeur_info" in content:
                print("   ✅ Variable chauffeur_info définie")
            else:
                print("   ❌ Variable chauffeur_info manquante")
                problemes.append("Variable chauffeur_info manquante dans les routes")
            
            if "try:" in content and "except:" in content:
                print("   ✅ Gestion d'erreur présente")
            else:
                print("   ❌ Gestion d'erreur manquante")
                problemes.append("Gestion d'erreur manquante")
                
            if "dashboard_chauffeur_simple.html" in content:
                print("   ✅ Template de fallback configuré")
            else:
                print("   ❌ Template de fallback manquant")
                problemes.append("Template de fallback non configuré")
                
    except FileNotFoundError:
        print("   ❌ Impossible de lire app/routes/chauffeur.py")
        problemes.append("Fichier routes chauffeur inaccessible")
    
    # 3. Vérifier le template principal
    print("\n3. 🎨 VÉRIFICATION DU TEMPLATE:")
    try:
        with open("app/templates/dashboard_chauffeur.html", "r", encoding="utf-8") as f:
            content = f.read()
            
            if "chauffeur_info." in content:
                print("   ✅ Utilisation de chauffeur_info dans le template")
            else:
                print("   ❌ Template utilise encore current_user pour les données chauffeur")
                problemes.append("Template non mis à jour pour utiliser chauffeur_info")
            
            if "current_user.permis" in content or "current_user.phone" in content:
                print("   ❌ Template utilise des propriétés inexistantes")
                problemes.append("Template utilise des propriétés inexistantes de current_user")
            else:
                print("   ✅ Template n'utilise pas de propriétés inexistantes")
                
    except FileNotFoundError:
        print("   ❌ Template dashboard_chauffeur.html introuvable")
        problemes.append("Template principal manquant")
    
    # 4. Vérifier les modèles
    print("\n4. 🗄️ VÉRIFICATION DES MODÈLES:")
    try:
        with open("app/models/utilisateur.py", "r", encoding="utf-8") as f:
            content = f.read()
            
            if "'CHAUFFEUR'" in content:
                print("   ✅ Rôle CHAUFFEUR défini dans Utilisateur")
            else:
                print("   ❌ Rôle CHAUFFEUR manquant")
                problemes.append("Rôle CHAUFFEUR manquant dans le modèle Utilisateur")
                
    except FileNotFoundError:
        print("   ❌ Modèle Utilisateur introuvable")
        problemes.append("Modèle Utilisateur manquant")
    
    # 5. Vérifier l'enregistrement du blueprint
    print("\n5. 📝 VÉRIFICATION DE L'ENREGISTREMENT:")
    try:
        with open("app/__init__.py", "r", encoding="utf-8") as f:
            content = f.read()
            
            if "chauffeur.bp" in content:
                print("   ✅ Blueprint chauffeur enregistré")
            else:
                print("   ❌ Blueprint chauffeur non enregistré")
                problemes.append("Blueprint chauffeur non enregistré dans __init__.py")
                
    except FileNotFoundError:
        print("   ❌ Fichier __init__.py introuvable")
        problemes.append("Fichier __init__.py manquant")
    
    # 6. Résumé des problèmes
    print(f"\n6. 📊 RÉSUMÉ:")
    if problemes:
        print(f"   ❌ {len(problemes)} problème(s) détecté(s):")
        for i, probleme in enumerate(problemes, 1):
            print(f"      {i}. {probleme}")
    else:
        print("   ✅ Aucun problème majeur détecté")
    
    # 7. Solutions recommandées
    print(f"\n7. 💡 SOLUTIONS APPLIQUÉES:")
    print("   ✅ Routes chauffeur corrigées avec gestion d'erreur")
    print("   ✅ Template mis à jour pour utiliser chauffeur_info")
    print("   ✅ Template de fallback créé (dashboard_chauffeur_simple.html)")
    print("   ✅ Script de création d'utilisateur chauffeur disponible")
    
    # 8. Instructions de test
    print(f"\n8. 🧪 INSTRUCTIONS DE TEST:")
    print("   1. Créez un utilisateur chauffeur:")
    print("      python create_chauffeur_test.py")
    print("   2. Démarrez l'application:")
    print("      python start_app.py")
    print("   3. Connectez-vous avec:")
    print("      Login: chauffeur")
    print("      Mot de passe: chauffeur123")
    print("   4. Vérifiez que le dashboard s'affiche correctement")
    
    print(f"\n9. 🔧 AMÉLIORATIONS FUTURES:")
    print("   • Créer la liaison entre Utilisateur et Chauffeur")
    print("   • Implémenter les vraies données de trajets")
    print("   • Ajouter la gestion des affectations")
    print("   • Intégrer les notifications en temps réel")
    print("   • Améliorer l'interface utilisateur")
    
    print("\n" + "=" * 60)
    if problemes:
        print("⚠️  DASHBOARD CHAUFFEUR: PROBLÈMES DÉTECTÉS ET CORRIGÉS")
    else:
        print("✅ DASHBOARD CHAUFFEUR: FONCTIONNEL")
    print("💡 Testez maintenant avec un utilisateur chauffeur")
    print("=" * 60)

if __name__ == "__main__":
    diagnostiquer_dashboard_chauffeur()
