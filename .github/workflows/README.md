# CI / CD Workflows

## `ci.yml`

Pipeline d'intégration continue déclenchée à chaque push sur `main`/`develop`
et à chaque pull request vers `main`.

### Jobs

1. **`test`** — installe les dépendances Python, exécute la suite pytest avec
   couverture, et publie `coverage.xml` comme artefact.
2. **`sonarqube`** — relance les tests pour générer un `coverage.xml` frais,
   puis exécute le scanner SonarQube et vérifie le Quality Gate.

### Secrets GitHub requis

Configurer dans **Settings → Secrets and variables → Actions** :

| Secret | Description |
|---|---|
| `SONAR_TOKEN` | Token utilisateur SonarQube (`Account → Security → Tokens`) |
| `SONAR_HOST_URL` | URL publique de l'instance SonarQube (ex : `https://sonar.example.com`) |

### Critères de réussite

- Tous les tests pytest doivent passer (un `skip` pour template optionnel
  est toléré).
- Le Quality Gate SonarQube doit retourner `OK` :
  - 0 violation sur le nouveau code
  - ≥ 80 % de couverture sur le nouveau code
  - ≤ 3 % de duplications sur le nouveau code

### En local

```bash
# Tests + couverture
pytest --cov=app --cov-report=xml --cov-report=term -W ignore

# Scan SonarQube (Docker)
docker run --rm --network sonar-net \
  -e SONAR_HOST_URL="http://sonarqube:9000" \
  -e SONAR_TOKEN="<token>" \
  -v "${PWD}:/usr/src" \
  sonarsource/sonar-scanner-cli
```
