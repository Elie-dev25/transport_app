-- Script de migration MySQL : AED vers Bus UdM
-- Ce script renomme toutes les tables et colonnes de AED vers Bus UdM
-- Date de création : 2025-09-02

-- ATTENTION: Effectuez une sauvegarde complète de votre base de données avant d'exécuter ce script !

-- ========================================
-- ÉTAPE 1: RENOMMER LES TABLES
-- ========================================

-- 1.1 Renommer la table principale aed vers bus_udm
RENAME TABLE aed TO bus_udm;

-- 1.2 Renommer la table document_aed vers document_bus_udm
RENAME TABLE document_aed TO document_bus_udm;

-- 1.3 Renommer la table panne_aed vers panne_bus_udm
RENAME TABLE panne_aed TO panne_bus_udm;

-- ========================================
-- ÉTAPE 2: METTRE À JOUR LES CLÉS ÉTRANGÈRES
-- ========================================

-- 2.1 Mettre à jour les contraintes de clés étrangères dans document_bus_udm
ALTER TABLE document_bus_udm 
DROP FOREIGN KEY document_bus_udm_ibfk_1;

ALTER TABLE document_bus_udm 
CHANGE COLUMN numero_aed numero_bus_udm VARCHAR(50) NOT NULL;

ALTER TABLE document_bus_udm 
ADD CONSTRAINT document_bus_udm_ibfk_1 
FOREIGN KEY (numero_bus_udm) REFERENCES bus_udm(numero);

-- 2.2 Mettre à jour les contraintes de clés étrangères dans panne_bus_udm
ALTER TABLE panne_bus_udm 
DROP FOREIGN KEY panne_bus_udm_ibfk_1;

ALTER TABLE panne_bus_udm 
CHANGE COLUMN aed_id bus_udm_id INT NULL;

ALTER TABLE panne_bus_udm 
CHANGE COLUMN numero_aed numero_bus_udm VARCHAR(50) NOT NULL;

ALTER TABLE panne_bus_udm 
ADD CONSTRAINT panne_bus_udm_ibfk_1 
FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id);

-- ========================================
-- ÉTAPE 3: METTRE À JOUR LES RÉFÉRENCES DANS LA TABLE TRAJET
-- ========================================

-- 3.1 Mettre à jour la clé étrangère dans la table trajet
ALTER TABLE trajet 
DROP FOREIGN KEY trajet_ibfk_1;

ALTER TABLE trajet 
CHANGE COLUMN numero_aed numero_bus_udm VARCHAR(50) NULL;

ALTER TABLE trajet
ADD CONSTRAINT trajet_ibfk_1
FOREIGN KEY (numero_bus_udm) REFERENCES bus_udm(numero);

-- 3.2 Mettre à jour la table fuel_alert_state
ALTER TABLE fuel_alert_state
DROP FOREIGN KEY fuel_alert_state_ibfk_1;

ALTER TABLE fuel_alert_state
CHANGE COLUMN aed_id bus_udm_id INT NOT NULL;

ALTER TABLE fuel_alert_state
ADD CONSTRAINT fuel_alert_state_ibfk_1
FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id);

-- 3.3 Mettre à jour la table vidange
ALTER TABLE vidange
DROP FOREIGN KEY vidange_ibfk_1;

ALTER TABLE vidange
CHANGE COLUMN aed_id bus_udm_id INT NOT NULL;

ALTER TABLE vidange
ADD CONSTRAINT vidange_ibfk_1
FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id);

-- 3.4 Mettre à jour la table carburation
ALTER TABLE carburation
DROP FOREIGN KEY carburation_ibfk_1;

ALTER TABLE carburation
CHANGE COLUMN aed_id bus_udm_id INT NOT NULL;

ALTER TABLE carburation
ADD CONSTRAINT carburation_ibfk_1
FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id);

-- ========================================
-- ÉTAPE 4: RENOMMER LES INDEX
-- ========================================

-- 4.1 Renommer les index dans bus_udm
ALTER TABLE bus_udm 
DROP INDEX idx_aed_numero_chassis,
DROP INDEX idx_aed_marque,
DROP INDEX idx_aed_type_vehicule;

CREATE INDEX idx_bus_udm_numero_chassis ON bus_udm(numero_chassis);
CREATE INDEX idx_bus_udm_marque ON bus_udm(marque);
CREATE INDEX idx_bus_udm_type_vehicule ON bus_udm(type_vehicule);

-- ========================================
-- ÉTAPE 5: METTRE À JOUR LES COMMENTAIRES
-- ========================================

-- 5.1 Mettre à jour les commentaires des colonnes
ALTER TABLE bus_udm 
MODIFY COLUMN numero VARCHAR(50) NOT NULL COMMENT 'Numéro Bus UdM unique du véhicule',
MODIFY COLUMN numero_chassis VARCHAR(100) NULL COMMENT 'Numéro de châssis du véhicule (unique)',
MODIFY COLUMN modele VARCHAR(100) NULL COMMENT 'Modèle du véhicule (ex: Sprinter 515, Hiace, etc.)',
MODIFY COLUMN marque VARCHAR(50) NULL COMMENT 'Marque du véhicule (ex: Mercedes, Toyota, etc.)';

-- ========================================
-- ÉTAPE 6: VÉRIFICATIONS POST-MIGRATION
-- ========================================

-- 6.1 Vérifier la structure des tables renommées
DESCRIBE bus_udm;
DESCRIBE document_bus_udm;
DESCRIBE panne_bus_udm;

-- 6.2 Vérifier les données
SELECT COUNT(*) as total_bus_udm FROM bus_udm;
SELECT COUNT(*) as total_documents FROM document_bus_udm;
SELECT COUNT(*) as total_pannes FROM panne_bus_udm;

-- 6.3 Vérifier les clés étrangères
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE REFERENCED_TABLE_NAME IN ('bus_udm') 
   OR TABLE_NAME IN ('bus_udm', 'document_bus_udm', 'panne_bus_udm');

-- 6.4 Vérifier les index
SHOW INDEX FROM bus_udm WHERE Key_name LIKE 'idx_bus_udm%';

-- ========================================
-- ÉTAPE 7: NETTOYAGE (OPTIONNEL)
-- ========================================

-- Si tout fonctionne correctement, vous pouvez supprimer les anciens fichiers de sauvegarde
-- et mettre à jour votre application pour utiliser les nouveaux noms de tables

-- ========================================
-- NOTES IMPORTANTES
-- ========================================

/*
APRÈS CETTE MIGRATION, VOUS DEVEZ :

1. Mettre à jour votre application Python pour utiliser les nouveaux modèles :
   - BusUdM au lieu de AED
   - DocumentBusUdM au lieu de DocumentAED  
   - PanneBusUdM au lieu de PanneAED

2. Mettre à jour toutes les requêtes SQL dans votre code

3. Mettre à jour les templates HTML

4. Tester toutes les fonctionnalités

5. Mettre à jour la documentation

ROLLBACK EN CAS DE PROBLÈME :
Si vous devez annuler cette migration, exécutez les commandes inverses :
- RENAME TABLE bus_udm TO aed;
- RENAME TABLE document_bus_udm TO document_aed;
- RENAME TABLE panne_bus_udm TO panne_aed;
- Puis restaurez les clés étrangères et index originaux
*/
