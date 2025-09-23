# Dockerfile pour l'application TransportUdM
# Version multi-stage pour optimiser la taille de l'image finale

# ===== STAGE 1: Builder =====
FROM python:3.11-slim as builder

# Métadonnées
LABEL maintainer="Transport UdM Team"
LABEL description="Système de gestion des transports - Université des Montagnes"
LABEL version="2.0.0"

# Variables d'environnement pour le build
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système nécessaires pour la compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Créer le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ===== STAGE 2: Runtime =====
FROM python:3.11-slim as runtime

# Variables d'environnement pour la production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV FLASK_APP=run.py

# Installer uniquement les dépendances runtime nécessaires
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Créer l'utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs/audit /app/uploads \
    && chown -R appuser:appuser /app

# Copier les dépendances Python depuis le stage builder
COPY --from=builder /root/.local /home/appuser/.local

# Définir le répertoire de travail
WORKDIR /app

# Copier le code de l'application
COPY --chown=appuser:appuser . .

# Créer les répertoires manquants et ajuster les permissions
RUN mkdir -p logs/audit uploads instance \
    && chown -R appuser:appuser logs uploads instance \
    && chmod 755 logs uploads instance

# Passer à l'utilisateur non-root
USER appuser

# Ajouter le répertoire local Python au PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Port d'exposition
EXPOSE 5000

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Point d'entrée par défaut
CMD ["python", "run.py"]
