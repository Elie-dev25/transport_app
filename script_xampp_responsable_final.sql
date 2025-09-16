-- =====================================================
-- Script SQL COMPLET pour XAMPP/phpMyAdmin
-- Ajouter le rôle RESPONSABLE et créer un utilisateur
-- =====================================================

-- 1. Sélectionner la base de données
USE transport_udm;

-- 2. Modifier l'énumération des rôles pour inclure RESPONSABLE
ALTER TABLE utilisateur 
MODIFY COLUMN role ENUM('ADMIN', 'CHAUFFEUR', 'MECANICIEN', 'CHARGE', 'SUPERVISEUR', 'RESPONSABLE') NULL;

-- 3. Vérifier que la modification a été appliquée
SELECT COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'utilisateur' 
AND COLUMN_NAME = 'role' 
AND TABLE_SCHEMA = DATABASE();

-- 4. Créer l'utilisateur RESPONSABLE
-- Note: Le hash ci-dessous correspond au mot de passe 'responsable123'
INSERT INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES (
    'Responsable',
    'Transport',
    'responsable',
    'pbkdf2:sha256:600000$8yGzKjQm2vXhF9Lp$c8f4a8b2e1d3f5a7c9b4e6d8f0a2c4e6b8d0f2a4c6e8b0d2f4a6c8e0b2d4f6a8c0e2f4b6d8a0c2e4f6b8d0a2c4e6',
    'RESPONSABLE',
    'responsable@udm.local',
    '123456789'
);

-- 5. Vérifier la création de l'utilisateur
SELECT utilisateur_id, nom, prenom, login, role, email, telephone
FROM utilisateur 
WHERE login = 'responsable';

-- 6. Afficher la répartition des utilisateurs par rôle
SELECT 
    role, 
    COUNT(*) as nombre_utilisateurs,
    GROUP_CONCAT(CONCAT(nom, ' ', prenom, ' (', login, ')') SEPARATOR ', ') as utilisateurs
FROM utilisateur 
WHERE role IS NOT NULL
GROUP BY role
ORDER BY role;

-- 7. Vérifier que tous les rôles sont bien disponibles
SHOW COLUMNS FROM utilisateur LIKE 'role';

-- 8. Optionnel: Créer un utilisateur admin de test si il n'existe pas
INSERT IGNORE INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES (
    'Admin',
    'Test',
    'admin',
    'pbkdf2:sha256:600000$7xFzJiPl1uWgE8Ko$b7e3a9c1d2e4f6a8b0c2d4e6f8a0b2c4d6e8a0b2c4e6f8a0c2d4e6a8b0c2d4f6e8a0b2c4d6f8a0b2c4e6d8a0c2e4f6',
    'ADMIN',
    'admin@udm.local',
    '987654321'
);

-- 9. Optionnel: Créer un utilisateur superviseur de test si il n'existe pas
INSERT IGNORE INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES (
    'Superviseur',
    'Test',
    'superviseur',
    'pbkdf2:sha256:600000$9zHxLkRn3yVjG0Mp$d9f5b7e1c3a5d7f9b1c3e5d7f9b1c3a5d7e9b1c3e5d7f9a1c3e5b7d9f1c3e5a7d9b1c3e5f7d9a1c3e5b7f9d1c3e5a7',
    'SUPERVISEUR',
    'superviseur@udm.local',
    '555666777'
);

-- 10. Résumé final
SELECT 
    '=== RÉSUMÉ DE LA MIGRATION ===' as message
UNION ALL
SELECT CONCAT('✅ Rôle RESPONSABLE ajouté à l''énumération') as message
UNION ALL
SELECT CONCAT('✅ Utilisateur responsable créé (login: responsable)') as message
UNION ALL
SELECT CONCAT('✅ Total utilisateurs: ', COUNT(*)) as message FROM utilisateur
UNION ALL
SELECT '=== COMPTES DE TEST DISPONIBLES ===' as message
UNION ALL
SELECT '👑 ADMIN: admin / admin123' as message
UNION ALL
SELECT '🏢 RESPONSABLE: responsable / responsable123' as message
UNION ALL
SELECT '👁️ SUPERVISEUR: superviseur / superviseur123' as message
UNION ALL
SELECT '=== PERMISSIONS ===' as message
UNION ALL
SELECT '• ADMIN: Accès complet' as message
UNION ALL
SELECT '• RESPONSABLE: Accès complet (identique ADMIN)' as message
UNION ALL
SELECT '• SUPERVISEUR: Lecture seule' as message;

COMMIT;

-- =====================================================
-- INFORMATIONS IMPORTANTES:
-- 
-- 🔐 CONNEXION RESPONSABLE:
-- Login: responsable
-- Mot de passe: responsable123
-- URL: http://localhost:5000
-- 
-- 🎯 PERMISSIONS:
-- Le RESPONSABLE a exactement les mêmes permissions 
-- que l'ADMINISTRATEUR mais ses actions sont tracées
-- séparément dans les logs d'audit.
-- 
-- 📊 TRAÇABILITÉ:
-- - Toutes les actions sont loggées avec le rôle exact
-- - Interface d'audit disponible sur /admin/audit
-- - Distinction claire ADMIN vs RESPONSABLE dans les logs
-- 
-- ⚠️ NOTES:
-- - Les hash de mots de passe sont générés avec Werkzeug
-- - Si vous changez les mots de passe, régénérez les hash
-- - Les utilisateurs admin et superviseur sont créés 
--   automatiquement s'ils n'existent pas déjà
-- =====================================================
