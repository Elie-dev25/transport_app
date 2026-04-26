# Script PowerShell pour exécuter les tests avec couverture
# Usage: .\run_tests.ps1

Write-Host "Installation des dépendances de test..." -ForegroundColor Cyan
pip install pytest pytest-cov coverage

Write-Host "`nExécution des tests avec couverture..." -ForegroundColor Cyan
python -m pytest tests/ -v --cov=app --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-report=term-missing

Write-Host "`nRapport de couverture généré:" -ForegroundColor Green
Write-Host "  - XML: coverage.xml (pour SonarQube)" -ForegroundColor Yellow
Write-Host "  - HTML: htmlcov/index.html (pour visualisation)" -ForegroundColor Yellow

Write-Host "`nPour envoyer à SonarQube, ajoutez ces paramètres au scanner:" -ForegroundColor Cyan
Write-Host "  -Dsonar.python.coverage.reportPaths=coverage.xml" -ForegroundColor Yellow
