# 🚌 Transport UdM

**Système de Gestion des Transports - Université des Montagnes**

Application web complète pour la gestion de la flotte de transport universitaire, développée avec Flask et MySQL.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Rôles et Permissions](#-rôles-et-permissions)
- [API](#-api)
- [Contribution](#-contribution)

---

## ✨ Fonctionnalités

### Gestion des Trajets
- **Trajets internes UdM** : Enregistrement des déplacements avec bus universitaires
- **Trajets prestataires** : Gestion des bus loués auprès d'agences externes
- **Suivi en temps réel** : Visualisation du trafic étudiant (arrivées/départs)
- **Historique complet** : Traçabilité de tous les trajets effectués

### Gestion de la Flotte
- **Parc de bus UdM** : Suivi de l'état, kilométrage et disponibilité
- **Documents administratifs** : Alertes d'expiration (assurance, contrôle technique)
- **Maintenance préventive** : Planification des vidanges et révisions
- **Gestion du carburant** : Suivi des consommations et approvisionnements

### Gestion des Chauffeurs
- **Profils chauffeurs** : Informations personnelles et permis de conduire
- **Statuts en temps réel** : Disponibilité, en mission, en repos
- **Affectations** : Attribution des chauffeurs aux véhicules

### Rapports et Statistiques
- **Tableaux de bord** : Statistiques en temps réel par rôle
- **Rapports d'activité** : Synthèse journalière, hebdomadaire, mensuelle
- **Export PDF** : Génération de rapports imprimables
- **Audit complet** : Traçabilité des actions utilisateurs

### Sécurité et Authentification
- **Authentification multi-sources** : MySQL local ou LDAP/Active Directory
- **Gestion des rôles** : 6 profils avec permissions différenciées
- **Sessions sécurisées** : Protection CSRF, cookies HTTPOnly
- **Audit de sécurité** : Journalisation des connexions et actions sensibles

---

## 🏗 Architecture

```
transport_app/
├── app/
│   ├── __init__.py          # Factory Flask et configuration
│   ├── config.py             # Configuration multi-environnement
│   ├── constants.py          # Constantes centralisées
│   ├── database.py           # Instance SQLAlchemy
│   ├── extensions.py         # Extensions Flask
│   │
│   ├── models/               # Modèles de données (ORM)
│   │   ├── utilisateur.py    # Utilisateurs et authentification
│   │   ├── bus_udm.py        # Véhicules universitaires
│   │   ├── chauffeur.py      # Chauffeurs
│   │   ├── trajet.py         # Trajets
│   │   ├── carburation.py    # Carburant
│   │   ├── vidange.py        # Maintenance
│   │   └── ...
│   │
│   ├── routes/               # Contrôleurs (Blueprints)
│   │   ├── auth.py           # Authentification
│   │   ├── admin/            # Routes administrateur
│   │   ├── charge_transport.py
│   │   ├── chauffeur.py
│   │   ├── mecanicien.py
│   │   ├── superviseur.py
│   │   └── responsable.py
│   │
│   ├── services/             # Logique métier
│   │   ├── dashboard_service.py
│   │   ├── trajet_service.py
│   │   ├── form_service.py
│   │   └── ...
│   │
│   ├── forms/                # Formulaires WTForms
│   │   ├── trajet_interne_bus_udm_form.py
│   │   ├── trajet_prestataire_form.py
│   │   └── ...
│   │
│   ├── templates/            # Templates Jinja2
│   │   ├── layout.html       # Layout principal
│   │   ├── roles/            # Interfaces par rôle
│   │   ├── pages/            # Pages communes
│   │   └── partials/         # Composants réutilisables
│   │
│   ├── static/               # Assets statiques
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── utils/                # Utilitaires
│       ├── audit_logger.py   # Journalisation
│       ├── trafic.py         # Calculs trafic
│       └── ...
│
├── scripts/                  # Scripts SQL et utilitaires
├── logs/                     # Fichiers de logs
├── requirements.txt          # Dépendances Python
├── Dockerfile                # Image Docker
├── docker-compose.yml        # Orchestration Docker
└── README.md
```

### Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Backend** | Python 3.9+, Flask 2.3 |
| **ORM** | SQLAlchemy 2.0 |
| **Base de données** | MySQL 8.0 / MariaDB |
| **Authentification** | Flask-Login, LDAP3 |
| **Formulaires** | Flask-WTF, WTForms |
| **Frontend** | Bootstrap 5, JavaScript |
| **Conteneurisation** | Docker, Docker Compose |

---

## 🚀 Installation

### Prérequis

- Python 3.9 ou supérieur
- MySQL 8.0 ou MariaDB 10.5+
- Git

### Installation locale

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-repo/transport_app.git
cd transport_app

# 2. Créer un environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la base de données
mysql -u root -p < transport_udm.sql

# 5. Configurer les variables d'environnement
copy .env.example .env
# Éditer .env avec vos paramètres

# 6. Lancer l'application
python run.py
```

### Installation avec Docker

```bash
# Développement
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d
```

---

## ⚙ Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Application
FLASK_ENV=development
SECRET_KEY=votre_cle_secrete_unique

# Base de données
DATABASE_URL=mysql+pymysql://user:password@localhost/transport_udm

# LDAP (optionnel)
ENABLE_LDAP=false
LDAP_SERVER=ldap://votre-serveur-ldap
LDAP_BASE_DN=dc=example,dc=com

# Email (optionnel)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe
```

### Environnements disponibles

| Environnement | Description |
|---------------|-------------|
| `development` | Debug activé, CSRF désactivé, logs verbeux |
| `testing` | Base SQLite en mémoire, tests automatisés |
| `production` | Sécurité renforcée, logs minimaux |

---

## 📖 Utilisation

### Démarrage

```bash
# Mode développement
python run.py

# Ou avec Flask CLI
flask run --host=0.0.0.0 --port=5000
```

L'application sera accessible sur `http://localhost:5000`

### Comptes par défaut

| Rôle | Login | Mot de passe |
|------|-------|--------------|
| Administrateur | `admin` | `admin123` |
| Superviseur | `superviseur` | `superviseur123` |
| Responsable | `responsable` | `responsable123` |

---

## 👥 Rôles et Permissions

| Rôle | Description | Permissions |
|------|-------------|-------------|
| **ADMIN** | Administrateur système | Accès complet, gestion utilisateurs |
| **RESPONSABLE** | Responsable transport | Gestion trajets, rapports, traçabilité |
| **SUPERVISEUR** | Superviseur (lecture seule) | Consultation dashboards et rapports |
| **CHARGE** | Chargé de transport | Enregistrement trajets, gestion bus |
| **CHAUFFEUR** | Chauffeur | Consultation planning, mise à jour carburant |
| **MECANICIEN** | Mécanicien | Gestion maintenance, état véhicules |

---

## 🔌 API

### Endpoints principaux

```
POST /login                    # Authentification
GET  /admin/dashboard          # Dashboard administrateur
GET  /admin/stats              # Statistiques JSON
POST /admin/trajet_interne_bus_udm  # Nouveau trajet interne
POST /admin/trajet_prestataire_modernise  # Nouveau trajet prestataire
GET  /charge/dashboard         # Dashboard chargé transport
GET  /superviseur/dashboard    # Dashboard superviseur (lecture seule)
```

### Format de réponse

```json
{
  "success": true,
  "message": "Trajet enregistré avec succès",
  "data": { ... }
}
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=app tests/

# Tests spécifiques
pytest tests/test_trajets.py -v
```

---

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 📞 Support

- **Email** : support@transport-udm.com
- **Documentation** : [Wiki du projet](https://github.com/votre-repo/transport_app/wiki)

---

*Développé avec ❤️ pour l'Université des Montagnes* 