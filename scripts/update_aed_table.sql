-- Script de mise à jour de la table AED pour MySQL
-- Ajout des nouveaux champs : numero_chassis, modele, type_vehicule, marque
-- Date de mise à jour : 2025-09-02

-- IMPORTANT: Vérifiez d'abord si les colonnes existent déjà
-- Si elles existent, ces commandes ALTER TABLE généreront des erreurs que vous pouvez ignorer

-- 1. Ajout des nouvelles colonnes à la table aed (syntaxe MySQL)
ALTER TABLE aed
ADD COLUMN numero_chassis VARCHAR(100) NULL UNIQUE COMMENT 'Numéro de châssis du véhicule (unique)';

ALTER TABLE aed
ADD COLUMN modele VARCHAR(100) NULL COMMENT 'Modèle du véhicule (ex: Sprinter 515, Hiace, Rosa, etc.)';

ALTER TABLE aed
ADD COLUMN type_vehicule ENUM('TOURISME', 'COASTER', 'MINIBUS', 'AUTOCAR', 'AUTRE') NULL COMMENT 'Type de véhicule';

ALTER TABLE aed
ADD COLUMN marque VARCHAR(50) NULL COMMENT 'Marque du véhicule (ex: Mercedes, Toyota, Nissan, Hyundai, etc.)';

-- 2. Ajout d'index pour améliorer les performances de recherche
CREATE INDEX idx_aed_numero_chassis ON aed(numero_chassis);
CREATE INDEX idx_aed_marque ON aed(marque);
CREATE INDEX idx_aed_type_vehicule ON aed(type_vehicule);

-- 4. Commentaires sur les colonnes existantes pour documentation
ALTER TABLE aed 
MODIFY COLUMN numero VARCHAR(50) NOT NULL COMMENT 'Numéro AED unique du véhicule',
MODIFY COLUMN immatriculation VARCHAR(20) NOT NULL COMMENT 'Plaque d\'immatriculation',
MODIFY COLUMN nombre_places INT NOT NULL COMMENT 'Nombre de places assises';

-- 5. Vérification de la structure mise à jour
-- DESCRIBE aed;

-- 4. Optionnel: Remplir les nouveaux champs pour les AED existants
-- Décommentez et adaptez ces requêtes selon vos données existantes
/*
-- Exemple 1: AED Toyota Hiace
UPDATE aed SET
    numero_chassis = 'JTFHZ50E500123456',
    modele = 'Hiace',
    type_vehicule = 'MINIBUS',
    marque = 'Toyota'
WHERE numero = 'AED-001';

-- Exemple 2: AED Nissan Civilian
UPDATE aed SET
    numero_chassis = 'JN1TBNT35U0123456',
    modele = 'Civilian',
    type_vehicule = 'COASTER',
    marque = 'Nissan'
WHERE numero = 'AED-002';

-- Exemple 3: AED Mercedes Sprinter
UPDATE aed SET
    numero_chassis = 'WDB9066131234567',
    modele = 'Sprinter 515',
    type_vehicule = 'MINIBUS',
    marque = 'Mercedes'
WHERE numero = 'AED-003';
*/

-- 5. Requêtes de vérification après mise à jour

-- Vérifier la structure de la table
DESCRIBE aed;

-- Vérifier les données avec les nouveaux champs
SELECT
    numero,
    immatriculation,
    numero_chassis,
    marque,
    modele,
    type_vehicule,
    nombre_places,
    etat_vehicule
FROM aed
ORDER BY numero;

-- Vérifier les index créés
SHOW INDEX FROM aed WHERE Key_name IN ('idx_aed_numero_chassis', 'idx_aed_marque', 'idx_aed_type_vehicule');
