# 🔧 Guide de Dépannage - Bouton Déclaration de Panne

## 🎯 Problème Identifié
Le bouton de déclaration de panne ne fonctionne plus après les modifications des notifications.

## 🔍 Diagnostic Étape par Étape

### 1. **Vérification JavaScript (PRIORITÉ 1)**

**Action :** Ouvrir la console JavaScript
- Appuyez sur `F12` dans votre navigateur
- Allez dans l'onglet "Console"
- Cliquez sur le bouton de déclaration
- **Regardez s'il y a des erreurs en rouge**

**Erreurs possibles :**
```javascript
// Erreur d'import circulaire
ReferenceError: Cannot access 'NotificationService' before initialization

// Erreur de route
404 Not Found: /admin/declarer_panne

// Erreur de formulaire
TypeError: Cannot read property 'value' of null
```

### 2. **Vérification Réseau (PRIORITÉ 2)**

**Action :** Vérifier les requêtes HTTP
- Dans F12, allez dans l'onglet "Network" (Réseau)
- Cliquez sur le bouton de déclaration
- **Regardez si une requête POST est envoyée vers `/admin/declarer_panne`**

**Statuts possibles :**
- ✅ `200 OK` : Succès
- ⚠️ `302 Found` : Redirection (normal si pas connecté)
- ⚠️ `401 Unauthorized` : Non autorisé (normal si pas connecté)
- ❌ `404 Not Found` : Route non trouvée (PROBLÈME)
- ❌ `500 Internal Server Error` : Erreur serveur (PROBLÈME)

### 3. **Vérification Authentification**

**Action :** Vérifier que vous êtes connecté
- Êtes-vous connecté avec un compte ADMIN, RESPONSABLE ou MECANICIEN ?
- Le bouton de déclaration nécessite des droits d'administration

### 4. **Vérification Cache Navigateur**

**Action :** Vider le cache
- Appuyez sur `Ctrl + F5` pour recharger complètement
- Ou `Ctrl + Shift + R`
- Ou vider le cache dans les paramètres du navigateur

## 🛠️ Solutions par Type d'Erreur

### **Erreur JavaScript**
```javascript
// Si vous voyez des erreurs comme :
// "NotificationService is not defined"
// "Cannot import before initialization"
```

**Solution :** Le problème vient des imports circulaires
1. Redémarrez l'application Flask
2. Si le problème persiste, les notifications peuvent être temporairement désactivées

### **Erreur 404 - Route non trouvée**
```
POST /admin/declarer_panne 404 Not Found
```

**Solution :** La route n'est pas enregistrée
1. Vérifiez que l'application a bien démarré
2. Redémarrez l'application Flask
3. Vérifiez les logs de démarrage

### **Erreur 500 - Erreur serveur**
```
POST /admin/declarer_panne 500 Internal Server Error
```

**Solution :** Erreur dans le code backend
1. Regardez les logs de l'application Flask
2. L'erreur est probablement dans la route `declarer_panne`

### **Pas de requête envoyée**
Si aucune requête n'apparaît dans l'onglet Network :

**Solution :** Problème JavaScript
1. Vérifiez la console pour les erreurs
2. Le gestionnaire d'événement du bouton ne fonctionne pas

## 🔧 Actions de Correction Immédiates

### **Option 1 : Désactiver temporairement les notifications**

Si le problème vient des notifications, vous pouvez les désactiver temporairement :

1. **Ouvrir** `app/routes/admin/maintenance.py`
2. **Commenter** les lignes de notification :

```python
# Envoyer notification email
# try:
#     from app.services.notification_service import NotificationService
#     NotificationService.send_panne_notification(nouvelle_panne, enregistre_par)
# except Exception as e:
#     # Ne pas faire échouer la déclaration si l'email échoue
#     current_app.logger.warning(f"Échec notification panne: {str(e)}")
```

3. **Redémarrer** l'application

### **Option 2 : Revenir à la version précédente**

Si vous avez une sauvegarde de `app/routes/admin/maintenance.py` avant mes modifications :

1. **Restaurer** le fichier original
2. **Redémarrer** l'application
3. **Tester** le bouton

### **Option 3 : Correction rapide**

Remplacer l'import dans `app/routes/admin/maintenance.py` :

```python
# Au lieu de :
from app.services.notification_service import NotificationService

# Utiliser :
try:
    from app.services.notification_service import NotificationService
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
```

## 📋 Checklist de Vérification

- [ ] Console JavaScript vérifiée (F12)
- [ ] Onglet Network vérifié (F12)
- [ ] Cache navigateur vidé (Ctrl+F5)
- [ ] Authentification vérifiée (connecté avec bons droits)
- [ ] Application Flask redémarrée
- [ ] Logs de l'application vérifiés

## 🚨 Si Rien ne Fonctionne

**Action d'urgence :** Revenir à l'état précédent

1. **Sauvegarder** les fichiers de notification créés
2. **Restaurer** `app/routes/admin/maintenance.py` à son état original
3. **Redémarrer** l'application
4. **Tester** le bouton
5. **Réintégrer** les notifications progressivement

## 📞 Informations de Debug

**Fichiers modifiés récemment :**
- `app/routes/admin/maintenance.py` (ajout notifications)
- `app/services/maintenance_service.py` (ajout notifications)
- `app/services/notification_service.py` (nouveau)
- `app/config.py` (configuration SMTP)

**Routes critiques :**
- `POST /admin/declarer_panne` (déclaration)
- `POST /admin/enregistrer_depannage` (réparation)

**Logs à vérifier :**
- Console JavaScript du navigateur
- Logs de l'application Flask
- Logs d'erreur du serveur web

---

## 🎯 Prochaines Étapes

1. **Suivez ce guide étape par étape**
2. **Notez les erreurs exactes** que vous voyez
3. **Appliquez la solution correspondante**
4. **Testez le bouton après chaque correction**

Le problème est très probablement lié aux imports circulaires ou à un redémarrage nécessaire de l'application.
