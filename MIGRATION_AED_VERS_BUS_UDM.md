# Migration Complète : AED vers Bus UdM

## Vue d'ensemble

Ce document décrit la migration complète du système de gestion des véhicules de "AED" vers "Bus UdM" dans l'application Transport UdM.

## Changements effectués

### 1. Modèles de données

#### Anciens modèles → Nouveaux modèles
- `AED` → `BusUdM`
- `DocumentAED` → `DocumentBusUdM`
- `PanneAED` → `PanneBusUdM`

#### Tables de base de données
- `aed` → `bus_udm`
- `document_aed` → `document_bus_udm`
- `panne_aed` → `panne_bus_udm`

#### Colonnes renommées
- `numero_aed` → `numero_bus_udm`
- `aed_id` → `bus_udm_id`

### 2. Fichiers Python modifiés

#### Modèles
- `app/models/aed.py` → `app/models/bus_udm.py`
- `app/models/document_aed.py` → `app/models/document_bus_udm.py`
- `app/models/panne_aed.py` → `app/models/panne_bus_udm.py`

#### Formulaires
- `app/forms/aed_form.py` → `app/forms/bus_udm_form.py`
- `app/forms/panne_form.py` : Mise à jour des références

#### Routes et contrôleurs
- `app/routes/admin/gestion_bus.py` : Toutes les références AED → BusUdM
- `app/routes/admin/dashboard.py` : Imports et requêtes mis à jour
- `app/routes/admin/maintenance.py` : Imports et références mis à jour
- `app/routes/charge_transport.py` : Imports mis à jour
- Autres fichiers de routes : Imports mis à jour

### 3. Templates HTML

#### Templates renommés
- `app/templates/bus_aed.html` → `app/templates/bus_udm.html`
- `app/templates/depart_aed.html` → `app/templates/depart_bus_udm.html`

#### Templates modifiés
- `app/templates/partials/admin/_add_bus_modal.html`
- `app/templates/partials/admin/_declaration_panne_modal.html`
- Tous les templates contenant des références AED

### 4. Scripts et tests

#### Scripts renommés
- `scripts/test_aed_nouveaux_champs.py` → `scripts/test_bus_udm_nouveaux_champs.py`
- `scripts/create_panne_aed_table.py` → `scripts/create_panne_bus_udm_table.py`

#### Nouveaux scripts
- `scripts/migration_aed_vers_bus_udm.sql` : Script de migration de base de données

### 5. Routes AJAX mises à jour

#### Anciennes routes → Nouvelles routes
- `/admin/aed_list_ajax` → `/admin/bus_udm_list_ajax`
- Toutes les références dans le JavaScript

## Instructions de déploiement

### Étape 1 : Sauvegarde
```bash
# Effectuer une sauvegarde complète de la base de données
mysqldump -u username -p database_name > backup_before_migration.sql
```

### Étape 2 : Migration de la base de données
```bash
# Exécuter le script de migration
mysql -u username -p database_name < scripts/migration_aed_vers_bus_udm.sql
```

### Étape 3 : Mise à jour du code
```bash
# Les fichiers Python ont déjà été mis à jour
# Redémarrer l'application
python app.py
```

### Étape 4 : Tests
```bash
# Tester les nouveaux modèles
python scripts/test_bus_udm_nouveaux_champs.py
```

## Nouveaux champs Bus UdM

### Champs ajoutés
1. **numero_chassis** (VARCHAR(100), UNIQUE)
   - Numéro de châssis unique du véhicule
   - Exemple : "VF1234567890123456"

2. **modele** (VARCHAR(100))
   - Modèle du véhicule
   - Exemple : "Sprinter 515", "Hiace", "Civilian"

3. **type_vehicule** (ENUM)
   - Type de véhicule
   - Valeurs : TOURISME, COASTER, MINIBUS, AUTOCAR, AUTRE

4. **marque** (VARCHAR(50))
   - Marque du véhicule
   - Exemple : "Mercedes", "Toyota", "Nissan", "Hyundai"

## Interface utilisateur

### Changements visuels
- Titre des pages : "Bus AED" → "Bus UdM"
- Formulaires : "Ajouter un bus AED" → "Ajouter un bus UdM"
- Champs : "Numéro AED" → "Numéro Bus UdM"
- Préfixe par défaut : "AED-" → "UDM-"

### Nouvelles fonctionnalités
- Affichage des informations détaillées du véhicule (marque, modèle, type)
- Validation des nouveaux champs obligatoires
- Contrainte d'unicité sur le numéro de châssis

## Points d'attention

### Données existantes
- Les Bus UdM existants peuvent avoir des valeurs NULL pour les nouveaux champs
- Il est recommandé de mettre à jour ces données progressivement

### Compatibilité
- Toutes les fonctionnalités existantes sont préservées
- Les relations avec les autres tables (trajets, chauffeurs, etc.) sont maintenues

### Performance
- Index ajoutés sur les nouveaux champs pour optimiser les recherches
- Pas d'impact négatif sur les performances

## Rollback

En cas de problème, pour revenir à l'état précédent :

```sql
-- Restaurer la sauvegarde
mysql -u username -p database_name < backup_before_migration.sql

-- Ou exécuter les commandes inverses
RENAME TABLE bus_udm TO aed;
RENAME TABLE document_bus_udm TO document_aed;
RENAME TABLE panne_bus_udm TO panne_aed;
-- Puis restaurer les clés étrangères et colonnes originales
```

## Vérifications post-migration

### 1. Base de données
```sql
-- Vérifier les tables
SHOW TABLES LIKE '%bus_udm%';

-- Vérifier les données
SELECT COUNT(*) FROM bus_udm;
SELECT COUNT(*) FROM document_bus_udm;
SELECT COUNT(*) FROM panne_bus_udm;
```

### 2. Application
- [ ] Connexion à l'application réussie
- [ ] Affichage de la liste des Bus UdM
- [ ] Ajout d'un nouveau Bus UdM avec tous les champs
- [ ] Déclaration de panne fonctionnelle
- [ ] Gestion des documents administrative
- [ ] Enregistrement des trajets

### 3. Tests automatisés
```bash
python scripts/test_bus_udm_nouveaux_champs.py
```

## Support

En cas de problème lors de la migration :
1. Vérifier les logs de l'application
2. Contrôler l'état de la base de données
3. Exécuter les tests automatisés
4. Consulter ce document pour le rollback si nécessaire

## Conclusion

Cette migration transforme complètement la terminologie du système de "AED" vers "Bus UdM" tout en ajoutant des fonctionnalités importantes pour la gestion détaillée des véhicules. Toutes les fonctionnalités existantes sont préservées et améliorées.
