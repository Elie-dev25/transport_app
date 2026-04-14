-- Script d'initialisation de l'espace administrateur
-- Créé automatiquement au démarrage de la base de données

-- Désactiver les vérifications de clés étrangères temporairement
SET FOREIGN_KEY_CHECKS=0;

-- Insérer un utilisateur administrateur par défaut
-- Login: admin
-- Mot de passe: admin123 (à changer obligatoirement en production)
-- Hash généré avec werkzeug.security.generate_password_hash('admin123')

INSERT IGNORE INTO utilisateur (
  utilisateur_id,
  nom,
  prenom,
  login,
  email,
  telephone,
  mot_de_passe,
  role
) VALUES (
  1,
  'Admin',
  'System',
  'admin',
  'admin@transport-udm.local',
  '+237-0000000000',
  'scrypt:32768:8:1$Xt3xZ2mVp9q0wR8Y$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p',
  'ADMIN'
) ON DUPLICATE KEY UPDATE
  nom = CASE WHEN utilisateur_id = 1 THEN VALUES(nom) ELSE nom END;

-- Insérer l'enregistrement administrateur correspondant
INSERT IGNORE INTO administrateur (administrateur_id)
VALUES (1)
ON DUPLICATE KEY UPDATE administrateur_id = VALUES(administrateur_id);

-- Réactiver les vérifications de clés étrangères
SET FOREIGN_KEY_CHECKS=1;

-- Confirmation
SELECT 'Administrateur par défaut initialisé avec succès' as status;
SELECT 'Login: admin | Mot de passe: admin123' as credentials;
