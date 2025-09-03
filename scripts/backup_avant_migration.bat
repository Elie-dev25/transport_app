@echo off
REM Script de sauvegarde avant migration Bus UdM
REM Date: 2025-09-03

echo ========================================
echo SAUVEGARDE AVANT MIGRATION BUS UDM
echo ========================================
echo.

REM Demander les informations de connexion
set /p DB_USER="Nom d'utilisateur MySQL: "
set /p DB_NAME="Nom de la base de donnees: "

REM Créer le nom du fichier de sauvegarde avec timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

set BACKUP_FILE=backup_bus_udm_%timestamp%.sql

echo.
echo Creation de la sauvegarde: %BACKUP_FILE%
echo.

REM Exécuter la sauvegarde
mysqldump -u %DB_USER% -p --single-transaction --routines --triggers %DB_NAME% > %BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SAUVEGARDE REUSSIE !
    echo ========================================
    echo Fichier cree: %BACKUP_FILE%
    echo Taille du fichier:
    dir %BACKUP_FILE% | find "%BACKUP_FILE%"
    echo.
    echo Vous pouvez maintenant executer la migration.
    echo.
) else (
    echo.
    echo ========================================
    echo ERREUR LORS DE LA SAUVEGARDE !
    echo ========================================
    echo Veuillez verifier vos parametres de connexion.
    echo.
)

pause
