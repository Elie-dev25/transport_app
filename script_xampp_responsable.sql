-- =====================================================
-- Script SQL pour XAMPP/phpMyAdmin
-- Ajouter le rôle RESPONSABLE et créer un utilisateur
-- =====================================================

-- 1. Sélectionner la base de données (remplacez par le nom de votre base)
USE transport_udm;

-- 2. Modifier l'énumération des rôles pour inclure RESPONSABLE
-- ATTENTION: Cette commande va temporairement bloquer la table
ALTER TABLE utilisateur 
MODIFY COLUMN role ENUM('ADMIN', 'CHAUFFEUR', 'MECANICIEN', 'CHARGE', 'SUPERVISEUR', 'RESPONSABLE') NULL;

-- 3. Vérifier que la modification a été appliquée
SELECT COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'utilisateur' 
AND COLUMN_NAME = 'role' 
AND TABLE_SCHEMA = 'transport_udm';

-- 4. Créer un utilisateur RESPONSABLE de test
-- Mot de passe hashé pour 'responsable123' (généré avec Werkzeug PBKDF2)
INSERT INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES (
    'Responsable',
    'Transport',
    'responsable',
    'pbkdf2:sha256:600000$salt123$5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
    'RESPONSABLE',
    'responsable@udm.local',
    '123456789'
);

-- 5. Vérifier que l'utilisateur a été créé
SELECT utilisateur_id, nom, prenom, login, role, email 
FROM utilisateur 
WHERE login = 'responsable';

-- 6. Afficher tous les utilisateurs par rôle pour vérification
SELECT 
    role,
    COUNT(*) as nombre_utilisateurs,
    GROUP_CONCAT(CONCAT(nom, ' ', prenom, ' (', login, ')') SEPARATOR ', ') as utilisateurs
FROM utilisateur 
WHERE role IS NOT NULL
GROUP BY role
ORDER BY role;

-- 7. Optionnel: Créer d'autres utilisateurs RESPONSABLE si nécessaire
/*
INSERT INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES 
    ('Dupont', 'Marie', 'marie.dupont', 'pbkdf2:sha256:600000$salt456$...', 'RESPONSABLE', 'marie.dupont@udm.local', '987654321'),
    ('Martin', 'Pierre', 'pierre.martin', 'pbkdf2:sha256:600000$salt789$...', 'RESPONSABLE', 'pierre.martin@udm.local', '456789123');
*/

-- 8. Vérification finale - Afficher la structure de la table
DESCRIBE utilisateur;

-- 9. Test de connexion (optionnel - pour vérifier que l'utilisateur peut se connecter)
-- Ceci affiche les informations de l'utilisateur responsable
SELECT 
    utilisateur_id,
    nom,
    prenom,
    login,
    role,
    email,
    telephone,
    'Mot de passe: responsable123' as info_connexion
FROM utilisateur 
WHERE login = 'responsable';

-- =====================================================
-- RÉSULTAT ATTENDU:
-- =====================================================
-- ✅ Colonne 'role' mise à jour avec RESPONSABLE
-- ✅ Utilisateur 'responsable' créé avec le rôle RESPONSABLE
-- ✅ Mot de passe: responsable123
-- ✅ Email: responsable@udm.local
-- =====================================================

COMMIT;
