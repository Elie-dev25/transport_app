# Script PowerShell pour configurer les notifications email TransportUdM
# Exécutez ce script en tant qu'administrateur

Write-Host "🔧 Configuration des Notifications Email - TransportUdM" -ForegroundColor Cyan
Write-Host "=" * 60

# Demander le mot de passe d'application Gmail
Write-Host "`n📧 Configuration Gmail" -ForegroundColor Yellow
Write-Host "IMPORTANT: Utilisez un mot de passe d'application Gmail (pas votre mot de passe principal)"
Write-Host "1. Activez l'authentification à 2 facteurs sur Gmail"
Write-Host "2. Générez un mot de passe d'application dans Paramètres Google > Sécurité"
Write-Host "3. Entrez ce mot de passe d'application ci-dessous"

$smtpPassword = Read-Host -Prompt "`nEntrez le mot de passe d'application Gmail" -AsSecureString
$smtpPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($smtpPassword))

# Configuration des variables d'environnement
Write-Host "`n⚙️ Configuration des variables d'environnement..." -ForegroundColor Green

try {
    # Variables SMTP
    [Environment]::SetEnvironmentVariable("SMTP_HOST", "smtp.gmail.com", "User")
    [Environment]::SetEnvironmentVariable("SMTP_PORT", "587", "User")
    [Environment]::SetEnvironmentVariable("SMTP_USERNAME", "elienjine15@gmail.com", "User")
    [Environment]::SetEnvironmentVariable("SMTP_PASSWORD", $smtpPasswordPlain, "User")
    [Environment]::SetEnvironmentVariable("SMTP_USE_TLS", "true", "User")
    [Environment]::SetEnvironmentVariable("SMTP_USE_SSL", "false", "User")
    [Environment]::SetEnvironmentVariable("MAIL_FROM", "elienjine15@gmail.com", "User")
    
    # Activation des notifications
    [Environment]::SetEnvironmentVariable("ENABLE_EMAIL_NOTIFICATIONS", "true", "User")
    
    Write-Host "✅ Variables d'environnement configurées avec succès!" -ForegroundColor Green
    
    # Afficher la configuration
    Write-Host "`n📋 Configuration actuelle:" -ForegroundColor Cyan
    Write-Host "SMTP_HOST: smtp.gmail.com"
    Write-Host "SMTP_PORT: 587"
    Write-Host "SMTP_USERNAME: elienjine15@gmail.com"
    Write-Host "SMTP_USE_TLS: true"
    Write-Host "MAIL_FROM: elienjine15@gmail.com"
    Write-Host "ENABLE_EMAIL_NOTIFICATIONS: true"
    
    Write-Host "`n🔔 Types de notifications automatiques:" -ForegroundColor Yellow
    Write-Host "• Déclaration de panne → Mécanicien, Superviseur, Responsable"
    Write-Host "• Véhicule réparé → Responsable, Superviseur"
    Write-Host "• Seuil vidange critique → Responsable, Superviseur"
    Write-Host "• Seuil carburant critique → Responsable, Chauffeur, Superviseur"
    Write-Host "• Affectation statut chauffeur → Chauffeur concerné"
    
    Write-Host "`n🧪 Pour tester la configuration:" -ForegroundColor Cyan
    Write-Host "python test_notifications.py config"
    
    Write-Host "`n⚠️ IMPORTANT:" -ForegroundColor Red
    Write-Host "• Redémarrez votre terminal/IDE pour que les variables prennent effet"
    Write-Host "• Gardez votre mot de passe d'application Gmail secret"
    Write-Host "• Ne partagez jamais vos credentials SMTP"
    
    Write-Host "`n✅ Configuration terminée avec succès!" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Erreur lors de la configuration:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host "`nVeuillez exécuter ce script en tant qu'administrateur"
}

# Nettoyer la variable en mémoire
$smtpPasswordPlain = $null

Write-Host "`nAppuyez sur une touche pour continuer..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
