# 📧 Guide des Notifications Email - TransportUdM

## 🎯 Vue d'ensemble

Le système de notifications email de TransportUdM envoie automatiquement des emails lors d'événements critiques pour informer les utilisateurs concernés.

## 📋 Types de Notifications

### 1. 🚨 Déclaration de Panne
**Déclencheur :** Lorsqu'une nouvelle panne est déclarée  
**Destinataires :** Mécanicien, Superviseur, Responsable  
**Contenu :**
- Détails du véhicule (numéro, immatriculation)
- Date/heure de la panne
- Kilométrage
- Niveau de criticité
- Description de la panne
- Statut d'immobilisation

### 2. ✅ Véhicule Réparé
**Déclencheur :** Lorsqu'une panne est marquée comme résolue  
**Destinataires :** Responsable, Superviseur  
**Contenu :**
- Détails du véhicule
- Date de déclaration et de résolution
- Personne ayant effectué la réparation
- Description de la panne initiale

### 3. 🔧 Seuil Vidange Critique
**Déclencheur :** Véhicule atteint 5000 km depuis dernière vidange  
**Destinataires :** Responsable, Superviseur  
**Contenu :**
- Détails du véhicule
- Kilométrage actuel
- Kilomètres depuis dernière vidange
- Dépassement du seuil

### 4. ⛽ Seuil Carburant Critique
**Déclencheur :** Niveau carburant ≤ 20%  
**Destinataires :** Responsable, Chauffeur, Superviseur  
**Contenu :**
- Détails du véhicule
- Niveau actuel en litres et pourcentage
- Capacité totale du réservoir

### 5. 👨‍💼 Affectation Statut Chauffeur
**Déclencheur :** Nouveau statut affecté à un chauffeur  
**Destinataire :** Le chauffeur concerné uniquement  
**Contenu :**
- Détails du statut (type, lieu, dates)
- Instructions spécifiques selon le statut
- Informations de contact

## ⚙️ Configuration

### Variables d'Environnement Requises

```bash
# Configuration SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=elienjine15@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app
SMTP_USE_TLS=true
MAIL_FROM=elienjine15@gmail.com
```

### Configuration Gmail

1. **Activer l'authentification à 2 facteurs**
2. **Générer un mot de passe d'application :**
   - Aller dans Paramètres Google → Sécurité
   - Mots de passe d'application
   - Créer un nouveau mot de passe pour "TransportUdM"
3. **Utiliser ce mot de passe d'application** (pas votre mot de passe Gmail)

## 🔧 Architecture Technique

### Services Principaux

#### `NotificationService`
- `send_panne_notification()` - Notification panne
- `send_vehicule_repare_notification()` - Notification réparation
- `send_seuil_vidange_notification()` - Alerte vidange
- `send_seuil_carburant_notification()` - Alerte carburant
- `send_statut_chauffeur_notification()` - Notification statut
- `test_email_configuration()` - Test configuration

#### `AlertService`
- `check_all_critical_thresholds()` - Vérification globale
- `check_vidange_threshold()` - Vérification vidange
- `check_carburant_threshold()` - Vérification carburant
- `get_buses_needing_maintenance()` - Liste buses maintenance

### Intégration dans les Services

Les notifications sont automatiquement déclenchées dans :
- `MaintenanceService.create_panne()` → Notification panne
- `MaintenanceService.resolve_panne()` → Notification réparation
- `gestion_utilisateurs.modifier_statut_chauffeur_ajax()` → Notification statut

## 🧪 Tests et Validation

### Script de Test
```bash
# Test complet du système
python test_notifications.py

# Test configuration uniquement
python test_notifications.py config

# Aide configuration
python test_notifications.py help
```

### Interface d'Administration
Accès via `/admin/notifications` pour :
- Tester la configuration email
- Envoyer des notifications de test
- Vérifier les seuils critiques
- Voir les buses nécessitant maintenance

## 📊 Monitoring et Logs

### Logs d'Audit
Toutes les notifications sont enregistrées dans les logs d'audit avec :
- Type d'action : `NOTIFICATION`
- Ressource concernée
- Nombre d'emails envoyés
- Statut de succès/échec

### Gestion d'Erreurs
- Les erreurs d'email n'interrompent pas les opérations métier
- Logs détaillés pour le débogage
- Fallback gracieux en cas d'échec SMTP

## 🔒 Sécurité

### Bonnes Pratiques
- Mots de passe d'application Gmail (jamais le mot de passe principal)
- Variables d'environnement pour les credentials
- Validation des adresses email
- Limitation du spam avec logique de déduplication

### Protection des Données
- Aucun mot de passe en clair dans les logs
- Emails chiffrés via TLS
- Audit trail complet

## 🚀 Déploiement

### Environnement de Développement
```bash
# Configuration minimale pour tests
export SMTP_HOST="smtp.gmail.com"
export SMTP_USERNAME="elienjine15@gmail.com"
export SMTP_PASSWORD="mot_de_passe_app"
export MAIL_FROM="elienjine15@gmail.com"
```

### Environnement de Production
- Utiliser un serveur SMTP dédié si possible
- Configurer la surveillance des emails
- Mettre en place des alertes de monitoring
- Sauvegarder les logs de notifications

## 🔍 Dépannage

### Problèmes Courants

#### Email non reçu
1. Vérifier la configuration SMTP
2. Contrôler les logs d'erreur
3. Tester avec `test_notifications.py config`
4. Vérifier les dossiers spam

#### Erreur d'authentification Gmail
1. Vérifier l'authentification 2FA activée
2. Régénérer le mot de passe d'application
3. Utiliser le bon format d'email

#### Notifications en double
- Le système inclut une logique de déduplication
- Vérifier les logs pour identifier la cause

### Commandes de Diagnostic
```bash
# Test configuration
python test_notifications.py config

# Vérification complète
python test_notifications.py

# Logs en temps réel
tail -f app.log | grep NOTIFICATION
```

## 📈 Évolutions Futures

### Améliorations Prévues
- Interface de gestion des templates d'email
- Notifications SMS en complément
- Tableau de bord des statistiques d'envoi
- Personnalisation des seuils par véhicule
- Notifications push pour l'application mobile

### Extensibilité
Le système est conçu pour être facilement extensible :
- Nouveaux types de notifications
- Nouveaux canaux (SMS, push, Slack)
- Règles de routage avancées
- Templates personnalisables

---

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs d'audit
2. Utiliser les outils de test intégrés
3. Vérifier la configuration SMTP
4. Contacter l'équipe de développement

**Email configuré :** elienjine15@gmail.com  
**Interface admin :** `/admin/notifications`  
**Script de test :** `test_notifications.py`
