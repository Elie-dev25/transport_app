-- Script pour ajouter le champ point_arrivee à la table trajet
-- Date: 2025-09-03

-- ATTENTION: Effectuez une sauvegarde avant d'exécuter ce script !

-- ========================================
-- AJOUTER LA COLONNE POINT_ARRIVEE
-- ========================================

-- Ajouter la nouvelle colonne point_arrivee
ALTER TABLE trajet 
ADD COLUMN point_arrivee VARCHAR(100) NULL 
COMMENT 'Lieu d\'arrivée du trajet';

-- ========================================
-- MIGRATION DES DONNÉES EXISTANTES
-- ========================================

-- Pour les trajets existants, définir point_arrivee basé sur la logique actuelle:
-- - Si point_depart = 'Mfetum' ou 'Ancienne Mairie', alors point_arrivee = 'Banekane'
-- - Si point_depart = 'Banekane', alors point_arrivee = 'Mfetum' (par défaut)

UPDATE trajet 
SET point_arrivee = 'Banekane' 
WHERE point_depart IN ('Mfetum', 'Ancienne Mairie', 'Ancienne mairie') 
AND point_arrivee IS NULL;

UPDATE trajet 
SET point_arrivee = 'Mfetum' 
WHERE point_depart = 'Banekane' 
AND point_arrivee IS NULL;

-- Pour les trajets avec des points de départ non standard, définir une arrivée par défaut
UPDATE trajet 
SET point_arrivee = 'Banekane' 
WHERE point_arrivee IS NULL;

-- ========================================
-- VÉRIFICATIONS POST-MIGRATION
-- ========================================

-- Vérifier la structure de la table
DESCRIBE trajet;

-- Vérifier les données migrées
SELECT 
    point_depart,
    point_arrivee,
    COUNT(*) as nombre_trajets
FROM trajet 
GROUP BY point_depart, point_arrivee
ORDER BY point_depart, point_arrivee;

-- Vérifier qu'il n'y a pas de valeurs NULL
SELECT COUNT(*) as trajets_sans_arrivee 
FROM trajet 
WHERE point_arrivee IS NULL;

SELECT 'Migration terminée avec succès !' AS statut;
