-- Script de migration MySQL : Mise à jour des colonnes pour Bus UdM
-- Ce script met à jour uniquement les colonnes et clés étrangères
-- Date de création : 2025-09-03
-- 
-- ATTENTION: Effectuez une sauvegarde complète de votre base de données avant d'exécuter ce script !

-- ========================================
-- ÉTAPE 1: VÉRIFICATION DE L'ÉTAT ACTUEL
-- ========================================

-- Vérifier que la table bus_udm existe
SELECT 'Table bus_udm existe' AS verification, COUNT(*) AS nombre_bus FROM bus_udm;

-- ========================================
-- ÉTAPE 2: METTRE À JOUR LA TABLE TRAJET
-- ========================================

-- 2.1 Supprimer la contrainte de clé étrangère existante (si elle existe)
SET @sql = (SELECT CONCAT('ALTER TABLE trajet DROP FOREIGN KEY ', CONSTRAINT_NAME)
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'trajet' 
            AND COLUMN_NAME = 'numero_aed' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
            LIMIT 1);

SET @sql = IFNULL(@sql, 'SELECT "Aucune contrainte FK à supprimer pour numero_aed"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.2 Renommer la colonne numero_aed vers numero_bus_udm
ALTER TABLE trajet 
CHANGE COLUMN numero_aed numero_bus_udm VARCHAR(50) NULL;

-- 2.3 Ajouter la nouvelle contrainte de clé étrangère
ALTER TABLE trajet 
ADD CONSTRAINT fk_trajet_bus_udm 
FOREIGN KEY (numero_bus_udm) REFERENCES bus_udm(numero);

-- ========================================
-- ÉTAPE 3: METTRE À JOUR LA TABLE FUEL_ALERT_STATE
-- ========================================

-- 3.1 Supprimer la contrainte de clé étrangère existante (si elle existe)
SET @sql = (SELECT CONCAT('ALTER TABLE fuel_alert_state DROP FOREIGN KEY ', CONSTRAINT_NAME)
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'fuel_alert_state' 
            AND COLUMN_NAME = 'aed_id' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
            LIMIT 1);

SET @sql = IFNULL(@sql, 'SELECT "Aucune contrainte FK à supprimer pour aed_id"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3.2 Renommer la colonne aed_id vers bus_udm_id
ALTER TABLE fuel_alert_state 
CHANGE COLUMN aed_id bus_udm_id INT NOT NULL;

-- 3.3 Ajouter la nouvelle contrainte de clé étrangère
ALTER TABLE fuel_alert_state 
ADD CONSTRAINT fk_fuel_alert_state_bus_udm 
FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id);

-- ========================================
-- ÉTAPE 4: METTRE À JOUR LA TABLE VIDANGE
-- ========================================

-- 4.1 Supprimer la contrainte de clé étrangère existante (si elle existe)
SET @sql = (SELECT CONCAT('ALTER TABLE vidange DROP FOREIGN KEY ', CONSTRAINT_NAME)
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'vidange' 
            AND COLUMN_NAME = 'aed_id' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
            LIMIT 1);

SET @sql = IFNULL(@sql, 'SELECT "Aucune contrainte FK à supprimer pour aed_id"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4.2 Renommer la colonne aed_id vers bus_udm_id
ALTER TABLE vidange 
CHANGE COLUMN aed_id bus_udm_id INT NOT NULL;

-- 4.3 Ajouter la nouvelle contrainte de clé étrangère
ALTER TABLE vidange 
ADD CONSTRAINT fk_vidange_bus_udm 
FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id);

-- ========================================
-- ÉTAPE 5: METTRE À JOUR LA TABLE CARBURATION
-- ========================================

-- 5.1 Supprimer la contrainte de clé étrangère existante (si elle existe)
SET @sql = (SELECT CONCAT('ALTER TABLE carburation DROP FOREIGN KEY ', CONSTRAINT_NAME)
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'carburation' 
            AND COLUMN_NAME = 'aed_id' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
            LIMIT 1);

SET @sql = IFNULL(@sql, 'SELECT "Aucune contrainte FK à supprimer pour aed_id"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 5.2 Renommer la colonne aed_id vers bus_udm_id
ALTER TABLE carburation 
CHANGE COLUMN aed_id bus_udm_id INT NOT NULL;

-- 5.3 Ajouter la nouvelle contrainte de clé étrangère
ALTER TABLE carburation 
ADD CONSTRAINT fk_carburation_bus_udm 
FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id);

-- ========================================
-- ÉTAPE 6: METTRE À JOUR LES TABLES DOCUMENT ET PANNE (SI ELLES EXISTENT)
-- ========================================

-- 6.1 Vérifier et mettre à jour document_bus_udm (si elle existe)
SET @table_exists = (SELECT COUNT(*) FROM information_schema.TABLES 
                     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'document_bus_udm');

-- Si la table document_bus_udm existe, mettre à jour la colonne
SET @sql = IF(@table_exists > 0, 
              'ALTER TABLE document_bus_udm CHANGE COLUMN numero_aed numero_bus_udm VARCHAR(50) NOT NULL',
              'SELECT "Table document_bus_udm n\'existe pas"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 6.2 Vérifier et mettre à jour panne_bus_udm (si elle existe)
SET @table_exists = (SELECT COUNT(*) FROM information_schema.TABLES 
                     WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'panne_bus_udm');

-- Si la table panne_bus_udm existe, mettre à jour les colonnes
SET @sql = IF(@table_exists > 0, 
              'ALTER TABLE panne_bus_udm CHANGE COLUMN aed_id bus_udm_id INT NULL, CHANGE COLUMN numero_aed numero_bus_udm VARCHAR(50) NOT NULL',
              'SELECT "Table panne_bus_udm n\'existe pas"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ========================================
-- ÉTAPE 7: VÉRIFICATIONS POST-MIGRATION
-- ========================================

-- 7.1 Vérifier la structure de la table trajet
DESCRIBE trajet;

-- 7.2 Vérifier la structure de la table fuel_alert_state
DESCRIBE fuel_alert_state;

-- 7.3 Vérifier la structure de la table vidange
DESCRIBE vidange;

-- 7.4 Vérifier la structure de la table carburation
DESCRIBE carburation;

-- 7.5 Vérifier les contraintes de clés étrangères
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = DATABASE() 
AND REFERENCED_TABLE_NAME = 'bus_udm'
ORDER BY TABLE_NAME, COLUMN_NAME;

-- 7.6 Compter les enregistrements dans chaque table
SELECT 'bus_udm' AS table_name, COUNT(*) AS nombre_enregistrements FROM bus_udm
UNION ALL
SELECT 'trajet' AS table_name, COUNT(*) AS nombre_enregistrements FROM trajet
UNION ALL
SELECT 'fuel_alert_state' AS table_name, COUNT(*) AS nombre_enregistrements FROM fuel_alert_state
UNION ALL
SELECT 'vidange' AS table_name, COUNT(*) AS nombre_enregistrements FROM vidange
UNION ALL
SELECT 'carburation' AS table_name, COUNT(*) AS nombre_enregistrements FROM carburation;

-- ========================================
-- MIGRATION TERMINÉE
-- ========================================

SELECT 'MIGRATION TERMINÉE AVEC SUCCÈS !' AS statut, NOW() AS date_fin;
