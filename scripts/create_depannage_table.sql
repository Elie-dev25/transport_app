-- Script de création de la table depannage
-- À exécuter après avoir créé la table panne_bus_udm

-- Créer la table depannage
CREATE TABLE IF NOT EXISTS depannage (
  id INT AUTO_INCREMENT PRIMARY KEY,
  panne_id INT NULL,
  bus_udm_id INT NULL,
  numero_bus_udm VARCHAR(50) NOT NULL,
  immatriculation VARCHAR(50) NULL,
  date_heure DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  kilometrage DECIMAL(12,2) NULL,
  cout_reparation DECIMAL(12,2) NULL,
  description_panne TEXT NOT NULL,
  cause_panne TEXT NULL,
  repare_par VARCHAR(100) NOT NULL,
  
  -- Contraintes de clés étrangères
  CONSTRAINT fk_depannage_panne
    FOREIGN KEY (panne_id) REFERENCES panne_bus_udm(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_depannage_bus
    FOREIGN KEY (bus_udm_id) REFERENCES bus_udm(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Index pour améliorer les performances
CREATE INDEX idx_depannage_numero_bus ON depannage(numero_bus_udm);
CREATE INDEX idx_depannage_date ON depannage(date_heure);
