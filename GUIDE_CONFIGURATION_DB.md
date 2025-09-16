# 🔧 GUIDE DE CONFIGURATION BASE DE DONNÉES

## ❌ **PROBLÈME RÉSOLU**

**Erreur rencontrée :**
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1049, "Unknown database 'transport_udm_dev'")
```

**Cause :** La nouvelle configuration centralisée utilisait automatiquement `DevelopmentConfig` qui tentait de se connecter à `transport_udm_dev` (base de développement) au lieu de `transport_udm` (base principale).

---

## ✅ **SOLUTION APPLIQUÉE**

### **1. Configuration corrigée (app/config.py)**

```python
class DevelopmentConfig(Config):
    # Base de données de développement (utilise la même DB que production pour l'instant)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:@localhost/transport_udm'
```

### **2. Logique de sélection améliorée (app/__init__.py)**

```python
# Utiliser la configuration de base pour éviter les problèmes de DB
env = os.environ.get("FLASK_ENV", "default")
if env == "production":
    from app.config import ProductionConfig as CurrentConfig
elif env == "development":
    from app.config import DevelopmentConfig as CurrentConfig
else:
    # Configuration par défaut (utilise transport_udm)
    from app.config import Config as CurrentConfig
```

---

## 🎯 **CONFIGURATIONS DISPONIBLES**

### **Configuration par défaut (recommandée)**
```bash
# Aucune variable d'environnement nécessaire
python run.py
```
- **Base de données :** `transport_udm`
- **Debug :** `False`
- **CSRF :** `Activé`

### **Configuration de développement**
```bash
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # Linux/Mac
python run.py
```
- **Base de données :** `transport_udm` (corrigé)
- **Debug :** `True`
- **CSRF :** `Désactivé`

### **Configuration de production**
```bash
set FLASK_ENV=production  # Windows
export FLASK_ENV=production  # Linux/Mac
python run.py
```
- **Base de données :** `transport_udm`
- **Debug :** `False`
- **Sécurité :** `Renforcée`

---

## 🛠️ **OUTILS DE GESTION**

### **Script de gestion d'environnement**
```bash
# Voir la configuration actuelle
python set_env.py show

# Définir un environnement
python set_env.py default
python set_env.py development
python set_env.py production
```

### **Test de connexion base de données**
```bash
python test_db_connection.py
```

---

## 🚨 **RÉSOLUTION DE PROBLÈMES**

### **Erreur "Unknown database"**

**Symptôme :** `(1049, "Unknown database 'nom_base'")`

**Solutions :**
1. **Vérifier la base de données existe :**
   ```sql
   SHOW DATABASES;
   ```

2. **Créer la base si nécessaire :**
   ```sql
   CREATE DATABASE transport_udm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Utiliser la configuration par défaut :**
   ```bash
   # Ne pas définir FLASK_ENV ou définir explicitement
   set FLASK_ENV=default
   ```

### **Erreur de connexion MySQL**

**Symptôme :** `(2003, "Can't connect to MySQL server")`

**Solutions :**
1. **Vérifier MySQL est démarré**
2. **Vérifier les paramètres de connexion dans config.py**
3. **Tester la connexion manuellement :**
   ```bash
   mysql -u root -p -h localhost
   ```

### **Erreur d'authentification**

**Symptôme :** `(1045, "Access denied for user")`

**Solutions :**
1. **Vérifier les identifiants MySQL**
2. **Modifier la chaîne de connexion :**
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://utilisateur:motdepasse@localhost/transport_udm'
   ```

---

## 📋 **CHECKLIST DE VÉRIFICATION**

### **Avant de démarrer l'application :**

- [ ] MySQL est démarré
- [ ] Base de données `transport_udm` existe
- [ ] Identifiants de connexion corrects
- [ ] Variable `FLASK_ENV` définie si nécessaire
- [ ] Test de connexion réussi (`python test_db_connection.py`)

### **En cas de problème :**

1. [ ] Vérifier les logs d'erreur
2. [ ] Tester la connexion base de données
3. [ ] Vérifier la configuration utilisée
4. [ ] Utiliser la configuration par défaut
5. [ ] Redémarrer MySQL si nécessaire

---

## 🎉 **STATUT ACTUEL**

✅ **Problème résolu !**
- Configuration corrigée
- Application démarre sans erreur
- Base de données accessible
- Services refactorisés fonctionnels

**L'application Transport UdM est maintenant opérationnelle avec la nouvelle architecture refactorisée !**
