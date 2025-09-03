# Migration AED vers Bus UdM - Nouveaux Champs Véhicule

## Résumé des modifications

**CHANGEMENT MAJEUR** : Remplacement de "AED" par "Bus UdM" dans tout le projet.

Ajout de 4 nouveaux champs obligatoires lors de l'enregistrement d'un Bus UdM :
- **Numéro de châssis** (unique)
- **Modèle** du véhicule
- **Type** de véhicule (Tourisme, Coaster, Minibus, Autocar, Autre)
- **Marque** du véhicule

## Fichiers modifiés

### 1. Modèle de données
- `app/models/aed.py` : ✅ Déjà mis à jour avec les nouveaux champs

### 2. Formulaires
- `app/forms/aed_form.py` : ✅ Ajout des nouveaux champs avec validation
  - `numero_chassis` : StringField obligatoire, unique
  - `modele` : StringField obligatoire
  - `type_vehicule` : SelectField avec options prédéfinies
  - `marque` : StringField obligatoire

### 3. Routes et contrôleurs
- `app/routes/admin/gestion_bus.py` : ✅ Mise à jour des routes
  - Route POST `/admin/ajouter_bus` : Ajout des nouveaux champs
  - Route AJAX `/admin/ajouter_bus_ajax` : Ajout des nouveaux champs
  - Validation des champs obligatoires

### 4. Templates
- `app/templates/partials/admin/_add_bus_modal.html` : ✅ Formulaire modal mis à jour
  - Ajout des 4 nouveaux champs dans le formulaire
  - Validation côté client
- `app/templates/bus_aed.html` : ✅ Liste des AED mise à jour
  - Nouvelles colonnes : Immatriculation, Marque, Modèle, Type
  - Indicateur visuel pour données incomplètes

### 5. Base de données
- `scripts/update_aed_table.sql` : ✅ Script SQL pour MySQL
  - Ajout des 4 nouvelles colonnes
  - Contrainte d'unicité sur `numero_chassis`
  - Index pour améliorer les performances

### 6. Tests
- `scripts/test_aed_nouveaux_champs.py` : ✅ Script de test
  - Test de création d'AED avec nouveaux champs
  - Test des contraintes d'unicité
  - Validation des données

## Instructions de déploiement

### 1. Mise à jour de la base de données
```sql
-- Exécuter le script SQL
mysql -u votre_utilisateur -p votre_base_de_donnees < scripts/update_aed_table.sql
```

### 2. Test des modifications
```bash
# Tester les nouveaux champs
python scripts/test_aed_nouveaux_champs.py
```

### 3. Redémarrage de l'application
```bash
# Redémarrer l'application Flask
python app.py
```

## Nouveaux champs détaillés

### 1. Numéro de châssis (`numero_chassis`)
- **Type** : VARCHAR(100)
- **Contrainte** : UNIQUE, NULL autorisé
- **Exemple** : "VF1234567890123456"
- **Validation** : Minimum 5 caractères, maximum 100

### 2. Modèle (`modele`)
- **Type** : VARCHAR(100)
- **Contrainte** : NULL autorisé
- **Exemple** : "Sprinter 515", "Hiace", "Civilian"
- **Validation** : Minimum 2 caractères, maximum 100

### 3. Type de véhicule (`type_vehicule`)
- **Type** : ENUM('TOURISME', 'COASTER', 'MINIBUS', 'AUTOCAR', 'AUTRE')
- **Contrainte** : NULL autorisé
- **Options** :
  - TOURISME : Véhicules de tourisme
  - COASTER : Bus de type coaster
  - MINIBUS : Minibus
  - AUTOCAR : Autocars
  - AUTRE : Autres types

### 4. Marque (`marque`)
- **Type** : VARCHAR(50)
- **Contrainte** : NULL autorisé
- **Exemple** : "Mercedes", "Toyota", "Nissan", "Hyundai"
- **Validation** : Minimum 2 caractères, maximum 50

## Interface utilisateur

### Formulaire d'ajout d'AED
Le formulaire modal d'ajout d'AED inclut maintenant :
1. Numéro du bus (existant)
2. **Immatriculation** (existant)
3. **Numéro de châssis** (nouveau, obligatoire)
4. **Modèle** (nouveau, obligatoire)
5. **Type de véhicule** (nouveau, liste déroulante, obligatoire)
6. **Marque** (nouveau, obligatoire)
7. Autres champs existants...

### Liste des AED
La table des AED affiche maintenant :
- Numéro
- **Immatriculation**
- **Marque**
- **Modèle**
- **Type**
- Kilométrage
- État
- Places
- Actions

### Indicateurs visuels
- ⚠️ Icône d'avertissement pour les AED avec des informations véhicule incomplètes
- Affichage formaté des types de véhicules

## Validation et contraintes

### Côté serveur (Python)
- Tous les nouveaux champs sont obligatoires lors de la création
- Validation de longueur pour chaque champ
- Contrainte d'unicité sur le numéro de châssis

### Côté client (JavaScript)
- Validation HTML5 avec attribut `required`
- Messages d'erreur en cas de données manquantes

### Base de données (MySQL)
- Contrainte UNIQUE sur `numero_chassis`
- Index pour optimiser les recherches
- Types de données appropriés avec limites de taille

## Notes importantes

1. **Compatibilité** : Les AED existants peuvent avoir des champs NULL pour les nouveaux champs
2. **Migration** : Utilisez le script SQL fourni pour mettre à jour la structure
3. **Performance** : Index ajoutés sur les nouveaux champs pour optimiser les requêtes
4. **Validation** : Double validation côté client et serveur
5. **Unicité** : Le numéro de châssis doit être unique dans toute la base

## Prochaines étapes suggérées

1. Exécuter le script SQL de mise à jour
2. Tester l'ajout d'un nouvel AED avec tous les champs
3. Vérifier l'affichage dans la liste des AED
4. Mettre à jour les AED existants avec les nouvelles informations
5. Former les utilisateurs sur les nouveaux champs obligatoires
