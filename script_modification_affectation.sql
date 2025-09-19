-- =====================================================
-- SCRIPT DE MODIFICATION DE LA TABLE CHAUFFEUR_STATUT
-- Ajout du champ 'lieu' et mise à jour des données
-- =====================================================

-- 1. Ajouter la colonne 'lieu' à la table chauffeur_statut
ALTER TABLE chauffeur_statut
ADD COLUMN lieu ENUM('CUM', 'CAMPUS', 'CONJOINTEMENT') NOT NULL DEFAULT 'CUM'
COMMENT 'Lieu d\'affectation du chauffeur';

-- 2. Remplir le nouveau champ pour les statuts existants
-- Logique de remplissage basée sur le type de statut
UPDATE chauffeur_statut
SET lieu = CASE
    WHEN statut = 'SERVICE_SEMAINE' THEN 'CAMPUS'
    WHEN statut = 'SERVICE_WEEKEND' THEN 'CUM'
    WHEN statut = 'PERMANENCE' THEN 'CONJOINTEMENT'
    WHEN statut = 'CONGE' THEN 'CUM'
    ELSE 'CUM'
END;

-- 3. Vérifier les modifications
SELECT
    id,
    chauffeur_id,
    statut,
    lieu,
    date_debut,
    date_fin
FROM chauffeur_statut
ORDER BY id;

-- 4. Afficher un résumé des modifications
SELECT
    '=== RÉSUMÉ DES MODIFICATIONS ===' as message
UNION ALL
SELECT CONCAT('✅ Colonne lieu ajoutée à la table chauffeur_statut') as message
UNION ALL
SELECT CONCAT('✅ ', COUNT(*), ' statuts mis à jour') as message FROM chauffeur_statut
UNION ALL
SELECT '=== RÉPARTITION PAR LIEU ===' as message
UNION ALL
SELECT CONCAT('📍 CUM: ', COUNT(*), ' statuts') as message
FROM chauffeur_statut WHERE lieu = 'CUM'
UNION ALL
SELECT CONCAT('📍 CAMPUS: ', COUNT(*), ' statuts') as message
FROM chauffeur_statut WHERE lieu = 'CAMPUS'
UNION ALL
SELECT CONCAT('📍 CONJOINTEMENT: ', COUNT(*), ' statuts') as message
FROM chauffeur_statut WHERE lieu = 'CONJOINTEMENT'
UNION ALL
SELECT '=== STRUCTURE FINALE ===' as message
UNION ALL
SELECT 'Table chauffeur_statut mise à jour avec succès !' as message;

-- 5. Vérifier la structure de la table
DESCRIBE chauffeur_statut;
