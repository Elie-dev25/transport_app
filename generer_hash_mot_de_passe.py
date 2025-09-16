#!/usr/bin/env python3
"""
Script pour générer le hash du mot de passe pour l'utilisateur RESPONSABLE
"""

from werkzeug.security import generate_password_hash

# Générer le hash pour le mot de passe 'responsable123'
password = 'responsable123'
password_hash = generate_password_hash(password)

print("=" * 60)
print("🔐 GÉNÉRATION DU HASH MOT DE PASSE")
print("=" * 60)
print(f"Mot de passe en clair: {password}")
print(f"Hash généré: {password_hash}")
print("=" * 60)

# Créer le script SQL avec le vrai hash
sql_script = f"""-- =====================================================
-- Script SQL FINAL pour XAMPP/phpMyAdmin
-- Ajouter le rôle RESPONSABLE et créer un utilisateur
-- =====================================================

-- 1. Sélectionner la base de données
USE transport_udm;

-- 2. Modifier l'énumération des rôles
ALTER TABLE utilisateur 
MODIFY COLUMN role ENUM('ADMIN', 'CHAUFFEUR', 'MECANICIEN', 'CHARGE', 'SUPERVISEUR', 'RESPONSABLE') NULL;

-- 3. Créer l'utilisateur RESPONSABLE avec le hash correct
INSERT INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES (
    'Responsable',
    'Transport',
    'responsable',
    '{password_hash}',
    'RESPONSABLE',
    'responsable@udm.local',
    '123456789'
);

-- 4. Vérifier la création
SELECT utilisateur_id, nom, prenom, login, role, email 
FROM utilisateur 
WHERE login = 'responsable';

-- 5. Afficher tous les rôles
SELECT role, COUNT(*) as nombre
FROM utilisateur 
WHERE role IS NOT NULL
GROUP BY role;

COMMIT;

-- =====================================================
-- INFORMATIONS DE CONNEXION:
-- Login: responsable
-- Mot de passe: responsable123
-- Rôle: RESPONSABLE (mêmes permissions que ADMIN)
-- =====================================================
"""

# Sauvegarder le script SQL final
with open('script_final_xampp_responsable.sql', 'w', encoding='utf-8') as f:
    f.write(sql_script)

print("✅ Script SQL final généré: script_final_xampp_responsable.sql")
print("\n📋 INSTRUCTIONS XAMPP:")
print("1. Ouvrez phpMyAdmin (http://localhost/phpmyadmin)")
print("2. Sélectionnez votre base de données 'transport_udm'")
print("3. Allez dans l'onglet 'SQL'")
print("4. Copiez-collez le contenu du fichier 'script_final_xampp_responsable.sql'")
print("5. Cliquez sur 'Exécuter'")
print("\n🔐 CONNEXION:")
print("Login: responsable")
print("Mot de passe: responsable123")
print("URL: http://localhost:5000")
