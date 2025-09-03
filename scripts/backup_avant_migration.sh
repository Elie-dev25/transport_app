#!/bin/bash
# Script de sauvegarde avant migration Bus UdM
# Date: 2025-09-03

echo "========================================"
echo "SAUVEGARDE AVANT MIGRATION BUS UDM"
echo "========================================"
echo

# Demander les informations de connexion
read -p "Nom d'utilisateur MySQL: " DB_USER
read -p "Nom de la base de données: " DB_NAME

# Créer le nom du fichier de sauvegarde avec timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="backup_bus_udm_${TIMESTAMP}.sql"

echo
echo "Création de la sauvegarde: $BACKUP_FILE"
echo

# Exécuter la sauvegarde
mysqldump -u "$DB_USER" -p --single-transaction --routines --triggers "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo "SAUVEGARDE RÉUSSIE !"
    echo "========================================"
    echo "Fichier créé: $BACKUP_FILE"
    echo "Taille du fichier: $(ls -lh $BACKUP_FILE | awk '{print $5}')"
    echo
    echo "Vous pouvez maintenant exécuter la migration."
    echo
else
    echo
    echo "========================================"
    echo "ERREUR LORS DE LA SAUVEGARDE !"
    echo "========================================"
    echo "Veuillez vérifier vos paramètres de connexion."
    echo
fi

read -p "Appuyez sur Entrée pour continuer..."
