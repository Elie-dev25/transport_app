#!/bin/bash

# Script de configuration des notifications email TransportUdM
# Pour Linux/Mac

echo "🔧 Configuration des Notifications Email - TransportUdM"
echo "============================================================"

# Vérifier si le script est exécuté avec les bonnes permissions
if [ "$EUID" -eq 0 ]; then
    echo "⚠️ Ne pas exécuter ce script en tant que root"
    exit 1
fi

echo ""
echo "📧 Configuration Gmail"
echo "IMPORTANT: Utilisez un mot de passe d'application Gmail (pas votre mot de passe principal)"
echo "1. Activez l'authentification à 2 facteurs sur Gmail"
echo "2. Générez un mot de passe d'application dans Paramètres Google > Sécurité"
echo "3. Entrez ce mot de passe d'application ci-dessous"

echo ""
read -s -p "Entrez le mot de passe d'application Gmail: " SMTP_PASSWORD
echo ""

# Créer le fichier .env
echo ""
echo "⚙️ Création du fichier .env..."

cat > .env << EOF
# Configuration des notifications email pour TransportUdM
# Généré automatiquement le $(date)

# Configuration SMTP pour Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=elienjine15@gmail.com
SMTP_PASSWORD=$SMTP_PASSWORD
SMTP_USE_TLS=true
SMTP_USE_SSL=false
MAIL_FROM=elienjine15@gmail.com

# Activation des notifications
ENABLE_EMAIL_NOTIFICATIONS=true

# Environnement
FLASK_ENV=development
EOF

# Sécuriser le fichier .env
chmod 600 .env

echo "✅ Fichier .env créé avec succès!"

# Exporter les variables pour la session actuelle
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="elienjine15@gmail.com"
export SMTP_PASSWORD="$SMTP_PASSWORD"
export SMTP_USE_TLS="true"
export SMTP_USE_SSL="false"
export MAIL_FROM="elienjine15@gmail.com"
export ENABLE_EMAIL_NOTIFICATIONS="true"

echo ""
echo "📋 Configuration actuelle:"
echo "SMTP_HOST: smtp.gmail.com"
echo "SMTP_PORT: 587"
echo "SMTP_USERNAME: elienjine15@gmail.com"
echo "SMTP_USE_TLS: true"
echo "MAIL_FROM: elienjine15@gmail.com"
echo "ENABLE_EMAIL_NOTIFICATIONS: true"

echo ""
echo "🔔 Types de notifications automatiques:"
echo "• Déclaration de panne → Mécanicien, Superviseur, Responsable"
echo "• Véhicule réparé → Responsable, Supervisable"
echo "• Seuil vidange critique → Responsable, Superviseur"
echo "• Seuil carburant critique → Responsable, Chauffeur, Superviseur"
echo "• Affectation statut chauffeur → Chauffeur concerné"

echo ""
echo "🧪 Pour tester la configuration:"
echo "python test_notifications.py config"

echo ""
echo "⚠️ IMPORTANT:"
echo "• Le fichier .env contient vos credentials - ne le partagez pas"
echo "• Ajoutez .env à votre .gitignore"
echo "• Gardez votre mot de passe d'application Gmail secret"

echo ""
echo "✅ Configuration terminée avec succès!"

# Nettoyer la variable
unset SMTP_PASSWORD
