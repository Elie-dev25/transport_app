# Script PowerShell de démarrage Docker pour TransportUdM
# Usage: .\docker-start.ps1 [dev|prod|stop|logs|status]

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "development", "prod", "production", "stop", "logs", "status")]
    [string]$Mode = "dev"
)

# Fonction d'affichage avec couleurs
function Write-Message {
    param([string]$Message, [string]$Color = "Blue")
    Write-Host "[TransportUdM] $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Vérifier que Docker est installé
function Test-Docker {
    try {
        $dockerVersion = docker --version
        $composeVersion = docker-compose --version
        Write-Success "Docker et Docker Compose sont installés"
        return $true
    }
    catch {
        Write-Error "Docker ou Docker Compose n'est pas installé ou accessible"
        Write-Error "Veuillez installer Docker Desktop pour Windows"
        return $false
    }
}

# Vérifier le fichier .env
function Test-EnvFile {
    if (-not (Test-Path ".env")) {
        Write-Warning "Fichier .env non trouvé"
        if (Test-Path ".env.example") {
            Write-Warning "Création du fichier .env depuis .env.example..."
            Copy-Item ".env.example" ".env"
            Write-Warning "Veuillez modifier le fichier .env avec vos configurations"
            Write-Warning "Notamment: SECRET_KEY, SMTP_PASSWORD, mots de passe MySQL"
        }
        else {
            Write-Error "Fichier .env.example non trouvé"
            return $false
        }
    }
    else {
        Write-Success "Fichier .env trouvé"
    }
    return $true
}

# Script principal
Write-Message "🚀 Démarrage de TransportUdM en mode: $Mode"
Write-Message "=================================================="

# Vérifications préliminaires
if (-not (Test-Docker)) {
    exit 1
}

if (-not (Test-EnvFile)) {
    exit 1
}

# Exécution selon le mode
switch ($Mode) {
    { $_ -in "dev", "development" } {
        Write-Message "Démarrage en mode développement..."
        
        # Arrêter les conteneurs existants
        Write-Message "Arrêt des conteneurs existants..."
        docker-compose down --remove-orphans
        
        # Construire les images
        Write-Message "Construction des images Docker..."
        docker-compose build --no-cache
        
        # Démarrer la base de données
        Write-Message "Démarrage de la base de données..."
        docker-compose up -d db
        
        # Attendre que la DB soit prête
        Write-Message "Attente de la base de données..."
        Start-Sleep -Seconds 30
        
        # Démarrer l'application
        Write-Message "Démarrage de l'application..."
        docker-compose up web
    }
    
    { $_ -in "prod", "production" } {
        Write-Message "Démarrage en mode production..."
        
        # Arrêter les conteneurs existants
        docker-compose down --remove-orphans
        
        # Construire les images
        Write-Message "Construction des images Docker..."
        docker-compose build --no-cache
        
        # Démarrer tous les services
        docker-compose --profile production up -d
        
        Write-Message "Attente du démarrage complet..."
        Start-Sleep -Seconds 30
        
        # Vérifier l'état des services
        $services = docker-compose ps
        if ($services -match "Up") {
            Write-Success "Services démarrés avec succès!"
            Write-Message "Application disponible sur:"
            Write-Message "  - HTTP: http://localhost"
            Write-Message "  - Direct Flask: http://localhost:5000"
            Write-Message "  - Base de données: localhost:3306"
        }
        else {
            Write-Error "Erreur lors du démarrage des services"
            docker-compose logs
            exit 1
        }
    }
    
    "stop" {
        Write-Message "Arrêt de tous les services..."
        docker-compose down
        Write-Success "Services arrêtés"
    }
    
    "logs" {
        Write-Message "Affichage des logs..."
        docker-compose logs -f
    }
    
    "status" {
        Write-Message "État des services:"
        docker-compose ps
    }
}

Write-Success "Opération terminée!"

# Pause pour voir les messages (optionnel)
if ($Mode -in "prod", "production", "dev", "development") {
    Write-Message "Appuyez sur une touche pour continuer..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
