-- Script de migration pour ajouter le rôle SUPERVISEUR
-- Date: 2025-09-06
-- Description: Ajoute le rôle SUPERVISEUR à l'énumération des rôles utilisateur

-- Sauvegarde de sécurité avant modification
-- IMPORTANT: Effectuer une sauvegarde complète avant d'exécuter ce script
-- mysqldump -u username -p database_name > backup_before_superviseur_role.sql

-- Étape 1: Vérifier l'état actuel de la table utilisateur
SELECT COLUMN_NAME, COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'utilisateur' 
AND COLUMN_NAME = 'role';

-- Étape 2: Modifier l'énumération pour ajouter SUPERVISEUR
-- Note: MySQL nécessite de redéfinir complètement l'ENUM
ALTER TABLE utilisateur 
MODIFY COLUMN role ENUM('ADMIN', 'CHAUFFEUR', 'MECANICIEN', 'CHARGE', 'SUPERVISEUR') NULL;

-- Étape 3: Vérifier que la modification a été appliquée
SELECT COLUMN_NAME, COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'utilisateur' 
AND COLUMN_NAME = 'role';

-- Étape 4: Créer un utilisateur superviseur de test (optionnel)
-- Décommentez les lignes suivantes si vous voulez créer un utilisateur de test

/*
INSERT INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES (
    'Superviseur',
    'Test',
    'superviseur.test',
    '$2b$12$LQv3c1yqBwEHxPuNYjHNTO.eMQZHYigqCzwc00OhS.MjnMJmOYaa2', -- mot de passe: 'password123'
    'SUPERVISEUR',
    'superviseur.test@udm.local',
    '123456789'
);
*/

-- Étape 5: Vérification finale
SELECT utilisateur_id, nom, prenom, login, role 
FROM utilisateur 
WHERE role = 'SUPERVISEUR';

-- Afficher un résumé des rôles
SELECT role, COUNT(*) as nombre_utilisateurs 
FROM utilisateur 
GROUP BY role 
ORDER BY role;

-- Script terminé avec succès
SELECT 'Migration du rôle SUPERVISEUR terminée avec succès!' as status;
