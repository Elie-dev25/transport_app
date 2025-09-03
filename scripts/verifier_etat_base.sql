-- Script de vérification de l'état actuel de la base de données
-- Date: 2025-09-03

SELECT 'VÉRIFICATION DE L\'ÉTAT ACTUEL DE LA BASE DE DONNÉES' AS titre;

-- ========================================
-- 1. VÉRIFIER LES TABLES EXISTANTES
-- ========================================

SELECT 'TABLES EXISTANTES:' AS section;
SELECT TABLE_NAME as 'Tables dans la base' 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME IN ('bus_udm', 'aed', 'trajet', 'fuel_alert_state', 'vidange', 'carburation', 'document_bus_udm', 'panne_bus_udm')
ORDER BY TABLE_NAME;

-- ========================================
-- 2. VÉRIFIER LA STRUCTURE DE LA TABLE TRAJET
-- ========================================

SELECT 'STRUCTURE DE LA TABLE TRAJET:' AS section;
DESCRIBE trajet;

-- ========================================
-- 3. VÉRIFIER LA STRUCTURE DE LA TABLE BUS_UDM
-- ========================================

SELECT 'STRUCTURE DE LA TABLE BUS_UDM:' AS section;
DESCRIBE bus_udm;

-- ========================================
-- 4. VÉRIFIER LA STRUCTURE DE LA TABLE FUEL_ALERT_STATE
-- ========================================

SELECT 'STRUCTURE DE LA TABLE FUEL_ALERT_STATE:' AS section;
DESCRIBE fuel_alert_state;

-- ========================================
-- 5. VÉRIFIER LA STRUCTURE DE LA TABLE VIDANGE
-- ========================================

SELECT 'STRUCTURE DE LA TABLE VIDANGE:' AS section;
DESCRIBE vidange;

-- ========================================
-- 6. VÉRIFIER LA STRUCTURE DE LA TABLE CARBURATION
-- ========================================

SELECT 'STRUCTURE DE LA TABLE CARBURATION:' AS section;
DESCRIBE carburation;

-- ========================================
-- 7. VÉRIFIER LES CLÉS ÉTRANGÈRES
-- ========================================

SELECT 'CLÉS ÉTRANGÈRES VERS BUS_UDM:' AS section;
SELECT 
    TABLE_NAME as 'Table',
    COLUMN_NAME as 'Colonne',
    CONSTRAINT_NAME as 'Contrainte',
    REFERENCED_TABLE_NAME as 'Table_Référencée',
    REFERENCED_COLUMN_NAME as 'Colonne_Référencée'
FROM information_schema.KEY_COLUMN_USAGE 
WHERE TABLE_SCHEMA = DATABASE() 
AND REFERENCED_TABLE_NAME = 'bus_udm'
ORDER BY TABLE_NAME, COLUMN_NAME;

-- ========================================
-- 8. COMPTER LES ENREGISTREMENTS
-- ========================================

SELECT 'NOMBRE D\'ENREGISTREMENTS:' AS section;
SELECT 'bus_udm' AS table_name, COUNT(*) AS nombre FROM bus_udm
UNION ALL
SELECT 'trajet' AS table_name, COUNT(*) AS nombre FROM trajet
UNION ALL
SELECT 'fuel_alert_state' AS table_name, COUNT(*) AS nombre FROM fuel_alert_state
UNION ALL
SELECT 'vidange' AS table_name, COUNT(*) AS nombre FROM vidange
UNION ALL
SELECT 'carburation' AS table_name, COUNT(*) AS nombre FROM carburation;

SELECT 'VÉRIFICATION TERMINÉE' AS statut;
