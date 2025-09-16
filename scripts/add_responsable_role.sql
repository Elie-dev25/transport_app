-- Script de migration pour ajouter le rôle RESPONSABLE
-- À exécuter sur la base de données MySQL

-- 1. Modifier l'énumération des rôles pour inclure RESPONSABLE
ALTER TABLE utilisateur 
MODIFY COLUMN role ENUM('ADMIN', 'CHAUFFEUR', 'MECANICIEN', 'CHARGE', 'SUPERVISEUR', 'RESPONSABLE') NULL;

-- 2. Vérifier que la modification a été appliquée
SELECT COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'utilisateur' 
AND COLUMN_NAME = 'role' 
AND TABLE_SCHEMA = DATABASE();

-- 3. Optionnel : Créer un utilisateur de test RESPONSABLE
-- (Décommentez les lignes suivantes si vous voulez créer un utilisateur de test)

/*
INSERT INTO utilisateur (nom, prenom, login, mot_de_passe, role, email, telephone)
VALUES (
    'Responsable',
    'Test',
    'responsable',
    -- Mot de passe hashé pour 'responsable123' (généré avec Werkzeug)
    'pbkdf2:sha256:600000$...',  -- Remplacez par le hash réel
    'RESPONSABLE',
    'responsable@udm.local',
    '000000000'
);
*/

-- 4. Vérifier les rôles existants
SELECT role, COUNT(*) as nombre_utilisateurs 
FROM utilisateur 
GROUP BY role;

COMMIT;
