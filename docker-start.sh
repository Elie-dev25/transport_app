#!/bin/bash

# Script de démarrage Docker pour TransportUdM
# Usage: ./docker-start.sh [dev|prod]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_message() {
    echo -e "${BLUE}[TransportUdM]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi

    print_success "Docker et Docker Compose sont installés"
}

# Vérifier le fichier .env
check_env_file() {
    if [ ! -f .env ]; then
        print_warning "Fichier .env non trouvé. Création depuis .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Veuillez modifier le fichier .env avec vos configurations"
            print_warning "Notamment: SECRET_KEY, SMTP_PASSWORD, mots de passe MySQL"
        else
            print_error "Fichier .env.example non trouvé"
            exit 1
        fi
    else
        print_success "Fichier .env trouvé"
    fi
}

# Mode de déploiement
MODE=${1:-dev}

print_message "🚀 Démarrage de TransportUdM en mode: $MODE"
print_message "=================================================="

# Vérifications préliminaires
check_docker
check_env_file

# Arrêter les conteneurs existants
print_message "Arrêt des conteneurs existants..."
docker-compose down --remove-orphans

# Construire les images
print_message "Construction des images Docker..."
docker-compose build --no-cache

# Démarrer selon le mode
case $MODE in
    "dev"|"development")
        print_message "Démarrage en mode développement..."
        print_message "Utilisation de docker-compose.dev.yml avec hot reload"

        docker-compose -f docker-compose.dev.yml down --remove-orphans
        docker-compose -f docker-compose.dev.yml build --no-cache
        docker-compose -f docker-compose.dev.yml up -d db

        print_message "Attente de la base de données..."
        sleep 30

        print_message "Démarrage de l'application avec hot reload..."
        docker-compose -f docker-compose.dev.yml up web
        ;;
        
    "prod"|"production")
        print_message "Démarrage en mode production..."
        docker-compose --profile production up -d
        
        print_message "Attente du démarrage complet..."
        sleep 30
        
        # Vérifier que les services sont en cours d'exécution
        if docker-compose ps | grep -q "Up"; then
            print_success "Services démarrés avec succès!"
            print_message "Application disponible sur:"
            print_message "  - HTTP: http://localhost"
            print_message "  - Direct Flask: http://localhost:5000"
            print_message "  - Base de données: localhost:3306"
        else
            print_error "Erreur lors du démarrage des services"
            docker-compose logs
            exit 1
        fi
        ;;
        
    "stop")
        print_message "Arrêt de tous les services..."
        docker-compose down
        print_success "Services arrêtés"
        ;;
        
    "logs")
        print_message "Affichage des logs..."
        docker-compose logs -f
        ;;
        
    "status")
        print_message "État des services:"
        docker-compose ps
        docker-compose -f docker-compose.dev.yml ps
        ;;

    "tools")
        print_message "Démarrage avec outils de développement..."
        docker-compose -f docker-compose.dev.yml --profile tools up -d

        print_message "Outils disponibles:"
        print_message "  - Adminer (DB): http://localhost:8080"
        print_message "  - MailHog (Email): http://localhost:8025"
        print_message "  - Application: http://localhost:5000"
        ;;

    *)
        print_error "Mode non reconnu: $MODE"
        print_message "Usage: $0 [dev|prod|stop|logs|status|tools]"
        print_message "  dev   - Mode développement (avec hot reload)"
        print_message "  prod  - Mode production (avec Nginx)"
        print_message "  stop  - Arrêter tous les services"
        print_message "  logs  - Afficher les logs"
        print_message "  status - Afficher l'état des services"
        print_message "  tools - Démarrer avec outils de dev (Adminer, MailHog)"
        exit 1
        ;;
esac

print_success "Opération terminée!"
