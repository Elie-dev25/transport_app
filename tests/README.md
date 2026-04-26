# Tests TransportUdM

## Installation des dépendances de test

```bash
pip install pytest pytest-cov coverage
```

## Exécution des tests

### Tests simples
```bash
python -m pytest tests/ -v
```

### Tests avec couverture
```bash
python -m pytest tests/ -v --cov=app --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-report=term-missing
```

## Envoi à SonarQube

Après avoir généré le rapport de couverture (`coverage.xml`), relancez l'analyse SonarQube :

```bash
docker run --rm --network sonar-net ^
  -e SONAR_HOST_URL="http://sonarqube:9000" ^
  -e SONAR_TOKEN="squ_46eb0ee624a4d13e3e75f6331504a4229cf52459" ^
  -v "%cd%:/usr/src" ^
  sonarsource/sonar-scanner-cli
```

Le fichier `sonar-project.properties` est configuré pour lire `coverage.xml`.

## Structure des tests

```
tests/
├── conftest.py              # Fixtures communes
├── test_config.py           # Tests de configuration
├── test_constants.py        # Tests des constantes
├── test_models/             # Tests des modèles
│   ├── test_utilisateur.py
│   ├── test_bus_udm.py
│   ├── test_chauffeur.py
│   ├── test_trajet.py
│   ├── test_vidange.py
│   ├── test_carburation.py
│   └── test_depannage.py
├── test_routes/             # Tests des routes
│   └── test_auth.py
├── test_services/           # Tests des services
│   └── test_trajet_service.py
└── test_utils/              # Tests des utilitaires
    └── test_audit_logger.py
```
