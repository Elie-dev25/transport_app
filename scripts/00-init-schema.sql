-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mar. 23 sep. 2025 à 15:46
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `transport_udm`
--

-- --------------------------------------------------------

--
-- Structure de la table `administrateur`
--

CREATE TABLE `administrateur` (
  `administrateur_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `administrateur`
--

INSERT INTO `administrateur` (`administrateur_id`) VALUES
(14),
(15),
(33);

-- --------------------------------------------------------

--
-- Structure de la table `affectation`
--

CREATE TABLE `affectation` (
  `affectation_id` int(11) NOT NULL,
  `type_affectation` enum('EN_SEMAINE','WEEK_END','PERMANENCE','CONGE') NOT NULL,
  `date_debut` date NOT NULL,
  `date_fin` date NOT NULL,
  `chauffeur_id` int(11) NOT NULL,
  `planifie_par` int(11) DEFAULT NULL,
  `lieu` enum('CUM','CAMPUS','CONJOINTEMENT') NOT NULL DEFAULT 'CUM' COMMENT 'Lieu d''affectation du chauffeur'
) ;

-- --------------------------------------------------------

--
-- Structure de la table `bus_udm`
--

CREATE TABLE `bus_udm` (
  `id` int(11) NOT NULL,
  `numero` varchar(50) NOT NULL,
  `immatriculation` varchar(20) NOT NULL,
  `etat_vehicule` enum('BON','DEFAILLANT') NOT NULL DEFAULT 'BON' COMMENT 'État du véhicule',
  `nombre_places` int(11) NOT NULL CHECK (`nombre_places` >= 1),
  `derniere_maintenance` date DEFAULT NULL,
  `kilometrage` int(11) DEFAULT NULL COMMENT 'Niveau de kilométrage actuel en km',
  `type_huile` varchar(50) DEFAULT NULL,
  `km_critique_huile` int(11) DEFAULT NULL COMMENT 'Kilométrage critique pour l''huile',
  `km_critique_carburant` int(11) DEFAULT NULL COMMENT 'Kilométrage critique pour le carburant',
  `capacite_plein_carburant` int(11) DEFAULT NULL COMMENT 'Capacité du plein de carburant en km',
  `date_derniere_vidange` date DEFAULT NULL COMMENT 'Date de la dernière vidange',
  `capacite_reservoir_litres` double DEFAULT NULL,
  `niveau_carburant_litres` double DEFAULT NULL,
  `consommation_km_par_litre` float DEFAULT NULL,
  `numero_chassis` varchar(100) NOT NULL,
  `modele` varchar(100) DEFAULT NULL,
  `type_vehicule` enum('TOURISME','COASTER','MINIBUS','AUTOCAR','AUTRE') DEFAULT NULL,
  `marque` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `bus_udm`
--

-- --------------------------------------------------------

--
-- Structure de la table `carburation`
--

CREATE TABLE `carburation` (
  `id` int(11) NOT NULL,
  `bus_udm_id` int(11) NOT NULL,
  `date_carburation` date NOT NULL,
  `kilometrage` int(11) NOT NULL,
  `quantite_litres` decimal(10,2) NOT NULL CHECK (`quantite_litres` >= 0),
  `prix_unitaire` decimal(10,2) NOT NULL CHECK (`prix_unitaire` >= 0),
  `cout_total` decimal(10,2) NOT NULL CHECK (`cout_total` >= 0),
  `remarque` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `carburation`
--


-- --------------------------------------------------------

--
-- Structure de la table `chargetransport`
--

CREATE TABLE `chargetransport` (
  `chargetransport_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `chargetransport`
--

INSERT INTO `chargetransport` (`chargetransport_id`) VALUES
(2),
(10),
(35),
(37);

-- --------------------------------------------------------

--
-- Structure de la table `chauffeur`
--

CREATE TABLE `chauffeur` (
  `chauffeur_id` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `numero_permis` varchar(50) NOT NULL,
  `telephone` varchar(20) NOT NULL,
  `date_delivrance_permis` date NOT NULL,
  `date_expiration_permis` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--

-- --------------------------------------------------------

--
-- Structure de la table `chauffeur_statut`
--

CREATE TABLE `chauffeur_statut` (
  `id` int(11) NOT NULL,
  `chauffeur_id` int(11) NOT NULL,
  `statut` enum('CONGE','PERMANENCE','SERVICE_WEEKEND','SERVICE_SEMAINE') NOT NULL,
  `date_debut` datetime NOT NULL,
  `date_fin` datetime NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `lieu` enum('CUM','CAMPUS','CONJOINTEMENT') NOT NULL DEFAULT 'CUM' COMMENT 'Lieu d''affectation du chauffeur'
) ;

--

-- Déclencheurs `chauffeur_statut`
--
DELIMITER $$
CREATE TRIGGER `bi_chauffeur_statut_rule` BEFORE INSERT ON `chauffeur_statut` FOR EACH ROW BEGIN
  IF NEW.statut = 'CONGE' THEN
    IF EXISTS (
      SELECT 1 FROM chauffeur_statut s
      WHERE s.chauffeur_id = NEW.chauffeur_id
        AND NOT (NEW.date_fin <= s.date_debut OR NEW.date_debut >= s.date_fin)
    ) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Chevauchement interdit: CONGE doit être exclusif';
    END IF;
  ELSE
    IF EXISTS (
      SELECT 1 FROM chauffeur_statut s
      WHERE s.chauffeur_id = NEW.chauffeur_id
        AND s.statut = 'CONGE'
        AND NOT (NEW.date_fin <= s.date_debut OR NEW.date_debut >= s.date_fin)
    ) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Chevauchement interdit avec une période de CONGE';
    END IF;
  END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `bu_chauffeur_statut_rule` BEFORE UPDATE ON `chauffeur_statut` FOR EACH ROW BEGIN
  IF NEW.statut = 'CONGE' THEN
    IF EXISTS (
      SELECT 1 FROM chauffeur_statut s
      WHERE s.chauffeur_id = NEW.chauffeur_id
        AND s.id <> OLD.id
        AND NOT (NEW.date_fin <= s.date_debut OR NEW.date_debut >= s.date_fin)
    ) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Chevauchement interdit: CONGE doit être exclusif';
    END IF;
  ELSE
    IF EXISTS (
      SELECT 1 FROM chauffeur_statut s
      WHERE s.chauffeur_id = NEW.chauffeur_id
        AND s.id <> OLD.id
        AND s.statut = 'CONGE'
        AND NOT (NEW.date_fin <= s.date_debut OR NEW.date_debut >= s.date_fin)
    ) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Chevauchement interdit avec une période de CONGE';
    END IF;
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `connexion_historique`
--

CREATE TABLE `connexion_historique` (
  `log_id` int(11) NOT NULL,
  `utilisateur_id` int(11) NOT NULL,
  `date_connexion` datetime NOT NULL,
  `ip_adresse` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `demandehuile`
--

CREATE TABLE `demandehuile` (
  `demande_huile_id` int(11) NOT NULL,
  `date_demande` date NOT NULL,
  `statut_demande` enum('EN_ATTENTE','APPROUVEE') NOT NULL,
  `numero_aed` varchar(50) NOT NULL,
  `mecanicien_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `depannage`
--

CREATE TABLE `depannage` (
  `id` int(11) NOT NULL,
  `panne_id` int(11) DEFAULT NULL,
  `bus_udm_id` int(11) DEFAULT NULL,
  `numero_bus_udm` varchar(50) NOT NULL,
  `immatriculation` varchar(50) DEFAULT NULL,
  `date_heure` datetime NOT NULL DEFAULT current_timestamp(),
  `kilometrage` decimal(12,2) DEFAULT NULL,
  `cout_reparation` decimal(12,2) DEFAULT NULL,
  `description_panne` text NOT NULL,
  `cause_panne` text DEFAULT NULL,
  `repare_par` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `depannage`
--

--
-- Structure de la table `document_bus_udm`
--

CREATE TABLE `document_bus_udm` (
  `document_id` int(11) NOT NULL,
  `numero_bus_udm` varchar(50) NOT NULL,
  `type_document` enum('VISITE_TECHNIQUE','ASSURANCE_VIGNETTE','TAXE_STATIONNEMENT','TAXE_PUBLICITAIRE','CARTE_GRISE') NOT NULL,
  `date_debut` date NOT NULL,
  `date_expiration` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--

--
-- Structure de la table `fuel_alert_state`
--

CREATE TABLE `fuel_alert_state` (
  `id` int(11) NOT NULL,
  `bus_udm_id` int(11) NOT NULL,
  `last_threshold` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `mecanicien`
--

CREATE TABLE `mecanicien` (
  `mecanicien_id` int(11) NOT NULL,
  `numero_permis` varchar(50) NOT NULL,
  `date_delivrance_permis` date NOT NULL,
  `date_expiration_permis` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-
--
-- Structure de la table `notification`
--

CREATE TABLE `notification` (
  `notification_id` int(11) NOT NULL,
  `utilisateur_id` int(11) NOT NULL,
  `message` varchar(255) NOT NULL,
  `date_notification` datetime NOT NULL DEFAULT current_timestamp(),
  `lue` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `panne_bus_udm`
--

CREATE TABLE `panne_bus_udm` (
  `id` int(11) NOT NULL,
  `bus_udm_id` int(11) DEFAULT NULL,
  `numero_bus_udm` varchar(50) NOT NULL,
  `immatriculation` varchar(50) DEFAULT NULL,
  `kilometrage` double DEFAULT NULL,
  `date_heure` datetime NOT NULL DEFAULT current_timestamp(),
  `description` text NOT NULL,
  `criticite` enum('FAIBLE','MOYENNE','HAUTE') NOT NULL,
  `immobilisation` tinyint(1) NOT NULL DEFAULT 0,
  `enregistre_par` varchar(100) NOT NULL,
  `resolue` tinyint(1) NOT NULL DEFAULT 0,
  `date_resolution` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `panne_bus_udm`
--

--
-- Structure de la table `presencecampus`
--

CREATE TABLE `presencecampus` (
  `date_presence` date NOT NULL,
  `nombre_arrives` int(11) NOT NULL DEFAULT 0 CHECK (`nombre_arrives` >= 0),
  `nombre_partis` int(11) NOT NULL DEFAULT 0 CHECK (`nombre_partis` >= 0),
  `mise_a_jour_par` int(11) DEFAULT NULL,
  `nombre_presents` int(11) GENERATED ALWAYS AS (`nombre_arrives` - `nombre_partis`) STORED
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `prestataire`
--

CREATE TABLE `prestataire` (
  `id` int(11) NOT NULL,
  `nom_prestataire` varchar(100) NOT NULL COMMENT 'Nom du prestataire',
  `telephone` varchar(20) DEFAULT NULL,
  `localisation` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `prestataire`
--

-- --------------------------------------------------------

--
-- Structure de la table `rapport_journalier`
--

CREATE TABLE `rapport_journalier` (
  `rapport_id` int(11) NOT NULL,
  `date_rapport` date NOT NULL,
  `createur_id` int(11) NOT NULL,
  `contenu` text NOT NULL,
  `date_creation` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `trajet`
--

CREATE TABLE `trajet` (
  `trajet_id` int(11) NOT NULL,
  `type_trajet` enum('UDM_INTERNE','PRESTATAIRE','AUTRE') NOT NULL,
  `prestataire_id` int(11) DEFAULT NULL,
  `date_heure_depart` datetime NOT NULL,
  `point_depart` enum('Mfetum','Ancienne Mairie','Banekane') NOT NULL,
  `type_passagers` enum('ETUDIANT','PERSONNEL','MALADE','INVITER','MALADE_PERSONNEL') DEFAULT NULL,
  `nombre_places_occupees` int(11) DEFAULT NULL,
  `chauffeur_id` int(11) DEFAULT NULL,
  `numero_bus_udm` varchar(50) DEFAULT NULL,
  `immat_bus` varchar(20) DEFAULT NULL,
  `nom_chauffeur` varchar(100) DEFAULT NULL,
  `enregistre_par` int(11) DEFAULT NULL,
  `point_arriver` varchar(100) DEFAULT NULL,
  `motif` varchar(255) DEFAULT NULL
) ;

--
-- Déchargement des données de la table `trajet`
--

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

CREATE TABLE `utilisateur` (
  `utilisateur_id` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `login` varchar(50) NOT NULL,
  `email` varchar(255) NOT NULL,
  `telephone` varchar(50) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL,
  `reset_token` varchar(100) DEFAULT NULL,
  `reset_expires` datetime DEFAULT NULL,
  `role` enum('ADMIN','CHAUFFEUR','MECANICIEN','CHARGE','SUPERVISEUR','RESPONSABLE') DEFAULT NULL
) ;

--
-- Déchargement des données de la table `utilisateur`
--

-- Déclencheurs `utilisateur`
--
DELIMITER $$
CREATE TRIGGER `before_delete_utilisateur_admin` BEFORE DELETE ON `utilisateur` FOR EACH ROW BEGIN
  IF OLD.role = 'ADMIN' THEN
    DELETE FROM administrateur WHERE administrateur_id = OLD.utilisateur_id;
  END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `before_delete_utilisateur_charge` BEFORE DELETE ON `utilisateur` FOR EACH ROW BEGIN
  IF OLD.role = 'CHARGE' THEN
    DELETE FROM chargetransport WHERE chargetransport_id = OLD.utilisateur_id;
  END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `before_delete_utilisateur_chauffeur` BEFORE DELETE ON `utilisateur` FOR EACH ROW BEGIN
  IF OLD.role = 'CHAUFFEUR' THEN
    DELETE FROM chauffeur WHERE chauffeur_id = OLD.utilisateur_id;
  END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `before_delete_utilisateur_mecanicien` BEFORE DELETE ON `utilisateur` FOR EACH ROW BEGIN
  IF OLD.role = 'MECANICIEN' THEN
    DELETE FROM mecanicien WHERE mecanicien_id = OLD.utilisateur_id;
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `vidange`
--

CREATE TABLE `vidange` (
  `id` int(11) NOT NULL,
  `bus_udm_id` int(11) NOT NULL,
  `date_vidange` date NOT NULL,
  `kilometrage` int(11) NOT NULL,
  `type_huile` enum('QUARTZ','RUBIA') NOT NULL,
  `remarque` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--


-- Index pour les tables déchargées
--

--
-- Index pour la table `administrateur`
--
ALTER TABLE `administrateur`
  ADD PRIMARY KEY (`administrateur_id`);

--
-- Index pour la table `affectation`
--
ALTER TABLE `affectation`
  ADD PRIMARY KEY (`affectation_id`),
  ADD KEY `chauffeur_id` (`chauffeur_id`),
  ADD KEY `planifie_par` (`planifie_par`);

--
-- Index pour la table `bus_udm`
--
ALTER TABLE `bus_udm`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero` (`numero`),
  ADD UNIQUE KEY `unique_immatriculation` (`immatriculation`),
  ADD UNIQUE KEY `numero_chassis` (`numero_chassis`);

--
-- Index pour la table `carburation`
--
ALTER TABLE `carburation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `aed_id` (`bus_udm_id`),
  ADD KEY `idx_carburation_aed_id` (`bus_udm_id`);

--
-- Index pour la table `chargetransport`
--
ALTER TABLE `chargetransport`
  ADD PRIMARY KEY (`chargetransport_id`);

--
-- Index pour la table `chauffeur`
--
ALTER TABLE `chauffeur`
  ADD PRIMARY KEY (`chauffeur_id`);

--
-- Index pour la table `chauffeur_statut`
--
ALTER TABLE `chauffeur_statut`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_chauffeur_period` (`chauffeur_id`,`date_debut`,`date_fin`);

--
-- Index pour la table `connexion_historique`
--
ALTER TABLE `connexion_historique`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `utilisateur_id` (`utilisateur_id`);

--
-- Index pour la table `demandehuile`
--
ALTER TABLE `demandehuile`
  ADD PRIMARY KEY (`demande_huile_id`),
  ADD KEY `numero_aed` (`numero_aed`),
  ADD KEY `mecanicien_id` (`mecanicien_id`);

--
-- Index pour la table `depannage`
--
ALTER TABLE `depannage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_depannage_panne` (`panne_id`),
  ADD KEY `fk_depannage_bus` (`bus_udm_id`);

--
-- Index pour la table `document_bus_udm`
--
ALTER TABLE `document_bus_udm`
  ADD PRIMARY KEY (`document_id`),
  ADD KEY `document_bus_udm_ibfk_1` (`numero_bus_udm`);

--
-- Index pour la table `fuel_alert_state`
--
ALTER TABLE `fuel_alert_state`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `aed_id` (`bus_udm_id`),
  ADD UNIQUE KEY `uq_fuel_alert_state_aed` (`bus_udm_id`);

--
-- Index pour la table `mecanicien`
--
ALTER TABLE `mecanicien`
  ADD PRIMARY KEY (`mecanicien_id`);

--
-- Index pour la table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `utilisateur_id` (`utilisateur_id`);

--
-- Index pour la table `panne_bus_udm`
--
ALTER TABLE `panne_bus_udm`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_panne_aed_aed_id` (`bus_udm_id`),
  ADD KEY `idx_panne_aed_numero` (`numero_bus_udm`),
  ADD KEY `idx_panne_aed_date` (`date_heure`);

--
-- Index pour la table `presencecampus`
--
ALTER TABLE `presencecampus`
  ADD PRIMARY KEY (`date_presence`),
  ADD KEY `mise_a_jour_par` (`mise_a_jour_par`);

--
-- Index pour la table `prestataire`
--
ALTER TABLE `prestataire`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_nom_prestataire` (`nom_prestataire`),
  ADD UNIQUE KEY `unique_telephone` (`telephone`),
  ADD UNIQUE KEY `unique_email` (`email`);

--
-- Index pour la table `rapport_journalier`
--
ALTER TABLE `rapport_journalier`
  ADD PRIMARY KEY (`rapport_id`),
  ADD KEY `createur_id` (`createur_id`);

--
-- Index pour la table `trajet`
--
ALTER TABLE `trajet`
  ADD PRIMARY KEY (`trajet_id`),
  ADD KEY `chauffeur_id` (`chauffeur_id`),
  ADD KEY `enregistre_par` (`enregistre_par`),
  ADD KEY `idx_depart_type` (`point_depart`,`type_passagers`),
  ADD KEY `trajet_ibfk_1` (`numero_bus_udm`),
  ADD KEY `fk_trajet_prestataire` (`prestataire_id`);

--
-- Index pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  ADD PRIMARY KEY (`utilisateur_id`),
  ADD UNIQUE KEY `login` (`login`),
  ADD UNIQUE KEY `unique_email` (`email`);

--
-- Index pour la table `vidange`
--
ALTER TABLE `vidange`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_vidange_aed_id` (`bus_udm_id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `affectation`
--
ALTER TABLE `affectation`
  MODIFY `affectation_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `bus_udm`
--
ALTER TABLE `bus_udm`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT pour la table `carburation`
--
ALTER TABLE `carburation`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT pour la table `chauffeur`
--
ALTER TABLE `chauffeur`
  MODIFY `chauffeur_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT pour la table `chauffeur_statut`
--
ALTER TABLE `chauffeur_statut`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `connexion_historique`
--
ALTER TABLE `connexion_historique`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `demandehuile`
--
ALTER TABLE `demandehuile`
  MODIFY `demande_huile_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `depannage`
--
ALTER TABLE `depannage`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT pour la table `document_bus_udm`
--
ALTER TABLE `document_bus_udm`
  MODIFY `document_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT pour la table `fuel_alert_state`
--
ALTER TABLE `fuel_alert_state`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `notification`
--
ALTER TABLE `notification`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `panne_bus_udm`
--
ALTER TABLE `panne_bus_udm`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT pour la table `prestataire`
--
ALTER TABLE `prestataire`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `rapport_journalier`
--
ALTER TABLE `rapport_journalier`
  MODIFY `rapport_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `trajet`
--
ALTER TABLE `trajet`
  MODIFY `trajet_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  MODIFY `utilisateur_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `vidange`
--
ALTER TABLE `vidange`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `administrateur`
--
ALTER TABLE `administrateur`
  ADD CONSTRAINT `administrateur_ibfk_1` FOREIGN KEY (`administrateur_id`) REFERENCES `utilisateur` (`utilisateur_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `affectation`
--
ALTER TABLE `affectation`
  ADD CONSTRAINT `affectation_ibfk_1` FOREIGN KEY (`chauffeur_id`) REFERENCES `chauffeur` (`chauffeur_id`),
  ADD CONSTRAINT `affectation_ibfk_2` FOREIGN KEY (`planifie_par`) REFERENCES `administrateur` (`administrateur_id`);

--
-- Contraintes pour la table `carburation`
--
ALTER TABLE `carburation`
  ADD CONSTRAINT `carburation_ibfk_1` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_carburation_aed_id` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON UPDATE CASCADE;

--
-- Contraintes pour la table `chargetransport`
--
ALTER TABLE `chargetransport`
  ADD CONSTRAINT `chargetransport_ibfk_1` FOREIGN KEY (`chargetransport_id`) REFERENCES `utilisateur` (`utilisateur_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `chauffeur_statut`
--
ALTER TABLE `chauffeur_statut`
  ADD CONSTRAINT `fk_chauffeur_statut_chauffeur` FOREIGN KEY (`chauffeur_id`) REFERENCES `chauffeur` (`chauffeur_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `connexion_historique`
--
ALTER TABLE `connexion_historique`
  ADD CONSTRAINT `connexion_historique_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateur` (`utilisateur_id`);

--
-- Contraintes pour la table `demandehuile`
--
ALTER TABLE `demandehuile`
  ADD CONSTRAINT `demandehuile_ibfk_1` FOREIGN KEY (`numero_aed`) REFERENCES `bus_udm` (`numero`),
  ADD CONSTRAINT `demandehuile_ibfk_2` FOREIGN KEY (`mecanicien_id`) REFERENCES `mecanicien` (`mecanicien_id`);

--
-- Contraintes pour la table `depannage`
--
ALTER TABLE `depannage`
  ADD CONSTRAINT `fk_depannage_bus` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_depannage_panne` FOREIGN KEY (`panne_id`) REFERENCES `panne_bus_udm` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Contraintes pour la table `document_bus_udm`
--
ALTER TABLE `document_bus_udm`
  ADD CONSTRAINT `document_bus_udm_ibfk_1` FOREIGN KEY (`numero_bus_udm`) REFERENCES `bus_udm` (`numero`),
  ADD CONSTRAINT `fk_document_aed` FOREIGN KEY (`numero_bus_udm`) REFERENCES `bus_udm` (`numero`);

--
-- Contraintes pour la table `fuel_alert_state`
--
ALTER TABLE `fuel_alert_state`
  ADD CONSTRAINT `fk_fuel_alert_aed` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_fuel_alert_state_aed` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fuel_alert_state_ibfk_1` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`);

--
-- Contraintes pour la table `mecanicien`
--
ALTER TABLE `mecanicien`
  ADD CONSTRAINT `mecanicien_ibfk_1` FOREIGN KEY (`mecanicien_id`) REFERENCES `utilisateur` (`utilisateur_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `notification`
--
ALTER TABLE `notification`
  ADD CONSTRAINT `notification_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateur` (`utilisateur_id`);

--
-- Contraintes pour la table `panne_bus_udm`
--
ALTER TABLE `panne_bus_udm`
  ADD CONSTRAINT `fk_panne_aed_aed_id` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_panne_aed_numero` FOREIGN KEY (`numero_bus_udm`) REFERENCES `bus_udm` (`numero`) ON UPDATE CASCADE,
  ADD CONSTRAINT `panne_bus_udm_ibfk_1` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`);

--
-- Contraintes pour la table `presencecampus`
--
ALTER TABLE `presencecampus`
  ADD CONSTRAINT `presencecampus_ibfk_1` FOREIGN KEY (`mise_a_jour_par`) REFERENCES `chargetransport` (`chargetransport_id`);

--
-- Contraintes pour la table `rapport_journalier`
--
ALTER TABLE `rapport_journalier`
  ADD CONSTRAINT `rapport_journalier_ibfk_1` FOREIGN KEY (`createur_id`) REFERENCES `administrateur` (`administrateur_id`);

--
-- Contraintes pour la table `trajet`
--
ALTER TABLE `trajet`
  ADD CONSTRAINT `fk_trajet_prestataire` FOREIGN KEY (`prestataire_id`) REFERENCES `prestataire` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `trajet_ibfk_2` FOREIGN KEY (`numero_bus_udm`) REFERENCES `bus_udm` (`numero`),
  ADD CONSTRAINT `trajet_ibfk_4` FOREIGN KEY (`enregistre_par`) REFERENCES `chargetransport` (`chargetransport_id`);

--
-- Contraintes pour la table `vidange`
--
ALTER TABLE `vidange`
  ADD CONSTRAINT `fk_vidange_aed` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_vidange_aed_id` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `vidange_ibfk_1` FOREIGN KEY (`bus_udm_id`) REFERENCES `bus_udm` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
